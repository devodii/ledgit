import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from receipts.seed import seed_fixtures
from receipts.settings import ConfigError, check_settings, get_settings


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
    counts = seed_fixtures(Path(settings.fixtures_dir))
    print(f"seeded synthetic fixtures: {counts}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="receipts", description="Ledgit command line")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="validate environment configuration")
    check.set_defaults(func=cmd_check)
    seed = sub.add_parser("seed-fixtures", help="load synthetic data for local UI work")
    seed.set_defaults(func=cmd_seed_fixtures)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
