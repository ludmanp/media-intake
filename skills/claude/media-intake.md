# Media Intake Guide For Claude

Use `/Users/mark/Projects/AI/media-intake/bin/media-intake` when asked to extract
knowledge from audio, voice recordings, local videos, YouTube links, or downloadable
online videos.

Default workflow:

1. Create an evidence packet with `media-intake extract <source> --output <packet-dir>`.
2. Use `--metadata-only` for source registration or when tools may be missing.
3. Use `--dry-run` before full media processing.
4. For video, inspect `frames/` and `transcript.srt`; visual frames are primary evidence
   for UI, slides, charts, prompts, and demos.
5. For audio, use `transcript.srt`, `metadata.json`, and `manifest.json`.
6. Keep `cache/` disposable unless the user asks to retain source media.

Useful commands:

```bash
media-intake extract /path/to/voice.ogg --output /tmp/voice-packet --metadata-only
media-intake extract /path/to/demo.mp4 --output /tmp/demo-packet --dry-run
media-intake extract /path/to/voice.ogg --output /tmp/voice-packet --lang ru
media-intake extract "https://www.youtube.com/watch?v=puen8F_IPkQ" --output /tmp/youtube-packet --profile ai-digest --metadata-only
media-intake inspect /tmp/youtube-packet
media-intake cleanup /tmp/youtube-packet --remove-cache
```
