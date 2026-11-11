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
BG = (0x0A, 0x0A, 0x0A)

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

# A0 kart önerileri. miknatisli için A0 kahraman seçmedi; ürün karesi DSC_8859.
HERO_FILE = {
    "canak-firca-sacakli": "DSC_9025-редакт.jpg",
    "miknatisli-anahtar-ucu": "DSC_8859-редакт.jpg",
}

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
    print("SILINECEK")
    for path in legacy:
        print(f"  {path.relative_to(ROOT)} {path.stat().st_size}")
    if dry_run:
        print("DRY-RUN yazılmadı")
        return {"slug": slug, "frames": len(frames), "legacy": len(legacy), "before": before}

    if replace_legacy:
        for path in legacy:
            path.unlink()

    written: list[Path] = []
    catalog_images: list[dict] = []
    name = "Mıknatıslı Anahtar Ucu (Manyetik Somun Adaptörü)"
    for i, frame in enumerate(frames, start=1):
        nn = f"{i:02d}"
        rgb = to_srgb(Image.open(frame))
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
        print(f"  {nn} {frame.name} -> {stem_full.name}.*")

    hero_rgb = to_srgb(Image.open(hero))
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
        "legacy": [str(p.relative_to(ROOT)) for p in legacy],
        "written": len(written),
        "before": before,
        "after": after,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Kasım 2026 fotoğraf aktarımı")
    parser.add_argument("--only", help="Tek slug işle")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--replace-legacy", action="store_true", help="Kart dışı eski dosyaları sil")
    parser.add_argument("--write-catalog", action="store_true", help="products.json ve products-data.js images[] güncelle")
    parser.add_argument("--cards", help="Kart örneklerini scripts/raporlar/a1a-kart altına yaz")
    args = parser.parse_args()

    if args.cards:
        write_cards(args.cards)
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
