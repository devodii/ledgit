# Blocked

Items waiting on the project owner. Work continues on everything not listed here.

## Secrets to provide in `.env`

- `LLM_MODEL`, `LLM_API_KEY`: only for production use of the `anthropic` or `openai` providers. Development uses `LLM_PROVIDER=claude_code` (the Claude Code CLI) and needs no key; tests use `fake`.
- `YOUTUBE_API_KEY`: optional, improves video discovery in M3 and M4.

Every other variable has a working local default.
