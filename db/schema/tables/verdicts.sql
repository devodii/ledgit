CREATE TABLE verdicts (
    claim_id TEXT PRIMARY KEY REFERENCES claims (id) ON DELETE CASCADE,
    status verdict_status NOT NULL,
    reason TEXT NOT NULL,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
