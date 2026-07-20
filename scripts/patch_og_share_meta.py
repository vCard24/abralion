#!/usr/bin/env python3
"""Generate full-bleed OG share JPGs and patch TR/RU HTML Open Graph / Twitter meta."""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "assets" / "images"
PRODUCTS = IMAGES / "products"
SHARE = IMAGES / "og-cover.jpg"
SITE = "https://abralion.com"
DEFAULT_OG = f"{SITE}/assets/images/og-cover.jpg"
BG = (10, 10, 10)
W, H = 1200, 630

SKIP_NAMES = {"google", "yandex"}
OLD_DEFAULTS = (
    f"{SITE}/assets/images/abralion-disc.webp",
    f"{SITE}/assets/images/og-share.jpg",
    f"{SITE}/assets/images/og-share.jpg?v=2",
    f"{SITE}/assets/images/og-default.jpg",
)


def to_rgb(src: Image.Image) -> Image.Image:
    img = src.convert("RGBA") if src.mode in ("RGBA", "P") else src.convert("RGB")
    if img.mode == "RGBA":
        base = Image.new("RGB", img.size, BG)
        base.paste(img, mask=img.split()[-1])
        return base
    return img.convert("RGB")


def edge_is_uniform(img: Image.Image, edge: str, tol: int = 14) -> tuple[bool, tuple[int, int, int]]:
    px = img.load()
    w, h = img.size
    if edge == "top":
        samples = [px[x, 0] for x in range(0, w, max(1, w // 80))]
    elif edge == "bottom":
        samples = [px[x, h - 1] for x in range(0, w, max(1, w // 80))]
    elif edge == "left":
        samples = [px[0, y] for y in range(0, h, max(1, h // 80))]
    else:
        samples = [px[w - 1, y] for y in range(0, h, max(1, h // 80))]
    r0, g0, b0 = samples[0]
    for r, g, b in samples[1:]:
        if abs(r - r0) > tol or abs(g - g0) > tol or abs(b - b0) > tol:
            return False, (r0, g0, b0)
    return True, (r0, g0, b0)


def trim_uniform_borders(img: Image.Image, max_frac: float = 0.28) -> Image.Image:
    """Strip solid white/near-white or solid dark letterbox bars."""
    img = to_rgb(img)
    w, h = img.size
    max_x, max_y = int(w * max_frac), int(h * max_frac)
    left = right = top = bottom = 0
    px = img.load()

    def row_ok(y: int, ref: tuple[int, int, int], tol: int = 14) -> bool:
        r0, g0, b0 = ref
        step = max(1, w // 100)
        for x in range(0, w, step):
            r, g, b = px[x, y]
            if abs(r - r0) > tol or abs(g - g0) > tol or abs(b - b0) > tol:
                return False
        return True

    def col_ok(x: int, ref: tuple[int, int, int], tol: int = 14) -> bool:
        r0, g0, b0 = ref
        step = max(1, h // 100)
        for y in range(0, h, step):
            r, g, b = px[x, y]
            if abs(r - r0) > tol or abs(g - g0) > tol or abs(b - b0) > tol:
                return False
        return True

    for edge, limit, setter in (
        ("top", max_y, "top"),
        ("bottom", max_y, "bottom"),
        ("left", max_x, "left"),
        ("right", max_x, "right"),
    ):
        ok, ref = edge_is_uniform(img, edge)
        if not ok:
            continue
        # Only trim near-white or near-black bars (true letterbox)
        lum = 0.299 * ref[0] + 0.587 * ref[1] + 0.114 * ref[2]
        if not (lum > 235 or lum < 28):
            continue
        n = 0
        if edge == "top":
            while n < limit and row_ok(n, ref):
                n += 1
            top = n
        elif edge == "bottom":
            while n < limit and row_ok(h - 1 - n, ref):
                n += 1
            bottom = n
        elif edge == "left":
            while n < limit and col_ok(n, ref):
                n += 1
            left = n
        else:
            while n < limit and col_ok(w - 1 - n, ref):
                n += 1
            right = n

    if left + right >= w - 20 or top + bottom >= h - 20:
        return img
    if left or right or top or bottom:
        return img.crop((left, top, w - right, h - bottom))
    return img


def subject_bbox(img: Image.Image, dark_thresh: int = 28) -> tuple[int, int, int, int] | None:
    """Bounding box of non-dark pixels (for packshots on black)."""
    img = to_rgb(img)
    w, h = img.size
    # Downsample for speed
    small = img.resize((min(320, w), min(320, h)), Image.Resampling.BILINEAR)
    sw, sh = small.size
    px = small.load()
    xs: list[int] = []
    ys: list[int] = []
    for y in range(sh):
        for x in range(sw):
            r, g, b = px[x, y]
            if 0.299 * r + 0.587 * g + 0.114 * b > dark_thresh:
                xs.append(x)
                ys.append(y)
    if len(xs) < 30:
        return None
    # Subject should not already fill most of the frame
    coverage = len(xs) / (sw * sh)
    if coverage > 0.55:
        return None
    sx0, sx1 = min(xs), max(xs)
    sy0, sy1 = min(ys), max(ys)
    pad_x = max(4, int((sx1 - sx0) * 0.12))
    pad_y = max(4, int((sy1 - sy0) * 0.12))
    scale_x, scale_y = w / sw, h / sh
    x0 = max(0, int((sx0 - pad_x) * scale_x))
    y0 = max(0, int((sy0 - pad_y) * scale_y))
    x1 = min(w, int((sx1 + pad_x) * scale_x))
    y1 = min(h, int((sy1 + pad_y) * scale_y))
    if x1 - x0 < w * 0.25 or y1 - y0 < h * 0.25:
        return None
    return x0, y0, x1, y1


def fit_cover(src: Image.Image, width: int = W, height: int = H) -> Image.Image:
    """Trim letterbox, optionally zoom to subject, then cover-crop to width x height."""
    img = trim_uniform_borders(to_rgb(src))
    box = subject_bbox(img)
    if box:
        img = img.crop(box)
    scale = max(width / img.width, height / img.height)
    new_w = max(width, int(round(img.width * scale)))
    new_h = max(height, int(round(img.height * scale)))
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (img.width - width) // 2
    top = (img.height - height) // 2
    return img.crop((left, top, left + width, top + height))


def make_share_image() -> None:
    hero = IMAGES / "home" / "hero-bg-1920.jpg"
    if not hero.exists():
        hero = IMAGES / "home" / "hero-bg.jpg"
    src = Image.open(hero)
    out = fit_cover(src)
    # Thin brand accent bar
    accent = Image.new("RGB", (W, 5), (226, 35, 26))
    out.paste(accent, (0, 0))
    SHARE.parent.mkdir(parents=True, exist_ok=True)
    out.save(SHARE, "JPEG", quality=90, optimize=True)
    print(f"Wrote {SHARE.relative_to(ROOT)} ({SHARE.stat().st_size} bytes) from {hero.name}")


def product_source(folder: Path, slug: str) -> Path | None:
    """Prefer kullanım / action photos; never tiny thumbs or generated OG."""
    skip_bits = (
        "-og.",
        "-wa.",
        "-cover.",
        "-share.",
        "-kart.",
        "-card.",
        "-menu-thumb",
        "-thumb",
        "-etiket",
    )
    preferred_globs = [
        f"{slug}-kullanim.*",
        "*kullanim*.*",
        f"{slug}.*",
    ]
    seen: set[Path] = set()
    ordered: list[Path] = []
    for pattern in preferred_globs:
        for p in sorted(folder.glob(pattern)):
            if p in seen:
                continue
            name = p.name.lower()
            if p.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                continue
            if any(bit in name for bit in skip_bits):
                continue
            if p.stat().st_size < 15000:
                continue
            seen.add(p)
            ordered.append(p)

    # Score: kullanim first, then larger files, prefer jpg over webp packshots
    def score(p: Path) -> tuple:
        name = p.name.lower()
        is_kullanim = "kullanim" in name
        is_exact = p.stem.lower() == slug
        ext_bonus = 2 if p.suffix.lower() in {".jpg", ".jpeg", ".png"} else 0
        return (is_kullanim, is_exact, ext_bonus, p.stat().st_size)

    if ordered:
        return max(ordered, key=score)

    candidates: list[Path] = []
    for pattern in ("*.webp", "*.png", "*.jpg", "*.jpeg"):
        for p in folder.glob(pattern):
            name = p.name.lower()
            if any(bit in name for bit in skip_bits):
                continue
            if p.stat().st_size < 15000:
                continue
            candidates.append(p)
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_size)


def ensure_product_og_jpg(folder: Path, slug: str, force: bool = True) -> Path | None:
    og_path = folder / f"{slug}-cover.jpg"
    src = product_source(folder, slug)
    if not src:
        return og_path if og_path.exists() else None
    if not force and og_path.exists() and og_path.stat().st_size > 40000:
        return og_path
    img = Image.open(src)
    fit_cover(img).save(og_path, "JPEG", quality=88, optimize=True)
    print(f"  COVER {slug}: {src.name} {img.size} -> {og_path.name} ({og_path.stat().st_size}b)")
    return og_path


def image_meta_block(image_url: str, alt: str, mime: str = "image/jpeg") -> str:
    return "\n".join(
        [
            f'  <meta property="og:image" content="{image_url}">',
            f'  <meta property="og:image:secure_url" content="{image_url}">',
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

    pattern = re.compile(
        r'(?:[ \t]*<meta\s+property="og:image(?::(?:secure_url|width|height|type|alt))?"\s+content="[^"]*"\s*/?>\s*)+',
        re.IGNORECASE,
    )
    if pattern.search(text):
        text = pattern.sub(block + "\n", text, count=1)
    else:
        text = re.sub(
            r'(<meta\s+property="og:description"\s+content="[^"]*"\s*/?>)',
            r"\1\n" + block,
            text,
            count=1,
            flags=re.IGNORECASE,
        )

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
    return f"{SITE}/assets/images/products/{slug}/{slug}-cover.jpg"


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
    for old in OLD_DEFAULTS:
        new_text = new_text.replace(old, DEFAULT_OG)
    new_text = re.sub(
        rf"{re.escape(SITE)}/assets/images/products/([^/]+)/\1-(?:og|wa)\.jpg(?:\?v=\d+)?",
        rf"{SITE}/assets/images/products/\1/\1-cover.jpg",
        new_text,
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
            '  <meta property="og:image:secure_url" content="{og_image}">',
            f'  <meta property="og:image:width" content="{W}">',
            f'  <meta property="og:image:height" content="{H}">',
            '  <meta property="og:image:type" content="image/jpeg">',
            '  <meta property="og:image:alt" content="{og_image_alt}">',
        ]
    )
    text2 = re.sub(
        r'(?:[ \t]*<meta\s+property="og:image(?::(?:secure_url|width|height|type|alt))?"\s+content="[^"]*"\s*/?>\s*)+',
        block + "\n",
        text,
        count=1,
        flags=re.I,
    )
    if text2 != text:
        tpl.write_text(text2, encoding="utf-8", newline="\n")
        print(f"Updated {tpl.relative_to(ROOT)}")


def patch_og_meta_js() -> None:
    for js in (ROOT / "assets" / "js" / "og-meta.js", ROOT / "ru" / "assets" / "js" / "og-meta.js"):
        if not js.exists():
            continue
        text = js.read_text(encoding="utf-8")
        text2 = text
        for old, new in (
            ("assets/images/abralion-disc.webp", "assets/images/og-cover.jpg"),
            ("assets/images/og-share.jpg?v=2", "assets/images/og-cover.jpg"),
            ("assets/images/og-share.jpg", "assets/images/og-cover.jpg"),
            ("assets/images/og-default.jpg", "assets/images/og-cover.jpg"),
            ("/${slug}-og.jpg", "/${slug}-cover.jpg"),
            ("/${slug}-wa.jpg", "/${slug}-cover.jpg"),
            ("/${slug}-og.jpg?v=2", "/${slug}-cover.jpg"),
        ):
            text2 = text2.replace(old, new)
        text2 = text2.replace(
            "`assets/images/products/${slug}/${slug}-wa.jpg`",
            "`assets/images/products/${slug}/${slug}-cover.jpg`",
        )
        text2 = text2.replace(
            "`assets/images/products/${slug}/${slug}-og.jpg`",
            "`assets/images/products/${slug}/${slug}-cover.jpg`",
        )
        if text2 != text:
            js.write_text(text2, encoding="utf-8", newline="\n")
            print(f"Updated {js.relative_to(ROOT)}")


def patch_generate_script() -> None:
    gen = ROOT / "scripts" / "generate-product-pages.py"
    text = gen.read_text(encoding="utf-8")
    text2 = text.replace(f"{'{slug}'}-wa.jpg", f"{'{slug}'}-cover.jpg")
    text2 = text2.replace("og-default.jpg", "og-cover.jpg")
    # Fix the f-string patterns more carefully
    text2 = re.sub(
        r'f"\{slug\}-wa\.jpg"',
        'f"{slug}-cover.jpg"',
        text2,
    )
    text2 = text2.replace("/{slug}-wa.jpg", "/{slug}-cover.jpg")
    if text2 != text:
        gen.write_text(text2, encoding="utf-8", newline="\n")
        print(f"Updated {gen.relative_to(ROOT)}")


def main() -> None:
    make_share_image()
    n_prod = 0
    for folder in sorted(PRODUCTS.iterdir()):
        if not folder.is_dir():
            continue
        if ensure_product_og_jpg(folder, folder.name, force=True):
            n_prod += 1
    print(f"Product cover JPGs ready: {n_prod}")

    updated = 0
    for path in sorted(ROOT.rglob("*.html")):
        if "scripts" in path.parts or "node_modules" in path.parts:
            continue
        if patch_html(path):
            updated += 1
            print(path.relative_to(ROOT))
    patch_template()
    patch_og_meta_js()
    patch_generate_script()
    ru_share = ROOT / "ru" / "assets" / "images" / "og-cover.jpg"
    if SHARE.exists():
        ru_share.parent.mkdir(parents=True, exist_ok=True)
        ru_share.write_bytes(SHARE.read_bytes())
        print(f"Copied {ru_share.relative_to(ROOT)}")
    print(f"\nPatched {updated} HTML files")


if __name__ == "__main__":
    main()
