# Media Intake MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local `media-intake` CLI that creates reusable evidence packets from local audio, local video, and YouTube-style URLs, then expose it globally and document agent reuse.

**Architecture:** Implement a small Python package under `src/media_intake` with focused modules for source detection, packet manifests, media distillation, adapter rendering, and CLI routing. Keep the first version dependency-light: standard library plus external commands (`ffmpeg`, `yt-dlp`/`uvx`, `whisper-cli`) discovered at runtime. Create a Codex skill that teaches agents to use the CLI and a repo-owned Claude guide with the same operational contract.

**Tech Stack:** Python 3 standard library, `unittest`, `argparse`, `ffmpeg`, `yt-dlp`, `whisper.cpp`, shell symlink through `~/bin`.

---

## File Structure

- Create `pyproject.toml`: package metadata and console script definition.
- Create `bin/media-intake`: project-owned wrapper for global symlink use.
- Create `src/media_intake/__init__.py`: package version.
- Create `src/media_intake/sources.py`: source type detection and stable source IDs.
- Create `src/media_intake/packet.py`: packet paths, manifest, metadata, and file writing.
- Create `src/media_intake/commands.py`: subprocess wrapper, tool resolution, and preflight.
- Create `src/media_intake/dedupe_frames.py`: reusable perceptual-hash frame dedupe.
- Create `src/media_intake/distill.py`: audio extraction, transcription, frame extraction, URL acquisition orchestration.
- Create `src/media_intake/adapters.py`: generic and AI Digest markdown rendering.
- Create `src/media_intake/cli.py`: `extract`, `inspect`, and `cleanup` commands.
- Create `tests/`: unit tests and generated fixture helpers.
- Create `docs/guides/video.md`, `docs/guides/audio.md`, `docs/guides/project-adapters.md`, `docs/guides/install-global-alias.md`.
- Create `skills/media-intake/SKILL.md`: repo-owned skill source for agents.
- Create `skills/claude/media-intake.md`: Claude-oriented reusable guide.
- Install Codex skill copy at `/Users/mark/.codex/skills/media-intake`.
- Add `origin` remote `git@github.com:ludmanp/media-intake.git`.

## Task 1: Package Skeleton And Source Detection

**Files:**
- Create: `pyproject.toml`
- Create: `bin/media-intake`
- Create: `src/media_intake/__init__.py`
- Create: `src/media_intake/sources.py`
- Test: `tests/test_sources.py`

- [ ] **Step 1: Write failing source detection tests**

```python
from media_intake.sources import SourceKind, detect_source, stable_source_id


def test_detects_youtube_url():
    source = detect_source("https://www.youtube.com/watch?v=puen8F_IPkQ")
    assert source.kind == SourceKind.URL
    assert source.platform == "youtube"
    assert source.media_type == "video"
    assert source.source_id == "puen8F_IPkQ"


def test_detects_local_audio_file():
    source = detect_source("/tmp/voice.ogg")
    assert source.kind == SourceKind.FILE
    assert source.platform == "local"
    assert source.media_type == "audio"


def test_detects_local_video_file():
    source = detect_source("/tmp/demo.mp4")
    assert source.kind == SourceKind.FILE
    assert source.platform == "local"
    assert source.media_type == "video"


def test_stable_source_id_for_local_paths_is_filesystem_safe():
    assert stable_source_id("/tmp/My Voice Note.ogg") == "my-voice-note"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python3 -m unittest tests.test_sources -v`
Expected: FAIL or import error because `media_intake.sources` does not exist.

- [ ] **Step 3: Implement minimal package skeleton**

Implement `SourceKind`, `Source`, `detect_source`, YouTube ID extraction, extension-based media type detection, and `stable_source_id`. Add `pyproject.toml` and executable wrapper.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python3 -m unittest tests.test_sources -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml bin/media-intake src/media_intake tests/test_sources.py
git commit -m "feat: add media intake package skeleton"
```

## Task 2: Packet Manifest And Inspection

**Files:**
- Create: `src/media_intake/packet.py`
- Modify: `src/media_intake/cli.py`
- Test: `tests/test_packet.py`

- [ ] **Step 1: Write failing packet tests**

```python
import json
import tempfile
import unittest
from pathlib import Path

from media_intake.packet import create_packet, inspect_packet
from media_intake.sources import detect_source


