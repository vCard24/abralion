# -*- coding: utf-8 -*-
"""Her urun klasorundeki tum gorselleri (kart haric) products-data.js images[] dizisine yazar."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "images" / "products"
CATALOG_PATH = ROOT / "assets" / "js" / "products-data.js"
ROOT_CATALOG = ROOT / "products-data.js"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
KART_SUFFIXES = ("-kart.jpg", "-kart.png", "-kart.jpeg", "-kart.webp")


def load_catalog():
    raw = CATALOG_PATH.read_text(encoding="utf-8")
    match = re.search(r"window\.ABRALION_CATALOG\s*=\s*(\{.*\})\s*;?\s*$", raw, re.S)
    return json.loads(match.group(1)), raw


def save_catalog(data, template_raw):
    body = json.dumps(data, ensure_ascii=False, indent=2)
    new_raw = re.sub(
        r"window\.ABRALION_CATALOG\s*=\s*\{.*\}\s*;?\s*$",
        f"window.ABRALION_CATALOG = {body};",
        template_raw,
        flags=re.S,
    )
    CATALOG_PATH.write_text(new_raw, encoding="utf-8")
    if ROOT_CATALOG.exists():
        ROOT_CATALOG.write_text(new_raw, encoding="utf-8")


def is_kart_file(name: str) -> bool:
    lower = name.lower()
    return any(lower.endswith(s) for s in KART_SUFFIXES)


def sort_key(name: str, slug: str) -> tuple:
    lower = name.lower()
    stem = Path(name).stem.lower()
    slug_l = slug.lower()

    def rank(*hints):
        for i, h in enumerate(hints):
            if h in lower or h in stem:
                return i
        return 99

    # Galeri sirasi: ana/genel -> etiket/kutu/detay -> kullanim -> varyant/olcu -> diger
    primary = rank(
        f"{slug_l}-ana",
        f"{slug_l}.webp",
        "-ana.",
        "-genel.",
        f"{slug_l}-",
        "ana",
        "genel",
    )
    secondary = rank("-etiket.", "-kutu", "-detay", "-serit", "-display", "-bas", "-ust")
    tertiary = rank("-kullanim", "-varyant", "-varyasyon", "x", "-125", "-350", "-400")
    return (primary, secondary, tertiary, lower)


def human_alt(product_name: str, filename: str) -> str:
    stem = Path(filename).stem
    # Dosya adindan slug on ekini kirp, okunabilir yap
    label = stem.replace("-", " ").replace("_", " ")
    return f"{product_name} - {label}"


def gallery_files(slug: str) -> list[str]:
    folder = IMG / slug
    if not folder.is_dir():
        return []
    files = [
        f.name
        for f in folder.iterdir()
        if f.is_file()
        and f.suffix.lower() in IMAGE_EXTS
        and f.name != ".gitkeep"
        and not is_kart_file(f.name)
    ]
    files.sort(key=lambda n: sort_key(n, slug))
    return files


def sync_images():
    data, raw = load_catalog()
    updated = 0
    empty = []
    for product in data["products"]:
        slug = product["slug"]
        names = gallery_files(slug)
        if not names:
            empty.append(slug)
            continue
        product["images"] = [
            {
                "src": f"assets/images/products/{slug}/{name}",
                "alt": human_alt(product.get("name", slug), name),
            }
            for name in names
        ]
        updated += 1
    save_catalog(data, raw)
    print(f"Guncellendi: {updated} urun")
    if empty:
        print("Gorsel yok:", ", ".join(empty))
    return updated


def main():
    sync_images()
    subprocess.check_call(
        ["python", str(ROOT / "scripts" / "generate-product-pages.py")],
        cwd=ROOT,
    )


if __name__ == "__main__":
    main()
