#!/usr/bin/env python3
"""Generate neutral product-card placeholder (JPG + WebP, ~600px wide)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "assets" / "images" / "products"
JPG = OUT_DIR / "placeholder-kart.jpg"
WEBP = OUT_DIR / "placeholder-kart.webp"

W, H = 600, 400
BG = (22, 22, 24)  # #161618
DISK = (58, 58, 62)
RING = (42, 42, 46)
ACCENT = (226, 35, 26, 90)  # faint Abralion red


def draw_placeholder() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img, "RGBA")

    cx, cy = W // 2, H // 2
    outer_r = 118
    inner_r = 38
    hole_r = 14

    draw.ellipse(
        (cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r),
        fill=DISK,
        outline=RING,
        width=3,
    )
    draw.ellipse(
        (cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r),
        outline=ACCENT,
        width=2,
    )
    draw.ellipse(
        (cx - hole_r, cy - hole_r, cx + hole_r, cy + hole_r),
        fill=BG,
        outline=RING,
        width=2,
    )

    # Subtle cross — disk silhouette hint
    draw.line((cx - outer_r + 20, cy, cx + outer_r - 20, cy), fill=RING, width=2)
    draw.line((cx, cy - outer_r + 20, cx, cy + outer_r - 20), fill=RING, width=2)

    return img


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img = draw_placeholder()
    img.save(JPG, format="JPEG", quality=82, optimize=True, progressive=True)
    img.save(WEBP, format="WEBP", quality=78, method=6)
    print(f"Wrote {JPG.relative_to(ROOT)} ({JPG.stat().st_size / 1024:.1f} KB)")
    print(f"Wrote {WEBP.relative_to(ROOT)} ({WEBP.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
