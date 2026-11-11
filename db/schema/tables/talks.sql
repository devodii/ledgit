CREATE TABLE talks (
    video_id TEXT PRIMARY KEY,
    event_slug TEXT NOT NULL REFERENCES events (slug),
    title TEXT NOT NULL,
    channel TEXT NOT NULL DEFAULT '',
    published_at TIMESTAMPTZ,
    url TEXT NOT NULL,
    accepted BOOLEAN NOT NULL DEFAULT TRUE,
    skip_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
