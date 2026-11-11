CREATE TABLE transcripts (
    video_id TEXT PRIMARY KEY REFERENCES talks (video_id),
    caption_source caption_source NOT NULL,
    segments JSONB NOT NULL,
    full_text TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
