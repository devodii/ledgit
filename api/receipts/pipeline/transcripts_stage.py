import json

from receipts.connectors.transcripts import NoCaptions, TranscriptConnector
from receipts.db.connection import connect
from receipts.pipeline.common import write_report


def run_transcripts(event: str) -> int:
    connector = TranscriptConnector()
    drops: dict[str, int] = {}
    stored = 0
    with connect() as conn:
        talks = conn.execute(
            "SELECT video_id FROM talks WHERE event_slug = %s AND accepted ORDER BY video_id",
            (event,),
        ).fetchall()
        for talk in talks:
            video_id = talk["video_id"]
            try:
                transcript = connector.fetch(video_id)
            except NoCaptions:
                drops["no_captions"] = drops.get("no_captions", 0) + 1
                conn.execute(
                    "UPDATE talks SET accepted = FALSE, skip_reason = 'no_captions' "
                    "WHERE video_id = %s",
                    (video_id,),
                )
                continue
            except Exception as exc:
                reason = f"fetch_error:{type(exc).__name__}"
                drops[reason] = drops.get(reason, 0) + 1
                continue
            conn.execute(
                """
                INSERT INTO transcripts (video_id, caption_source, segments, full_text, sha256)
                VALUES (%s, %s, %s::jsonb, %s, %s)
                ON CONFLICT (video_id) DO UPDATE SET
                    caption_source = EXCLUDED.caption_source, segments = EXCLUDED.segments,
                    full_text = EXCLUDED.full_text, sha256 = EXCLUDED.sha256
                """,
                (
                    video_id,
                    transcript.caption_source,
                    json.dumps([s.model_dump() for s in transcript.segments]),
                    transcript.full_text,
                    transcript.sha256,
                ),
            )
            stored += 1
        conn.commit()
    write_report("transcripts", event, len(talks), stored, drops)
    return stored
