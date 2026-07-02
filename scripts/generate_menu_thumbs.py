#!/usr/bin/env python3
"""Generate 64px menu thumbnails (128px @2x) from product kart.jpg files."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PRODUCTS_IMG = ROOT / "assets" / "images" / "products"
SOURCE = ROOT / "assets" / "js" / "products-data.js"
HOME_IMG = ROOT / "assets" / "images" / "home"
CATALOG_RE = re.compile(
    r"window\.ABRALION_CATALOG\s*=\s*(\{.*\})\s*;?\s*$",
    re.S,
)
MENU_THUMB_PX = 128  # 2x for 32–64px display boxes
HOME_CARD_PX = 400


def catalog_slugs() -> list[str]:
    text = SOURCE.read_text(encoding="utf-8")
    match = CATALOG_RE.search(text)
    if not match:
        raise ValueError("ABRALION_CATALOG not found")
    catalog = json.loads(match.group(1))
    return [p.get("slug") or p.get("id") for p in catalog.get("products", []) if p.get("slug") or p.get("id")]


def save_webp_thumb(src: Path, dest: Path, size: int) -> bool:
    if dest.is_file() and dest.stat().st_mtime >= src.stat().st_mtime:
        return False
    with Image.open(src) as im:
        im = im.convert("RGB")
        im.thumbnail((size, size), Image.Resampling.LANCZOS)
        dest.parent.mkdir(parents=True, exist_ok=True)
        im.save(dest, "WEBP", quality=82, method=6)
    return True


def generate_product_menu_thumbs() -> tuple[int, int, int]:
    created = up_to_date = missing = 0
    for slug in catalog_slugs():
        kart = PRODUCTS_IMG / slug / f"{slug}-kart.jpg"
        out = PRODUCTS_IMG / slug / f"{slug}-menu-thumb.webp"
        if not kart.is_file():
            missing += 1
            continue
        if save_webp_thumb(kart, out, MENU_THUMB_PX):
            created += 1
        else:
            up_to_date += 1
    return created, up_to_date, missing


def generate_home_card_thumb() -> bool:
    src = HOME_IMG / "kesici-taslar.jpg"
    dest = HOME_IMG / "kesici-taslar-400.webp"
    if not src.is_file():
        return False
    return save_webp_thumb(src, dest, HOME_CARD_PX)


def main() -> int:
    created, skipped, missing = generate_product_menu_thumbs()
    print(
        f"Product menu thumbs: {created} created, {skipped} up-to-date, {missing} missing kart source"
    )
    if generate_home_card_thumb():
        print(f"Home card: wrote {HOME_IMG.name}/kesici-taslar-400.webp")
    else:
        print("Home card: kesici-taslar-400.webp up-to-date or source missing")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
