import contextlib
import io
import json
import unittest

from formula_trace.cli import main

SHEET = """cell,formula
A1,10
A2,20
B1,=A1+A2
B2,=SUM(A1:A2)
C1,=B1*B2
"""


class JsonFormatTests(unittest.TestCase):
    def _run(self, argv):
        stdout = io.StringIO()
        stdin = io.StringIO(SHEET)
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stdin(stdin):
            status = main(argv)
        return status, stdout.getvalue()

    def test_default_format_is_plain_text(self):
        status, output = self._run(["--cell", "C1"])
        self.assertEqual(status, 0)
        self.assertEqual(output.splitlines(), ["A1", "A2", "B1", "B2"])

    def test_json_format_is_a_single_object(self):
        status, output = self._run(["--cell", "C1", "--format", "json"])
        self.assertEqual(status, 0)
        payload = json.loads(output)
        self.assertEqual(payload["cell"], "C1")
        self.assertEqual(payload["direction"], "precedents")
        self.assertFalse(payload["direct_only"])
        self.assertEqual(payload["references"], ["A1", "A2", "B1", "B2"])

    def test_json_format_respects_direct_only_and_direction(self):
        status, output = self._run(
            ["--cell", "A1", "--direction", "dependents", "--direct-only", "--format", "json"]
        )
        self.assertEqual(status, 0)
        payload = json.loads(output)
        self.assertEqual(payload["direction"], "dependents")
        self.assertTrue(payload["direct_only"])
        self.assertEqual(payload["references"], ["B1", "B2"])

    def test_json_output_is_a_single_line(self):
        _, output = self._run(["--cell", "C1", "--format", "json"])
        self.assertEqual(len(output.strip().splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
