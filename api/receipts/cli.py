import argparse
import sys
from collections.abc import Sequence

from receipts.settings import ConfigError, check_settings, get_settings


def cmd_check(_: argparse.Namespace) -> int:
    try:
        check_settings(get_settings())
    except ConfigError as exc:
        print(exc, file=sys.stderr)
        return 1
    print("configuration ok")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="receipts", description="Ledgit command line")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="validate environment configuration")
    check.set_defaults(func=cmd_check)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
