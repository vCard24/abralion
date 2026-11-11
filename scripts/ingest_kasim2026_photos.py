#!/usr/bin/env python3
"""Kasım 2026 fotoğraf aktarımı.

Kaynak klasör salt okunur. Çıktı assets/images/products/{slug}/ altına yazılır.
Kart dosyaları (*-kart.jpg, *-kart-card.*) silinmez.

Örnek:
  python scripts/ingest_kasim2026_photos.py --only miknatisli-anahtar-ucu --dry-run
  python scripts/ingest_kasim2026_photos.py --only miknatisli-anahtar-ucu --replace-legacy --write-catalog
  python scripts/ingest_kasim2026_photos.py --cards canak-firca-sacakli
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageCms, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SOURCE = Path(r"C:\Users\mosta\Desktop\abralion-kasim-2026-fotograflar")
PRODUCTS = ROOT / "assets" / "images" / "products"
CATALOG_JSON = ROOT / "data" / "products.json"
CATALOG_JS = ROOT / "assets" / "js" / "products-data.js"
CATALOG_JS_ROOT = ROOT / "products-data.js"
CARD_OUT = ROOT / "scripts" / "raporlar" / "a1a-kart"
CARD_PREVIEW = ROOT / "scripts" / "raporlar" / "a1b-kartlar"
BG = (0x0A, 0x0A, 0x0A)
CARD_LARGE = (600, 316)
CARD_SMALL = (190, 110)

# A0 klasör → slug. Kaynak adları diskteki klasörle birebir.
FOLDER_BY_SLUG = {
    "canak-firca-sacakli": "canak-firca-sacakli",
    "canak-firca-burgulu": "canak-firca-burgulu",
    "plastik-sapli-celik-tel-firca": "PLASTİK SAPLI ÇELİK TEL FIRÇA (EL FIRÇASI)",
    "genis-agizli-keski": "Geniş Ağızlı Keski",
    "cam-seramik-matkap-ucu": "Cam ve Seramik Matkap Ucu (4 Kesicili)",
    "hss-matkap-ucu": "HSS Matkap Ucu",
    "sds-plus-2-kesicili-beton-matkap-ucu": "SDS Plus 2 Kesicili Beton Matkap Ucu",
    "sds-plus-4-kesicili-beton-matkap-ucu": "SDS Plus 4 Kesicili Beton Matkap Ucu (Quadro)",
    "sds-max-burc-aleti": "SDS MAX Burç Aleti (Taraklı Murç)",
    "miknatisli-anahtar-ucu": "Mıknatıslı Anahtar Ucu (Manyetik Somun Adaptörü)",
    "ph2-manyetik-bits-uc": "PH2 Manyetik Bits Uç",
    "duz-keski-sds-max": "Düz Keski SDS Max",
    "sivri-uclu-keski-murc-sds-plus": "Sivri Uçlu Keski Murç SDS Plus",
}

# Ana foto: ürün tek başına, ambalaj/aksiyon karesi değil. Seçim A1b raporunda.
HERO_FILE = {
    "canak-firca-sacakli": "DSC_8984-редакт.jpg",
    "canak-firca-burgulu": "DSC_8974-редакт.jpg",
    "plastik-sapli-celik-tel-firca": "DSC_8926-редакт.jpg",
    "genis-agizli-keski": "DSC_9114-редакт.jpg",
    "cam-seramik-matkap-ucu": "DSC_9327-редакт.jpg",
    "hss-matkap-ucu": "DSC_8892-редакт.jpg",
    "sds-plus-2-kesicili-beton-matkap-ucu": "DSC_9233-редакт.jpg",
    "sds-plus-4-kesicili-beton-matkap-ucu": "DSC_9170-редакт.jpg",
    "sds-max-burc-aleti": "DSC_9189-редакт.jpg",
    "miknatisli-anahtar-ucu": "DSC_8859-редакт.jpg",
    "ph2-manyetik-bits-uc": "DSC_9045-редакт.jpg",
    "duz-keski-sds-max": "DSC_8950-редакт.jpg",
    "sivri-uclu-keski-murc-sds-plus": "DSC_8944-редакт.jpg",
}

# Kart karesi ana fotodan ayrı olabilir: yatay kartta ürünün kendisi dolsun.
CARD_FILE = {
    "canak-firca-sacakli": "DSC_9025-редакт.jpg",
    "canak-firca-burgulu": "DSC_8978-редакт.jpg",
    "plastik-sapli-celik-tel-firca": "DSC_8926-редакт.jpg",
    "genis-agizli-keski": "DSC_9114-редакт.jpg",
}

NEW_SLUGS = (
    "canak-firca-sacakli",
    "canak-firca-burgulu",
    "plastik-sapli-celik-tel-firca",
    "genis-agizli-keski",
)
EXISTING_A1B = (
    "cam-seramik-matkap-ucu",
    "hss-matkap-ucu",
    "sds-plus-2-kesicili-beton-matkap-ucu",
    "sds-plus-4-kesicili-beton-matkap-ucu",
    "sds-max-burc-aleti",
    "ph2-manyetik-bits-uc",
    "duz-keski-sds-max",
    "sivri-uclu-keski-murc-sds-plus",
)
# Kardeş images[] kaynak galeriye bakar. Slug'a göre aranan 5 dosya kopyalanır.
SIBLINGS = (
    ("duz-keski-sds-plus", "duz-keski-sds-max"),
    ("sivri-uclu-keski-murc-sds-max", "sivri-uclu-keski-murc-sds-plus"),
)
WIRE_SLUGS = {
    "canak-firca-sacakli",
    "canak-firca-burgulu",
    "plastik-sapli-celik-tel-firca",
}
PRODUCT_NAME = {
    "canak-firca-sacakli": "Saçaklı Çanak Fırça",
    "canak-firca-burgulu": "Burgulu Çanak Fırça",
    "plastik-sapli-celik-tel-firca": "Plastik Saplı Çelik Tel Fırça",
    "genis-agizli-keski": "Geniş Ağızlı Keski",
    "cam-seramik-matkap-ucu": "Cam ve Seramik Matkap Ucu (4 Kesicili)",
    "hss-matkap-ucu": "HSS Matkap Ucu",
    "sds-plus-2-kesicili-beton-matkap-ucu": "SDS Plus 2 Kesicili Beton Matkap Ucu",
    "sds-plus-4-kesicili-beton-matkap-ucu": "SDS Plus 4 Kesicili Beton Matkap Ucu (Quadro)",
    "sds-max-burc-aleti": "SDS MAX Burç Aleti (Taraklı Murç)",
    "miknatisli-anahtar-ucu": "Mıknatıslı Anahtar Ucu (Manyetik Somun Adaptörü)",
    "ph2-manyetik-bits-uc": "PH2 Manyetik Bits Uç",
    "duz-keski-sds-max": "Düz Keski SDS Max",
    "duz-keski-sds-plus": "Düz Keski SDS Plus",
    "sivri-uclu-keski-murc-sds-plus": "Sivri Uçlu Keski Murç SDS Plus",
    "sivri-uclu-keski-murc-sds-max": "Sivri Uçlu Keski Murç SDS Max",
}
SLUG_KEYED_SUFFIXES = (
    ".webp",
    "-cover.jpg",
    "-og.jpg",
    "-wa.jpg",
    "-menu-thumb.webp",
)

KEEP_KART_JPG = re.compile(r"-kart\.jpg$", re.I)
KEEP_KART_CARD = re.compile(r"-kart-card\.", re.I)
DUP_COPY = re.compile(r" \(1\)\.jpe?g$", re.I)

THUMB_EDGE = 480
FULL_EDGE = 1600
HERO_EDGE = 1200
SHARE_SIZE = (1200, 630)
MENU_EDGE = 64


def is_duplicate_name(name: str) -> bool:
    return bool(DUP_COPY.search(name))


def is_kept(name: str) -> bool:
    if name == ".gitkeep":
        return True
    return bool(KEEP_KART_JPG.search(name) or KEEP_KART_CARD.search(name))


def to_srgb(im: Image.Image) -> Image.Image:
    """EXIF Orientation yoksa döndürme. Varsa uygula. Çıktı sRGB RGB."""
    exif = im.getexif()
    orientation = exif.get(274) if exif else None
    if orientation and orientation != 1:
        im = ImageOps.exif_transpose(im)
    icc = im.info.get("icc_profile")
    if icc:
        try:
            src = ImageCms.ImageCmsProfile(BytesIO(icc))
            dst = ImageCms.createProfile("sRGB")
            im = ImageCms.profileToProfile(im, src, dst, outputMode="RGB")
            return im
        except Exception:
            pass
    if im.mode == "RGBA":
        base = Image.new("RGB", im.size, (255, 255, 255))
        base.paste(im, mask=im.split()[-1])
        return base
    return im.convert("RGB")


def fit_long_edge(im: Image.Image, edge: int) -> Image.Image:
    w, h = im.size
    long_edge = max(w, h)
    if long_edge == edge:
        return im
    scale = edge / long_edge
    nw = max(1, int(round(w * scale)))
    nh = max(1, int(round(h * scale)))
    if max(nw, nh) != edge:
        if w >= h:
            nw = edge
            nh = max(1, int(round(h * edge / w)))
        else:
            nh = edge
            nw = max(1, int(round(w * edge / h)))
    return im.resize((nw, nh), Image.Resampling.LANCZOS)


def save_set(im: Image.Image, dest_stem: Path, qualities: dict[str, int]) -> list[Path]:
    dest_stem.parent.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    jpg = dest_stem.with_suffix(".jpg")
    webp = dest_stem.with_suffix(".webp")
    avif = dest_stem.with_suffix(".avif")
    im.save(jpg, "JPEG", quality=qualities["jpg"], optimize=True, progressive=True)
    im.save(webp, "WEBP", quality=qualities["webp"], method=6)
    im.save(avif, "AVIF", quality=qualities["avif"])
    written.extend([jpg, webp, avif])
    return written


def source_frames(slug: str) -> tuple[Path, list[Path], Path]:
    folder_name = FOLDER_BY_SLUG[slug]
    folder = SOURCE / folder_name
    if not folder.is_dir():
        raise SystemExit(f"Kaynak klasör yok: {folder}")
    frames = sorted(
        (p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg"}),
        key=lambda p: p.name,
    )
    kept = [p for p in frames if not is_duplicate_name(p.name)]
    hero_name = HERO_FILE.get(slug)
    hero = None
    if hero_name:
        hero = next((p for p in kept if p.name == hero_name), None)
        if hero is None:
            raise SystemExit(f"Kahraman kare yok: {hero_name}")
        kept = [hero] + [p for p in kept if p != hero]
    elif kept:
        hero = kept[0]
    if hero is None:
        raise SystemExit(f"Kare yok: {slug}")
    return folder, kept, hero


def legacy_files(dest: Path) -> list[Path]:
    if not dest.exists():
        return []
    return sorted(p for p in dest.iterdir() if p.is_file() and not is_kept(p.name))


def contain_on_canvas(im: Image.Image, size: tuple[int, int], bg: tuple[int, int, int], margin: float = 0.92) -> Image.Image:
    canvas = Image.new("RGB", size, bg)
    tw, th = size
    scale = min(tw / im.width, th / im.height) * margin
    nw = max(1, int(round(im.width * scale)))
    nh = max(1, int(round(im.height * scale)))
    fitted = im.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas.paste(fitted, ((tw - nw) // 2, (th - nh) // 2))
    return canvas


def subject_mask(im: Image.Image, thresh: int = 246) -> Image.Image:
    gray = im.convert("L")
    mask = gray.point(lambda p: 0 if p >= thresh else 255)
    return mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.6))


def bbox_of(mask: Image.Image) -> tuple[int, int, int, int]:
    box = mask.getbbox()
    if not box:
        w, h = mask.size
        return (0, 0, w, h)
    return box


def crop_aspect(im: Image.Image, aspect: float = 190 / 110) -> Image.Image:
    mask = subject_mask(im)
    x0, y0, x1, y1 = bbox_of(mask)
    bw, bh = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    pad = 1.28
    crop_w = bw * pad
    crop_h = crop_w / aspect
    if crop_h < bh * pad:
        crop_h = bh * pad
        crop_w = crop_h * aspect
    left = int(round(cx - crop_w / 2))
    top = int(round(cy - crop_h / 2))
    right = int(round(left + crop_w))
    bottom = int(round(top + crop_h))
    w, h = im.size
    if right - left > w:
        left, right = 0, w
    if bottom - top > h:
        top, bottom = 0, h
    if left < 0:
        right -= left
        left = 0
    if top < 0:
        bottom -= top
        top = 0
    if right > w:
        left -= right - w
        right = w
    if bottom > h:
        top -= bottom - h
        bottom = h
    left = max(0, left)
    top = max(0, top)
    return im.crop((left, top, right, bottom))


def add_ground_shadow(im: Image.Image) -> Image.Image:
    mask = subject_mask(im)
    x0, y0, x1, y1 = bbox_of(mask)
    shadow = Image.new("L", im.size, 0)
    draw = ImageDraw.Draw(shadow)
    cx = (x0 + x1) // 2
    rx = max(8, int((x1 - x0) * 0.42))
    ry = max(4, int((y1 - y0) * 0.06))
    draw.ellipse((cx - rx, y1 - ry, cx + rx, y1 + ry), fill=90)
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    base = im.convert("RGBA")
    shade = Image.new("RGBA", im.size, (40, 40, 40, 0))
    shade.putalpha(shadow)
    out = Image.alpha_composite(base, shade)
    out.paste(im, mask=mask)
    return out.convert("RGB")


def dark_composite(im: Image.Image, size: tuple[int, int] = (692, 400)) -> Image.Image:
    mask = subject_mask(im)
    x0, y0, x1, y1 = bbox_of(mask)
    subject = im.crop((x0, y0, x1, y1))
    smask = mask.crop((x0, y0, x1, y1))
    tw, th = size
    scale = min((tw * 0.78) / subject.width, (th * 0.62) / subject.height)
    nw = max(1, int(round(subject.width * scale)))
    nh = max(1, int(round(subject.height * scale)))
    subject = subject.resize((nw, nh), Image.Resampling.LANCZOS)
    smask = smask.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, BG + (255,))
    ox = (tw - nw) // 2
    oy = int(th * 0.46) - nh // 2

    shadow = Image.new("L", size, 0)
    draw = ImageDraw.Draw(shadow)
    draw.ellipse((ox + int(nw * 0.12), oy + nh - 8, ox + int(nw * 0.88), oy + nh + 22), fill=160)
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    shade = Image.new("RGBA", size, (0, 0, 0, 0))
    shade.putalpha(shadow.point(lambda p: int(p * 0.65)))
    canvas = Image.alpha_composite(canvas, shade)

    sprite = Image.new("RGBA", (nw, nh), (0, 0, 0, 0))
    sprite.paste(subject, mask=smask)
    canvas.paste(sprite, (ox, oy), sprite)

    refl = ImageOps.flip(sprite)
    fade = Image.new("L", (nw, nh), 0)
    pixels = fade.load()
    for y in range(nh):
        alpha = int(90 * (1 - y / nh) ** 1.6)
        for x in range(nw):
            pixels[x, y] = alpha
    r, g, b, a = refl.split()
    a = ImageChops_multiply(a, fade)
    refl = Image.merge("RGBA", (r, g, b, a))
    canvas.paste(refl, (ox, oy + nh - 2), refl)
    return canvas.convert("RGB")


def ImageChops_multiply(a: Image.Image, b: Image.Image) -> Image.Image:
    from PIL import ImageChops

    return ImageChops.multiply(a, b)


def write_cards(slug: str) -> list[Path]:
    _folder, _frames, hero = source_frames(slug)
    im = to_srgb(Image.open(hero))
    aspect = 190 / 110
    target = (692, 400)
    white = crop_aspect(im, aspect).resize(target, Image.Resampling.LANCZOS)
    white = add_ground_shadow(white)
    dark = dark_composite(im, target)

    CARD_OUT.mkdir(parents=True, exist_ok=True)
    a_path = CARD_OUT / "beyaz-studyo-kirpim.jpg"
    b_path = CARD_OUT / "koyu-kompozit.jpg"
    white.save(a_path, "JPEG", quality=86, optimize=True)
    dark.save(b_path, "JPEG", quality=86, optimize=True)

    existing = PRODUCTS / "miknatisli-anahtar-ucu" / "miknatisli-anahtar-ucu-kart.jpg"
    if not existing.exists():
        existing = PRODUCTS / "hss-matkap-ucu" / "hss-matkap-ucu-kart.jpg"
    old = Image.open(existing).convert("RGB").resize(target, Image.Resampling.LANCZOS)
    gap = 16
    label_h = 36
    sheet = Image.new("RGB", (target[0] * 3 + gap * 2, target[1] + label_h), (18, 18, 18))
    for i, panel in enumerate((old, white, dark)):
        sheet.paste(panel, (i * (target[0] + gap), label_h))
    draw = ImageDraw.Draw(sheet)
    labels = ("Mevcut kart", "A  beyaz kirpim", "B  koyu kompozit")
    for i, label in enumerate(labels):
        draw.text((i * (target[0] + gap) + 12, 8), label, fill=(230, 230, 230))
    cmp_path = CARD_OUT / "karsilastirma.jpg"
    sheet.save(cmp_path, "JPEG", quality=86, optimize=True)
    try:
        import rembg  # noqa: F401

        print("rembg var; bu pilot eşik maskesi kullandı (beyaz stüdyo).")
    except ImportError:
        print("rembg yok; maske beyaz eşik ile üretildi.")
    for path in (a_path, b_path, cmp_path):
        print(f"CARD {path.relative_to(ROOT)} {path.stat().st_size}")
    return [a_path, b_path, cmp_path]


def images_block(images: list[dict]) -> str:
    lines = ['"images": [']
    for i, img in enumerate(images):
        comma = "," if i < len(images) - 1 else ""
        lines.append("        {")
        lines.append(f'          "src": {json.dumps(img["src"], ensure_ascii=False)},')
        lines.append(f'          "alt": {json.dumps(img["alt"], ensure_ascii=False)}')
        lines.append("        }" + comma)
    lines.append("      ]")
    return "\n".join(lines)


def patch_catalog_file(path: Path, slug: str, images: list[dict]) -> None:
    text = path.read_text(encoding="utf-8")
    idx = text.find(f'"slug": "{slug}"')
    if idx < 0:
        raise SystemExit(f"{path.name}: slug yok {slug}")
    sub = text[idx:]
    match = re.search(r'"images"\s*:\s*\[.*?\]', sub, re.S)
    if not match:
        raise SystemExit(f"{path.name}: images dizisi yok {slug}")
    start = idx + match.start()
    end = idx + match.end()
    path.write_text(text[:start] + images_block(images) + text[end:], encoding="utf-8")
    print(f"CATALOG {path.relative_to(ROOT)} images güncellendi ({len(images)})")


def ingest(slug: str, dry_run: bool, replace_legacy: bool, write_catalog: bool) -> dict:
    _folder, frames, hero = source_frames(slug)
    dest = PRODUCTS / slug
    legacy = legacy_files(dest)
    before = sum(p.stat().st_size for p in dest.iterdir() if p.is_file()) if dest.exists() else 0

    print(f"SLUG {slug}")
    print(f"HERO {hero.name}")
    print(f"FRAMES {len(frames)}")
    deleted = [f"{path.relative_to(ROOT).as_posix()} {path.stat().st_size}" for path in legacy]
    print("SILINECEK")
    for line in deleted:
        print(f"  {line}")
    if dry_run:
        print("DRY-RUN yazılmadı")
        return {"slug": slug, "frames": len(frames), "legacy": len(legacy), "before": before}

    if replace_legacy:
        for path in legacy:
            path.unlink()

    written: list[Path] = []
    catalog_images: list[dict] = []
    name = PRODUCT_NAME.get(slug, slug)
    for i, frame in enumerate(frames, start=1):
        nn = f"{i:02d}"
        with Image.open(frame) as opened:
            rgb = to_srgb(opened)
        full = fit_long_edge(rgb, FULL_EDGE)
        thumb = fit_long_edge(rgb, THUMB_EDGE)
        stem_full = dest / f"{slug}-galeri-{nn}"
        stem_thumb = dest / f"{slug}-galeri-{nn}-thumb"
        written += save_set(full, stem_full, {"avif": 50, "webp": 75, "jpg": 82})
        written += save_set(thumb, stem_thumb, {"avif": 70, "webp": 75, "jpg": 80})
        catalog_images.append(
            {
                "src": f"assets/images/products/{slug}/{slug}-galeri-{nn}.jpg",
                "alt": f"{name} - galeri {nn}",
            }
        )
        print(f"  {nn} {frame.name} -> {stem_full.name}.*", flush=True)

    with Image.open(hero) as opened:
        hero_rgb = to_srgb(opened)
    main = fit_long_edge(hero_rgb, HERO_EDGE)
    main_path = dest / f"{slug}.webp"
    main.save(main_path, "WEBP", quality=75, method=6)
    written.append(main_path)

    share = contain_on_canvas(hero_rgb, SHARE_SIZE, BG)
    for suffix in ("-cover.jpg", "-og.jpg", "-wa.jpg"):
        path = dest / f"{slug}{suffix}"
        share.save(path, "JPEG", quality=86, optimize=True, progressive=True)
        written.append(path)

    menu = fit_long_edge(hero_rgb, MENU_EDGE)
    menu_path = dest / f"{slug}-menu-thumb.webp"
    menu.save(menu_path, "WEBP", quality=75, method=6)
    written.append(menu_path)

    after = sum(p.stat().st_size for p in dest.iterdir() if p.is_file())
    print(f"SIZE before={before} after={after} written={len(written)}")

    if write_catalog:
        patch_catalog_file(CATALOG_JSON, slug, catalog_images)
        patch_catalog_file(CATALOG_JS, slug, catalog_images)
        CATALOG_JS_ROOT.write_text(CATALOG_JS.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"ROOT {CATALOG_JS_ROOT.name} kopyalandı")

    return {
        "slug": slug,
        "frames": len(frames),
        "hero": hero.name,
        "deleted": deleted if replace_legacy else [],
        "written": len(written),
        "before": before,
        "after": after,
        "catalog": write_catalog,
        "images": [img["src"] for img in catalog_images],
    }


def frame_by_name(slug: str, filename: str) -> Path:
    folder = SOURCE / FOLDER_BY_SLUG[slug]
    path = folder / filename
    if not path.is_file():
        raise SystemExit(f"Kare yok: {path}")
    return path


def white_halo_fraction(im: Image.Image) -> float:
    rgba = im.convert("RGBA")
    edge = 0
    white = 0
    for r, g, b, a in rgba.getdata():
        if 12 < a < 248:
            edge += 1
            if r > 220 and g > 220 and b > 220:
                white += 1
    if edge < 30:
        return 0.0
    return white / edge


def dark_feather(im: Image.Image, radius: int = 2) -> Image.Image:
    """Tel kenarındaki beyaz haleyi 1–2 px içeri çekip zemine yaklaştır."""
    rgba = im.convert("RGBA")
    r, g, b, a = rgba.split()
    shrunk = a.filter(ImageFilter.MinFilter(radius * 2 + 1))
    outside = a.point(lambda p: 255 if p < 24 else 0)
    grown = outside.filter(ImageFilter.MaxFilter(radius * 2 + 1))
    rgb = Image.merge("RGB", (r, g, b))
    luma = ImageOps.grayscale(rgb)
    bright = luma.point(lambda p: 255 if p > 170 else 0)
    from PIL import ImageChops

    band = ImageChops.multiply(bright, grown)
    dark = Image.new("RGB", rgba.size, BG)
    rgb = Image.composite(dark, rgb, band)
    return Image.merge("RGBA", (*rgb.split(), shrunk))


def rembg_session():
    try:
        from rembg import new_session
    except ImportError as exc:
        raise SystemExit("rembg kurulu değil. Kartlar üretilmedi.") from exc
    return new_session("u2net")


def cutout(im: Image.Image, session) -> Image.Image:
    from rembg import remove

    out = remove(im, session=session)
    if not isinstance(out, Image.Image):
        out = Image.open(BytesIO(out))
    return out.convert("RGBA")


def composite_rgba(rgba: Image.Image, size: tuple[int, int]) -> Image.Image:
    alpha = rgba.split()[-1]
    box = alpha.point(lambda p: 255 if p > 16 else 0).getbbox() or (0, 0, rgba.width, rgba.height)
    subject = rgba.crop(box)
    tw, th = size
    scale = min((tw * 0.86) / subject.width, (th * 0.62) / subject.height)
    nw = max(1, int(round(subject.width * scale)))
    nh = max(1, int(round(subject.height * scale)))
    subject = subject.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, BG + (255,))
    ox = (tw - nw) // 2
    oy = int(th * 0.42) - nh // 2

    shadow = Image.new("L", size, 0)
    draw = ImageDraw.Draw(shadow)
    draw.ellipse((ox + int(nw * 0.12), oy + nh - 6, ox + int(nw * 0.88), oy + nh + 18), fill=160)
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    shade = Image.new("RGBA", size, (0, 0, 0, 0))
    shade.putalpha(shadow.point(lambda p: int(p * 0.65)))
    canvas = Image.alpha_composite(canvas, shade)

    canvas.paste(subject, (ox, oy), subject)
    refl = ImageOps.flip(subject)
    fade = Image.new("L", (nw, nh), 0)
    pixels = fade.load()
    for y in range(nh):
        alpha_y = int(80 * (1 - y / nh) ** 1.6)
        for x in range(nw):
            pixels[x, y] = alpha_y
    rr, gg, bb, aa = refl.split()
    aa = ImageChops_multiply(aa, fade)
    refl = Image.merge("RGBA", (rr, gg, bb, aa))
    canvas.paste(refl, (ox, oy + nh - 2), refl)
    return canvas.convert("RGB")


def write_product_cards(slugs: tuple[str, ...] | None = None) -> list[dict]:
    session = rembg_session()
    CARD_PREVIEW.mkdir(parents=True, exist_ok=True)
    rows = []
    for slug in slugs or NEW_SLUGS:
        filename = CARD_FILE.get(slug) or HERO_FILE[slug]
        src = frame_by_name(slug, filename)
        with Image.open(src) as opened:
            rgb = to_srgb(opened)
        rgba = cutout(rgb, session)
        halo_before = white_halo_fraction(rgba)
        feathered = False
        if slug in WIRE_SLUGS:
            rgba = dark_feather(rgba, radius=2)
            feathered = True
        halo_after = white_halo_fraction(rgba) if feathered else halo_before
        large = composite_rgba(rgba, CARD_LARGE)
        small = large.resize(CARD_SMALL, Image.Resampling.LANCZOS)
        dest = PRODUCTS / slug
        dest.mkdir(parents=True, exist_ok=True)
        kart = dest / f"{slug}-kart.jpg"
        webp = dest / f"{slug}-kart-card.webp"
        avif = dest / f"{slug}-kart-card.avif"
        small.save(kart, "JPEG", quality=82, optimize=True, progressive=True)
        large.save(webp, "WEBP", quality=75, method=6)
        large.save(avif, "AVIF", quality=50)
        preview = CARD_PREVIEW / f"{slug}.jpg"
        large.save(preview, "JPEG", quality=86, optimize=True)
        row = {
            "slug": slug,
            "source": filename,
            "halo_before": round(halo_before, 3),
            "halo_after": round(halo_after, 3),
            "feather": feathered,
            "kart": kart.stat().st_size,
            "webp": webp.stat().st_size,
            "avif": avif.stat().st_size,
            "preview": preview.relative_to(ROOT).as_posix(),
        }
        rows.append(row)
        print(
            f"CARD {slug} {filename} halo {halo_before:.2f}->{halo_after:.2f} feather={feathered}",
            flush=True,
        )
    return rows


def gallery_images_for(slug: str) -> list[dict]:
    dest = PRODUCTS / slug
    files = sorted(dest.glob(f"{slug}-galeri-*.jpg"))
    files = [p for p in files if "-thumb" not in p.name]
    name = PRODUCT_NAME.get(slug, slug)
    images = []
    for path in files:
        nn = path.stem.rsplit("-", 1)[-1]
        images.append(
            {
                "src": f"assets/images/products/{slug}/{path.name}",
                "alt": f"{name} - galeri {nn}",
            }
        )
    if not images:
        raise SystemExit(f"Galeri yok: {slug}")
    return images


def link_siblings() -> list[dict]:
    rows = []
    for dest_slug, source_slug in SIBLINGS:
        images = gallery_images_for(source_slug)
        name = PRODUCT_NAME[dest_slug]
        for img in images:
            nn = img["src"].rsplit("-", 1)[-1].split(".")[0]
            img["alt"] = f"{name} - galeri {nn}"
        patch_catalog_file(CATALOG_JSON, dest_slug, images)
        patch_catalog_file(CATALOG_JS, dest_slug, images)
        src_dir = PRODUCTS / source_slug
        dst_dir = PRODUCTS / dest_slug
        dst_dir.mkdir(parents=True, exist_ok=True)
        removed = []
        for path in legacy_files(dst_dir):
            removed.append(f"{path.relative_to(ROOT).as_posix()} {path.stat().st_size}")
            path.unlink()
        copied = []
        for suffix in SLUG_KEYED_SUFFIXES:
            src = src_dir / f"{source_slug}{suffix}"
            dst = dst_dir / f"{dest_slug}{suffix}"
            if not src.is_file():
                raise SystemExit(f"Kardeş kopyası için kaynak yok: {src}")
            dst.write_bytes(src.read_bytes())
            copied.append(dst.relative_to(ROOT).as_posix())
        rows.append(
            {
                "dest": dest_slug,
                "source": source_slug,
                "images": len(images),
                "copied": copied,
                "removed": removed,
            }
        )
        print(f"SIBLING {dest_slug} <- {source_slug} images={len(images)} copy={len(copied)}", flush=True)
    CATALOG_JS_ROOT.write_text(CATALOG_JS.read_text(encoding="utf-8"), encoding="utf-8")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Kasım 2026 fotoğraf aktarımı")
    parser.add_argument("--only", help="Tek slug işle")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--replace-legacy", action="store_true", help="Kart dışı eski dosyaları sil")
    parser.add_argument("--write-catalog", action="store_true", help="products.json ve products-data.js images[] güncelle")
    parser.add_argument("--cards", help="Kart örneklerini scripts/raporlar/a1a-kart altına yaz")
    parser.add_argument("--remaining", action="store_true", help="Pilot dışı 12 klasör, kardeş bağlama ve yeni kartlar")
    parser.add_argument("--product-cards", action="store_true", help="Dört yeni ürünün koyu kartını üret")
    parser.add_argument("--link-siblings", action="store_true", help="Kardeş images[] ve slug dosya kopyası")
    args = parser.parse_args()

    if args.cards:
        write_cards(args.cards)
        return 0
    if args.product_cards:
        write_product_cards()
        return 0
    if args.link_siblings:
        link_siblings()
        return 0
    if args.remaining:
        import json as jsonlib

        summary = {"products": [], "cards": [], "siblings": []}
        for slug in EXISTING_A1B:
            summary["products"].append(ingest(slug, args.dry_run, True, not args.dry_run))
        for slug in NEW_SLUGS:
            summary["products"].append(ingest(slug, args.dry_run, True, False))
        if not args.dry_run:
            summary["cards"] = write_product_cards()
            summary["siblings"] = link_siblings()
            log = ROOT / "scripts" / "raporlar" / "a1b-run.json"
            log.write_text(jsonlib.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"LOG {log.relative_to(ROOT)}", flush=True)
        return 0
    if not args.only:
        print("--only <slug> gerekli", file=sys.stderr)
        return 2
    if args.only not in FOLDER_BY_SLUG:
        print(f"Bilinmeyen slug: {args.only}", file=sys.stderr)
        return 2
    ingest(args.only, args.dry_run, args.replace_legacy, args.write_catalog)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
