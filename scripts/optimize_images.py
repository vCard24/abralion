#!/usr/bin/env python3
"""Hero görseli için responsive AVIF/WebP/JPG türevleri üretir."""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import pillow_avif  # noqa: F401 — AVIF kayıt
except ImportError:
    print("pillow-avif-plugin gerekli: pip install pillow-avif-plugin", file=sys.stderr)
    sys.exit(1)

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "assets" / "images" / "home"
SOURCE = HOME / "hero-bg.jpg"

HERO_WIDTHS = (640, 1024, 1440, 1920)
CARD_WIDTH = 480
CARD_ASPECT = 16 / 9  # aspect-video (kategori kartı)
AVIF_QUALITY = 45
WEBP_QUALITY = 75
JPG_QUALITY = 80


def fmt_bytes(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KiB"
    return f"{n / (1024 * 1024):.2f} MiB"


def report(path: Path, original_size: int) -> None:
    size = path.stat().st_size
    saved = original_size - size
    pct = (saved / original_size * 100) if original_size else 0
    sign = "kazanç" if saved > 0 else "artış"
    print(f"  {path.name}: {fmt_bytes(size)} ({abs(pct):.1f}% {sign} vs orijinal {fmt_bytes(original_size)})")


def resize_width(img: Image.Image, width: int) -> Image.Image:
    w, h = img.size
    height = max(1, round(h * width / w))
    return img.resize((width, height), Image.Resampling.LANCZOS)


def center_crop_aspect(img: Image.Image, target_w: int, aspect: float) -> Image.Image:
    target_h = max(1, round(target_w / aspect))
    src_w, src_h = img.size
    src_aspect = src_w / src_h

    if src_aspect > aspect:
        crop_h = src_h
        crop_w = max(1, round(src_h * aspect))
    else:
        crop_w = src_w
        crop_h = max(1, round(src_w / aspect))

    left = (src_w - crop_w) // 2
    top = (src_h - crop_h) // 2
    cropped = img.crop((left, top, left + crop_w, top + crop_h))
    return cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)


def save_avif(img: Image.Image, path: Path) -> None:
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    img.save(path, "AVIF", quality=AVIF_QUALITY)


def save_webp(img: Image.Image, path: Path) -> None:
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    img.save(path, "WEBP", quality=WEBP_QUALITY, method=6)


def save_jpg(img: Image.Image, path: Path, progressive: bool = True) -> None:
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(path, "JPEG", quality=JPG_QUALITY, optimize=True, progressive=progressive)


def main() -> None:
    if not SOURCE.exists():
        print(f"Kaynak bulunamadı: {SOURCE}", file=sys.stderr)
        sys.exit(1)

    original_size = SOURCE.stat().st_size
    base = Image.open(SOURCE)
    if base.mode not in ("RGB", "RGBA"):
        base = base.convert("RGB")
    else:
        base = base.copy()

    src_w, src_h = base.size
    print(f"Kaynak: {SOURCE.name} ({src_w}x{src_h}, {fmt_bytes(original_size)})\n")

    print("Hero responsive türevler:")
    for width in HERO_WIDTHS:
        variant = resize_width(base, width)
        avif_path = HOME / f"hero-bg-{width}.avif"
        webp_path = HOME / f"hero-bg-{width}.webp"
        save_avif(variant, avif_path)
        save_webp(variant, webp_path)
        if width == 640:
            save_jpg(variant, HOME / "hero-bg-640.jpg")
        report(avif_path, original_size)
        report(webp_path, original_size)

    hero_1920 = resize_width(base, 1920)
    jpg_path = HOME / "hero-bg-1920.jpg"
    save_jpg(hero_1920, jpg_path)
    print("\nHero JPG fallback:")
    report(jpg_path, original_size)

    print("\nKategori kartı (16:9, 480px):")
    card = center_crop_aspect(base, CARD_WIDTH, CARD_ASPECT)
    card_avif = HOME / "hero-card-480.avif"
    card_webp = HOME / "hero-card-480.webp"
    card_jpg = HOME / "hero-card-480.jpg"
    save_avif(card, card_avif)
    save_webp(card, card_webp)
    save_jpg(card, card_jpg, progressive=True)
    report(card_avif, original_size)
    report(card_webp, original_size)
    report(card_jpg, original_size)

    print(f"\nTamamlandı. Çıktılar: {HOME}")
    print(f"Hero img önerilen boyutlar: width=\"1920\" height=\"{hero_1920.size[1]}\"")
    print(f"Kart img önerilen boyutlar: width=\"480\" height=\"{card.size[1]}\"")


if __name__ == "__main__":
    main()
