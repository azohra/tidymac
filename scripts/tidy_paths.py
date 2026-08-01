#!/usr/bin/env python3
"""Prepare and apply guarded filesystem cleanup plans for TidyMac."""

from __future__ import annotations

import argparse
import datetime as dt
import errno
import hashlib
import hmac
import json
import secrets
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any

PLAN_VERSION = 1
RECOGNIZED_NAMES = {
    "cache",
    "caches",
    "code cache",
    "gpucache",
    "service worker",
    "blob_storage",
    "indexeddb",
    "deriveddata",
    "node_modules",
    "target",
    ".build",
    "build",
    "dist",
    ".next",
    ".nuxt",
    ".venv",
    "venv",
    "__pycache__",
    ".tox",
    ".terraform",
    "pods",
    ".dart_tool",
    ".parcel-cache",
    "vendor",
    ".gradle",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}


class SafetyError(RuntimeError):
    pass


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def overlap(left: Path, right: Path) -> bool:
    return is_relative_to(left, right) or is_relative_to(right, left)


def allocated_size(path: Path) -> int:
    try:
        proc = subprocess.run(
            ["/usr/bin/du", "-sk", str(path)],
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SafetyError(f"could not measure {path}: {exc}") from exc
    line = proc.stdout.splitlines()[0] if proc.stdout.splitlines() else ""
    if not line:
        raise SafetyError(
            f"could not measure {path}: {proc.stderr.strip() or proc.returncode}"
        )
    try:
        return int(line.split(maxsplit=1)[0]) * 1024
    except ValueError as exc:
        raise SafetyError(f"unexpected du output for {path}") from exc


def metadata(path: Path) -> dict[str, Any]:
    info = path.lstat()
    return {
        "device": info.st_dev,
        "inode": info.st_ino,
        "mode": info.st_mode,
        "mtime_ns": info.st_mtime_ns,
        "allocated_bytes": allocated_size(path),
    }


def canonical_existing(path: Path) -> Path:
    expanded = path.expanduser()
    if not expanded.is_absolute():
        expanded = Path.cwd() / expanded
    if not expanded.exists() and not expanded.is_symlink():
        raise SafetyError(f"target does not exist: {expanded}")
    if expanded.is_symlink():
        raise SafetyError(f"refusing symbolic-link target: {expanded}")
    return expanded.resolve(strict=True)


def validate_target(
    target: Path,
    allowed_roots: list[Path],
    home: Path,
    cwd: Path,
    allow_unrecognized: bool,
) -> None:
    forbidden_exact = {
        Path("/"),
        home,
        home / "Library",
        home / "Desktop",
        home / "Documents",
        home / "Downloads",
        home / "Pictures",
        home / "Movies",
        home / "Music",
        Path("/Applications"),
        Path("/Library"),
        Path("/System"),
        Path("/Users"),
    }
    if target in forbidden_exact:
        raise SafetyError(f"refusing broad or protected target: {target}")
    if target.is_mount():
        raise SafetyError(f"refusing mount point: {target}")
    protected_trees = (
        home / "Desktop",
        home / "Documents",
        home / "Downloads",
        home / "Pictures",
        home / "Movies",
        home / "Music",
        home / ".ssh",
        home / ".gnupg",
        home / ".aws",
        home / ".kube",
        home / "Library" / "Keychains",
        home / "Library" / "Mail",
        home / "Library" / "Messages",
    )
    if is_relative_to(target, Path("/System")) or is_relative_to(
        target, Path("/private/var/vm")
    ):
        raise SafetyError(f"refusing system target: {target}")
    if any(is_relative_to(target, protected) for protected in protected_trees):
        raise SafetyError(f"refusing user content or credential target: {target}")
    if not any(
        is_relative_to(target, root) and target != root for root in allowed_roots
    ):
        raise SafetyError(f"target is outside the allowed roots: {target}")
    if overlap(target, cwd):
        raise SafetyError(f"target overlaps the current project: {target}")
    if target.name.casefold() not in RECOGNIZED_NAMES and not allow_unrecognized:
        raise SafetyError(
            f"unrecognized target name {target.name!r}; prepare it separately with --allow-unrecognized"
        )


def prepare(args: argparse.Namespace) -> int:
    home = args.home.expanduser().resolve(strict=False)
    cwd = args.cwd.expanduser().resolve(strict=False)
    allowed_roots = [
        root.expanduser().resolve(strict=False) for root in args.allowed_root
    ]
    if not allowed_roots:
        allowed_roots = [home]
    forbidden_allowed_roots = {
        Path("/"),
        Path("/System"),
        Path("/Library"),
        Path("/Applications"),
        Path("/Users"),
    }
    for root in allowed_roots:
        if root in forbidden_allowed_roots:
            raise SafetyError(f"allowed root is too broad: {root}")
    if args.mode == "delete" and not args.acknowledge_permanent:
        raise SafetyError("permanent deletion requires --acknowledge-permanent")

    items: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for raw_target in args.targets:
        target = canonical_existing(raw_target)
        if target in seen:
            continue
        validate_target(target, allowed_roots, home, cwd, args.allow_unrecognized)
        item = {"path": str(target), **metadata(target)}
        item["action_id"] = hashlib.sha256(
            str(target).encode("utf-8", "surrogateescape")
        ).hexdigest()[:12]
        item["recognized_name"] = target.name.casefold() in RECOGNIZED_NAMES
        items.append(item)
        seen.add(target)

    unique_targets = list(seen)
    for index, left in enumerate(unique_targets):
        for right in unique_targets[index + 1 :]:
            if overlap(left, right):
                raise SafetyError(
                    f"plan contains overlapping targets: {left} and {right}"
                )
    if not items:
        raise SafetyError("plan contains no targets")
    plan_path = args.plan.expanduser()
    if not plan_path.is_absolute():
        plan_path = Path.cwd() / plan_path
    plan_path = plan_path.resolve(strict=False)
    if any(is_relative_to(plan_path, target) for target in seen):
        raise SafetyError("plan file cannot be stored inside a cleanup target")

    token = secrets.token_urlsafe(12)
    plan = {
        "schema_version": PLAN_VERSION,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "mode": args.mode,
        "home": str(home),
        "cwd_excluded": str(cwd),
        "allowed_roots": [str(root) for root in allowed_roots],
        "requires_individual_confirmation": any(
            not item["recognized_name"] for item in items
        ),
        "items": items,
    }
    plan["approval_signature"] = sign_plan(plan, token)
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(
        json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    total = sum(item["allocated_bytes"] for item in items)
    print(
        f"Prepared {len(items)} target(s), {total} allocated bytes, mode={args.mode}."
    )
    print(f"Approval token: {token}")
    print(f"Plan: {plan_path}")
    return 0


def load_plan(path: Path) -> dict[str, Any]:
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SafetyError(f"could not load plan: {exc}") from exc
    if plan.get("schema_version") != PLAN_VERSION:
        raise SafetyError("unsupported plan version")
    if plan.get("mode") not in {"trash", "delete"}:
        raise SafetyError("invalid plan mode")
    if not isinstance(plan.get("items"), list) or not plan["items"]:
        raise SafetyError("plan has no items")
    return plan


def sign_plan(plan: dict[str, Any], token: str) -> str:
    body = {key: value for key, value in plan.items() if key != "approval_signature"}
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hmac.new(token.encode("utf-8"), encoded, hashlib.sha256).hexdigest()


def revalidate(plan: dict[str, Any]) -> list[Path]:
    home = Path(plan["home"]).resolve(strict=False)
    cwd = Path(plan["cwd_excluded"]).resolve(strict=False)
    allowed_roots = [Path(root).resolve(strict=False) for root in plan["allowed_roots"]]
    targets: list[Path] = []
    for item in plan["items"]:
        target = canonical_existing(Path(item["path"]))
        validate_target(target, allowed_roots, home, cwd, allow_unrecognized=True)
        current = metadata(target)
        for field in ("device", "inode", "mode", "mtime_ns", "allocated_bytes"):
            if current[field] != item.get(field):
                raise SafetyError(f"target changed since planning ({field}): {target}")
        targets.append(target)
    return targets


def trash_destination(home: Path, target: Path) -> Path:
    trash_root = home / ".Trash"
    if not trash_root.is_dir():
        raise SafetyError(f"trash directory is unavailable: {trash_root}")
    destination = trash_root / target.name
    counter = 1
    while destination.exists() or destination.is_symlink():
        destination = trash_root / f"{target.name} {counter}"
        counter += 1
    return destination


def move_to_trash(home: Path, target: Path) -> Path:
    destination = trash_destination(home, target)
    try:
        target.rename(destination)
    except OSError as exc:
        if exc.errno == errno.EXDEV:
            raise SafetyError(
                f"refusing cross-volume Trash move for {target}; no data was copied or deleted"
            ) from exc
        raise
    return destination


def delete_permanently(target: Path) -> None:
    mode = target.lstat().st_mode
    if stat.S_ISDIR(mode):
        shutil.rmtree(target)
    else:
        target.unlink()


def write_receipt(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def apply(args: argparse.Namespace) -> int:
    plan_path = args.plan.resolve(strict=True)
    plan = load_plan(plan_path)
    signature = plan.get("approval_signature")
    if not isinstance(signature, str) or not hmac.compare_digest(
        signature, sign_plan(plan, args.approval_token)
    ):
        raise SafetyError(
            "approval token does not match the prepared plan, or the plan was modified"
        )
    targets = revalidate(plan)
    home = Path(plan["home"]).resolve(strict=False)
    completed: list[dict[str, str]] = []
    failure: str | None = None
    receipt = plan_path.with_suffix(plan_path.suffix + ".receipt.json")
    receipt_payload: dict[str, Any] = {
        "schema_version": 1,
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "mode": plan["mode"],
        "completed": completed,
        "failure": failure,
    }
    write_receipt(receipt, receipt_payload)
    for target in targets:
        try:
            if plan["mode"] == "trash":
                destination = move_to_trash(home, target)
                completed.append(
                    {"path": str(target), "result": f"moved to {destination}"}
                )
            else:
                delete_permanently(target)
                completed.append({"path": str(target), "result": "deleted permanently"})
            receipt_payload["completed"] = completed
            write_receipt(receipt, receipt_payload)
        except (OSError, SafetyError) as exc:
            failure = f"{target}: {exc}"
            break
    receipt_payload["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    receipt_payload["failure"] = failure
    write_receipt(receipt, receipt_payload)
    if failure:
        raise SafetyError(
            f"cleanup stopped after {len(completed)} target(s): {failure}; receipt: {receipt}"
        )
    print(f"Applied {len(completed)} target(s); receipt: {receipt}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser(
        "prepare", help="validate targets and write an immutable cleanup plan"
    )
    prepare_parser.add_argument("targets", type=Path, nargs="+")
    prepare_parser.add_argument("--plan", type=Path, required=True)
    prepare_parser.add_argument("--home", type=Path, default=Path.home())
    prepare_parser.add_argument("--cwd", type=Path, default=Path.cwd())
    prepare_parser.add_argument(
        "--allowed-root", type=Path, action="append", default=[]
    )
    prepare_parser.add_argument("--mode", choices=("trash", "delete"), default="trash")
    prepare_parser.add_argument("--allow-unrecognized", action="store_true")
    prepare_parser.add_argument("--acknowledge-permanent", action="store_true")
    prepare_parser.set_defaults(handler=prepare)

    apply_parser = subparsers.add_parser(
        "apply", help="revalidate and apply a prepared plan"
    )
    apply_parser.add_argument("--plan", type=Path, required=True)
    apply_parser.add_argument("--approval-token", required=True)
    apply_parser.set_defaults(handler=apply)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.handler(args)
    except (OSError, SafetyError) as exc:
        print(f"tidy_paths: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
