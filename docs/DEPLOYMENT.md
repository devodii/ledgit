# Deployment guide

Ledgit is three things: a Postgres database, the FastAPI service with a daily verification worker, and a static web app served by nginx.

## Requirements

- Docker with Compose.
- A host that can reach the public Stellar services (Horizon, Soroban RPC, stellar.toml hosts) and YouTube.
- Optional: an LLM API key if you run the pipeline in production (see below).

## 1. Configure

```bash
cp .env.example .env
```

Set at least:

- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `DATABASE_URL=postgresql://USER:PASSWORD@db:5432/DB`
- `ENV=production`
- `SITE_URL` to the public address, used in share links, Open Graph tags and the sitemap
- `LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY` if the pipeline runs on this host. `claude_code` only works where the Claude Code CLI is installed and signed in, so production should use `anthropic` or `openai`.

## 2. Start

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

The `migrate` service applies `db/schema/` with pgschema before the API starts. The `worker` runs the daily verification at `VERIFY_CRON` (UTC).

The web container listens on port 8080 and proxies `/api`, `/share`, `/sitemap.xml` and `/robots.txt` to the API. Put a TLS terminating proxy in front of it.

## 3. Load data

The registry is committed in `data/registry/`. Load it and run the first verification:

```bash
docker compose -f docker-compose.prod.yml run --rm api python -m receipts.cli sync-registry --event meridian-2025
docker compose -f docker-compose.prod.yml run --rm api python -m receipts.cli verify
```

To rebuild the registry from the source recordings, run the pipeline stages from the `worker` image, which has Chromium for the browser connector:

```bash
docker compose -f docker-compose.prod.yml run --rm worker python -m receipts.cli pipeline build --event meridian-2025
```

## 4. Share links

Share a claim with `https://YOUR_HOST/share/claims/<id>`. That page carries the Open Graph tags and a per-claim image, then sends people to the app.

## 5. Monitoring

- API logs go to stdout. Set `LOG_LEVEL` as needed.
- The web app reports client errors to `VITE_ERROR_ENDPOINT` if you set it at build time, otherwise to the browser console.
- `GET /api/v1/meta` returns the time of the last verification run and a data version, which is useful for an uptime check.

## 6. Human tasks

When the pipeline needs a person (for example a captcha), it records a task. Run `receipts tasks list` to see open tasks and `receipts tasks resolve <id>` once handled.
