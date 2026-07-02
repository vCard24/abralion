#!/usr/bin/env python3
"""Merge site CSS layers into bundle.min.css and bump cache-bust query params."""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS_DIR = ROOT / "assets" / "css"
OUT = CSS_DIR / "bundle.min.css"

# Load order must match historical <link> order on every page.
SOURCES = (
    "tailwind.css",
    "main.css",
    "components.css",
    "responsive.css",
    "site-extra.css",
)

HTML_GLOBS = ("*.html",)

# (regex on href/src value, replacement template with {v})
VERSIONED_ASSETS = (
    (
        re.compile(r"(bundle\.min\.css\?v=)[^\"'\s>]+"),
        r"\g<1>{v}",
    ),
    (
        re.compile(r"(icons\.js\?v=)[^\"'\s>]+"),
        r"\g<1>{v}",
    ),
    (
        re.compile(r"(bundle\.min\.css)(?!\?v=)"),
        r"\1?v={v}",
    ),
    (
        re.compile(r"(icons\.js)(?!\?v=)"),
        r"\1?v={v}",
    ),
)


def minify_css(css: str) -> str:
    """Conservative minify: strip comments and collapse whitespace."""
    css = re.sub(r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/", "", css)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>+~])\s*", r"\1", css)
    return css.strip()


def cache_version() -> str:
    return date.today().strftime("%Y%m%d")


def bump_versioned_assets(version: str) -> list[str]:
    """Update ?v=YYYYMMDD for versioned static assets across HTML."""
    changed: list[str] = []
    for path in sorted(ROOT.rglob("*.html")):
        if "node_modules" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        orig = text
        for pattern, repl_tpl in VERSIONED_ASSETS:
            text = pattern.sub(repl_tpl.format(v=version), text)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    return changed


def build() -> str:
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

    version = cache_version()
    bumped = bump_versioned_assets(version)

    raw_kb = sum(n for _, n in sizes) / 1024
    out_kb = OUT.stat().st_size / 1024
    print(f"Cache bust version: {version}")
    print(f"Wrote {OUT.relative_to(ROOT)} ({out_kb:.1f} KB minified)")
    print(f"Sources total: {raw_kb:.1f} KB pre-minify")
    for name, nbytes in sizes:
        print(f"  {name}: {nbytes / 1024:.1f} KB")
    print(f"Updated ?v= in {len(bumped)} HTML files")
    return version


if __name__ == "__main__":
    build()
