# Audio And Voice Workflow

Use Media Intake for dictaphone recordings, audio files, exported voice messages, and
audio-only online media.

Supported audio-like extensions include `.mp3`, `.m4a`, `.wav`, `.ogg`, `.oga`, `.opus`,
`.flac`, `.aac`, and `.webm`.

## Local Audio

```bash
media-intake extract /path/to/voice.ogg --output /tmp/voice-packet --dry-run
media-intake extract /path/to/recording.m4a --output /tmp/recording-packet --overwrite
```

The audio pipeline extracts a normalized `cache/audio.wav` at 16 kHz mono, then runs
`whisper-cli` to produce `transcript.srt`.

## Telegram-Style Voice Files

Telegram voice messages usually export as `.ogg` / Opus files. In the MVP, Media Intake
does not connect to Telegram chats directly; pass the exported local file to `extract`.

```bash
media-intake extract ~/Downloads/voice-message.ogg --output /tmp/voice-message-packet
```

## Metadata-Only Skeleton

Use this when media tooling is missing or when you want to reserve a packet before full
processing:

```bash
media-intake extract /path/to/voice.ogg --output /tmp/voice-packet --metadata-only
```
