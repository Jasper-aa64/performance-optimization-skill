"""Fixture tests for the convergence chart renderer. Run: python -B -m unittest discover -s <skill-root>/scripts -v."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("render_convergence_chart.py")

ROWS = [
    ("iter", "runtime_s", "label", "status", "lost", "unknown_pushes"),
    ("0", "72", "baseline", "PASS", "0", "0"),
    ("1", "66", "reuse bar template", "PASS", "0", "0"),
    ("2", "61", "lost pushes", "WARN_LOST_PUSH", "3", "0"),
    ("3", "60", "cache output strings", "PASS", "0", "0"),
]


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.tsv = self.dir / "points.tsv"
        self.tsv.write_text("\n".join("\t".join(row) for row in ROWS) + "\n", encoding="utf-8")

    def render(self, *extra):
        out = self.dir / "chart.svg"
        result = subprocess.run(
            [
                sys.executable, "-B", str(SCRIPT),
                "--input", str(self.tsv), "--output", str(out),
                "--y-column", "runtime_s", "--label-column", "label",
                "--title", "Landed safe optimizations: 2", "--subtitle", "72s -> 60s",
                "--y-title", "Runtime (s)", "--unit", "s", *extra,
            ],
            capture_output=True,
            text=True,
        )
        return result, out

    def test_one_point_per_row(self):
        result, out = self.render()
        self.assertEqual(result.returncode, 0, result.stderr)
        svg = out.read_text(encoding="utf-8")
        self.assertEqual(svg.count("<circle"), 4)
        self.assertIn("Landed safe optimizations: 2", svg)
        self.assertIn(">72s<", svg)

    def test_safe_only_drops_unsafe_rows(self):
        result, out = self.render("--safe-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        svg = out.read_text(encoding="utf-8")
        self.assertEqual(svg.count("<circle"), 3)
        self.assertNotIn("lost pushes", svg)

    def test_no_rows_fails_without_output(self):
        result, out = self.render("--filter", "status=NONE")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
