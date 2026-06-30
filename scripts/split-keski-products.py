# -*- coding: utf-8 -*-
"""duz-keski ve sivri-uclu-keski-murc birlesik urunlerini 4 ayri urune bol."""
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "images" / "products"
CATALOG_PATH = ROOT / "assets" / "js" / "products-data.js"
ROOT_CATALOG = ROOT / "products-data.js"
URUN = ROOT / "urun"

REMOVE_SLUGS = {"duz-keski", "sivri-uclu-keski-murc"}
INSERT_SLUGS = [
    "duz-keski-sds-plus",
    "duz-keski-sds-max",
    "sivri-uclu-keski-murc-sds-plus",
    "sivri-uclu-keski-murc-sds-max",
]

NAME_OVERRIDES = {
    "sivri-uclu-keski-murc-sds-plus": "Sivri Uçlu Keski Murç SDS Plus",
    "sivri-uclu-keski-murc-sds-max": "Sivri Uçlu Keski Murç SDS Max",
}

IMAGE_SPLITS = {
    "duz-keski-sds-plus": [
        "duz-keski-sds-plus-ana.png",
        "duz-keski-sds-plus-kullanim.png",
        "duz-keski-sds-plus-kart.jpg",
    ],
    "duz-keski-sds-max": [
        "duz-keski-sds-max-ana.png",
        "duz-keski-sds-max-kullanim.png",
        "duz-keski-sds-max-kart.jpg",
    ],
    "sivri-uclu-keski-murc-sds-plus": [
        "sivri-uclu-keski-murc-sds-plus-ana.png",
        "sivri-uclu-keski-murc-sds-plus-kullanim.png",
        "sivri-uclu-keski-murc-sds-plus-kart.jpg",
    ],
    "sivri-uclu-keski-murc-sds-max": [
        "sivri-uclu-keski-murc-sds-max-ana.png",
        "sivri-uclu-keski-murc-sds-max-kullanim.png",
        "sivri-uclu-keski-murc-sds-max-kart.jpg",
    ],
}


def load_catalog(path):
    raw = path.read_text(encoding="utf-8")
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


def clean_variant(v):
    out = dict(v)
    if out.get("urun_kodu") is None:
        out.pop("urun_kodu", None)
    return out


def product_from_legacy(legacy):
    p = {
        "id": legacy["slug"],
        "slug": legacy["slug"],
        "name": NAME_OVERRIDES.get(legacy["slug"], legacy["name"]),
        "categoryId": "kirici-delici",
        "categoryName": "Kırıcı & Delici",
        "featured": legacy.get("featured", False),
        "description": legacy["description"],
        "features": legacy["features"],
        "applications": legacy["applications"],
        "images": legacy["images"],
        "variants": [clean_variant(v) for v in legacy["variants"]],
    }
    return p


def split_catalog():
    legacy_data = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
    legacy_by_slug = {p["slug"]: p for p in legacy_data["products"] if p["slug"] in INSERT_SLUGS}

    data, raw = load_catalog(CATALOG_PATH)
    products = [p for p in data["products"] if p["slug"] not in REMOVE_SLUGS]

    insert_at = next(
        (i for i, p in enumerate(products) if p["slug"] == "cam-seramik-matkap-ucu"),
        len(products),
    )
    new_products = [product_from_legacy(legacy_by_slug[s]) for s in INSERT_SLUGS]
    products[insert_at:insert_at] = new_products
    data["products"] = products
    save_catalog(data, raw)
    print(f"Katalog: {len(products)} urun ({len(REMOVE_SLUGS)} silindi, {len(new_products)} eklendi)")


def move_images():
    src_plus = IMG / "duz-keski"
    src_sivri = IMG / "sivri-uclu-keski-murc"
    sources = {
        "duz-keski-sds-plus": src_plus,
        "duz-keski-sds-max": src_plus,
        "sivri-uclu-keski-murc-sds-plus": src_sivri,
        "sivri-uclu-keski-murc-sds-max": src_sivri,
    }
    for slug, names in IMAGE_SPLITS.items():
        dst = IMG / slug
        dst.mkdir(parents=True, exist_ok=True)
        src_dir = sources[slug]
        for name in names:
            src = src_dir / name
            if src.is_file():
                shutil.move(str(src), str(dst / name))
    for old in ("duz-keski", "sivri-uclu-keski-murc"):
        old_dir = IMG / old
        if old_dir.is_dir():
            shutil.rmtree(old_dir)
    print("Gorsel klasorleri ayristirildi")


def remove_old_pages():
    for slug in REMOVE_SLUGS:
        path = URUN / f"{slug}.html"
        if path.is_file():
            path.unlink()
    print("Eski urun sayfalari silindi")


def regenerate_pages():
    subprocess.check_call(
        ["python", str(ROOT / "scripts" / "generate-product-pages.py")],
        cwd=ROOT,
    )


def main():
    split_catalog()
    move_images()
    remove_old_pages()
    regenerate_pages()


if __name__ == "__main__":
    main()
