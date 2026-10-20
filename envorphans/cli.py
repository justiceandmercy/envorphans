"""Command-line interface for envorphans."""
import argparse
import json
from pathlib import Path

from .scanner import find_orphans, DEFAULT_EXTS, DEFAULT_IGNORE


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="envorphans",
        description="Find env vars defined in .env files but never referenced in source.",
    )
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    parser.add_argument("--extensions", default=None, help="comma-separated extensions")
    parser.add_argument("--ignore", default=None, help="comma-separated dir names to ignore")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--strict", action="store_true", help="exit 1 if orphans found")
    args = parser.parse_args(argv)

    exts = set(DEFAULT_EXTS)
    if args.extensions:
        exts = {e if e.startswith(".") else "." + e for e in args.extensions.split(",") if e.strip()}

    ignore = set(DEFAULT_IGNORE)
    if args.ignore:
        ignore |= {d.strip() for d in args.ignore.split(",") if d.strip()}

    result = find_orphans(args.path, exts, ignore)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        orphans = result["orphans"]
        if not orphans:
            print("No orphaned environment variables found.")
        else:
            print(f"Found {len(orphans)} orphaned environment variable(s):")
            for name in orphans:
                print(f"  - {name}")
        print(
            f"\nScanned {len(result['env_files'])} env file(s), "
            f"{result['referenced_count']} referenced var(s)."
        )

    if args.strict and result["orphans"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
