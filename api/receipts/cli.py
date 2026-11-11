import argparse
import importlib
import sys
from collections.abc import Sequence
from pathlib import Path

from receipts.connectors.errors import HumanActionRequired
from receipts.seed import seed_fixtures
from receipts.settings import ConfigError, check_settings, get_settings
from receipts.tasks.queue import create_task, list_tasks, resolve_task

CONNECTORS = {
    "youtube": ("receipts.connectors.youtube", "YouTubeConnector"),
    "transcripts": ("receipts.connectors.transcripts", "TranscriptConnector"),
    "sessions": ("receipts.connectors.sessions", "SessionsConnector"),
    "stellar_toml": ("receipts.connectors.stellar_toml", "StellarTomlConnector"),
    "sep_info": ("receipts.connectors.sep_info", "SepInfoConnector"),
    "horizon": ("receipts.connectors.horizon", "HorizonConnector"),
    "soroban": ("receipts.connectors.soroban", "SorobanConnector"),
    "stellar_expert": ("receipts.connectors.stellar_expert", "StellarExpertConnector"),
    "scf": ("receipts.connectors.scf", "ScfConnector"),
    "browser": ("receipts.connectors.browser", "BrowserConnector"),
    "lumenloop": ("receipts.connectors.lumenloop", "LumenLoopConnector"),
    "stellarlight": ("receipts.connectors.stellarlight", "StellarLightConnector"),
}
STAGES = ["discover", "transcripts", "extract", "judge", "resolve", "rank", "write", "build"]


def cmd_check(_: argparse.Namespace) -> int:
    try:
        check_settings(get_settings())
    except ConfigError as exc:
        print(exc, file=sys.stderr)
        return 1
    print("configuration ok")
    return 0


def cmd_seed_fixtures(_: argparse.Namespace) -> int:
    settings = get_settings()
    if settings.env != "local":
        print("seed-fixtures only runs when ENV=local", file=sys.stderr)
        return 1
    print(f"seeded synthetic fixtures: {seed_fixtures(settings.fixtures_dir)}")
    return 0


def cmd_connector(args: argparse.Namespace) -> int:
    module, cls = CONNECTORS[args.name]
    connector = getattr(importlib.import_module(module), cls)()
    try:
        result = connector.healthcheck()
    except HumanActionRequired as exc:
        create_task(exc)
        return 2
    print(result.model_dump_json())
    return 0 if result.ok else 1


def cmd_tasks(args: argparse.Namespace) -> int:
    if args.action == "list":
        for task in list_tasks():
            print(f"#{task.id} [{task.kind}] {task.description} {task.url}")
        return 0
    return 0 if resolve_task(args.id) else 1


def cmd_pipeline(args: argparse.Namespace) -> int:
    from receipts.pipeline import run_stage

    try:
        run_stage(args.stage, args.event)
    except HumanActionRequired as exc:
        create_task(exc)
        return 2
    return 0


def cmd_verify(_: argparse.Namespace) -> int:
    from receipts.verify.engine import run_verify

    print(run_verify())
    return 0


def cmd_sync_registry(args: argparse.Namespace) -> int:
    from receipts.db.connection import connect
    from receipts.registry.loader import read_registry, sync_registry

    settings = get_settings()
    entries = read_registry(settings.data_dir / "registry" / f"{args.event}.yaml")
    with connect() as conn:
        count = sync_registry(conn, entries)
        conn.commit()
    print(f"synced {count} claims")
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    from receipts.evals.report import run_eval

    print(run_eval(args.event))
    return 0


def cmd_openapi(args: argparse.Namespace) -> int:
    import json

    from receipts.main import create_app

    schema = json.dumps(create_app().openapi(), indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(schema)
    else:
        sys.stdout.write(schema)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="receipts", description="Ledgit command line")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="validate environment configuration").set_defaults(func=cmd_check)
    sub.add_parser("seed-fixtures", help="load synthetic data for local UI work").set_defaults(
        func=cmd_seed_fixtures
    )
    connector = sub.add_parser("connector", help="run one connector's healthcheck")
    connector.add_argument("name", choices=sorted(CONNECTORS))
    connector.set_defaults(func=cmd_connector)
    tasks = sub.add_parser("tasks", help="manage human tasks")
    tasks.add_argument("action", choices=["list", "resolve"])
    tasks.add_argument("id", nargs="?", type=int)
    tasks.set_defaults(func=cmd_tasks)
    pipeline = sub.add_parser("pipeline", help="run a pipeline stage")
    pipeline.add_argument("stage", choices=STAGES)
    pipeline.add_argument("--event", required=True)
    pipeline.set_defaults(func=cmd_pipeline)
    sub.add_parser("verify", help="run the verification engine").set_defaults(func=cmd_verify)
    openapi = sub.add_parser("openapi", help="print the OpenAPI schema")
    openapi.add_argument("--out")
    openapi.set_defaults(func=cmd_openapi)
    evals = sub.add_parser("eval", help="write the eval report for an event")
    evals.add_argument("--event", required=True)
    evals.set_defaults(func=cmd_eval)
    sync = sub.add_parser("sync-registry", help="load the registry yaml into the database")
    sync.add_argument("--event", required=True)
    sync.set_defaults(func=cmd_sync_registry)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
