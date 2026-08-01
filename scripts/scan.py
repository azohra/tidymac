#!/usr/bin/env python3
"""Read-only, structured disk-space inventory for TidyMac."""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import plistlib
import shutil
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

MIB = 1024 * 1024
CACHE_NAMES = {
    "cache",
    "caches",
    "code cache",
    "gpucache",
    "service worker",
    "blob_storage",
    "indexeddb",
}
TOOLS = (
    "brew",
    "npm",
    "yarn",
    "pnpm",
    "bun",
    "pip3",
    "pip",
    "poetry",
    "conda",
    "cargo",
    "go",
    "gem",
    "bundle",
    "pod",
    "composer",
    "mvn",
    "gradle",
    "flutter",
    "dart",
    "swift",
    "mise",
    "asdf",
    "pyenv",
    "rbenv",
    "rustup",
    "goenv",
    "docker",
    "orbctl",
    "podman",
    "colima",
)

DEV_RULES: dict[str, tuple[str, tuple[str, ...]]] = {
    "node_modules": ("javascript-dependencies", ("package.json",)),
    "target": ("rust-build", ("Cargo.toml",)),
    ".build": ("swift-build", ("Package.swift",)),
    "build": (
        "build-output",
        (
            "CMakeLists.txt",
            "Makefile",
            "build.gradle",
            "build.gradle.kts",
            "package.json",
            "pyproject.toml",
        ),
    ),
    "dist": (
        "build-output",
        ("package.json", "pyproject.toml", "setup.py", "setup.cfg"),
    ),
    ".next": (
        "next-build",
        ("package.json", "next.config.js", "next.config.mjs", "next.config.ts"),
    ),
    ".nuxt": ("nuxt-build", ("package.json", "nuxt.config.js", "nuxt.config.ts")),
    ".venv": ("python-environment", ("pyvenv.cfg",)),
    "venv": ("python-environment", ("pyvenv.cfg",)),
    "__pycache__": ("python-cache", ("*.py",)),
    ".tox": ("python-test-environment", ("tox.ini", "pyproject.toml")),
    ".terraform": ("terraform-cache", ("*.tf",)),
    "Pods": ("cocoapods-dependencies", ("Podfile",)),
    ".dart_tool": ("dart-cache", ("pubspec.yaml",)),
    ".parcel-cache": ("parcel-cache", ("package.json",)),
    "vendor": ("vendored-dependencies", ("go.mod", "composer.json", "Gemfile")),
    ".gradle": (
        "gradle-cache",
        ("build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"),
    ),
    ".pytest_cache": (
        "python-cache",
        ("pyproject.toml", "pytest.ini", "setup.cfg", "*.py"),
    ),
    ".mypy_cache": (
        "python-cache",
        ("pyproject.toml", "mypy.ini", "setup.cfg", "*.py"),
    ),
    ".ruff_cache": (
        "python-cache",
        ("pyproject.toml", "ruff.toml", ".ruff.toml", "*.py"),
    ),
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def stable_id(category: str, path: Path) -> str:
    value = f"{category}\0{path}".encode("utf-8", "surrogateescape")
    return hashlib.sha256(value).hexdigest()[:12]


def human_size(value: int) -> str:
    size = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    raise AssertionError("unreachable")


def allocated_size(path: Path) -> tuple[int | None, str | None]:
    """Return filesystem blocks used, without following a top-level symlink."""
    try:
        if path.is_symlink():
            return None, "skipped symbolic link"
        command = ["/usr/bin/du", "-sk", str(path)]
        proc = subprocess.run(
            command, capture_output=True, text=True, timeout=120, check=False
        )
        first_line = proc.stdout.splitlines()[0] if proc.stdout.splitlines() else ""
        if first_line:
            blocks_kib = int(first_line.split(maxsplit=1)[0])
            warning = proc.stderr.strip() or None
            return blocks_kib * 1024, warning
        return None, proc.stderr.strip() or f"du exited with status {proc.returncode}"
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)


