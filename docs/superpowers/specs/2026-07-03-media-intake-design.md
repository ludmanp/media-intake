# Media Intake Design

Date: 2026-07-03
Status: accepted-for-planning

## Goal

Create a local reusable project in `/Users/mark/Projects/AI/media-intake` for extracting
knowledge from media sources:

- local video files, using the validated Tron-Wiki distillation pattern;
- YouTube and other downloadable online video URLs;
- audio files and voice recordings, including Telegram-style `.ogg` / Opus voice files
  when provided as local files.

The tool should be callable from any project through a global local command:

```bash
media-intake extract <url-or-file> --output <packet-dir>
```

## Non-Goals

- Do not build a long-running local service in the MVP.
- Do not add Telegram chat integration in the MVP.
- Do not make AI Digest or Tron-Wiki the canonical output format.
- Do not commit heavy source media into knowledge bases by default.
- Do not use a vision model for baseline frame selection.
- Do not create a database until packet files become insufficient.

## Recommended Approach

Build a Python CLI with a reusable Python package underneath it. The CLI is the primary
interface for humans and project scripts. The package keeps acquisition, distillation,
packet writing, and adapters testable as separate modules.

Alternatives considered:

- Shell scripts only: fast to start, but weak for multiple source types, manifests,
  adapters, and tests.
- Local worker/API service: useful later for queues, but unnecessary operational weight
  for the first reusable version.

## Architecture

The pipeline has five stages:

1. Source resolution: identify whether input is a local file, YouTube URL, generic URL,
   video, or audio.
2. Acquisition: download online media with `yt-dlp` when possible, or copy/reference a
   local file into the packet cache.
3. Distillation: extract 16 kHz mono audio, transcribe with `whisper.cpp`, sample video
   frames with `ffmpeg`, remove near-consecutive duplicates with `mpdecimate`, then
   cluster frames using perceptual hash dedupe.
4. Packet writing: write stable files and a manifest that records inputs, outputs,
   commands, versions, status, and errors.
5. Adapter rendering: optionally convert a packet into a project-specific draft, such as
   AI Digest markdown.

The core packet stage is the system boundary. Adapters consume packets; they should not
own media extraction logic.

## Evidence Packet Contract

Default packet layout:

```text
<packet-dir>/
  manifest.json
  metadata.json
  transcript.srt
  transcript.json
  summary.md
  frames/
    0001.png
    0002.png
  cache/
    source.<ext>
    audio.wav
```

`cache/` may be deleted after a successful run unless the user asks to retain source
media. The durable artifacts are the manifest, metadata, transcript, summary, and selected
frames.

`manifest.json` records:

- tool version and run timestamp;
- input path or URL;
- detected source type and platform;
- output files;
- command status for acquisition, transcription, and frame extraction;
- warnings and recoverable errors;
- settings such as language, hash size, hash threshold, max frames, and model path.

`metadata.json` records source facts:

- title, author/channel, source URL, platform, duration, upload date when available;
- local source path and checksums when available;
- language when known or user-provided.

## CLI Design

Initial commands:

```bash
media-intake extract <url-or-file> --output <packet-dir>
media-intake extract <url-or-file> --profile ai-digest --output <export-root>
media-intake inspect <packet-dir>
media-intake cleanup <packet-dir> --remove-cache
```

Important options:

```text
--lang <code|auto>
--whisper-bin <path>
--whisper-model <path>
--fps <number>
--hash-size <number>
--hash-threshold <number>
--max-frames <number>
--metadata-only
--dry-run
--overwrite
--retain-source
--profile generic|ai-digest|tron-wiki
```

MVP profiles:

- `generic`: write only the evidence packet.
- `ai-digest`: render a draft AI Digest-compatible note from the packet.

Future profile:

- `tron-wiki`: render a storyboard/wiki-oriented layout compatible with the current
  Tron-Wiki media distillation pattern.

## Local Installation

The source of truth remains inside the project:

```text
/Users/mark/Projects/AI/media-intake/bin/media-intake
```

The global command is a symlink:

```text
/Users/mark/bin/media-intake -> /Users/mark/Projects/AI/media-intake/bin/media-intake
```

This follows the existing local pattern where `~/bin` exposes commands but does not own
their implementation.

## Dependencies

Required for the MVP:

- Python 3 standard library;
- `ffmpeg`;
- `yt-dlp`, or `uvx` / `uv` fallback for running `yt-dlp`;
- `whisper.cpp` `whisper-cli`;
- a local Whisper model, defaulting to a configurable path.

The frame dedupe implementation should remain dependency-light and may reuse the
stdlib-plus-ffmpeg perceptual hash approach from Tron-Wiki.

## Error Handling

- Preflight checks fail before expensive media work when required tools or models are
  missing.
- `--metadata-only` succeeds without media tooling when the source metadata can be
  captured.
- Existing packets are not overwritten unless `--overwrite` is passed.
- Failed stages are recorded in `manifest.json` with enough detail to rerun or continue.
- Online download failures should leave a packet skeleton when metadata is available, so
  the source can be manually acquired and retried.

## Testing

Unit tests should cover:

- source type detection;
- YouTube ID and metadata normalization;
- packet path generation;
- manifest writing and status transitions;
- frame dedupe behavior on generated or fixture images;
- adapter rendering for AI Digest.

Smoke tests should cover:

```bash
media-intake extract tests/fixtures/sample-audio.wav --output "$(mktemp -d)"
media-intake extract tests/fixtures/sample-video.mp4 --output "$(mktemp -d)" --metadata-only
media-intake inspect tests/fixtures/packet
```

Full media tests may be manual because they depend on local `ffmpeg`, `whisper.cpp`, and
models.

## Documentation

The project should include:

- `README.md`: purpose, quick start, install, examples;
- `docs/guides/video.md`: local video and online video workflow;
- `docs/guides/audio.md`: audio files, dictaphone recordings, and Telegram-style voice
  files;
- `docs/guides/project-adapters.md`: how AI Digest and future projects consume packets;
- `docs/guides/install-global-alias.md`: symlink setup and PATH expectations.

## Acceptance Criteria

The MVP is complete when:

- `/Users/mark/Projects/AI/media-intake` is a runnable local project;
- `media-intake` is available globally through `~/bin`;
- a local audio file produces a transcript packet;
- a local video file produces transcript plus deduplicated frames;
- a YouTube URL can be downloaded or at least metadata-captured and packetized;
- the AI Digest adapter can render a draft note from a packet;
- README and guides explain the local workflow without relying on chat history.
