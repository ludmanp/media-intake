from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from media_intake.commands import resolve_ytdlp_command, run_command
from media_intake.packet import Packet, update_manifest_status
from media_intake.sources import SourceKind


DEFAULT_WHISPER_BIN = "whisper-cli"
DEFAULT_WHISPER_MODEL = "models/ggml-large-v3-turbo-q5_0.bin"


@dataclass(frozen=True)
class DistillationPlan:
    commands: list[list[str]] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)


def plan_distillation(
    packet: Packet,
    lang: str = "auto",
    whisper_bin: str = DEFAULT_WHISPER_BIN,
    whisper_model: str = DEFAULT_WHISPER_MODEL,
    fps: int = 1,
    hash_size: int = 16,
    hash_threshold: int = 10,
) -> DistillationPlan:
    commands: list[list[str]] = []
    source_path = source_media_path(packet)

    if packet.source.kind == SourceKind.URL:
        source_path = packet.cache_dir / "source.%(ext)s"
        commands.append(
            [
                *resolve_ytdlp_command(),
                "--no-playlist",
                "--write-info-json",
                "--write-thumbnail",
                "--convert-thumbnails",
                "jpg",
                "-f",
                "bv*[height<=720]+ba/b[height<=720]/best",
                "-o",
                str(source_path),
                packet.source.raw,
            ]
        )
        source_path = packet.cache_dir / "source.mp4"

    audio_path = packet.cache_dir / "audio.wav"
    commands.append(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(source_path),
            "-ar",
            "16000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            str(audio_path),
        ]
    )
    commands.append(
        [
            whisper_bin,
            "-m",
            whisper_model,
            "-l",
            lang,
            "-mc",
            "0",
            "-et",
            "2.8",
            "-f",
            str(audio_path),
            "-of",
            str(packet.root / "transcript"),
            "--output-srt",
        ]
    )

    outputs = ["transcript.srt"]
    if packet.source.media_type == "video":
        commands.append(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(source_path),
                "-vf",
                f"fps={fps},mpdecimate=hi=64*48:lo=64*16:frac=0.05,setpts=N/TB",
                "-vsync",
                "vfr",
                str(packet.frames_dir / "%04d.png"),
            ]
        )
        commands.append(
            [
                "media-intake",
                "dedupe-frames",
                str(packet.frames_dir),
                "--hash-size",
                str(hash_size),
                "--threshold",
                str(hash_threshold),
            ]
        )
        outputs.append("frames/")

    return DistillationPlan(commands=commands, outputs=outputs)


def run_distillation(packet: Packet, dry_run: bool = False, **kwargs) -> DistillationPlan:
    plan = plan_distillation(packet, **kwargs)
    for command in plan.commands:
        run_command(command, dry_run=dry_run)
    update_manifest_status(packet, "dry-run" if dry_run else "distilled", outputs=plan.outputs)
    return plan


def source_media_path(packet: Packet) -> Path:
    if packet.source.kind == SourceKind.FILE:
        return Path(packet.source.raw).expanduser()
    return packet.cache_dir / "source.mp4"