class PacketTests(unittest.TestCase):
    def test_create_packet_writes_manifest_and_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = detect_source("/tmp/voice.ogg")
            packet = create_packet(source, Path(tmp), overwrite=False)
            manifest = json.loads(packet.manifest_path.read_text())
            metadata = json.loads(packet.metadata_path.read_text())
            self.assertEqual(manifest["status"], "created")
            self.assertEqual(manifest["source"]["media_type"], "audio")
            self.assertEqual(metadata["platform"], "local")

    def test_create_packet_refuses_existing_without_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = detect_source("/tmp/voice.ogg")
            create_packet(source, Path(tmp), overwrite=False)
            with self.assertRaises(FileExistsError):
                create_packet(source, Path(tmp), overwrite=False)

    def test_inspect_packet_returns_manifest_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = detect_source("/tmp/demo.mp4")
            packet = create_packet(source, Path(tmp), overwrite=False)
            summary = inspect_packet(packet.root)
            self.assertIn("status: created", summary)
            self.assertIn("media_type: video", summary)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python3 -m unittest tests.test_packet -v`
Expected: FAIL or import error because `media_intake.packet` does not exist.

- [ ] **Step 3: Implement packet writing and inspection**

Create packet directories, write `manifest.json`, `metadata.json`, `summary.md`, and expose `inspect_packet`.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python3 -m unittest tests.test_packet -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/media_intake/packet.py src/media_intake/cli.py tests/test_packet.py
git commit -m "feat: write reusable evidence packets"
```

## Task 3: CLI Commands

