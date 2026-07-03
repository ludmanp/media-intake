from __future__ import annotations

import shutil
import subprocess


def resolve_ytdlp_command() -> list[str]:
    if shutil.which("yt-dlp"):
        return ["yt-dlp"]
    if shutil.which("uvx"):
        return ["uvx", "--from", "yt-dlp", "yt-dlp"]
    if shutil.which("uv"):
        return ["uv", "tool", "run", "yt-dlp", "yt-dlp"]
    return ["yt-dlp"]


def run_command(command: list[str], dry_run: bool = False) -> None:
    print("+ " + " ".join(command))
    if not dry_run:
        subprocess.run(command, check=True)
