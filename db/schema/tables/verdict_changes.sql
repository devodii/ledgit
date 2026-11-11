CREATE TABLE verdict_changes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    claim_id TEXT NOT NULL REFERENCES claims (id) ON DELETE CASCADE,
    from_status verdict_status,
    to_status verdict_status NOT NULL,
    reason TEXT NOT NULL,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
