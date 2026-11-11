CREATE TABLE events (
    slug TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    window_start DATE NOT NULL,
    window_end DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
