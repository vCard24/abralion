#!/usr/bin/env python3
"""Minify assets/js/products-data.js to products-data.min.js via terser."""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "js" / "products-data.js"
OUTPUT = ROOT / "assets" / "js" / "products-data.min.js"
ROOT_COPY = ROOT / "products-data.js"


def main() -> int:
    if not SOURCE.is_file():
        print(f"Missing source: {SOURCE}", file=sys.stderr)
        return 1

    terser = shutil.which("npx")
    if not terser:
        print("npx not found", file=sys.stderr)
        return 1

    cmd = [
        terser,
        "--yes",
        "terser",
        str(SOURCE),
        "-c",
        "-m",
        "-o",
        str(OUTPUT),
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)

    before = SOURCE.stat().st_size
    after = OUTPUT.stat().st_size
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({before} -> {after} bytes, saved {before - after})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
