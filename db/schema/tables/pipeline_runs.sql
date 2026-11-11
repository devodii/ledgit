CREATE TABLE pipeline_runs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_slug TEXT NOT NULL,
    stage TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    report JSONB NOT NULL DEFAULT '{}'::JSONB
);
