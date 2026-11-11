CREATE TABLE human_tasks (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kind TEXT NOT NULL,
    description TEXT NOT NULL,
    url TEXT NOT NULL DEFAULT '',
    resume_hint TEXT NOT NULL DEFAULT '',
    state task_state NOT NULL DEFAULT 'open',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ
);
