import json
import re
from datetime import UTC, datetime
from typing import Any, ClassVar

import yt_dlp

from receipts.connectors.base import Connector, HealthResult
from receipts.connectors.http import HttpClient
from receipts.models.talks import VideoMeta
from receipts.settings import get_settings

API = "https://www.googleapis.com/youtube/v3"


class YouTubeConnector(Connector):
    name: ClassVar[str] = "youtube"
    allowed_domains: ClassVar[list[str]] = ["youtube.com", "googleapis.com", "ytimg.com"]
    rate_limit_rps: ClassVar[float] = 2.0
    emits: ClassVar[list[str]] = ["VideoMeta"]

    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.youtube_api_key
        self.cache_dir = settings.cache_dir / "youtube"
        self.http = HttpClient(
            name=self.name, allowed_domains=self.allowed_domains, rate_limit_rps=self.rate_limit_rps
        )

    def _ydl(self, **opts: Any) -> yt_dlp.YoutubeDL:
        return yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True, **opts})

    def list_playlist(self, playlist_id: str) -> list[VideoMeta]:
        cache = self.cache_dir / f"playlist-{playlist_id}.json"
        if cache.is_file():
            return [VideoMeta.model_validate(v) for v in json.loads(cache.read_text())]
        if self.api_key:
            videos = self._list_playlist_api(playlist_id)
        else:
            with self._ydl(extract_flat=True) as ydl:
                info = ydl.extract_info(
                    f"https://www.youtube.com/playlist?list={playlist_id}", download=False
                )
            videos = [
                VideoMeta(
                    video_id=e["id"],
                    title=e.get("title") or "",
                    channel=e.get("channel") or e.get("uploader") or "",
                    duration=e.get("duration"),
                )
                for e in (info or {}).get("entries", [])
                if e and e.get("id")
            ]
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps([v.model_dump(mode="json") for v in videos]))
        return videos

    def _list_playlist_api(self, playlist_id: str) -> list[VideoMeta]:
        videos: list[VideoMeta] = []
        token = ""
        while True:
            params = {
                "part": "snippet",
                "playlistId": playlist_id,
                "maxResults": 50,
                "key": self.api_key,
                **({"pageToken": token} if token else {}),
            }
            data = self.http.get(f"{API}/playlistItems", params=params, cache_ttl=3600).data()
            for item in data.get("items", []):
                snippet = item["snippet"]
                videos.append(
                    VideoMeta(
                        video_id=snippet["resourceId"]["videoId"],
                        title=snippet["title"],
                        channel=snippet.get("videoOwnerChannelTitle", ""),
                    )
                )
            token = data.get("nextPageToken", "")
            if not token:
                return videos

    def metadata(self, video_id: str) -> VideoMeta:
        cache = self.cache_dir / f"video-{video_id}.json"
        if cache.is_file():
            return VideoMeta.model_validate_json(cache.read_text())
        with self._ydl() as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        assert info is not None
        published = None
        if info.get("upload_date"):
            published = datetime.strptime(info["upload_date"], "%Y%m%d").replace(tzinfo=UTC)
        meta = VideoMeta(
            video_id=video_id,
            title=info.get("title") or "",
            channel=info.get("channel") or "",
            published_at=published,
            duration=info.get("duration"),
        )
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(meta.model_dump_json())
        return meta

    def healthcheck(self) -> HealthResult:
        try:
            videos = self.list_playlist("PLmr3tp_7-7Gg3deAwuGQEjAMbhAtt8Yi3")
        except Exception as exc:
            return HealthResult(connector=self.name, ok=False, detail=str(exc)[:200])
        return HealthResult(connector=self.name, ok=bool(videos), detail=f"{len(videos)} videos")


def passes_gates(
    meta: VideoMeta, title_must_match: list[str], after: datetime | None, before: datetime | None
) -> tuple[bool, str]:
    title = meta.title.lower()
    if title_must_match and not any(re.search(p.lower(), title) for p in title_must_match):
        return False, "title_gate"
    if meta.published_at:
        if after and meta.published_at < after:
            return False, "published_before_window"
        if before and meta.published_at > before:
            return False, "published_after_window"
    return True, ""
