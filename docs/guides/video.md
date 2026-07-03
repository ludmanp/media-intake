# Video Workflow

Use Media Intake for local screen recordings, downloaded videos, and YouTube URLs.

## Local Video

```bash
media-intake extract /path/to/demo.mp4 --output /tmp/demo-packet --dry-run
media-intake extract /path/to/demo.mp4 --output /tmp/demo-packet --overwrite
```

The video path is treated as the source. The packet keeps extracted audio in `cache/`,
transcript output at `transcript.srt`, and deduplicated visual evidence in `frames/`.

Frame extraction follows the Tron-Wiki pattern:

1. sample frames with `ffmpeg`;
2. remove near-consecutive duplicates with `mpdecimate`;
3. cluster remaining frames with perceptual hash dedupe;
4. keep the source video disposable.

## YouTube And Online Video

```bash
media-intake extract "https://www.youtube.com/watch?v=puen8F_IPkQ" --output /tmp/youtube-packet --dry-run
```

For YouTube, Media Intake plans a `yt-dlp` acquisition step before audio and frame
distillation. If download fails, create a metadata-only packet and manually acquire the
media into `cache/source.mp4` before retrying.

## Useful Options

```bash
media-intake extract /path/to/demo.mp4 --output /tmp/demo-packet --metadata-only
media-intake extract /path/to/demo.mp4 --output /tmp/demo-packet --dry-run
media-intake extract /path/to/demo.mp4 --output /tmp/demo-packet --overwrite
media-intake cleanup /tmp/demo-packet --remove-cache
```

Use `--dry-run` before the first full run on a new machine to confirm the exact commands.
