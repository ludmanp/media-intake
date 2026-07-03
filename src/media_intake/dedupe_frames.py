from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def dhash(path: Path, size: int = 16) -> int:
    raw = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(path),
            "-vf",
            f"scale={size + 1}:{size},format=gray",
            "-f",
            "rawvideo",
            "-",
        ],
        capture_output=True,
        check=True,
    ).stdout
    if len(raw) < (size + 1) * size:
        return 0
    bits = 0
    for row in range(size):
        base = row * (size + 1)
        for col in range(size):
            bits = (bits << 1) | (1 if raw[base + col] > raw[base + col + 1] else 0)
    return bits


def hamming(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def dedupe_frames(frames_dir: Path, threshold: int = 10, hash_size: int = 16, dry_run: bool = False) -> tuple[int, int]:
    frames = sorted(frames_dir.glob("*.png"))
    representatives: list[tuple[int, Path]] = []
    drop: list[Path] = []
    for frame in frames:
        frame_hash = dhash(frame, hash_size)
        if any(hamming(frame_hash, rep_hash) <= threshold for rep_hash, _ in representatives):
            drop.append(frame)
        else:
            representatives.append((frame_hash, frame))
    if not dry_run:
        for frame in drop:
            frame.unlink()
    return len(frames), len(representatives)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="media-intake dedupe-frames")
    parser.add_argument("frames_dir")
    parser.add_argument("--threshold", type=int, default=10)
    parser.add_argument("--hash-size", type=int, default=16)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    total, kept = dedupe_frames(
        Path(args.frames_dir),
        threshold=args.threshold,
        hash_size=args.hash_size,
        dry_run=args.dry_run,
    )
    print(f"frames: {total} -> {kept} distinct")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
