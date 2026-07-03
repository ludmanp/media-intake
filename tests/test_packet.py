import json
import tempfile
import unittest
from pathlib import Path

from media_intake.packet import create_packet, inspect_packet, update_manifest_status
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
            self.assertTrue(packet.summary_path.exists())
            self.assertTrue(packet.cache_dir.exists())

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
            self.assertIn("platform: local", summary)

    def test_update_manifest_status_records_output_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet = create_packet(detect_source("/tmp/demo.mp4"), Path(tmp), overwrite=False)

            update_manifest_status(packet, "metadata-only", outputs=["metadata.json"])

            manifest = json.loads(packet.manifest_path.read_text())
            self.assertEqual(manifest["status"], "metadata-only")
            self.assertEqual(manifest["outputs"], ["metadata.json"])


if __name__ == "__main__":
    unittest.main()
