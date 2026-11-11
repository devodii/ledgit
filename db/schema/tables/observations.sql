CREATE TABLE observations (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    evidence_id BIGINT NOT NULL REFERENCES evidence (id) ON DELETE CASCADE,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    result observation_result NOT NULL,
    detail JSONB NOT NULL DEFAULT '{}'::JSONB
);
