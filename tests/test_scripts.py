from __future__ import annotations

import json
import plistlib
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN = ROOT / "scripts" / "scan.py"
ORPHANS = ROOT / "scripts" / "scan_orphans.py"
TIDY = ROOT / "scripts" / "tidy_paths.py"


def allocate(path: Path, mib: int = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x" * mib * 1024 * 1024)


def run(*args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *(str(arg) for arg in args)],
        capture_output=True,
        text=True,
        check=False,
    )


def approval_token(output: str) -> str:
    match = re.search(r"^Approval token: (.+)$", output, re.MULTILINE)
    if not match:
        raise AssertionError(f"missing approval token in: {output}")
    return match.group(1)


class ScanTests(unittest.TestCase):
    def test_library_and_dev_scans_are_structured_and_exclude_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / "home"
            cwd = home / "Development" / "active"
            cache = home / "Library" / "Caches" / "example"
            nested = home / "Library" / "Application Support" / "Editor" / "Code Cache"
            stale_modules = home / "Development" / "stale" / "node_modules"
            active_modules = cwd / "node_modules"
            allocate(cache / "data")
            allocate(nested / "data")
            allocate(stale_modules / "data")
            allocate(active_modules / "data")
            (stale_modules.parent / "package.json").write_text("{}", encoding="utf-8")
            (cwd / "package.json").write_text("{}", encoding="utf-8")

            library_result = run(
                SCAN,
                "--scope",
                "library",
                "--home",
                home,
                "--cwd",
                cwd,
                "--min-size-mb",
                1,
            )
            self.assertEqual(library_result.returncode, 0, library_result.stderr)
            library_payload = json.loads(library_result.stdout)
            paths = {item["path"] for item in library_payload["findings"]}
            self.assertIn(str(cache.resolve()), paths)
            self.assertIn(str(nested.resolve()), paths)
            self.assertTrue(library_payload["read_only"])

            dev_result = run(
                SCAN,
                "--scope",
                "dev",
                "--home",
                home,
                "--cwd",
                cwd,
                "--dev-root",
                home / "Development",
                "--min-size-mb",
                1,
            )
            self.assertEqual(dev_result.returncode, 0, dev_result.stderr)
            dev_payload = json.loads(dev_result.stdout)
            paths = {item["path"] for item in dev_payload["findings"]}
            self.assertIn(str(stale_modules.resolve()), paths)
            self.assertNotIn(str(active_modules.resolve()), paths)

    def test_orphan_scan_reports_unmatched_without_calling_it_orphaned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / "home"
            apps = root / "Applications"
            info = apps / "Example.app" / "Contents" / "Info.plist"
            info.parent.mkdir(parents=True)
            with info.open("wb") as handle:
                plistlib.dump(
                    {
                        "CFBundleIdentifier": "com.example.editor",
                        "CFBundleName": "Example",
                    },
                    handle,
                )
            matched = home / "Library" / "Caches" / "com.example.editor"
            unmatched = home / "Library" / "Caches" / "com.absent.tool"
            allocate(matched / "data")
            allocate(unmatched / "data")

            result = run(
                ORPHANS,
                "--home",
                home,
                "--applications-root",
                apps,
                "--min-size-mb",
                1,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            by_path = {item["path"]: item for item in payload["candidates"]}
            self.assertEqual(by_path[str(matched.resolve())]["status"], "matched")
            self.assertEqual(by_path[str(unmatched.resolve())]["status"], "unmatched")
            self.assertNotIn(
                "orphan", json.dumps(by_path[str(unmatched.resolve())]).casefold()
            )


class TidyPathTests(unittest.TestCase):
    def test_prepare_then_move_to_trash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / "home"
            cwd = home / "Development" / "active"
            target = home / "Library" / "Caches" / "Example" / "Cache"
            plan = root / "plan.json"
            (home / ".Trash").mkdir(parents=True)
            cwd.mkdir(parents=True)
            allocate(target / "data")

            prepared = run(
                TIDY,
                "prepare",
                target,
                "--plan",
                plan,
                "--home",
                home,
                "--cwd",
                cwd,
            )
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            applied = run(
                TIDY,
                "apply",
                "--plan",
                plan,
                "--approval-token",
                approval_token(prepared.stdout),
            )
            self.assertEqual(applied.returncode, 0, applied.stderr)
            self.assertFalse(target.exists())
            self.assertTrue((home / ".Trash" / "Cache").exists())
            self.assertTrue(plan.with_suffix(".json.receipt.json").exists())

    def test_refuses_current_project_and_changed_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / "home"
            cwd = home / "Development" / "active"
            active_target = cwd / "node_modules"
            stale_target = home / "Development" / "stale" / "node_modules"
            plan = root / "plan.json"
            (home / ".Trash").mkdir(parents=True)
            allocate(active_target / "data")
            allocate(stale_target / "data")

            refused = run(
                TIDY,
                "prepare",
                active_target,
                "--plan",
                plan,
                "--home",
                home,
                "--cwd",
                cwd,
            )
            self.assertEqual(refused.returncode, 2)
            self.assertIn("current project", refused.stderr)

            prepared = run(
                TIDY,
                "prepare",
                stale_target,
                "--plan",
                plan,
                "--home",
                home,
                "--cwd",
                cwd,
            )
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            allocate(stale_target / "new-data")
            changed = run(
                TIDY,
                "apply",
                "--plan",
                plan,
                "--approval-token",
                approval_token(prepared.stdout),
            )
            self.assertEqual(changed.returncode, 2)
            self.assertIn("changed since planning", changed.stderr)
            self.assertTrue(stale_target.exists())

    def test_refuses_user_content_and_modified_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / "home"
            cwd = home / "Development" / "active"
            protected = home / "Documents" / "node_modules"
            target = home / "Development" / "stale" / "node_modules"
            plan = root / "plan.json"
            (home / ".Trash").mkdir(parents=True)
            cwd.mkdir(parents=True)
            allocate(protected / "data")
            allocate(target / "data")

            refused = run(
                TIDY,
                "prepare",
                protected,
                "--plan",
                plan,
                "--home",
                home,
                "--cwd",
                cwd,
            )
            self.assertEqual(refused.returncode, 2)
            self.assertIn("user content", refused.stderr)

            prepared = run(
                TIDY,
                "prepare",
                target,
                "--plan",
                plan,
                "--home",
                home,
                "--cwd",
                cwd,
            )
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            payload = json.loads(plan.read_text(encoding="utf-8"))
            payload["mode"] = "delete"
            plan.write_text(json.dumps(payload), encoding="utf-8")
            modified = run(
                TIDY,
                "apply",
                "--plan",
                plan,
                "--approval-token",
                approval_token(prepared.stdout),
            )
            self.assertEqual(modified.returncode, 2)
            self.assertIn("plan was modified", modified.stderr)
            self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()
