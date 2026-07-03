# Project Adapters

The core Media Intake contract is the evidence packet. Adapters render that packet into a
project-specific draft without owning extraction logic.

## Generic Packet

```bash
media-intake extract /path/to/demo.mp4 --output /tmp/demo-packet --metadata-only
```

This writes only the packet files.

## AI Digest

```bash
media-intake extract "https://www.youtube.com/watch?v=puen8F_IPkQ" \
  --output /tmp/youtube-packet \
  --metadata-only \
  --profile ai-digest
```

The AI Digest profile writes `ai-digest-note.md` inside the packet. Treat it as a draft:
read `transcript.srt`, inspect `frames/`, then move or adapt the note into the AI Digest
vault.

## Tron-Wiki

The Tron-Wiki profile is reserved for a later adapter. Until then, use the generic packet
and compose a wiki page from `transcript.srt` plus `frames/`, following the existing
Tron-Wiki distillation pattern.
