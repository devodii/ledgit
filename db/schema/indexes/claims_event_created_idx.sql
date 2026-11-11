CREATE INDEX claims_event_created_idx ON claims (event_slug, created_at DESC, id);
