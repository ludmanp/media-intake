# Media Intake

Local reusable media extraction toolkit for turning videos, online media links, audio
files, and voice recordings into durable evidence packets that other projects can adapt
into their own formats.

## Status

Design stage. The accepted design lives in
`docs/superpowers/specs/2026-07-03-media-intake-design.md`.

## Target Command

```bash
media-intake extract <url-or-file> --output <packet-dir>
```

The global command should be installed as a symlink from `~/bin/media-intake` to the
project-owned entrypoint.

## Core Idea

Media Intake prepares evidence. It does not decide how a project should publish that
evidence. The core output is an evidence packet containing metadata, transcript,
selected frames when video has a visual layer, status, errors, and a draft summary.

Project adapters can later convert that packet into AI Digest notes, Tron-Wiki pages, or
other knowledge-base formats.
