import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        return subprocess.run(
            [sys.executable, "-m", "media_intake.cli", *args],
            text=True,
            capture_output=True,
            env=env,
        )

    def test_extract_metadata_only_creates_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("extract", "/tmp/voice.ogg", "--output", tmp, "--metadata-only")

            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((Path(tmp) / "manifest.json").read_text())
            self.assertEqual(manifest["status"], "metadata-only")

    def test_extract_dry_run_plans_distillation(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("extract", "/tmp/voice.ogg", "--output", tmp, "--dry-run")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("+ ffmpeg", result.stdout)
            manifest = json.loads((Path(tmp) / "manifest.json").read_text())
            self.assertEqual(manifest["status"], "dry-run")

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


if __name__ == "__main__":
    unittest.main()