def finding(
    path: Path,
    category: str,
    evidence: Iterable[str],
    consequence: str,
    confidence: str = "verified",
    context_only: bool = False,
) -> tuple[dict[str, Any] | None, str | None]:
    resolved = path.resolve(strict=False)
    size, warning = allocated_size(resolved)
    if size is None:
        return None, warning
    item = {
        "id": stable_id(category, resolved),
        "path": str(resolved),
        "allocated_bytes": size,
        "allocated_human": human_size(size),
        "category": category,
        "evidence": list(evidence),
        "confidence": confidence,
        "consequence": consequence,
        "context_only": context_only,
    }
    return item, warning


class Inventory:
    def __init__(self, minimum_bytes: int) -> None:
        self.minimum_bytes = minimum_bytes
        self.findings: list[dict[str, Any]] = []
        self.errors: list[dict[str, str]] = []
        self._keys: set[tuple[str, str]] = set()

    def add(
        self,
        path: Path,
        category: str,
        evidence: Iterable[str],
        consequence: str,
        *,
        confidence: str = "verified",
        context_only: bool = False,
        minimum_bytes: int | None = None,
    ) -> None:
        if not path.exists() or path.is_symlink():
            return
        resolved = path.resolve(strict=False)
        key = (category, str(resolved))
        if key in self._keys:
            return
        item, warning = finding(
            resolved,
            category,
            evidence,
            consequence,
            confidence,
            context_only,
        )
        if warning:
            self.errors.append({"path": str(resolved), "error": warning})
        threshold = self.minimum_bytes if minimum_bytes is None else minimum_bytes
        if item and item["allocated_bytes"] >= threshold:
            self._keys.add(key)
            self.findings.append(item)


def children(path: Path) -> list[Path]:
    try:
        return sorted(path.iterdir(), key=lambda item: item.name.casefold())
    except OSError:
        return []


def scan_nested_caches(
    inventory: Inventory, app_support: Path, max_depth: int = 3
) -> None:
    if not app_support.is_dir():
        return
    for app_dir in children(app_support):
        if not app_dir.is_dir() or app_dir.is_symlink():
            continue
        base_depth = len(app_dir.parts)
        for current, dirs, _files in os.walk(app_dir, followlinks=False):
            current_path = Path(current)
            depth = len(current_path.parts) - base_depth
            if depth >= max_depth:
                dirs[:] = []
                continue
            kept: list[str] = []
            for name in dirs:
                candidate = current_path / name
                if name.casefold() in CACHE_NAMES:
                    inventory.add(
                        candidate,
                        "app-internal-cache",
                        [f"cache-shaped directory inside {app_dir.name}"],
                        "silent-regeneration",
                    )
                else:
                    kept.append(name)
            dirs[:] = kept


def scan_library(inventory: Inventory, home: Path) -> None:
    library = home / "Library"
    roots = (
        (library / "Caches", "app-cache", "redownload-or-regeneration", False),
        (library / "Application Support", "application-support", "unknown", True),
        (library / "Logs", "logs", "diagnostic-history-loss", False),
        (
            library / "Saved Application State",
            "saved-state",
            "window-state-reset",
            False,
        ),
        (library / "HTTPStorages", "http-storage", "session-or-cache-reset", False),
        (home / ".cache", "xdg-cache", "redownload-or-regeneration", False),
    )
    for root, category, consequence, context_only in roots:
        for path in children(root):
            inventory.add(
                path,
                category,
                [f"direct child of {root}"],
                consequence,
                context_only=context_only,
            )

    scan_nested_caches(inventory, library / "Application Support")

    for data in glob.glob(str(library / "Containers" / "*" / "Data")):
        inventory.add(
            Path(data),
            "sandbox-container-data",
            ["Data directory inside a sandboxed app container"],
            "application-state-loss-possible",
            context_only=True,
        )

    xcode_paths = (
        (
            library / "Developer/Xcode/DerivedData",
            "xcode-derived-data",
            "rebuild-required",
            False,
        ),
        (
            library / "Developer/Xcode/Archives",
            "xcode-archives",
            "non-regenerable",
            True,
        ),
        (
            library / "Developer/Xcode/iOS DeviceSupport",
            "xcode-device-support",
            "redownload-or-reconnect",
            False,
        ),
        (
            library / "Developer/Xcode/watchOS DeviceSupport",
            "xcode-device-support",
            "redownload-or-reconnect",
            False,
        ),
        (
            library / "Developer/Xcode/tvOS DeviceSupport",
            "xcode-device-support",
            "redownload-or-reconnect",
            False,
        ),
        (
            library / "Developer/Xcode/Products",
            "xcode-products",
            "rebuild-required",
            False,
        ),
        (
            library / "Developer/Xcode/iOS Device Logs",
            "xcode-device-logs",
            "diagnostic-history-loss",
            False,
        ),
        (
            library / "Developer/CoreSimulator/Devices",
            "simulator-devices",
            "simulator-state-loss-possible",
            True,
        ),
        (
            library / "Developer/CoreSimulator/Caches",
            "simulator-cache",
            "regeneration-required",
            False,
        ),
        (
            library / "Application Support/MobileSync/Backup",
            "ios-device-backups",
            "non-regenerable",
            True,
        ),
        (home / ".Trash", "trash", "non-regenerable-unless-reviewed", True),
        (
            home / ".orbstack",
            "container-runtime-data",
            "runtime-state-loss-possible",
            True,
        ),
        (
            home / ".colima",
            "container-runtime-data",
            "runtime-state-loss-possible",
            True,
        ),
        (
            library / "Group Containers" / "HUAQ24HBR6.dev.orbstack" / "data",
            "container-runtime-data",
            "runtime-state-loss-possible",
            True,
        ),
    )
    for path, category, consequence, context_only in xcode_paths:
        inventory.add(
            path,
            category,
            ["known macOS development or backup location"],
            consequence,
            context_only=context_only,
        )


