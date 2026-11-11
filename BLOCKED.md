# Blocked

Items waiting on the project owner. Work continues on everything not listed here.

## Production LLM access

- `LLM_MODEL`, `LLM_API_KEY`: only needed to run the pipeline in production with the `anthropic` or `openai` provider. Development uses `LLM_PROVIDER=claude_code` (the Claude Code CLI on the owner's plan) and needs no key. Tests use `fake`.

## Optional

- `YOUTUBE_API_KEY`: improves video discovery. Get it in Google Cloud console: create a project, enable YouTube Data API v3, create an API key under Credentials. The scraper works without it.

## Environment

- Docker Hub (`registry-1.docker.io`) is unreachable from the development machine (the system DNS resolver has no route for it). Images could not be pulled here, so `docker compose up` and the pgschema migrate service were not run locally. CI builds all images. The schema was applied and the whole app exercised against a local Postgres with the pgschema binary instead. Fix the machine's DNS (for example 1.1.1.1) and run `task up` to confirm the container stack.
- Stellar Expert asset and contract statistics return 402 Payment Required, so only its free directory endpoint is used.
- Soroban RPC keeps about seven days of history, so contract activity is checked over that window.
