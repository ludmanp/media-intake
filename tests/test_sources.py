import unittest

from media_intake.sources import SourceKind, detect_source, stable_source_id


class SourceDetectionTests(unittest.TestCase):
    def test_detects_youtube_url(self):
        source = detect_source("https://www.youtube.com/watch?v=puen8F_IPkQ")

        self.assertEqual(source.kind, SourceKind.URL)
        self.assertEqual(source.platform, "youtube")
        self.assertEqual(source.media_type, "video")
        self.assertEqual(source.source_id, "puen8F_IPkQ")

    def test_detects_youtu_be_url(self):
        source = detect_source("https://youtu.be/puen8F_IPkQ?si=abc")

        self.assertEqual(source.source_id, "puen8F_IPkQ")
        self.assertEqual(source.platform, "youtube")
        self.assertEqual(source.media_type, "video")

    def test_detects_local_audio_file(self):
        source = detect_source("/tmp/voice.ogg")

        self.assertEqual(source.kind, SourceKind.FILE)
        self.assertEqual(source.platform, "local")
        self.assertEqual(source.media_type, "audio")

    def test_detects_local_video_file(self):
        source = detect_source("/tmp/demo.mp4")

        self.assertEqual(source.kind, SourceKind.FILE)
        self.assertEqual(source.platform, "local")
        self.assertEqual(source.media_type, "video")

    def test_stable_source_id_for_local_paths_is_filesystem_safe(self):
        self.assertEqual(stable_source_id("/tmp/My Voice Note.ogg"), "my-voice-note")


if __name__ == "__main__":
    unittest.main()