def has_marker(parent: Path, candidate: Path, markers: tuple[str, ...]) -> list[str]:
    matched: list[str] = []
    for marker in markers:
        if marker == "pyvenv.cfg" and (candidate / marker).is_file():
            matched.append(str(candidate / marker))
        elif "*" in marker:
            matched.extend(str(path) for path in parent.glob(marker) if path.is_file())
        elif (parent / marker).exists():
            matched.append(str(parent / marker))
    return matched


def paths_overlap(left: Path, right: Path) -> bool:
    return is_relative_to(left, right) or is_relative_to(right, left)


def scan_dev_root(inventory: Inventory, root: Path, cwd: Path, max_depth: int) -> None:
    root = root.resolve(strict=False)
    if not root.is_dir():
        return
    for current, dirs, _files in os.walk(root, followlinks=False):
        current_path = Path(current).resolve(strict=False)
        depth = len(current_path.parts) - len(root.parts)
        if current_path == cwd or is_relative_to(current_path, cwd):
            dirs[:] = []
            continue
        if depth >= max_depth:
            dirs[:] = []
            continue
        kept: list[str] = []
        for name in dirs:
            candidate = (current_path / name).resolve(strict=False)
            if paths_overlap(candidate, cwd):
                if not is_relative_to(cwd, candidate):
                    continue
                kept.append(name)
                continue
            rule = DEV_RULES.get(name)
            if not rule:
                kept.append(name)
                continue
            category, markers = rule
            evidence = has_marker(current_path, candidate, markers)
            if evidence:
                consequence = "rebuild-required"
                if category.endswith("cache"):
                    consequence = "regeneration-required"
                inventory.add(
                    candidate,
                    category,
                    [f"matched project marker {path}" for path in evidence],
                    consequence,
                )
            else:
                kept.append(name)
        dirs[:] = kept


def discover_dev_roots(home: Path) -> list[Path]:
    roots = [home / name for name in ("Development", "Projects", "Code", "src")]
    found = [path.resolve(strict=False) for path in roots if path.is_dir()]
    if found:
        return found
    for path in children(home):
        if path.is_dir() and any(child.name == ".git" for child in children(path)):
            found.append(path.resolve(strict=False))
    return found


def scan_system(inventory: Inventory) -> None:
    roots = (
        (Path("/Library/Caches"), "system-cache", "regeneration-required"),
        (Path("/Library/Logs"), "system-logs", "diagnostic-history-loss"),
    )
    for root, category, consequence in roots:
        for path in children(root):
            inventory.add(
                path,
                category,
                [f"direct child of {root}"],
                consequence,
                context_only=True,
            )
    for installer in Path("/Applications").glob("Install macOS*.app"):
        inventory.add(
            installer,
            "macos-installer",
            ["macOS installer application"],
            "redownload-required",
            context_only=True,
        )
    for media_path in (
        Path("/Library/Application Support/GarageBand"),
        Path("/Library/Application Support/Logic"),
        Path("/Library/Audio/Apple Loops"),
    ):
        inventory.add(
            media_path,
            "apple-media-library",
            ["optional Apple audio content"],
            "redownload-required",
            context_only=True,
        )


