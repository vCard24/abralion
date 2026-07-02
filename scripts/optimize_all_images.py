#!/usr/bin/env python3
"""Hero responsive türevleri + ürün kartı (-card) AVIF/WebP varyantları üretir."""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import pillow_avif  # noqa: F401
except ImportError:
    print("pillow-avif-plugin gerekli: pip install pillow-avif-plugin", file=sys.stderr)
    sys.exit(1)

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "assets" / "images" / "home"
PRODUCTS = ROOT / "assets" / "images" / "products"
HERO_SOURCE = HOME / "hero-bg.jpg"

HERO_WIDTHS = (640, 1024, 1440, 1920)
CARD_WIDTH = 600
CARD_ASPECT = 1.9  # product-card aspect-[1.9]
HERO_AVIF_QUALITY = 45
CARD_AVIF_QUALITY = 45
WEBP_QUALITY = 72
JPG_QUALITY = 78
CARD_MAX_BYTES = 50 * 1024

SKIP_NAME_PARTS = (
    "-card.",
    "-kullanim",
    "-varyantlar",
    "abralion-",
    "-2.",
    "-3.",
    "-4.",
    "-5.",
    "-6.",
    "-7.",
    "-8.",
    "-9.",
    "-10.",
    "-11.",
    "-12.",
)


def fmt_bytes(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KiB"
    return f"{n / (1024 * 1024):.2f} MiB"


def report(path: Path, original_size: int | None = None) -> None:
    size = path.stat().st_size
    if original_size is None:
        print(f"  {path.relative_to(ROOT)}: {fmt_bytes(size)}")
        return
    saved = original_size - size
    pct = (saved / original_size * 100) if original_size else 0
    sign = "kazanç" if saved > 0 else "artış"
    print(
        f"  {path.name}: {fmt_bytes(size)} ({abs(pct):.1f}% {sign} vs orijinal {fmt_bytes(original_size)})"
    )


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


def to_rgb(img: Image.Image) -> Image.Image:
    if img.mode in ("RGB", "RGBA"):
        return img
    return img.convert("RGB")


def save_avif(img: Image.Image, path: Path, quality: int) -> None:
    to_rgb(img).save(path, "AVIF", quality=quality)


def save_webp(img: Image.Image, path: Path, quality: int) -> None:
    to_rgb(img).save(path, "WEBP", quality=quality, method=6)


def save_jpg(img: Image.Image, path: Path) -> None:
    to_rgb(img).save(path, "JPEG", quality=JPG_QUALITY, optimize=True, progressive=True)


def save_card_variants(img: Image.Image, stem_path: Path) -> tuple[Path, Path]:
    """600px kart kırpması; AVIF kalitesini ≤50 KiB olana kadar düşür."""
    card = center_crop_aspect(img, CARD_WIDTH, CARD_ASPECT)
    avif_path = stem_path.parent / f"{stem_path.stem}-card.avif"
    webp_path = stem_path.parent / f"{stem_path.stem}-card.webp"

    quality = CARD_AVIF_QUALITY
    while quality >= 28:
        save_avif(card, avif_path, quality)
        if avif_path.stat().st_size <= CARD_MAX_BYTES:
            break
        quality -= 4

    save_webp(card, webp_path, WEBP_QUALITY)
    return avif_path, webp_path


def should_skip_product_image(path: Path) -> bool:
    name = path.name.lower()
    if path.suffix.lower() not in {".webp", ".jpg", ".jpeg", ".png"}:
        return True
    if any(part in name for part in SKIP_NAME_PARTS):
        return True
    if path.stat().st_size < 40 * 1024:
        return True
    return False


def optimize_hero() -> None:
    if not HERO_SOURCE.exists():
        print(f"Hero kaynağı yok: {HERO_SOURCE}", file=sys.stderr)
        return

    original_size = HERO_SOURCE.stat().st_size
    base = to_rgb(Image.open(HERO_SOURCE))
    src_w, src_h = base.size
    print(f"Hero kaynak: {HERO_SOURCE.name} ({src_w}x{src_h}, {fmt_bytes(original_size)})\n")
    print("Hero responsive türevler (AVIF q45):")

    for width in HERO_WIDTHS:
        variant = resize_width(base, width)
        avif_path = HOME / f"hero-bg-{width}.avif"
        webp_path = HOME / f"hero-bg-{width}.webp"
        jpg_path = HOME / f"hero-bg-{width}.jpg"
        save_avif(variant, avif_path, HERO_AVIF_QUALITY)
        save_webp(variant, webp_path, WEBP_QUALITY)
        if width == 640:
            save_jpg(variant, jpg_path)
        report(avif_path, original_size)
        report(webp_path, original_size)

    hero_1920 = resize_width(base, 1920)
    jpg_path = HOME / "hero-bg-1920.jpg"
    save_jpg(hero_1920, jpg_path)
    print("\nHero JPG fallback:")
    report(jpg_path, original_size)

    print(f"\nHero img boyut önerisi: width=\"1920\" height=\"{hero_1920.size[1]}\"")
    hero_640 = resize_width(base, 640)
    print(f"Hero mobil fallback: width=\"640\" height=\"{hero_640.size[1]}\"")


def optimize_product_cards() -> list[tuple[Path, Path, Path]]:
    """Ürün klasörlerindeki ana görsellerden -card varyantları üret."""
    results: list[tuple[Path, Path, Path]] = []
    patterns = ("*.webp", "*.jpg", "*.jpeg", "*.png")
    files: list[Path] = []
    for pattern in patterns:
        files.extend(PRODUCTS.rglob(pattern))

    files = sorted({p for p in files if not should_skip_product_image(p)})
    print(f"\nÜrün kart varyantları ({len(files)} kaynak):")

    for path in files:
        try:
            img = Image.open(path)
        except OSError as exc:
            print(f"  ATLA {path.name}: {exc}")
            continue

        original_size = path.stat().st_size
        avif_path, webp_path = save_card_variants(img, path)
        results.append((path, avif_path, webp_path))
        print(f"\n  Kaynak: {path.relative_to(ROOT)} ({fmt_bytes(original_size)})")
        report(avif_path)
        report(webp_path)

    return results


def main() -> None:
    optimize_hero()
    optimize_product_cards()
    print(f"\nTamamlandı.")


if __name__ == "__main__":
    main()
