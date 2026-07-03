---
name: media-intake
description: Use when Codex needs to extract reusable evidence from local audio files, voice recordings, local videos, YouTube links, or downloadable online videos with the local /Users/mark/Projects/AI/media-intake CLI; includes generic evidence packets and AI Digest style draft workflows.
---

# Media Intake

Use the local Media Intake CLI to create evidence packets before summarizing or adapting
media content. Prefer packet evidence over transcript-only reasoning when video has a
visual layer.

## Command

```bash
/Users/mark/Projects/AI/media-intake/bin/media-intake extract <url-or-file> --output <packet-dir>
```

If `media-intake` is available on `PATH`, that global command points to the same
project-owned entrypoint.

## Workflow

1. Choose an output directory outside the target knowledge base unless the user names a
   target path.
2. Run `--metadata-only` when only source registration is needed or media tooling may be
   unavailable.
3. Run `--dry-run` before a full media run on a new machine or unknown source.
4. For video, inspect both `transcript.srt` and `frames/`; frames are evidence, not
   decoration.
5. For audio or voice files, use the transcript plus `metadata.json` and `manifest.json`.
6. Use `--profile ai-digest` only to create a draft `ai-digest-note.md`; review it before
   moving content into the vault.

## Examples

```bash
media-intake extract /path/to/voice.ogg --output /tmp/voice-packet --metadata-only
media-intake extract /path/to/demo.mp4 --output /tmp/demo-packet --dry-run
media-intake extract /path/to/voice.ogg --output /tmp/voice-packet --lang ru
media-intake inspect /tmp/demo-packet
media-intake cleanup /tmp/demo-packet --remove-cache
```

## Boundaries

- Do not commit heavy source media by default.
- Do not treat transcript-only output as enough for screen demos, slides, UI flows,
  diagrams, or code walkthroughs.
- Do not call graph builders as part of extraction; graph analysis is a later sidecar.
