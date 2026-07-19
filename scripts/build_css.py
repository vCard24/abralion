#!/usr/bin/env python3
"""Merge site CSS layers into bundle.min.css and bump cache-bust query params."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from asset_cache_version import bump_versioned_assets_in_html, content_hash

CSS_DIR = ROOT / "assets" / "css"
OUT = CSS_DIR / "bundle.min.css"
ICONS = ROOT / "assets" / "js" / "icons.js"
HOME = ROOT / "index.html"
HOME_CSS_BLOCK = re.compile(
    r"\s*<!-- HOME_CSS_START -->.*?<!-- HOME_CSS_END -->\s*",
    re.S,
)
HOME_BUNDLE_LINK = re.compile(
    r'\s*<link rel="stylesheet" href="assets/css/bundle\.min\.css\?v=[a-f0-9]+">\s*'
)

# Load order must match historical <link> order on every page.
SOURCES = (
    "tailwind.css",
    "main.css",
    "components.css",
    "responsive.css",
    "site-extra.css",
)


def minify_css(css: str) -> str:
    """Conservative minify: strip comments and collapse whitespace."""
    css = re.sub(r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/", "", css)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>+~])\s*", r"\1", css)
    return css.strip()


def inline_home_css(css: str) -> None:
    """Make homepage first paint independent from a separate CDN CSS request."""
    html = HOME.read_text(encoding="utf-8")
    block = (
        "\n  <!-- HOME_CSS_START -->\n"
        f'  <style id="home-styles">{css}</style>\n'
        "  <!-- HOME_CSS_END -->\n"
    )
    if HOME_CSS_BLOCK.search(html):
        updated = HOME_CSS_BLOCK.sub(lambda _match: block, html, count=1)
    elif HOME_BUNDLE_LINK.search(html):
        updated = HOME_BUNDLE_LINK.sub(lambda _match: block, html, count=1)
    else:
        raise RuntimeError("Homepage bundle stylesheet marker/link not found")
    HOME.write_text(updated, encoding="utf-8")


def build() -> dict[str, str]:
    parts: list[str] = []
    sizes: list[tuple[str, int]] = []

    for name in SOURCES:
        path = CSS_DIR / name
        if not path.is_file():
            raise FileNotFoundError(path)
        raw = path.read_text(encoding="utf-8")
        sizes.append((name, len(raw.encode("utf-8"))))
        parts.append(f"/* --- {name} --- */\n{raw}")

    combined = "\n".join(parts)
    minified = minify_css(combined)
    OUT.write_text(minified, encoding="utf-8")
    inline_home_css(minified)

    versions = bump_versioned_assets_in_html()

    bundle_v = versions.get("bundle.min.css") or content_hash(OUT)
    icons_v = versions.get("icons.js") or (content_hash(ICONS) if ICONS.is_file() else "—")

    raw_kb = sum(n for _, n in sizes) / 1024
    out_kb = OUT.stat().st_size / 1024
    print(f"bundle.min.css ?v={bundle_v}")
    print(f"icons.js ?v={icons_v}")
    print(f"Wrote {OUT.relative_to(ROOT)} ({out_kb:.1f} KB minified)")
    print(f"Sources total: {raw_kb:.1f} KB pre-minify")
    for name, nbytes in sizes:
        print(f"  {name}: {nbytes / 1024:.1f} KB")
    print(f"Updated HTML cache keys: {len(versions)} assets")
    return versions


if __name__ == "__main__":
    build()