**Files:**
- Create: `src/media_intake/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI tests**

```python
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "media_intake.cli", *args],
            text=True,
            capture_output=True,
            env={"PYTHONPATH": "src"},
        )

    def test_extract_metadata_only_creates_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("extract", "/tmp/voice.ogg", "--output", tmp, "--metadata-only")
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((Path(tmp) / "manifest.json").read_text())
            self.assertEqual(manifest["status"], "metadata-only")

    def test_inspect_prints_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.run_cli("extract", "/tmp/demo.mp4", "--output", tmp, "--metadata-only")
            result = self.run_cli("inspect", tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("media_type: video", result.stdout)

    def test_cleanup_removes_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.run_cli("extract", "/tmp/demo.mp4", "--output", tmp, "--metadata-only")
            cache = Path(tmp) / "cache"
            cache.mkdir(exist_ok=True)
            (cache / "source.mp4").write_text("x")
            result = self.run_cli("cleanup", tmp, "--remove-cache")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(cache.exists())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python3 -m unittest tests.test_cli -v`
Expected: FAIL because CLI commands are not implemented.

- [ ] **Step 3: Implement CLI command routing**

Implement `argparse` subcommands `extract`, `inspect`, and `cleanup`. `--metadata-only` updates manifest status without requiring external media tools.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python3 -m unittest tests.test_cli -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/media_intake/cli.py tests/test_cli.py
git commit -m "feat: add media-intake cli commands"
```

## Task 4: Media Commands And Deterministic Distillation

**Files:**
- Create: `src/media_intake/commands.py`
- Create: `src/media_intake/dedupe_frames.py`
- Create: `src/media_intake/distill.py`
- Test: `tests/test_distill.py`

- [ ] **Step 1: Write failing distillation tests with dry-run command recorder**

```python
import tempfile
import unittest
from pathlib import Path

from media_intake.distill import plan_distillation
from media_intake.packet import create_packet
from media_intake.sources import detect_source


class DistillTests(unittest.TestCase):
    def test_audio_file_plan_extracts_wav_and_transcribes(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet = create_packet(detect_source("/tmp/voice.ogg"), Path(tmp), overwrite=False)
            plan = plan_distillation(packet, lang="auto")
            joined = "\n".join(" ".join(cmd) for cmd in plan.commands)
            self.assertIn("ffmpeg", joined)
            self.assertIn("audio.wav", joined)
            self.assertIn("whisper-cli", joined)
            self.assertNotIn("frames", joined)

    def test_video_file_plan_extracts_audio_transcript_and_frames(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet = create_packet(detect_source("/tmp/demo.mp4"), Path(tmp), overwrite=False)
            plan = plan_distillation(packet, lang="auto")
            joined = "\n".join(" ".join(cmd) for cmd in plan.commands)
            self.assertIn("ffmpeg", joined)
            self.assertIn("mpdecimate", joined)
            self.assertIn("frames/%04d.png", joined)
            self.assertIn("dedupe", joined)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python3 -m unittest tests.test_distill -v`
Expected: FAIL because `media_intake.distill` does not exist.

- [ ] **Step 3: Implement command planning and execution hooks**

Add preflight helpers, command plan objects, audio extraction, Whisper command construction, frame extraction, and the dedupe function entrypoint. Keep dry-run and metadata-only independent from external tool presence.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python3 -m unittest tests.test_distill -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/media_intake/commands.py src/media_intake/dedupe_frames.py src/media_intake/distill.py tests/test_distill.py
git commit -m "feat: plan media distillation commands"
```

## Task 5: AI Digest Adapter

**Files:**
- Create: `src/media_intake/adapters.py`
- Modify: `src/media_intake/cli.py`
- Test: `tests/test_adapters.py`

- [ ] **Step 1: Write failing adapter tests**

```python
import tempfile
import unittest
from pathlib import Path

from media_intake.adapters import render_ai_digest_note
from media_intake.packet import create_packet
from media_intake.sources import detect_source


class AdapterTests(unittest.TestCase):
    def test_ai_digest_note_uses_packet_as_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet = create_packet(detect_source("https://www.youtube.com/watch?v=puen8F_IPkQ"), Path(tmp), overwrite=False)
            note = render_ai_digest_note(packet)
            self.assertIn("source_type: video", note)
            self.assertIn("source_packet:", note)
            self.assertIn("## Visual Evidence", note)
            self.assertIn("puen8F_IPkQ", note)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python3 -m unittest tests.test_adapters -v`
Expected: FAIL because adapter module does not exist.

- [ ] **Step 3: Implement adapter rendering**

Render AI Digest markdown draft from packet metadata. Wire `--profile ai-digest` to write `ai-digest-note.md` inside the packet for MVP.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python3 -m unittest tests.test_adapters -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/media_intake/adapters.py src/media_intake/cli.py tests/test_adapters.py
git commit -m "feat: render ai digest packet drafts"
```

## Task 6: Documentation And Agent Skills

**Files:**
- Modify: `README.md`
- Create: `docs/guides/video.md`
- Create: `docs/guides/audio.md`
- Create: `docs/guides/project-adapters.md`
- Create: `docs/guides/install-global-alias.md`
- Create: `skills/media-intake/SKILL.md`
- Create: `skills/claude/media-intake.md`
- Install: `/Users/mark/.codex/skills/media-intake/SKILL.md`

- [ ] **Step 1: Write docs and skill validation checks**

Run after docs exist:

```bash
test -f docs/guides/video.md
test -f docs/guides/audio.md
test -f skills/media-intake/SKILL.md
test -f /Users/mark/.codex/skills/media-intake/SKILL.md
```

- [ ] **Step 2: Create documentation**

Write concise guides for local video, online video, audio/voice files, adapters, and global symlink installation.

- [ ] **Step 3: Create reusable agent skill content**

Create `skills/media-intake/SKILL.md` with frontmatter:

```yaml
---
name: media-intake
description: Use when Codex needs to extract reusable evidence from local audio files, voice recordings, local videos, YouTube links, or downloadable online videos with the local /Users/mark/Projects/AI/media-intake CLI; includes AI Digest and Tron-Wiki style packet workflows.
---
```

Install a copy to `/Users/mark/.codex/skills/media-intake/SKILL.md`.

- [ ] **Step 4: Validate skill**

Run: `python3 /Users/mark/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/mark/.codex/skills/media-intake`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add README.md docs/guides skills
git commit -m "docs: add media intake guides and agent skill"
```

## Task 7: Global Alias, Verification, And GitHub Remote

**Files:**
- Create symlink: `/Users/mark/bin/media-intake`
- Modify git remote config.

- [ ] **Step 1: Install global symlink**

```bash
mkdir -p /Users/mark/bin
ln -sfn /Users/mark/Projects/AI/media-intake/bin/media-intake /Users/mark/bin/media-intake
```

- [ ] **Step 2: Verify command and tests**

```bash
PYTHONPATH=src python3 -m unittest -v
/Users/mark/bin/media-intake extract /tmp/voice.ogg --output "$(mktemp -d)" --metadata-only
/Users/mark/bin/media-intake --help
```

Expected: all tests pass; metadata-only extract exits 0; help prints command usage.

- [ ] **Step 3: Add remote and push**

```bash
git remote add origin git@github.com:ludmanp/media-intake.git
git push -u origin main
```

- [ ] **Step 4: Commit final install note if needed**

If README or docs changed during verification:

```bash
git add README.md docs/guides/install-global-alias.md
git commit -m "docs: document local media-intake install"
```
