#!/usr/bin/env python3
"""Generate OG share JPGs and patch TR/RU HTML Open Graph / Twitter meta."""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "assets" / "images"
PRODUCTS = IMAGES / "products"
SHARE = IMAGES / "og-share.jpg"
SITE = "https://abralion.com"
DEFAULT_OG = f"{SITE}/assets/images/og-share.jpg"
BG = (18, 20, 20)
W, H = 1200, 630

SKIP_NAMES = {"google", "yandex"}


def fit_on_canvas(src: Image.Image, width: int = W, height: int = H, pad: float = 0.86) -> Image.Image:
    canvas = Image.new("RGB", (width, height), BG)
    img = src.convert("RGBA") if src.mode in ("RGBA", "P") else src.convert("RGB")
    if img.mode == "RGBA":
        base = Image.new("RGB", img.size, BG)
        base.paste(img, mask=img.split()[-1])
        img = base
    else:
        img = img.convert("RGB")
    max_w, max_h = int(width * pad), int(height * pad)
    img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    x = (width - img.width) // 2
    y = (height - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas


def make_share_image() -> None:
    disc = Image.open(IMAGES / "abralion-disc.webp")
    out = fit_on_canvas(disc, pad=0.78)
    # subtle top accent bar
    accent = Image.new("RGB", (width := W, 6), (196, 30, 58))
    out.paste(accent, (0, 0))
    SHARE.parent.mkdir(parents=True, exist_ok=True)
    out.save(SHARE, "JPEG", quality=88, optimize=True)
    print(f"Wrote {SHARE.relative_to(ROOT)} ({SHARE.stat().st_size} bytes)")


def product_source(folder: Path, slug: str) -> Path | None:
    preferred = [
        folder / f"{slug}-og.jpg",
        folder / f"{slug}-kart.jpg",
        folder / f"{slug}.jpg",
        folder / f"{slug}.png",
        folder / f"{slug}.webp",
    ]
    for p in preferred:
        if p.exists():
            return p
    # any png/jpg then webp
    for pattern in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
        hits = sorted(folder.glob(pattern))
        if hits:
            return hits[0]
    return None


def ensure_product_og_jpg(folder: Path, slug: str) -> Path | None:
    og_path = folder / f"{slug}-og.jpg"
    if og_path.exists() and og_path.stat().st_size > 5000:
        return og_path
    src = product_source(folder, slug)
    if not src:
        return None
    # Prefer existing non-webp raster if already good enough for OG URL
    if src.suffix.lower() in {".jpg", ".jpeg", ".png"} and src.name != og_path.name:
        # Still generate consistent 1200x630 for scrapers
        img = Image.open(src)
        fit_on_canvas(img).save(og_path, "JPEG", quality=88, optimize=True)
        return og_path
    img = Image.open(src)
    fit_on_canvas(img).save(og_path, "JPEG", quality=88, optimize=True)
    return og_path


def image_meta_block(image_url: str, alt: str, mime: str = "image/jpeg") -> str:
    return "\n".join(
        [
            f'  <meta property="og:image" content="{image_url}">',
            f'  <meta property="og:image:width" content="{W}">',
            f'  <meta property="og:image:height" content="{H}">',
            f'  <meta property="og:image:type" content="{mime}">',
            f'  <meta property="og:image:alt" content="{alt}">',
        ]
    )


def extract_alt(text: str, fallback: str) -> str:
    m = re.search(r'<meta\s+property="og:image:alt"\s+content="([^"]*)"', text)
    return m.group(1) if m else fallback


def replace_og_image_block(text: str, image_url: str, alt: str) -> str:
    mime = "image/png" if image_url.lower().endswith(".png") else "image/jpeg"
    block = image_meta_block(image_url, alt, mime)

    # Replace contiguous og:image* block if present
    pattern = re.compile(
        r'(?:[ \t]*<meta\s+property="og:image(?::(?:width|height|type|alt))?"\s+content="[^"]*"\s*/?>\s*)+',
        re.IGNORECASE,
    )
    if pattern.search(text):
        text = pattern.sub(block + "\n", text, count=1)
    else:
        # Insert after og:description
        text = re.sub(
            r'(<meta\s+property="og:description"\s+content="[^"]*"\s*/?>)',
            r"\1\n" + block,
            text,
            count=1,
            flags=re.IGNORECASE,
        )

    # twitter:image (+ alt)
    if re.search(r'<meta\s+name="twitter:image"', text, re.I):
        text = re.sub(
            r'<meta\s+name="twitter:image"\s+content="[^"]*"\s*/?>',
            f'<meta name="twitter:image" content="{image_url}">',
            text,
            count=1,
            flags=re.I,
        )
    else:
        text = re.sub(
            r'(<meta\s+name="twitter:card"\s+content="[^"]*"\s*/?>)',
            rf'\1\n  <meta name="twitter:image" content="{image_url}">',
            text,
            count=1,
            flags=re.I,
        )

    if re.search(r'<meta\s+name="twitter:image:alt"', text, re.I):
        text = re.sub(
            r'<meta\s+name="twitter:image:alt"\s+content="[^"]*"\s*/?>',
            f'<meta name="twitter:image:alt" content="{alt}">',
            text,
            count=1,
            flags=re.I,
        )
    elif re.search(r'<meta\s+name="twitter:image"', text, re.I):
        text = re.sub(
            r'(<meta\s+name="twitter:image"\s+content="[^"]*"\s*/?>)',
            rf'\1\n  <meta name="twitter:image:alt" content="{alt}">',
            text,
            count=1,
            flags=re.I,
        )

    # Ensure twitter title/description if missing (copy from og when possible)
    if not re.search(r'<meta\s+name="twitter:title"', text, re.I):
        og_title = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', text)
        if og_title:
            text = re.sub(
                r'(<meta\s+name="twitter:card"\s+content="[^"]*"\s*/?>)',
                rf'\1\n  <meta name="twitter:title" content="{og_title.group(1)}">',
                text,
                count=1,
                flags=re.I,
            )
    if not re.search(r'<meta\s+name="twitter:description"', text, re.I):
        og_desc = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', text)
        if og_desc:
            text = re.sub(
                r'(<meta\s+name="twitter:title"\s+content="[^"]*"\s*/?>)',
                rf'\1\n  <meta name="twitter:description" content="{og_desc.group(1)}">',
                text,
                count=1,
                flags=re.I,
            )

    return text


def is_product_page(path: Path) -> bool:
    return path.parent.name == "urun"


def product_og_url(slug: str) -> str:
    return f"{SITE}/assets/images/products/{slug}/{slug}-og.jpg"


def patch_html(path: Path) -> bool:
    if path.name.startswith(tuple(SKIP_NAMES)):
        return False
    text = path.read_text(encoding="utf-8")
    if 'property="og:image"' not in text and "og:title" not in text:
        return False

    alt = extract_alt(text, "Abralion")
    if is_product_page(path):
        slug = path.stem
        folder = PRODUCTS / slug
        og_file = ensure_product_og_jpg(folder, slug) if folder.exists() else None
        image_url = product_og_url(slug) if og_file else DEFAULT_OG
    else:
        image_url = DEFAULT_OG

    new_text = replace_og_image_block(text, image_url, alt)
    # Also catch any leftover abralion-disc.webp in twitter/og
    new_text = new_text.replace(
        f"{SITE}/assets/images/abralion-disc.webp",
        DEFAULT_OG,
    )
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8", newline="\n")
    return True


def patch_template() -> None:
    tpl = ROOT / "scripts" / "templates" / "product-detail-noir.html"
    text = tpl.read_text(encoding="utf-8")
    block = "\n".join(
        [
            '  <meta property="og:image" content="{og_image}">',
            f'  <meta property="og:image:width" content="{W}">',
            f'  <meta property="og:image:height" content="{H}">',
            '  <meta property="og:image:type" content="image/jpeg">',
            '  <meta property="og:image:alt" content="{og_image_alt}">',
        ]
    )
    text2 = re.sub(
        r'(?:[ \t]*<meta\s+property="og:image(?::(?:width|height|type|alt))?"\s+content="[^"]*"\s*/?>\s*)+',
        block + "\n",
        text,
        count=1,
        flags=re.I,
    )
    if text2 != text:
        tpl.write_text(text2, encoding="utf-8", newline="\n")
        print(f"Updated {tpl.relative_to(ROOT)}")


def patch_og_meta_js() -> None:
    js = ROOT / "assets" / "js" / "og-meta.js"
    text = js.read_text(encoding="utf-8")
    text2 = text.replace(
        "assets/images/abralion-disc.webp",
        "assets/images/og-share.jpg",
    )
    # Prefer jpg/png candidates before webp in productOgImage
    old = """  function productOgImage(product, base) {
    const slug = product.slug;
    const candidates = [];
    if (product.images?.[0]?.src) candidates.push(product.images[0].src);
    candidates.push(`assets/images/products/${slug}/${slug}-kart.jpg`);
    for (const src of candidates) {
      const url = toAbsoluteUrl(src, base);
      if (url && url !== DEFAULT_IMAGE) return url;
    }
    return toAbsoluteUrl(candidates[0], base);
  }"""
    new = """  function productOgImage(product, base) {
    const slug = product.slug;
    const candidates = [];
    candidates.push(`assets/images/products/${slug}/${slug}-og.jpg`);
    candidates.push(`assets/images/products/${slug}/${slug}-kart.jpg`);
    if (product.images?.[0]?.src) candidates.push(product.images[0].src);
    candidates.push(`assets/images/products/${slug}/${slug}.jpg`);
    candidates.push(`assets/images/products/${slug}/${slug}.png`);
    candidates.push(`assets/images/products/${slug}/${slug}.webp`);
    for (const src of candidates) {
      const url = toAbsoluteUrl(src, base);
      if (url && url !== DEFAULT_IMAGE) return url;
    }
    return DEFAULT_IMAGE;
  }"""
    if old in text2:
        text2 = text2.replace(old, new)
    if text2 != text:
        js.write_text(text2, encoding="utf-8", newline="\n")
        print(f"Updated {js.relative_to(ROOT)}")


def main() -> None:
    make_share_image()
    # Pre-generate all product OG JPGs
    n_prod = 0
    for folder in sorted(PRODUCTS.iterdir()):
        if not folder.is_dir():
            continue
        if ensure_product_og_jpg(folder, folder.name):
            n_prod += 1
    print(f"Product OG JPGs ready: {n_prod}")

    updated = 0
    for path in sorted(ROOT.rglob("*.html")):
        if "scripts" in path.parts or "node_modules" in path.parts:
            continue
        if patch_html(path):
            updated += 1
            print(path.relative_to(ROOT))
    patch_template()
    patch_og_meta_js()
    # Mirror share image into ru/assets for local parity (meta still uses root URL)
    ru_share = ROOT / "ru" / "assets" / "images" / "og-share.jpg"
    if SHARE.exists():
        ru_share.parent.mkdir(parents=True, exist_ok=True)
        ru_share.write_bytes(SHARE.read_bytes())
        print(f"Copied {ru_share.relative_to(ROOT)}")
    print(f"\nPatched {updated} HTML files")


if __name__ == "__main__":
    main()
