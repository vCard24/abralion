#!/usr/bin/env python3
"""Rebuild ru/assets/css/bundle.min.css and refresh ru/index.html HOME_CSS block."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RU = ROOT / "ru"
CSS_DIR = RU / "assets" / "css"
SOURCES = ("tailwind.css", "main.css", "components.css", "responsive.css", "site-extra.css")
HOME = RU / "index.html"
HOME_CSS = re.compile(r"\s*<!-- HOME_CSS_START -->.*?<!-- HOME_CSS_END -->\s*", re.S)
CRIT_MOBILE = re.compile(
    r"@media\(max-width:768px\)\{"
    r"\.home-hero-section,#home-hero\{min-height:520px\}"
    r"\.header-nav\{[^}]+\}"
    r"\.mobile-menu-toggle\{display:flex\}"
    r"\}",
    re.S,
)
CRIT_REPLACEMENT = (
    "@media(max-width:768px){"
    ".home-hero-section,#home-hero{min-height:520px}"
    ".header-nav{position:fixed;inset:0 auto auto 0;width:100%;height:100dvh;display:flex!important;"
    "flex-direction:column;opacity:0;visibility:hidden;pointer-events:none;z-index:1100}"
    ".mobile-menu-toggle{display:flex}"
    "header.header .header-container{gap:.75rem;padding-left:12px;padding-right:12px}"
    "header.header .header-brand-nav{flex:1 1 auto;min-width:0;overflow:hidden}"
    "header.header .header-logo{height:2.5rem;max-width:min(148px,42vw);width:auto;object-fit:contain}"
    "header.header .header-actions{gap:.5rem;flex-shrink:0}"
    "header.header .header-cta-btn{display:none!important}"
    "header.header .header-compare-link{display:none!important}"
    ".lang-switcher{gap:4px;font-size:12px;flex-shrink:0}"
    ".lang-btn{padding:2px 6px}"
    "}"
)


def minify(css: str) -> str:
    css = re.sub(r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/", "", css)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>+~])\s*", r"\1", css)
    return css.strip()


def main() -> None:
    parts = [(CSS_DIR / name).read_text(encoding="utf-8") for name in SOURCES]
    minified = minify("\n".join(parts))
    out = CSS_DIR / "bundle.min.css"
    out.write_text(minified + "\n", encoding="utf-8", newline="\n")
    ver = hashlib.sha256(minified.encode("utf-8")).hexdigest()[:8]

    html = HOME.read_text(encoding="utf-8")
    block = (
        "\n  <!-- HOME_CSS_START -->\n"
        f'  <style id="home-styles">{minified}</style>\n'
        "  <!-- HOME_CSS_END -->\n"
    )
    if HOME_CSS.search(html):
        html = HOME_CSS.sub(lambda _m: block, html, count=1)
    if CRIT_MOBILE.search(html):
        html = CRIT_MOBILE.sub(CRIT_REPLACEMENT, html, count=1)
        print("Patched RU critical mobile header CSS")
    else:
        # looser fallback: inject after .mobile-menu-toggle{display:flex}
        html2, n = re.subn(
            r"(@media\(max-width:768px\)\{[^\}]*\.mobile-menu-toggle\{display:flex\})",
            r"\1"
            "header.header .header-container{gap:.75rem;padding-left:12px;padding-right:12px}"
            "header.header .header-brand-nav{flex:1 1 auto;min-width:0;overflow:hidden}"
            "header.header .header-logo{height:2.5rem;max-width:min(148px,42vw);width:auto;object-fit:contain}"
            "header.header .header-actions{gap:.5rem;flex-shrink:0}"
            "header.header .header-cta-btn{display:none!important}"
            "header.header .header-compare-link{display:none!important}"
            ".lang-switcher{gap:4px;font-size:12px;flex-shrink:0}"
            ".lang-btn{padding:2px 6px}",
            html,
            count=1,
        )
        if n:
            html = html2
            print("Patched RU critical mobile header CSS (fallback)")
    HOME.write_text(html, encoding="utf-8", newline="\n")

    # bump bundle query on ru html only
    for path in RU.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        new, n = re.subn(
            r'(href="(?:\.\./)?assets/css/bundle\.min\.css\?v=)[a-f0-9]+(")',
            rf"\g<1>{ver}\2",
            text,
        )
        if n:
            path.write_text(new, encoding="utf-8", newline="\n")
    print(f"RU bundle.min.css ?v={ver} ({len(minified)} bytes)")


if __name__ == "__main__":
    main()
