CREATE TABLE evidence (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    claim_id TEXT NOT NULL REFERENCES claims (id) ON DELETE CASCADE,
    kind evidence_kind NOT NULL,
    network network NOT NULL,
    ref TEXT NOT NULL,
    found_via TEXT NOT NULL,
    UNIQUE (claim_id, kind, network, ref)
);
