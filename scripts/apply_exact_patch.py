#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_ROOT = (ROOT / "docs" / "master").resolve()
ARCHIVE_ROOT = (ALLOWED_ROOT / "_archive").resolve()


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def resolve_target(raw_path: str) -> tuple[Path, str]:
    if not raw_path or Path(raw_path).is_absolute():
        fail("path must be a non-empty repository-relative path")

    target = (ROOT / raw_path).resolve()
    try:
        target.relative_to(ALLOWED_ROOT)
    except ValueError:
        fail("path must stay under docs/master/")

    try:
        target.relative_to(ARCHIVE_ROOT)
    except ValueError:
        pass
    else:
        fail("docs/master/_archive/ is immutable through this patch workflow")

    rel = target.relative_to(ROOT).as_posix()
    if rel == "docs/master/README.md":
        return target, rel
    if target.suffix.lower() != ".md":
        fail("only Markdown master documents may be patched")
    return target, rel


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def load_replacements(raw: str) -> list[dict[str, str]]:
    try:
        value: Any = json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"replacements_json is invalid JSON: {exc}")

    if not isinstance(value, list) or not value:
        fail("replacements_json must be a non-empty JSON array")

    replacements: list[dict[str, str]] = []
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            fail(f"replacement {i} must be an object")
        old = item.get("old")
        new = item.get("new")
        if not isinstance(old, str) or not old:
            fail(f"replacement {i}.old must be a non-empty string")
        if not isinstance(new, str):
            fail(f"replacement {i}.new must be a string")
        if old == new:
            fail(f"replacement {i} does not change content")
        replacements.append({"old": old, "new": new})
    return replacements


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply exact, source-preserving replacements to one master Markdown file."
    )
    parser.add_argument("--path", required=True)
    parser.add_argument("--expected-blob-sha", required=True)
    parser.add_argument("--replacements-json", required=True)
    args = parser.parse_args()

    target, rel = resolve_target(args.path)
    if not target.is_file():
        fail(f"target does not exist: {rel}")

    status = git("status", "--porcelain")
    if status:
        fail("working tree must be clean before patching")

    original_bytes = target.read_bytes()
    actual_sha = git_blob_sha(original_bytes)
    expected_sha = args.expected_blob_sha.strip().lower()
    if actual_sha != expected_sha:
        fail(
            f"blob SHA mismatch for {rel}: expected {expected_sha}, actual {actual_sha}"
        )

    try:
        original = original_bytes.decode("utf-8")
    except UnicodeDecodeError:
        fail("target must be valid UTF-8")

    replacements = load_replacements(args.replacements_json)
    updated = original

    for i, replacement in enumerate(replacements):
        old = replacement["old"]
        new = replacement["new"]
        count = updated.count(old)
        if count != 1:
            fail(
                f"replacement {i}.old must match exactly once at application time; found {count}"
            )
        updated = updated.replace(old, new, 1)

    if updated == original:
        fail("patch produced no content change")

    target.write_text(updated, encoding="utf-8", newline="")

    changed = [line for line in git("status", "--porcelain").splitlines() if line]
    if len(changed) != 1 or not changed[0].endswith(rel):
        fail(f"patch must modify only {rel}; status={changed}")

    print(f"PATCH_TARGET={rel}")
    print(f"OLD_BLOB_SHA={actual_sha}")
    print(f"NEW_BLOB_SHA={git_blob_sha(target.read_bytes())}")
    print(f"REPLACEMENT_COUNT={len(replacements)}")


if __name__ == "__main__":
    main()
