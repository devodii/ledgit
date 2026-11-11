# Blocked

Items waiting on the project owner. Work continues on everything not listed here.

## Secrets to provide in `.env`

- `LLM_MODEL`, `LLM_API_KEY`: only for production use of the `anthropic` or `openai` providers. Development uses `LLM_PROVIDER=claude_code` (the Claude Code CLI) and needs no key; tests use `fake`.
- `YOUTUBE_API_KEY`: optional, improves video discovery in M3 and M4. Get it in Google Cloud console: create a project, enable YouTube Data API v3, create an API key under Credentials.

Every other variable has a working local default.

## Environment

- Docker Hub (`registry-1.docker.io`) is unreachable from this machine (no route over IPv6). Images cannot be pulled, so the compose stack, the pgschema migrate service and the Docker build check are unverified locally. Fix your network or Docker proxy settings, then run `task up`.
