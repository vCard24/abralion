#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Optimize hero AVIF assets for mobile LCP (no layout changes)."""
from __future__ import annotations

import io
import sys
from pathlib import Path

try:
    import pillow_avif  # noqa: F401
except ImportError:
    print("pillow-avif-plugin required: pip install pillow-avif-plugin", file=sys.stderr)
    sys.exit(1)

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "assets" / "images" / "home"
AVIF_QUALITY = 40
WEBP_QUALITY = 75
MASTER = HOME / "hero-bg-1920.jpg"


def kb(n: int) -> str:
    return f"{n / 1024:.1f} KB"


def resize_width(img: Image.Image, width: int) -> Image.Image:
    if img.width == width:
        return img
    h = max(1, round(img.height * width / img.width))
    return img.resize((width, h), Image.Resampling.LANCZOS)


def encode_avif(img: Image.Image, quality: int) -> bytes:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="AVIF", quality=quality)
    return buf.getvalue()


def write_if_smaller(path: Path, data: bytes, label: str, dims: tuple[int, int]) -> None:
    before = path.stat().st_size if path.is_file() else 0
    after = len(data)
    if before and after >= before:
        print(f"{label}: KEEP {dims[0]}x{dims[1]} {kb(before)} (new {kb(after)} not smaller)")
        return
    path.write_bytes(data)
    print(
        f"{label}: {dims[0]}x{dims[1]} | "
        f"{kb(before) if before else 'n/a'} -> {kb(after)} (q={AVIF_QUALITY})"
    )


def optimize_from_master(name: str, width: int) -> None:
    if not MASTER.is_file():
        raise FileNotFoundError(MASTER)
    with Image.open(MASTER) as im:
        out = resize_width(im.convert("RGB"), width)
        data = encode_avif(out, AVIF_QUALITY)
    write_if_smaller(HOME / name, data, name, out.size)


def optimize_card() -> None:
    name = "hero-card-480.avif"
    src = HOME / "hero-card-480.jpg"
    if not src.is_file():
        src = HOME / "hero-card-480.webp"
    with Image.open(src) as im:
        out = im.convert("RGB")
        if out.width != 480:
            out = resize_width(out, 480)
        data = encode_avif(out, AVIF_QUALITY)
    write_if_smaller(HOME / name, data, name, out.size)


def optimize_kesici() -> None:
    path = HOME / "kesici-taslar-400.webp"
    if not path.is_file():
        print("kesici-taslar-400.webp: missing")
        return
    before = path.stat().st_size
    with Image.open(path) as im:
        im = im.convert("RGB")
        buf = io.BytesIO()
        im.save(buf, format="WEBP", quality=WEBP_QUALITY, method=6)
        data = buf.getvalue()
    if len(data) >= before:
        print(f"kesici-taslar-400.webp: KEEP {kb(before)}")
        return
    path.write_bytes(data)
    print(f"kesici-taslar-400.webp: {im.size[0]}x{im.size[1]} | {kb(before)} -> {kb(len(data))} (q={WEBP_QUALITY})")


def main() -> int:
    print(f"Master: {MASTER.name} | AVIF q={AVIF_QUALITY}\n")
    for name, width in (
        ("hero-bg-1440.avif", 1440),
        ("hero-bg-1024.avif", 1024),
    ):
        optimize_from_master(name, width)
    optimize_card()
    # Dedicated mobile full-bleed hero (480w) — smaller LCP candidate
    optimize_from_master("hero-bg-480.avif", 480)
    print()
    optimize_kesici()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
