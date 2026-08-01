#!/usr/bin/env python3
"""Collect evidence for unmatched macOS app data without declaring it orphaned."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

MIB = 1024 * 1024
APP_SUFFIXES = ("app", "application", "desktop", "helper", "launcher")


def normalize(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "", value.casefold())
    for suffix in APP_SUFFIXES:
        if normalized.endswith(suffix) and len(normalized) > len(suffix) + 2:
            normalized = normalized[: -len(suffix)]
    return normalized


def looks_like_bundle_id(value: str) -> bool:
    return value.count(".") >= 2 and all(part for part in value.split("."))


def allocated_size(path: Path) -> tuple[int | None, str | None]:
    try:
        if path.is_symlink():
            return None, "skipped symbolic link"
        proc = subprocess.run(
            ["/usr/bin/du", "-sk", str(path)],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        line = proc.stdout.splitlines()[0] if proc.stdout.splitlines() else ""
        if line:
            return int(line.split(maxsplit=1)[0]) * 1024, proc.stderr.strip() or None
        return None, proc.stderr.strip() or f"du exited with status {proc.returncode}"
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)


def read_bundle(app: Path) -> dict[str, str] | None:
    plist = app / "Contents" / "Info.plist"
    try:
        with plist.open("rb") as handle:
            info = plistlib.load(handle)
    except (OSError, plistlib.InvalidFileException):
        return None
    bundle_id = info.get("CFBundleIdentifier")
    name = info.get("CFBundleDisplayName") or info.get("CFBundleName") or app.stem
    executable = info.get("CFBundleExecutable")
    if not isinstance(bundle_id, str):
        bundle_id = ""
    if not isinstance(name, str):
        name = app.stem
    if not isinstance(executable, str):
        executable = ""
    return {
        "path": str(app.resolve(strict=False)),
        "bundle_id": bundle_id,
        "name": name,
        "executable": executable,
    }


def nested_login_items(app: Path) -> Iterable[Path]:
    login_items = app / "Contents" / "Library" / "LoginItems"
    if not login_items.is_dir():
        return []
    try:
        return [
            path for path in login_items.iterdir() if path.suffix.casefold() == ".app"
        ]
    except OSError:
        return []


def scan_app_root(root: Path, max_depth: int = 4) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    if not root.is_dir():
        return records
    root = root.resolve(strict=False)
    for current, dirs, _files in os.walk(root, followlinks=False):
        current_path = Path(current)
        depth = len(current_path.parts) - len(root.parts)
        if depth > max_depth:
            dirs[:] = []
            continue
        app_dirs = [name for name in dirs if name.casefold().endswith(".app")]
        for name in app_dirs:
            app = current_path / name
            record = read_bundle(app)
            if record:
                records.append(record)
            for helper in nested_login_items(app):
                helper_record = read_bundle(helper)
                if helper_record:
                    records.append(helper_record)
        dirs[:] = [name for name in dirs if name not in app_dirs]
    return records


def spotlight_apps() -> list[Path]:
    mdfind = Path("/usr/bin/mdfind")
    if sys.platform != "darwin" or not mdfind.exists():
        return []
    try:
        proc = subprocess.run(
            [str(mdfind), "kMDItemContentType == 'com.apple.application-bundle'"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        return [
            Path(line) for line in proc.stdout.splitlines() if line.endswith(".app")
        ]
    except (OSError, subprocess.TimeoutExpired):
        return []


def dedupe_apps(apps: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    result: list[dict[str, str]] = []
    for app in apps:
        key = (app["path"], app["bundle_id"])
        if key not in seen:
            seen.add(key)
            result.append(app)
    return result


def bundle_match(candidate: str, installed_id: str) -> bool:
    if not installed_id:
        return False
    left = candidate.casefold()
    right = installed_id.casefold()
    return left == right or left.startswith(right + ".") or right.startswith(left + ".")


def matching_evidence(name: str, apps: list[dict[str, str]]) -> list[str]:
    evidence: list[str] = []
    normalized = normalize(name)
    for app in apps:
        if looks_like_bundle_id(name) and bundle_match(name, app["bundle_id"]):
            evidence.append(
                f"bundle identifier relationship with {app['bundle_id']} at {app['path']}"
            )
        app_names = {normalize(app["name"]), normalize(Path(app["path"]).stem)}
        if normalized and normalized in app_names:
            evidence.append(f"name match with {app['name']} at {app['path']}")
    executable_name = name.split(".")[-1] if looks_like_bundle_id(name) else name
    if re.fullmatch(r"[A-Za-z0-9_.+-]+", executable_name):
        executable = shutil.which(executable_name)
        if executable:
            evidence.append(f"CLI executable found at {executable}")
    return sorted(set(evidence))


def candidate_roots(home: Path) -> list[tuple[Path, int]]:
    library = home / "Library"
    return [
        (library / "Application Support", 0),
        (library / "Caches", 0),
        (library / "Containers", 0),
        (library / "Group Containers", 0),
        (library / "Saved Application State", 0),
        (library / "HTTPStorages", MIB),
        (library / "Preferences", MIB),
    ]


def children(root: Path) -> Iterable[Path]:
    try:
        return list(root.iterdir())
    except OSError:
        return []


def stable_id(path: Path) -> str:
    return hashlib.sha256(str(path).encode("utf-8", "surrogateescape")).hexdigest()[:12]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--applications-root", type=Path, action="append", default=[])
    parser.add_argument("--min-size-mb", type=int, default=50)
    parser.add_argument("--use-spotlight", action="store_true")
    parser.add_argument("--output", type=Path, help="Write JSON here instead of stdout")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    home = args.home.expanduser().resolve(strict=False)
    roots = [path.expanduser().resolve(strict=False) for path in args.applications_root]
    if not roots:
        roots = [
            Path("/Applications"),
            home / "Applications",
            Path("/System/Applications"),
        ]

    apps: list[dict[str, str]] = []
    for root in roots:
        apps.extend(scan_app_root(root))
    if args.use_spotlight:
        for path in spotlight_apps():
            record = read_bundle(path)
            if record:
                apps.append(record)
    apps = dedupe_apps(apps)

    candidates: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    global_minimum = max(args.min_size_mb, 0) * MIB
    for root, root_minimum in candidate_roots(home):
        threshold = max(global_minimum, root_minimum)
        for path in children(root):
            if path.name.casefold().startswith("com.apple.") or path.is_symlink():
                continue
            size, warning = allocated_size(path)
            if warning:
                errors.append({"path": str(path), "error": warning})
            if size is None or size < threshold:
                continue
            evidence = matching_evidence(
                path.stem if path.is_file() else path.name, apps
            )
            status = "matched" if evidence else "unmatched"
            candidates.append(
                {
                    "id": stable_id(path.resolve(strict=False)),
                    "path": str(path.resolve(strict=False)),
                    "allocated_bytes": size,
                    "status": status,
                    "evidence": evidence,
                    "confidence": "verified-match" if evidence else "unknown",
                    "recommendation": "keep" if evidence else "inspect-and-research",
                }
            )

    candidates.sort(key=lambda item: item["allocated_bytes"], reverse=True)
    payload = {
        "schema_version": 1,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "read_only": True,
        "home": str(home),
        "application_roots": [str(path) for path in roots],
        "installed_apps_indexed": len(apps),
        "candidates": candidates,
        "errors": errors,
        "notes": [
            "Unmatched means no evidence was found; it does not mean orphaned or safe to delete.",
            "Inspect contents, timestamps, launch agents, login items, package managers, and web sources before recommending removal.",
        ],
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
