# -*- coding: utf-8 -*-
"""duz-keski-sds-max.html referansindan product-detail-noir.html sablonunu gunceller."""
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "urun" / "duz-keski-sds-max.html"
TEMPLATE = ROOT / "scripts" / "templates" / "product-detail-noir.html"
PRODUCTS = ROOT / "data" / "products.json"


def main():
    ref = REF.read_text(encoding="utf-8")
    with open(PRODUCTS, encoding="utf-8") as f:
        products = {p["slug"]: p for p in json.load(f)["products"]}
    p = products["duz-keski-sds-max"]
    slug = p["slug"]
    name = p["name"]
    konu = quote(name, safe="")

    replacements = [
        (slug, "{slug}"),
        (name, "{name}"),
        (f"https://abralion.com/urun/{slug}.html", "{canonical}"),
        (f"{name} - Abralion", "{og_title}"),
        (konu, "{konu}"),
    ]

    # meta description (first 160 chars, escaped in HTML)
    desc_raw = (p.get("description") or "")[:160]
    desc_esc = desc_raw.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
    if desc_esc in ref:
        replacements.append((desc_esc, "{description}"))

    images = p.get("images") or []
    if images and images[0].get("src"):
        src = images[0]["src"].lstrip("/")
        og_image = f"https://abralion.com/{src}"
        replacements.append((og_image, "{og_image}"))
        alt = images[0].get("alt") or name
        alt_esc = alt.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
        if alt_esc in ref:
            replacements.append((alt_esc, "{og_image_alt}"))

    template = ref
    for old, new in replacements:
        template = template.replace(old, new)

    if "{slug}" not in template or "{name}" not in template:
        raise SystemExit("Placeholder substitution failed — check reference page content.")

    TEMPLATE.write_text(template, encoding="utf-8")
    print(f"Template synced from {REF.name}")


if __name__ == "__main__":
    main()
