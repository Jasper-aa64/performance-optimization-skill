#!/usr/bin/env python3
"""Read-only local HFT-wf inventory; never imports or executes inspected scripts.

stdout is JSON. Exit 0: core inventory and exact Git root read successfully.
Exit 2: incomplete inventory. Neither exit status approves execution.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess


CORE = (
    "docs/optimization_harness_operator_manual.md",
    "scripts/headless_auto_loop.py",
    "scripts/headless_remote.sh",
    "scripts/patch_agent.py",
    "scripts/attempts_schema.py",
    "scripts/perf_validation_lock.py",
)
OPTIONAL = (
    "AGENTS.md",
    "scripts/perf_capability.py",
    "scripts/performance_report_gate.py",
    "scripts/twap_headless_remote.sh",
    "docs/twap_perf_runbook.md",
    ".trellis/workflow.md",
    ".trellis/scripts/task.py",
    "05-Paper/experiments/public_second_target_202609/scripts/candidate_runner.py",
)


def literal_options(source: str) -> list[str]:
    """Extract literal add_argument flags, not a claim of full CLI semantics."""
    options = set()
    for node in ast.walk(ast.parse(source)):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_argument"):
            continue
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                if arg.value.startswith("-"):
                    options.add(arg.value)
    return sorted(options)


def inspect_file(root: Path, relative: str) -> dict:
    row = {"path": relative, "required_for_core_inventory": relative in CORE}
    path = root / relative
    try:
        if not path.resolve().is_relative_to(root):
            return {**row, "status": "outside_root"}
        if not path.is_file():
            return {**row, "status": "missing"}
        raw = path.read_bytes()
        row.update(status="present", size_bytes=len(raw),
                   sha256=hashlib.sha256(raw).hexdigest())
        if not raw.strip():
            row["status"] = "empty"
        elif path.suffix == ".py":
            row["literal_cli_options"] = literal_options(raw.decode("utf-8-sig"))
    except (OSError, UnicodeError, SyntaxError, RuntimeError) as exc:
        row.update(status="unreadable_or_unparseable", error_type=type(exc).__name__)
    return row


def git_inventory(root: Path) -> dict:
    def run(*args: str) -> subprocess.CompletedProcess:
        # No shell, hooks, fetch, index refresh, submodule traversal or env dump.
        return subprocess.run(
            ["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-C",
             str(root), *args], capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=15, check=False,
        )

    try:
        top = run("rev-parse", "--show-toplevel")
        if top.returncode:
            return {"status": "unavailable", "reason": "git root not readable"}
        if Path(top.stdout.strip()).resolve() != root:
            return {"status": "wrong_root", "reason": "ancestor repository is not this root"}
        head = run("rev-parse", "--verify", "HEAD")
        state = run("status", "--porcelain=v1", "--untracked-files=no", "--ignore-submodules=all")
        if head.returncode or state.returncode:
            return {"status": "unavailable", "reason": "HEAD or tracked status not readable"}
        return {"status": "readable", "head": head.stdout.strip(),
                "tracked_changes_present": bool(state.stdout.strip()),
                "untracked_files": "not_enumerated", "submodules": "not_inspected"}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "unavailable", "reason": type(exc).__name__}


def inspect(root: Path) -> dict:
    root = root.resolve()
    files = [inspect_file(root, rel) for rel in (*CORE, *OPTIONAL)]
    git = git_inventory(root) if root.is_dir() else {"status": "unavailable", "reason": "missing root"}
    issues = [row["path"] for row in files
              if row["required_for_core_inventory"] and row["status"] != "present"]
    if git["status"] != "readable":
        issues.append("git_exact_root")
    return {
        "schema_version": 1, "root": str(root), "git": git, "files": files,
        "inventory_status": "complete" if not issues else "incomplete",
        "core_issues": issues,
        "execution_readiness": "not_assessed",
        "unverified": ["remote host and lock", "toolchain and services", "workload",
                       "correctness", "model dispatch and provenance", "run budget",
                       "policy validity", "actual terminal and replication evidence"],
        "notes": ["Local read-only inventory, not a runner or promotion gate.",
                  "File hashes establish current content only, not prior freezing.",
                  "Optional missing adapters remain missing; no substitute was selected.",
                  "CLI options are literal AST observations, not executable command plans."],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    result = inspect(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["inventory_status"] == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
