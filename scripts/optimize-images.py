#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recursively optimize images under assets/images/."""

from __future__ import annotations

import io
import sys
from pathlib import Path

try:
    import pillow_avif  # noqa: F401
except ImportError:
    pass

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = ROOT / "assets" / "images"
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}


def human_bytes(n: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    size = float(n)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} {unit}"
        size /= 1024
    return f"{n} B"


def save_optimized(img: Image.Image, path: Path) -> bytes | None:
    buf = io.BytesIO()
    ext = path.suffix.lower()

    if ext in {".jpg", ".jpeg"}:
        rgb = img.convert("RGB") if img.mode not in ("RGB", "L") else img
        rgb.save(buf, format="JPEG", quality=82, optimize=True, progressive=True)
    elif ext == ".png":
        # PNG: Pillow has no JPEG quality/progressive; optimize + max zlib compression.
        # Palette images keep mode; others stay lossless PNG.
        if img.mode == "P":
            img.save(buf, format="PNG", optimize=True, compress_level=9)
        elif img.mode in ("RGBA", "LA"):
            img.save(buf, format="PNG", optimize=True, compress_level=9)
        else:
            img.convert("RGB").save(buf, format="PNG", optimize=True, compress_level=9)
    elif ext == ".webp":
        img.save(buf, format="WEBP", quality=80, method=6)
    elif ext == ".avif":
        img.save(buf, format="AVIF", quality=70)
    else:
        return None

    return buf.getvalue()


def optimize_file(path: Path) -> tuple[str, int, int, bool]:
    original = path.read_bytes()
    original_size = len(original)

    try:
        with Image.open(io.BytesIO(original)) as img:
            img.load()
            # Preserve animation frames if present (rare for product assets)
            optimized = save_optimized(img, path)
    except Exception as exc:  # noqa: BLE001
        print(f"  SKIP (error): {path.relative_to(ROOT)} — {exc}")
        return ("error", original_size, original_size, False)

    if optimized is None:
        return ("skip", original_size, original_size, False)

    new_size = len(optimized)
    if new_size >= original_size:
        print(
            f"  KEEP  {path.relative_to(ROOT)}  "
            f"{human_bytes(original_size)} -> {human_bytes(new_size)} (no gain)"
        )
        return ("kept", original_size, original_size, False)

    path.write_bytes(optimized)
    print(
        f"  SAVE  {path.relative_to(ROOT)}  "
        f"{human_bytes(original_size)} -> {human_bytes(new_size)} "
        f"(-{human_bytes(original_size - new_size)})"
    )
    return ("saved", original_size, new_size, True)


def main() -> int:
    if not IMAGES_DIR.is_dir():
        print(f"Images directory not found: {IMAGES_DIR}", file=sys.stderr)
        return 1

    files = sorted(
        p
        for p in IMAGES_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() in EXTENSIONS
    )
    print(f"Found {len(files)} image(s) under {IMAGES_DIR.relative_to(ROOT)}")

    saved = kept = errors = 0
    before_total = after_total = 0

    for path in files:
        status, before, after, changed = optimize_file(path)
        before_total += before
        after_total += after if changed else before
        if status == "saved":
            saved += 1
        elif status == "kept":
            kept += 1
        elif status == "error":
            errors += 1

    print()
    print(
        f"Done. saved={saved} kept={kept} errors={errors} | "
        f"total {human_bytes(before_total)} -> {human_bytes(after_total)} "
        f"(-{human_bytes(before_total - after_total)})"
    )
    return 0 if errors == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
