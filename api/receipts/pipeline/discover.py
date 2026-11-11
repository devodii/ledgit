from datetime import UTC, datetime, time

from receipts.connectors.youtube import YouTubeConnector, passes_gates
from receipts.db.connection import Conn, connect
from receipts.models.registry import EventSeed
from receipts.models.talks import VideoMeta
from receipts.pipeline.common import write_report
from receipts.registry.loader import sync_event


def run_discover(seed: EventSeed) -> list[VideoMeta]:
    youtube = YouTubeConnector()
    drops: dict[str, int] = {}
    seen: dict[str, VideoMeta] = {}
    for playlist in seed.discovery.playlists:
        for video in youtube.list_playlist(playlist):
            seen.setdefault(video.video_id, video)
    after = (
        datetime.combine(seed.discovery.published_after, time.min, tzinfo=UTC)
        if seed.discovery.published_after
        else None
    )
    before = (
        datetime.combine(seed.discovery.published_before, time.max, tzinfo=UTC)
        if seed.discovery.published_before
        else None
    )
    accepted: list[VideoMeta] = []
    rejected: list[tuple[VideoMeta, str]] = []
    for video in seen.values():
        ok, reason = passes_gates(video, seed.discovery.title_must_match, None, None)
        if not ok:
            rejected.append((video, reason))
            continue
        meta = youtube.metadata(video.video_id)
        ok, reason = passes_gates(meta, [], after, before)
        if ok:
            accepted.append(meta)
        else:
            rejected.append((meta, reason))
    for _, reason in rejected:
        drops[reason] = drops.get(reason, 0) + 1
    accepted.sort(key=lambda v: v.video_id)
    if len(accepted) > seed.limits.max_videos:
        drops["over_max_videos"] = len(accepted) - seed.limits.max_videos
        accepted = accepted[: seed.limits.max_videos]
    with connect() as conn:
        sync_event(conn, seed)
        for meta in accepted:
            _upsert_talk(conn, seed.slug, meta, True, None)
        for meta, reason in rejected:
            _upsert_talk(conn, seed.slug, meta, False, reason)
        conn.commit()
    write_report("discover", seed.slug, len(seen), len(accepted), drops)
    return accepted


def _upsert_talk(
    conn: Conn, event: str, meta: VideoMeta, accepted: bool, reason: str | None
) -> None:
    conn.execute(
        """
        INSERT INTO talks (
            video_id, event_slug, title, channel, published_at, url, accepted, skip_reason
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (video_id) DO UPDATE SET
            title = EXCLUDED.title, channel = EXCLUDED.channel,
            published_at = EXCLUDED.published_at, accepted = EXCLUDED.accepted,
            skip_reason = EXCLUDED.skip_reason
        """,
        (
            meta.video_id,
            event,
            meta.title,
            meta.channel,
            meta.published_at,
            meta.url,
            accepted,
            reason,
        ),
    )
