"""Local fixture tests only. Run: python -B -m unittest discover -s <skill-root>/adapters/hft-wf -v."""

import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import inspect_harness as inventory


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def write(self, rel, value):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")
        return path

    def fill_core(self):
        for rel in inventory.CORE:
            self.write(rel, "# fixture\n")

    def test_literal_options_no_execution(self):
        sentinel = self.root / "MUST_NOT_EXIST"
        src = (f"from pathlib import Path\nPath({str(sentinel)!r}).touch()\n"
               "parser.add_argument('--dry-run', '-d')\n"
               "parser.add_argument(dynamic_option)\n")
        self.assertEqual(inventory.literal_options(src), ["--dry-run", "-d"])
        self.assertFalse(sentinel.exists())

    def test_duplicate_options_deduplicated(self):
        self.assertEqual(inventory.literal_options("p.add_argument('--x')\np.add_argument('--x')"), ["--x"])

    def test_no_fake_cli_from_comments(self):
        self.assertEqual(inventory.literal_options("# p.add_argument('--x')\ns = '--y'"), [])

    def test_content_hash_and_options(self):
        rel = "scripts/headless_auto_loop.py"
        path = self.write(rel, "p.add_argument('--run-dir')\n")
        row = inventory.inspect_file(self.root, rel)
        self.assertEqual(row["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(row["literal_cli_options"], ["--run-dir"])

    def test_bad_python_is_not_present(self):
        rel = "scripts/headless_auto_loop.py"
        self.write(rel, "def broken(:")
        self.assertEqual(inventory.inspect_file(self.root, rel)["status"], "unreadable_or_unparseable")

    def test_missing_file_explicit(self):
        self.assertEqual(inventory.inspect_file(self.root, inventory.CORE[0])["status"], "missing")

    def test_empty_file_explicit(self):
        self.write(inventory.CORE[0], "  \n")
        self.assertEqual(inventory.inspect_file(self.root, inventory.CORE[0])["status"], "empty")

    def test_path_escape_refused(self):
        self.assertEqual(inventory.inspect_file(self.root, "../outside.txt")["status"], "outside_root")

    def test_complete_inventory_does_not_grant_readiness(self):
        self.fill_core()
        with patch.object(inventory, "git_inventory", return_value={"status": "readable"}):
            result = inventory.inspect(self.root)
        self.assertEqual(result["inventory_status"], "complete")
        self.assertEqual(result["execution_readiness"], "not_assessed")
        self.assertTrue(all(r["status"] == "missing" for r in result["files"] if not r["required_for_core_inventory"]))

    def test_missing_core_scans_all_files(self):
        with patch.object(inventory, "git_inventory", return_value={"status": "readable"}):
            result = inventory.inspect(self.root)
        self.assertEqual(result["inventory_status"], "incomplete")
        self.assertEqual(len(result["core_issues"]), len(inventory.CORE))
        self.assertEqual(len(result["files"]), len(inventory.CORE) + len(inventory.OPTIONAL))

    def test_inspection_does_not_write_tree(self):
        self.fill_core()
        before = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        with patch.object(inventory, "git_inventory", return_value={"status": "readable"}):
            inventory.inspect(self.root)
        after = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_ancestor_git_is_not_own_repository(self):
        fake = subprocess.CompletedProcess([], 0, str(self.root.parent), "")
        with patch.object(inventory.subprocess, "run", return_value=fake) as call:
            result = inventory.git_inventory(self.root)
        self.assertEqual(result["status"], "wrong_root")
        self.assertEqual(call.call_count, 1)

    def test_missing_git_and_timeout_visible(self):
        for error in (FileNotFoundError(), subprocess.TimeoutExpired("git", 15)):
            with self.subTest(error=type(error).__name__):
                with patch.object(inventory.subprocess, "run", side_effect=error):
                    self.assertEqual(inventory.git_inventory(self.root)["status"], "unavailable")

    def test_git_invocations_are_read_only(self):
        responses = [subprocess.CompletedProcess([], 0, str(self.root), ""),
                     subprocess.CompletedProcess([], 0, "a" * 40, ""),
                     subprocess.CompletedProcess([], 0, " M user.txt\n", "")]
        with patch.object(inventory.subprocess, "run", side_effect=responses) as call:
            result = inventory.git_inventory(self.root)
        self.assertTrue(result["tracked_changes_present"])
        self.assertEqual(result["untracked_files"], "not_enumerated")
        for invocation in call.call_args_list:
            command = invocation.args[0]
            self.assertIn("--no-optional-locks", command)
            self.assertIn("core.fsmonitor=false", command)
            self.assertNotIn("shell", invocation.kwargs)


if __name__ == "__main__":
    unittest.main()
