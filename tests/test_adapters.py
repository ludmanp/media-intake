import tempfile
import unittest
from pathlib import Path

from media_intake.adapters import render_ai_digest_note
from media_intake.packet import create_packet
from media_intake.sources import detect_source


class AdapterTests(unittest.TestCase):
    def test_ai_digest_note_uses_packet_as_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet = create_packet(
                detect_source("https://www.youtube.com/watch?v=puen8F_IPkQ"),
                Path(tmp),
                overwrite=False,
            )

            note = render_ai_digest_note(packet)

            self.assertIn("source_type: video", note)
            self.assertIn("source_packet:", note)
            self.assertIn("## Visual Evidence", note)
            self.assertIn("puen8F_IPkQ", note)


if __name__ == "__main__":
    unittest.main()
