from datetime import datetime

from pydantic import BaseModel

from receipts.models.enums import CaptionSource


class VideoMeta(BaseModel):
    video_id: str
    title: str
    channel: str = ""
    published_at: datetime | None = None
    duration: int | None = None

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"


class Segment(BaseModel):
    start: float
    text: str


class Transcript(BaseModel):
    video_id: str
    caption_source: CaptionSource
    segments: list[Segment]
    full_text: str
    sha256: str
    method: str = "youtube_captions"
