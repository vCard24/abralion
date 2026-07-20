"""Align RU lang-switcher markup/CSS with Turkish side (TR | RU order)."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RU = ROOT / "ru"

SWITCHER_RE = re.compile(
    r'<div class="lang-switcher"[^>]*>[\s\S]*?</div>',
    re.MULTILINE,
)
TR_HREF_RE = re.compile(
    r'<a[^>]*href="(https://abralion\.com[^"]*)"[^>]*hreflang="tr"[^>]*>|'
    r'<a[^>]*hreflang="tr"[^>]*href="(https://abralion\.com[^"]*)"[^>]*>'
)

CSS_SOURCES = (
    "tailwind.css",
    "main.css",
    "components.css",
    "responsive.css",
    "site-extra.css",
)

LANG_CSS = """
.lang-switcher {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: inherit;
}

.lang-btn {
  padding: 3px 8px;
  border: 1px solid currentColor;
  border-radius: 3px;
  opacity: 0.6;
  text-decoration: none;
  color: inherit;
  transition: opacity 0.2s;
  line-height: 1.2;
}

.lang-btn--active {
  opacity: 1;
}

.lang-btn:hover {
  opacity: 1;
}
"""

HOME_CSS_BLOCK = re.compile(
    r"\s*<!-- HOME_CSS_START -->.*?<!-- HOME_CSS_END -->\s*",
    re.S,
)
BUNDLE_V_RE = re.compile(
    r'(href="(?:\.\./)?assets/css/bundle\.min\.css\?v=)[a-f0-9]+(")'
)


def minify_css(css: str) -> str:
    css = re.sub(r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/", "", css)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>+~])\s*", r"\1", css)
    return css.strip()


def sync_site_extra() -> None:
    path = RU / "assets" / "css" / "site-extra.css"
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r"\.lang-switcher\s*\{[\s\S]*?\.lang-btn:hover\s*\{[\s\S]*?\}\n?",
        LANG_CSS.strip() + "\n",
        text,
        count=1,
    )
    path.write_text(text, encoding="utf-8", newline="\n")


def rebuild_bundle() -> str:
    css_dir = RU / "assets" / "css"
    parts = [(css_dir / name).read_text(encoding="utf-8") for name in CSS_SOURCES]
    minified = minify_css("\n".join(parts))
    out = css_dir / "bundle.min.css"
    out.write_text(minified + "\n", encoding="utf-8", newline="\n")
    version = hashlib.sha256(minified.encode("utf-8")).hexdigest()[:8]

    home = RU / "index.html"
    html = home.read_text(encoding="utf-8")
    block = (
        "\n  <!-- HOME_CSS_START -->\n"
        f'  <style id="home-styles">{minified}</style>\n'
        "  <!-- HOME_CSS_END -->\n"
    )
    if HOME_CSS_BLOCK.search(html):
        home.write_text(
            HOME_CSS_BLOCK.sub(lambda _m: block, html, count=1),
            encoding="utf-8",
            newline="\n",
        )

    for path in RU.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        new_text, n = BUNDLE_V_RE.subn(rf"\g<1>{version}\2", text)
        if n:
            path.write_text(new_text, encoding="utf-8", newline="\n")

    return version


def switcher_html(tr_url: str) -> str:
    return (
        '<div class="lang-switcher" role="navigation" aria-label="Выбор языка">'
        f'<a href="{tr_url}" class="lang-btn" hreflang="tr" lang="tr" aria-label="Türkçe sürüm">TR</a>'
        '<span class="lang-btn lang-btn--active" aria-current="page">RU</span>'
        "</div>"
    )


def extract_tr_url(block: str, path: Path) -> str:
    m = TR_HREF_RE.search(block)
    if m:
        return m.group(1) or m.group(2)
    # Fallback from path
    rel = path.relative_to(RU).as_posix()
    if rel == "index.html":
        return "https://abralion.com/"
    if rel.startswith("urun/"):
        return f"https://abralion.com/{rel}"
    fallback = {
        "produkty.html": "https://abralion.com/urunler.html",
        "dokumenty.html": "https://abralion.com/dokumanlar.html",
        "o-kompanii.html": "https://abralion.com/hakkimizda.html",
        "kontakty.html": "https://abralion.com/iletisim.html",
        "zapros-tseny.html": "https://abralion.com/fiyat-teklifi.html",
        "sravnenie.html": "https://abralion.com/karsilastir.html",
        "politika-konfidentsialnosti.html": "https://abralion.com/gizlilik-politikasi.html",
        "usloviya-ispolzovaniya.html": "https://abralion.com/kullanim-kosullari.html",
        "zashhita-dannykh.html": "https://abralion.com/kvkk.html",
        "spasibo.html": "https://abralion.com/teklif-tesekkur.html",
    }
    return fallback.get(path.name, "https://abralion.com/")


def update_html() -> int:
    updated = 0
    for path in sorted(RU.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        match = SWITCHER_RE.search(text)
        if not match:
            continue
        tr_url = extract_tr_url(match.group(0), path)
        new_block = switcher_html(tr_url)
        if match.group(0) == new_block:
            continue
        path.write_text(text[: match.start()] + new_block + text[match.end() :], encoding="utf-8", newline="\n")
        updated += 1
        print(path.relative_to(ROOT))
    return updated


def main() -> None:
    sync_site_extra()
    n = update_html()
    version = rebuild_bundle()
    print(f"\nUpdated {n} HTML files; RU bundle.min.css ?v={version}")


if __name__ == "__main__":
    main()
