# Decisions

- **Name:** the product is Ledgit. The Python package keeps the `receipts` module name and CLI to match the build plan layout.
- **CLI:** argparse instead of Typer, to keep dependencies small.
- **Database access:** raw SQL through psycopg 3 with Pydantic models for rows. No SQLAlchemy, no Alembic.
- **Migrations:** pgschema (declarative). `db/schema/` is the desired state, `db/migrations/` is a record of planned DDL. Mirrors the home-database setup. A compose `migrate` service applies it before the api starts.
- **Models:** Pydantic everywhere in the backend, `dataclasses` banned via ruff.
- **Task runner:** Taskfile instead of Makefile.
- **LLM in development:** a `claude_code` provider shells out to the Claude Code CLI so the Max plan is used instead of API credits. `fake` is used in tests. API providers are for production.
- **pnpm builds:** esbuild is allowed to run its install script in `web/pnpm-workspace.yaml`, everything else stays blocked.
- **Tests:** owner asked for no new tests from M1 onward, overriding the build plan. Existing api and home page tests stay.
- **YouTube:** yt-dlp is our scraper for listing videos, metadata and captions (hand-run infrastructure we control). LumenLoop and StellarLight are never used as the source for videos or transcripts.
- **Secondary sources:** LumenLoop (MCP over HTTP) and StellarLight (public API) enrich org data (website, region, SCF, contract and asset pointers). Every value taken from them is tagged with its source in the registry `sources` list. Our own checks (Horizon, Soroban RPC, stellar.toml, SEP, SCF site) are primary.
- **DNS fallback:** the system resolver here fails for some hosts (horizon.stellar.org, mcp.lumenloop.com, Docker Hub). The http client retries unresolved lookups through Cloudflare DNS over HTTPS. Disable with `DNS_FALLBACK=0`.
- **Soroban XDR:** the contract instance ledger key is encoded by hand (`connectors/xdr.py`), verified byte for byte against the Stellar SDK, so the SDK is not a dependency.
- **Horizon:** `horizon.stellar.org` no longer resolves, so the default is the public community Horizon at `horizon.stellar.lobstr.co`, configurable with `HORIZON_URL`.
- **Stellar Expert:** asset and contract stats return 402 Payment Required, so only its free directory endpoint is used. Holder counts come from Horizon.
- **Soroban history:** RPC keeps about 7 days of events, so contract activity is checked over `min(VERIFY_CONTRACT_ACTIVITY_DAYS, retention)` and the effective window is recorded in each observation.
