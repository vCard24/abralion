# -*- coding: utf-8 -*-
"""24 urun detay HTML sayfasi uretir (Precision Industrial Noir sablon)."""
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SITE_ORIGIN = "https://abralion.com"
TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "product-detail-noir.html"


def esc(s):
    return (s or "").replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def product_og_image(product):
    images = product.get("images") or []
    if images and images[0].get("src"):
        src = images[0]["src"].lstrip("/")
        return f"{SITE_ORIGIN}/{src}"
    slug = product["slug"]
    return f"{SITE_ORIGIN}/assets/images/products/{slug}/{slug}-kart.jpg"


def product_og_image_alt(product):
    images = product.get("images") or []
    if images and images[0].get("alt"):
        return esc(images[0]["alt"])
    return esc(product.get("name", ""))


def main():
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    with open(ROOT / "data/products.json", encoding="utf-8") as f:
        data = json.load(f)
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
        }.items():
            html = html.replace("{" + key + "}", val)
        path = out_dir / f"{slug}.html"
        path.write_text(html, encoding="utf-8")
        count += 1
    print(f"OK: {count} sayfa -> urun/")


if __name__ == "__main__":
    main()
