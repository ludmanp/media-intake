from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from urllib.parse import parse_qs, urlparse


AUDIO_EXTENSIONS = {".aac", ".flac", ".m4a", ".mp3", ".oga", ".ogg", ".opus", ".wav", ".webm"}
VIDEO_EXTENSIONS = {".m4v", ".mkv", ".mov", ".mp4", ".webm"}


class SourceKind(str, Enum):
    FILE = "file"
    URL = "url"


@dataclass(frozen=True)
class Source:
    raw: str
    kind: SourceKind
    platform: str
    media_type: str
    source_id: str
    suffix: str = ""


def detect_source(value: str) -> Source:
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https"}:
        platform = detect_url_platform(parsed)
        media_type = "video" if platform == "youtube" else media_type_from_suffix(Path(parsed.path).suffix)
        return Source(
            raw=value,
            kind=SourceKind.URL,
            platform=platform,
            media_type=media_type,
            source_id=source_id_for_url(value, platform),
            suffix=Path(parsed.path).suffix.lower(),
        )

    suffix = Path(value).suffix.lower()
    return Source(
        raw=value,
        kind=SourceKind.FILE,
        platform="local",
        media_type=media_type_from_suffix(suffix),
        source_id=stable_source_id(value),
        suffix=suffix,
    )


def detect_url_platform(parsed) -> str:
    host = parsed.netloc.lower()
    if "youtube.com" in host or "youtu.be" in host:
        return "youtube"
    return host.removeprefix("www.") or "url"


def source_id_for_url(value: str, platform: str) -> str:
    if platform == "youtube":
        return extract_youtube_id(value)
    return stable_source_id(value)


def extract_youtube_id(value: str) -> str:
    parsed = urlparse(value)
    host = parsed.netloc.lower()
    path = parsed.path.strip("/")
    if "youtu.be" in host and path:
        return path.split("/")[0]
    if "youtube.com" in host:
        query_id = parse_qs(parsed.query).get("v", [""])[0]
        if query_id:
            return query_id
        parts = [part for part in path.split("/") if part]
        for marker in ("shorts", "embed", "live"):
            if marker in parts:
                index = parts.index(marker)
                if index + 1 < len(parts):
                    return parts[index + 1]
    raise ValueError(f"cannot extract YouTube video id from {value!r}")


def media_type_from_suffix(suffix: str) -> str:
    lowered = suffix.lower()
    if lowered in VIDEO_EXTENSIONS:
        return "video"
    if lowered in AUDIO_EXTENSIONS:
        return "audio"
    return "unknown"


def stable_source_id(value: str) -> str:
    stem = Path(urlparse(value).path).stem or value
    normalized = unicodedata.normalize("NFKD", stem)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    words = re.findall(r"[a-z0-9]+", ascii_text.lower())
    return "-".join(words) or "media-source"
