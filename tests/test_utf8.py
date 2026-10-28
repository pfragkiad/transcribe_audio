import os
import subprocess
import sys
import unittest
from pathlib import Path


class Utf8Tests(unittest.TestCase):
    def test_cli_overrides_legacy_console_encoding(self):
        code = (
            "import sys; import transcript; "
            "sys.argv = ['transcript.py', '--help']\n"
            "try:\n"
            "    transcript.main()\n"
            "except SystemExit as exc:\n"
            "    assert exc.code == 0\n"
            "print('你好(nǐ hǎo)')\n"
            "print('中文', file=sys.stderr)\n"
            "assert sys.stdin.encoding == 'utf-8'\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=Path(__file__).resolve().parents[1],
            env={**os.environ, "PYTHONIOENCODING": "cp1253", "PYTHONUTF8": "0"},
            capture_output=True,
            check=True,
        )
        self.assertIn("你好(nǐ hǎo)", result.stdout.decode("utf-8"))
        self.assertEqual(result.stderr.decode("utf-8").strip(), "中文")


if __name__ == "__main__":
    unittest.main()
