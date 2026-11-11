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
