# Ledgit

[![ci](https://github.com/devodii/ledgit/actions/workflows/ci.yml/badge.svg)](https://github.com/devodii/ledgit/actions/workflows/ci.yml)

Ledgit takes specific, checkable claims made on stage at Meridian 2025 and shows what the Stellar network says about each one today. Verdicts are computed from on-chain and public evidence, never typed by hand.

## Requirements

Docker, [Task](https://taskfile.dev), Python 3.12+ with [uv](https://docs.astral.sh/uv/), Node 22 with pnpm.

## Setup

```bash
cp .env.example .env
task up
```

- Web: http://localhost:5173
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

Every variable in `.env.example` has a working local default. See the comments there for the few secrets (LLM keys, YouTube key) that are optional or only needed for production.

## Everyday tasks

Run `task --list`. The common ones:

| Task | What it does |
| --- | --- |
| `task up` / `task down` | start or stop the stack |
| `task test` | api and web unit tests |
| `task lint` / `task format` | lint or format everything |
| `task schema:plan` / `task schema:apply` | plan or apply database schema changes |
| `task watch-tasks` | play a sound when the pipeline needs a human |

## Database

The schema is declarative. Edit the SQL files under `db/schema/`, run `task schema:plan` to write the pending DDL to `db/migrations/`, then `task schema:apply`. `manifest.sql` is generated, do not edit it.

## Layout

`api/` FastAPI backend and CLI, `web/` React app, `db/` schema, `data/` event seeds and the generated registry.
