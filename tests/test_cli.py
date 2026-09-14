import json
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

from envdrift.cli import main


class CliTests(unittest.TestCase):
    def test_json_output_and_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            reference = tmp / ".env.example"
            target = tmp / ".env"

            reference.write_text("API_KEY=required\nPORT=8000\n", encoding="utf-8")
            target.write_text("API_KEY=value\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main([str(reference), str(target), "--json"])

            payload = json.loads(stdout.getvalue())
            self.assertEqual(code, 1)
            self.assertEqual(payload["missing"], ["PORT"])
            self.assertFalse(payload["ok"])

    def test_missing_file_returns_two(self):
        stderr = StringIO()
        with redirect_stderr(stderr):
            code = main(["missing.example", "missing.env"])

        self.assertEqual(code, 2)
        self.assertIn("not found", stderr.getvalue().lower())


if __name__ == "__main__":
    unittest.main()
