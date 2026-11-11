import argparse
import os
import re
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_DIR = ROOT / "db"
SCHEMA_DIR = DB_DIR / "schema"
MIGRATIONS_DIR = DB_DIR / "migrations"
LAYERS = ["types", "functions", "tables", "constraints", "indexes", "triggers"]
REFERENCES_RE = re.compile(r'REFERENCES "?([A-Za-z_][A-Za-z0-9_]*)"?')
CREATE_TABLE_RE = re.compile(r'CREATE TABLE (?:IF NOT EXISTS )?"?([A-Za-z_][A-Za-z0-9_]*)"?', re.I)


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    env_file = ROOT / ".env"
    if env_file.is_file():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                values[key.strip()] = value.strip()
    values.update({k: v for k, v in os.environ.items() if k in values or k.startswith("PG")})
    return values


def table_name(path: Path) -> str | None:
    match = CREATE_TABLE_RE.search(path.read_text())
    return match.group(1) if match else None


def order_tables(tables_dir: Path) -> list[Path]:
    by_name: dict[str, Path] = {}
    for path in sorted(tables_dir.glob("*.sql")):
        name = table_name(path)
        if name:
            by_name[name] = path
    ordered: list[Path] = []
    seen: set[str] = set()

    def visit(name: str) -> None:
        if name in seen or name not in by_name:
            return
        seen.add(name)
        for dep in REFERENCES_RE.findall(by_name[name].read_text()):
            if dep != name:
                visit(dep)
        ordered.append(by_name[name])

    for name in by_name:
        visit(name)
    return ordered


def generate_manifest() -> None:
    lines: list[str] = []
    for layer in LAYERS:
        layer_dir = SCHEMA_DIR / layer
        if not layer_dir.is_dir():
            continue
        files = order_tables(layer_dir) if layer == "tables" else sorted(layer_dir.glob("*.sql"))
        lines.extend(f"\\i {layer}/{f.name}" for f in files)
    (SCHEMA_DIR / "manifest.sql").write_text("\n".join(lines) + "\n" if lines else "")


def next_migration_path() -> Path:
    MIGRATIONS_DIR.mkdir(parents=True, exist_ok=True)
    numbers = [int(p.stem) for p in MIGRATIONS_DIR.glob("[0-9][0-9][0-9][0-9][0-9][0-9].sql")]
    return MIGRATIONS_DIR / f"{max(numbers, default=0) + 1:06d}.sql"


def run_pgschema(command: str, *extra: str) -> int:
    env = load_env()
    local_bin = env.get("PGSCHEMA_BIN")
    if local_bin:
        return run_local(local_bin, env, command, *extra)
    image = env.get("PGSCHEMA_IMAGE", "pgplex/pgschema:latest")
    cmd = [
        "docker", "run", "--rm", "-i", "--network", "host",
        "-e", f"PGPASSWORD={env['POSTGRES_PASSWORD']}",
        "-v", f"{DB_DIR}:/db", "-w", "/db",
        image, command,
        "--host", env.get("PGHOST", "localhost"),
        "--port", env.get("POSTGRES_PORT", "5432"),
        "--db", env["POSTGRES_DB"],
        "--user", env["POSTGRES_USER"],
        "--schema", "public",
        "--sslmode", "disable",
        *extra,
    ]  # fmt: skip
    return subprocess.run(cmd, check=False).returncode


def run_local(binary: str, env: dict[str, str], command: str, *extra: str) -> int:
    translated = [a.replace("/db/", f"{DB_DIR}/") for a in extra]
    cmd = [
        binary, command,
        "--host", env.get("PGHOST", "localhost"),
        "--port", env.get("POSTGRES_PORT", "5432"),
        "--db", env["POSTGRES_DB"],
        "--user", env["POSTGRES_USER"],
        "--schema", "public",
        "--sslmode", "disable",
        *translated,
    ]  # fmt: skip
    return subprocess.run(cmd, check=False, env={**os.environ, "PGPASSWORD": env["POSTGRES_PASSWORD"]}, cwd=DB_DIR).returncode


def plan() -> int:
    generate_manifest()
    target = next_migration_path()
    rc = run_pgschema(
        "plan", "--file", "/db/schema/manifest.sql", "--output-sql", f"/db/migrations/{target.name}"
    )
    if rc != 0:
        return rc
    if not target.is_file() or target.stat().st_size == 0:
        target.unlink(missing_ok=True)
        print("No changes detected.")
        return 0
    print(f"Wrote migration plan to db/migrations/{target.name}")
    return 0


def apply() -> int:
    generate_manifest()
    return run_pgschema("apply", "--file", "/db/schema/manifest.sql", "--auto-approve")


def dump() -> int:
    return run_pgschema("dump", "--multi-file", "--file", "/db/schema/manifest.sql")


COMMANDS = {"plan": plan, "apply": apply, "dump": dump, "manifest": lambda: (generate_manifest(), 0)[1]}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run pgschema against the local Ledgit database.")
    parser.add_argument("command", choices=sorted(COMMANDS))
    args = parser.parse_args(argv)
    return COMMANDS[args.command]()


if __name__ == "__main__":
    sys.exit(main())
