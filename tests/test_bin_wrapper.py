import os
import subprocess
import tempfile
import unittest
from pathlib import Path


class BinWrapperTests(unittest.TestCase):
    def test_wrapper_works_through_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "media-intake"
            link.symlink_to(Path.cwd() / "bin" / "media-intake")

            env = dict(os.environ)
            env.pop("PYTHONPATH", None)
            result = subprocess.run([str(link), "--help"], text=True, capture_output=True, env=env)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("media-intake", result.stdout)


if __name__ == "__main__":
    unittest.main()
