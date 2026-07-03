from __future__ import annotations

import datetime as dt
import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from media_intake import __version__
from media_intake.sources import Source


@dataclass(frozen=True)
class Packet:
    root: Path
    source: Source
    manifest_path: Path
    metadata_path: Path
    transcript_srt_path: Path
    transcript_json_path: Path
    summary_path: Path
    frames_dir: Path
    cache_dir: Path


def create_packet(source: Source, output: Path, overwrite: bool = False) -> Packet:
    root = output.expanduser().resolve()
    if root.exists() and any(root.iterdir()):
        if not overwrite:
            raise FileExistsError(f"packet directory already exists and is not empty: {root}")
        shutil.rmtree(root)

    packet = build_packet(source, root)
    packet.frames_dir.mkdir(parents=True, exist_ok=True)
    packet.cache_dir.mkdir(parents=True, exist_ok=True)
    write_json(packet.manifest_path, initial_manifest(source))
    write_json(packet.metadata_path, initial_metadata(source))
    packet.summary_path.write_text(initial_summary(source), encoding="utf-8")
    return packet


def build_packet(source: Source, root: Path) -> Packet:
    return Packet(
        root=root,
        source=source,
        manifest_path=root / "manifest.json",
        metadata_path=root / "metadata.json",
        transcript_srt_path=root / "transcript.srt",
        transcript_json_path=root / "transcript.json",
        summary_path=root / "summary.md",
        frames_dir=root / "frames",
        cache_dir=root / "cache",
    )


def initial_manifest(source: Source) -> dict[str, Any]:
    return {
        "tool": "media-intake",
        "version": __version__,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "created",
        "source": asdict(source),
        "outputs": [],
        "warnings": [],
        "errors": [],
        "settings": {},
    }


def initial_metadata(source: Source) -> dict[str, Any]:
    return {
        "input": source.raw,
        "platform": source.platform,
        "media_type": source.media_type,
        "source_id": source.source_id,
        "title": "",
        "author": "",
        "duration_seconds": None,
        "language": "",
    }


def initial_summary(source: Source) -> str:
    return (
        f"# Media Intake Packet\n\n"
        f"- Input: {source.raw}\n"
        f"- Platform: {source.platform}\n"
        f"- Media type: {source.media_type}\n"
        f"- Status: created\n"
    )


def update_manifest_status(packet: Packet, status: str, outputs: list[str] | None = None) -> None:
    manifest = read_json(packet.manifest_path)
    manifest["status"] = status
    if outputs is not None:
        manifest["outputs"] = outputs
    manifest["updated_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    write_json(packet.manifest_path, manifest)


def inspect_packet(root: Path) -> str:
    manifest = read_json(root / "manifest.json")
    source = manifest.get("source", {})
    outputs = manifest.get("outputs", [])
    lines = [
        f"status: {manifest.get('status', '')}",
        f"platform: {source.get('platform', '')}",
        f"media_type: {source.get('media_type', '')}",
        f"source_id: {source.get('source_id', '')}",
        "outputs: " + (", ".join(outputs) if outputs else "none"),
    ]
    return "\n".join(lines) + "\n"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