def disk_state() -> dict[str, Any]:
    usage = shutil.disk_usage("/")
    result: dict[str, Any] = {
        "filesystem_total_bytes": usage.total,
        "filesystem_used_bytes": usage.used,
        "filesystem_free_bytes": usage.free,
    }
    if sys.platform != "darwin" or not Path("/usr/sbin/diskutil").exists():
        return result
    try:
        proc = subprocess.run(
            ["/usr/sbin/diskutil", "info", "-plist", "/"],
            capture_output=True,
            timeout=20,
            check=False,
        )
        if proc.returncode == 0:
            info = plistlib.loads(proc.stdout)
            apfs_mapping = (
                ("APFSContainerSize", "container_total_bytes"),
                ("APFSContainerFree", "container_free_bytes"),
            )
            legacy_container_mapping = (
                ("ContainerTotalSpace", "container_total_bytes"),
                ("ContainerFreeSpace", "container_free_bytes"),
            )
            volume_mapping = (
                ("TotalSize", "volume_total_bytes"),
                ("FreeSpace", "volume_free_bytes"),
            )
            if isinstance(info.get("APFSContainerSize"), int):
                mapping = apfs_mapping
            elif isinstance(info.get("ContainerTotalSpace"), int):
                mapping = legacy_container_mapping
            else:
                mapping = volume_mapping
            for source, target in mapping:
                value = info.get(source)
                if isinstance(value, int):
                    result[target] = value
    except (OSError, plistlib.InvalidFileException, subprocess.TimeoutExpired):
        pass
    return result


def time_machine_snapshots() -> list[str]:
    tmutil = Path("/usr/bin/tmutil")
    if sys.platform != "darwin" or not tmutil.exists():
        return []
    try:
        proc = subprocess.run(
            [str(tmutil), "listlocalsnapshots", "/"],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        return [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    except (OSError, subprocess.TimeoutExpired):
        return []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scope", choices=("quick", "library", "dev", "all"), default="quick"
    )
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--cwd", type=Path, default=Path.cwd())
    parser.add_argument("--dev-root", type=Path, action="append", default=[])
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--min-size-mb", type=int, default=100)
    parser.add_argument("--include-system", action="store_true")
    parser.add_argument("--output", type=Path, help="Write JSON here instead of stdout")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    home = args.home.expanduser().resolve(strict=False)
    cwd = args.cwd.expanduser().resolve(strict=False)
    inventory = Inventory(max(args.min_size_mb, 0) * MIB)
    dev_roots = [path.expanduser().resolve(strict=False) for path in args.dev_root]
    if not dev_roots:
        dev_roots = discover_dev_roots(home)

    if args.scope in {"quick", "library", "all"}:
        scan_library(inventory, home)
    if args.scope in {"dev", "all"}:
        for root in dev_roots:
            scan_dev_root(inventory, root, cwd, max(args.max_depth, 1))
    if args.include_system or args.scope == "all":
        scan_system(inventory)

    inventory.findings.sort(key=lambda item: item["allocated_bytes"], reverse=True)
    payload = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "read_only": True,
        "parameters": {
            "scope": args.scope,
            "home": str(home),
            "cwd_excluded": str(cwd),
            "dev_roots": [str(path) for path in dev_roots],
            "minimum_bytes": inventory.minimum_bytes,
            "maximum_dev_depth": args.max_depth,
        },
        "disk": disk_state(),
        "tools": {tool: path for tool in TOOLS if (path := shutil.which(tool))},
        "time_machine_snapshots": time_machine_snapshots(),
        "findings": inventory.findings,
        "errors": inventory.errors,
        "notes": [
            "Allocated sizes are estimates; APFS clones, snapshots, sparse files, and purgeable space can differ.",
            "Do not sum findings whose paths are ancestors or descendants of one another.",
            "Time Machine snapshots are context only and are not included as reclaimable findings.",
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
