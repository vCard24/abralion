# -*- coding: utf-8 -*-
"""sitemap.xml ve robots.txt uretir."""
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://www.abralion.com"
TODAY = date.today().isoformat()

STATIC_PAGES = [
    "",
    "index.html",
    "urunler.html",
    "dokumanlar.html",
    "hakkimizda.html",
    "iletisim.html",
    "karsilastir.html",
]


def loc(path: str) -> str:
    if not path or path == "index.html":
        return f"{BASE_URL}/"
    return f"{BASE_URL}/{path}"


def main() -> None:
    urls = []
    for page in STATIC_PAGES:
        urls.append((loc(page), "weekly" if page in ("", "index.html", "urunler.html") else "monthly", "1.0" if page in ("", "index.html") else "0.8"))

    for html_file in sorted((ROOT / "urun").glob("*.html")):
        urls.append((f"{BASE_URL}/urun/{html_file.name}", "monthly", "0.7"))

    for cat in [
        "kesici-taslama-flap-disk",
        "elmas-kesici",
        "uclar",
        "maket-bicaklari",
        "metreler",
    ]:
        urls.append((f"{BASE_URL}/urunler.html?kategori={cat}", "weekly", "0.75"))

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url, changefreq, priority in urls:
        lines.extend(
            [
                "  <url>",
                f"    <loc>{url}</loc>",
                f"    <lastmod>{TODAY}</lastmod>",
                f"    <changefreq>{changefreq}</changefreq>",
                f"    <priority>{priority}</priority>",
                "  </url>",
            ]
        )
    lines.append("</urlset>")

    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: https://www.abralion.com/sitemap.xml\n",
        encoding="utf-8",
    )
    print(f"sitemap.xml ({len(urls)} URLs), robots.txt")


if __name__ == "__main__":
    main()
