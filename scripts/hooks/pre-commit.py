#!/usr/bin/env python3
"""Git pre-commit: products-data.js değiştiyse min.js üret ve stage'e ekle."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CATALOG_PATHS = {
    "assets/js/products-data.js",
    "products-data.js",
}


def repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("git repo kökü bulunamadı")
    return Path(result.stdout.strip())


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def staged_catalog_changed(root: Path) -> bool:
    result = git(root, "diff", "--cached", "--name-only")
    if result.returncode != 0:
        return False
    staged = set(result.stdout.splitlines())
    return bool(staged.intersection(CATALOG_PATHS))


def min_is_stale(root: Path) -> bool:
    source = root / "assets" / "js" / "products-data.js"
    min_output = root / "assets" / "js" / "products-data.min.js"
    if not source.is_file() or not min_output.is_file():
        return True
    return source.stat().st_mtime > min_output.stat().st_mtime


def main() -> int:
    root = repo_root()

    if not staged_catalog_changed(root) and not min_is_stale(root):
        return 0

    print("pre-commit: katalog kaynağı güncellendi — sync:catalog çalıştırılıyor…")
    sync = subprocess.run(
        [sys.executable, str(root / "scripts" / "sync_catalog.py")],
        cwd=root,
    )
    if sync.returncode != 0:
        print("pre-commit: sync_catalog başarısız; commit iptal.", file=sys.stderr)
        return sync.returncode

    add = git(
        root,
        "add",
        "assets/js/products-data.js",
        "products-data.js",
        "assets/js/products-data.min.js",
    )
    if add.returncode != 0:
        print(add.stderr or add.stdout, file=sys.stderr)
        return add.returncode

    print("pre-commit: products-data.min.js güncellendi ve commit'e eklendi.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
