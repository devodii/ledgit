# Ledgit

[![ci](https://github.com/devodii/ledgit/actions/workflows/ci.yml/badge.svg)](https://github.com/devodii/ledgit/actions/workflows/ci.yml)

Ledgit takes specific, checkable claims made on stage at Meridian 2025, shows the speaker saying them on video, and reports what public Stellar data says about each one today. Verdicts are computed by code from on-chain and public evidence, never typed by hand.

Each claim has four parts: the claim (a verbatim quote with a link to the exact moment in the talk), the backing (a Stellar Community Fund award, if public), the evidence (issuer accounts, Soroban contracts, anchor stellar.toml files, protocol releases) and the verdict.

## Requirements

Docker, [Task](https://taskfile.dev), Python 3.12+ with [uv](https://docs.astral.sh/uv/), Node 22 with pnpm.

## Run it

```bash
cp .env.example .env
task up
```

- Web: http://localhost:5173
- API docs: http://localhost:8000/docs
- Storybook: `task storybook` then http://localhost:6006

Every variable in `.env.example` has a working local default. The comments there say which ones are secrets and when you need them.

## How the data gets there

```bash
task pipeline EVENT=meridian-2025   # discover, transcripts, extract, judge, rank, resolve, write
task verify                         # check every evidence item and compute verdicts
```

The stages can also be run one at a time: `receipts pipeline <stage> --event meridian-2025`.

1. **Discover** lists the event recordings and applies title and date gates.
2. **Transcripts** reads timed captions (all Meridian 2025 captions are auto-generated, and the UI says so).
3. **Extract** asks an LLM for checkable claims. A quote is only accepted if it is an exact substring of the transcript.
4. **Judge** is a second, skeptical LLM pass that reviews each claim against the transcript.
5. **Rank** scores, removes duplicates and caps claims per talk.
6. **Resolve** links each organisation to a domain, addresses and SCF data, labelling the source of every fact, and selects only the evidence that relates to what was actually said.
7. **Write** produces `data/registry/<event>.yaml` (deterministic: a second run produces no diff).

The LLM provider is chosen with `LLM_PROVIDER`: `claude_code` (the local Claude Code CLI, no API key), `anthropic`, `openai`, or `fake` for tests.

## Evals

`receipts eval --event meridian-2025` writes [`evals/meridian-2025/report.md`](evals/meridian-2025/report.md): the funnel, an independent verbatim re-check of every quote, judge statistics, source coverage, verdicts, and a 20 claim sample for human labelling. See [`evals/README.md`](evals/README.md).

## Everyday tasks

Run `task --list`. The common ones:

| Task | What it does |
| --- | --- |
| `task up` / `task down` | start or stop the stack |
| `task lint` / `task format` / `task typecheck` | quality checks |
| `task schema:plan` / `task schema:apply` | plan or apply database schema changes |
| `task watch-tasks` | play a sound when the pipeline needs a human |
| `task storybook` | component library |

## Database

The schema is declarative. Edit the SQL files under `db/schema/`, run `task schema:plan` to write the pending DDL to `db/migrations/`, then `task schema:apply`. `manifest.sql` is generated, do not edit it. Set `PGSCHEMA_BIN` to use a local pgschema binary instead of Docker.

## Layout

`api/` FastAPI backend, CLI and pipeline. `web/` React app and Storybook. `db/` schema. `data/` event seeds, the generated registry, corrections and reports. `evals/` eval reports. `docs/` deployment guide.

More: [Deployment guide](docs/DEPLOYMENT.md), [Contributing](CONTRIBUTING.md), [Decisions](DECISIONS.md).
