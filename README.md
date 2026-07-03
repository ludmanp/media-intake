# Media Intake

Local reusable media extraction toolkit for turning videos, YouTube links, audio files,
and voice recordings into durable evidence packets.

Media Intake prepares evidence. It does not decide how a project should publish that
evidence. Project adapters can convert packets into AI Digest notes, Tron-Wiki pages, or
other knowledge-base formats.

## Quick Start

```bash
/Users/mark/Projects/AI/media-intake/bin/media-intake extract /path/to/audio.m4a --output /tmp/audio-packet --metadata-only
/Users/mark/Projects/AI/media-intake/bin/media-intake inspect /tmp/audio-packet
```

After installing the global symlink:

```bash
media-intake extract /path/to/demo.mp4 --output /tmp/demo-packet --dry-run
media-intake extract "https://www.youtube.com/watch?v=puen8F_IPkQ" --output /tmp/youtube-packet --metadata-only --profile ai-digest
```

## Packet Layout

```text
<packet-dir>/
  manifest.json
  metadata.json
  summary.md
  transcript.srt
  transcript.json
  frames/
  cache/
```

`cache/` is disposable. The durable evidence is the manifest, metadata, transcript,
summary, and selected frames.

## Commands

```bash
media-intake extract <url-or-file> --output <packet-dir>
media-intake extract <url-or-file> --output <packet-dir> --metadata-only
media-intake extract <url-or-file> --output <packet-dir> --dry-run
media-intake extract <url-or-file> --output <packet-dir> --profile ai-digest
media-intake inspect <packet-dir>
media-intake cleanup <packet-dir> --remove-cache
```

## Guides

- [Video workflow](docs/guides/video.md)
- [Audio and voice workflow](docs/guides/audio.md)
- [Project adapters](docs/guides/project-adapters.md)
- [Global alias install](docs/guides/install-global-alias.md)

## Design And Plan

- [Design spec](docs/superpowers/specs/2026-07-03-media-intake-design.md)
- [Implementation plan](docs/superpowers/plans/2026-07-03-media-intake-mvp.md)
