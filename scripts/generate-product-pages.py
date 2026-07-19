# -*- coding: utf-8 -*-
"""ABRALION_CATALOG ürünleri için urun/*.html sayfaları üretir."""
import json
import re
from pathlib import Path
from urllib.parse import quote

from structured_data import inject, product_schema

ROOT = Path(__file__).resolve().parent.parent
SITE_ORIGIN = "https://abralion.com"
TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "product-detail-noir.html"
CATALOG_PATH = ROOT / "assets" / "js" / "products-data.js"


def esc(s):
    return (s or "").replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def load_catalog():
    raw = CATALOG_PATH.read_text(encoding="utf-8")
    match = re.search(r"window\.ABRALION_CATALOG\s*=\s*(\{.*\})\s*;?\s*$", raw, re.S)
    if not match:
        raise SystemExit("ABRALION_CATALOG bulunamadı")
    return json.loads(match.group(1))


def product_og_image(product):
    slug = product["slug"]
    images = product.get("images") or []
    if images and images[0].get("src"):
        src = images[0]["src"].lstrip("/")
        return f"{SITE_ORIGIN}/{src}"
    return f"{SITE_ORIGIN}/assets/images/products/{slug}/{slug}.webp"


def product_og_image_alt(product):
    images = product.get("images") or []
    if images and images[0].get("alt"):
        return esc(images[0]["alt"])
    return esc(product.get("name", ""))


def product_technical_catalog_href(product):
    catalog = product.get("technicalCatalog")
    if catalog:
        return f"../{catalog.lstrip('/')}"
    return "../dokumanlar.html"


def main():
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    data = load_catalog()
    out_dir = ROOT / "urun"
    out_dir.mkdir(exist_ok=True)

    count = 0
    for p in data["products"]:
        slug = p["slug"]
        canonical = f"{SITE_ORIGIN}/urun/{slug}.html"
        og_title = esc(f'{p["name"]} - Abralion')
        html = template
        for key, val in {
            "slug": slug,
            "name": esc(p["name"]),
            "konu": quote(p["name"], safe=""),
            "description": esc((p.get("description") or "")[:160]),
            "canonical": canonical,
            "og_title": og_title,
            "og_image": product_og_image(p),
            "og_image_alt": product_og_image_alt(p),
            "technical_catalog_href": product_technical_catalog_href(p),
        }.items():
            html = html.replace("{" + key + "}", val)
        html = inject(html, product_schema(p))
        (out_dir / f"{slug}.html").write_text(html, encoding="utf-8")
        count += 1
    print(f"OK: {count} sayfa -> urun/")


if __name__ == "__main__":
    main()
