# -*- coding: utf-8 -*-
"""sitemap.xml — katalogdaki 24 urun + statik sayfalar."""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "assets" / "js" / "products-data.js"
OUT = ROOT / "sitemap.xml"
BASE = "https://www.abralion.com"
TODAY = date.today().isoformat()

STATIC = [
    ("", "weekly", "1.0"),
    ("urunler.html", "weekly", "0.8"),
    ("dokumanlar.html", "monthly", "0.8"),
    ("hakkimizda.html", "monthly", "0.8"),
    ("iletisim.html", "monthly", "0.8"),
    ("karsilastir.html", "monthly", "0.8"),
]


def load_slugs():
    raw = CATALOG.read_text(encoding="utf-8")
    m = re.search(r"window\.ABRALION_CATALOG\s*=\s*(\{.*\})\s*;?\s*$", raw, re.S)
    data = json.loads(m.group(1))
    return sorted(p["slug"] for p in data["products"])


def url(loc, freq, priority):
    return f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>"""


def main():
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path, freq, pri in STATIC:
        loc = f"{BASE}/{path}" if path else f"{BASE}/"
        lines.append(url(loc, freq, pri))
    for slug in load_slugs():
        lines.append(url(f"{BASE}/urun/{slug}.html", "monthly", "0.7"))
    lines.append("</urlset>")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK: sitemap.xml ({len(load_slugs())} urun)")


if __name__ == "__main__":
    main()
