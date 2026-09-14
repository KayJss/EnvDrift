from __future__ import annotations

import argparse
import json
import sys

from .core import compare_envs, parse_env_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdrift",
        description=(
            "Detect configuration drift between a reference .env file "
            "and a target environment without printing secret values."
        ),
    )
    parser.add_argument(
        "reference",
        nargs="?",
        default=".env.example",
        help="Reference env file (default: .env.example)",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".env",
        help="Target env file (default: .env)",
    )
    parser.add_argument(
        "--allow-unexpected",
        action="store_true",
        help="Do not report variables that exist only in the target file.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Print a machine-readable JSON report.",
    )
    return parser


def _print_human(report) -> None:
    if report.ok and not report.unexpected:
        print("✓ No configuration drift detected.")
        return

    if report.missing:
        print("Missing variables:")
        for key in report.missing:
            print(f"  - {key}")

    if report.empty_required:
        print("Required variables with empty values:")
        for key in report.empty_required:
            print(f"  - {key}")

    if report.unexpected:
        print("Unexpected variables:")
        for key in report.unexpected:
            print(f"  - {key}")

    if report.duplicate_keys:
        print("Duplicate variable declarations:")
        for key in report.duplicate_keys:
            print(f"  - {key}")

    if report.invalid_lines:
        print("Invalid .env syntax on line(s):")
        for line in report.invalid_lines:
            print(f"  - {line}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        reference = parse_env_file(args.reference)
        target = parse_env_file(args.target)
    except (FileNotFoundError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    report = compare_envs(
        reference,
        target,
        allow_unexpected=args.allow_unexpected,
    )

    if args.json_output:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        _print_human(report)

    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
