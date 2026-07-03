from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from media_intake.packet import create_packet, inspect_packet, update_manifest_status
from media_intake.sources import detect_source


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="media-intake")
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract = subparsers.add_parser("extract", help="Create an evidence packet from media")
    extract.add_argument("source")
    extract.add_argument("--output", required=True)
    extract.add_argument("--metadata-only", action="store_true")
    extract.add_argument("--overwrite", action="store_true")
    extract.add_argument("--profile", choices=["generic", "ai-digest", "tron-wiki"], default="generic")
    extract.set_defaults(func=cmd_extract)

    inspect = subparsers.add_parser("inspect", help="Print packet summary")
    inspect.add_argument("packet")
    inspect.set_defaults(func=cmd_inspect)

    cleanup = subparsers.add_parser("cleanup", help="Remove disposable packet files")
    cleanup.add_argument("packet")
    cleanup.add_argument("--remove-cache", action="store_true")
    cleanup.set_defaults(func=cmd_cleanup)

    return parser


def cmd_extract(args: argparse.Namespace) -> int:
    source = detect_source(args.source)
    packet = create_packet(source, Path(args.output), overwrite=args.overwrite)
    if args.metadata_only:
        update_manifest_status(packet, "metadata-only", outputs=["metadata.json", "summary.md"])
        print(f"packet: {packet.root}")
        return 0
    raise RuntimeError("media distillation is not available yet; pass --metadata-only for packet skeletons")


def cmd_inspect(args: argparse.Namespace) -> int:
    print(inspect_packet(Path(args.packet)), end="")
    return 0


def cmd_cleanup(args: argparse.Namespace) -> int:
    packet = Path(args.packet)
    if args.remove_cache:
        shutil.rmtree(packet / "cache", ignore_errors=True)
        print(f"removed cache: {packet / 'cache'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
