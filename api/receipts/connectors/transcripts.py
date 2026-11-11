import hashlib
import json
import re
from typing import Any, ClassVar

import yt_dlp

from receipts.connectors.base import Connector, HealthResult
from receipts.connectors.http import HttpClient
from receipts.models.enums import CaptionSource
from receipts.models.talks import Segment, Transcript
from receipts.settings import get_settings


class NoCaptions(Exception):
    pass


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def build_transcript(
    video_id: str, source: CaptionSource, segments: list[Segment], method: str = "youtube_captions"
) -> Transcript:
    full_text = normalize(" ".join(s.text for s in segments))
    return Transcript(
        video_id=video_id,
        caption_source=source,
        segments=segments,
        full_text=full_text,
        sha256=hashlib.sha256(full_text.encode()).hexdigest(),
        method=method,
    )


def parse_json3(raw: str) -> list[Segment]:
    segments: list[Segment] = []
    for event in json.loads(raw).get("events", []):
        parts = event.get("segs")
        if not parts:
            continue
        text = normalize("".join(p.get("utf8", "") for p in parts))
        if text:
            segments.append(Segment(start=event.get("tStartMs", 0) / 1000, text=text))
    return segments


class TranscriptConnector(Connector):
    name: ClassVar[str] = "transcripts"
    allowed_domains: ClassVar[list[str]] = ["youtube.com", "googlevideo.com"]
    rate_limit_rps: ClassVar[float] = 0.5
    emits: ClassVar[list[str]] = ["Transcript"]

    def __init__(self) -> None:
        self.cache_dir = get_settings().cache_dir / "transcripts"
        self.http = HttpClient(
            name=self.name, allowed_domains=self.allowed_domains, rate_limit_rps=self.rate_limit_rps
        )

    def fetch(self, video_id: str) -> Transcript:
        cache = self.cache_dir / f"{video_id}.json"
        if cache.is_file():
            return Transcript.model_validate_json(cache.read_text())
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        opts: dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "js_runtimes": {"node": {}},
            "remote_components": ["ejs:github"],
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        assert info is not None
        track, source = self._pick_track(info)
        if track is None:
            raise NoCaptions(video_id)
        raw = self.http.get(track["url"]).text
        segments = parse_json3(raw)
        if not segments:
            raise NoCaptions(video_id)
        transcript = build_transcript(video_id, source, segments)
        cache.write_text(transcript.model_dump_json())
        return transcript

    @staticmethod
    def _pick_track(info: dict[str, Any]) -> tuple[dict[str, Any] | None, CaptionSource]:
        for lang in sorted(k for k in (info.get("subtitles") or {}) if k.startswith("en")):
            tracks = [t for t in info["subtitles"][lang] if t["ext"] == "json3"]
            if tracks:
                return tracks[0], CaptionSource.manual
        auto = info.get("automatic_captions") or {}
        for lang in ("en-orig", "en"):
            tracks = [t for t in auto.get(lang, []) if t["ext"] == "json3"]
            if tracks:
                return tracks[0], CaptionSource.auto
        return None, CaptionSource.auto

    def healthcheck(self) -> HealthResult:
        try:
            transcript = self.fetch("ard4j13AnnI")
        except Exception as exc:
            return HealthResult(connector=self.name, ok=False, detail=str(exc)[:200])
        return HealthResult(
            connector=self.name,
            ok=True,
            detail=f"{len(transcript.segments)} segments ({transcript.caption_source})",
        )
