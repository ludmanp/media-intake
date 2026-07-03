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
            self.assertIn(".cache/media-intake/models/ggml-large-v3-turbo-q5_0.bin", joined)
            self.assertNotIn("frames/%04d.png", joined)

    def test_custom_whisper_model_is_used_in_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet = create_packet(detect_source("/tmp/voice.ogg"), Path(tmp), overwrite=False)

            plan = plan_distillation(packet, lang="ru", whisper_model="/models/custom.bin")

            joined = "\n".join(" ".join(cmd) for cmd in plan.commands)
            self.assertIn("-l ru", joined)
            self.assertIn("/models/custom.bin", joined)

    def test_video_file_plan_extracts_audio_transcript_and_frames(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet = create_packet(detect_source("/tmp/demo.mp4"), Path(tmp), overwrite=False)

            plan = plan_distillation(packet, lang="auto")

            joined = "\n".join(" ".join(cmd) for cmd in plan.commands)
            self.assertIn("ffmpeg", joined)
            self.assertIn("mpdecimate", joined)
            self.assertIn("frames/%04d.png", joined)
            self.assertIn("dedupe-frames", joined)

    def test_youtube_plan_downloads_before_distilling(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet = create_packet(
                detect_source("https://www.youtube.com/watch?v=puen8F_IPkQ"),
                Path(tmp),
                overwrite=False,
            )

            plan = plan_distillation(packet, lang="auto")

            first = " ".join(plan.commands[0])
            self.assertIn("yt-dlp", first)
            self.assertIn("puen8F_IPkQ", first)


if __name__ == "__main__":
    unittest.main()
