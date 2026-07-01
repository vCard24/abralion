#!/usr/bin/env python3
"""Cursor afterFileEdit: products-data.js kaydedilince min.js üret."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG_SUFFIXES = (
    "assets/js/products-data.js",
    "products-data.js",
)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    file_path = payload.get("file_path") or payload.get("path") or ""
    normalized = str(file_path).replace("\\", "/")
    if not any(normalized.endswith(suffix) for suffix in CATALOG_SUFFIXES):
        return 0

    print(f"sync-catalog hook: {normalized}", file=sys.stderr)
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "sync_catalog.py")],
        cwd=ROOT,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
