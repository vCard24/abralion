#!/usr/bin/env python3
"""Async bundle CSS + Inter/Montserrat-only fonts on all HTML pages."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE_VERSION = "20260525"
FONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Inter:wght@400;500;700&family=Montserrat:wght@600;700&display=swap"
)

# Remove stale CSS preloads (legacy 7-file stack).
STALE_PRELOADS = re.compile(
    r'\s*<link rel="preload" href="[^"]*assets/css/(?:tailwind|noir-migration|dark-theme)\.css[^"]*" as="style">\s*',
    re.IGNORECASE,
)

BLOCKING_BUNDLE = re.compile(
    r'\s*<link rel="stylesheet" href="([^"]*assets/css/bundle\.min\.css\?v=[^"]+)">\s*',
    re.IGNORECASE,
)

MATERIAL_BLOCK = re.compile(
    r"\s*<link rel=\"(?:preload|stylesheet)\" href=\"https://fonts\.googleapis\.com/css2\?"
    r"family=Material\+Symbols[^\"]+\"[^>]*>\s*"
    r"(?:<noscript><link rel=\"stylesheet\" href=\"https://fonts\.googleapis\.com/css2\?"
    r"family=Material\+Symbols[^\"]+\"></noscript>\s*)?",
    re.IGNORECASE,
)

OLD_FONTS = re.compile(
    r"https://fonts\.googleapis\.com/css2\?family=Inter[^\"]+JetBrains[^\"]+",
    re.IGNORECASE,
)


def asset_prefix(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("urun/") or rel.startswith("scripts/templates/"):
        return "../"
    return ""


def async_bundle_block(prefix: str) -> str:
    href = f"{prefix}assets/css/bundle.min.css?v={BUNDLE_VERSION}"
    return (
        f'  <link rel="stylesheet" href="{href}" media="print" onload="this.media=\'all\'">\n'
        f'  <noscript><link rel="stylesheet" href="{href}"></noscript>\n'
    )


def async_fonts_block() -> str:
    return (
        '  <link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        f'  <link rel="stylesheet" href="{FONTS_URL}" media="print" onload="this.media=\'all\'">\n'
        f'  <noscript><link rel="stylesheet" href="{FONTS_URL}"></noscript>\n'
    )


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text
    prefix = asset_prefix(path)

    text = STALE_PRELOADS.sub("\n", text)
    text = MATERIAL_BLOCK.sub("\n", text)

    if BLOCKING_BUNDLE.search(text):
        text = BLOCKING_BUNDLE.sub("\n" + async_bundle_block(prefix), text, count=1)
    elif "bundle.min.css" not in text:
        text = text.replace("<link rel=\"icon\"", async_bundle_block(prefix) + "  <link rel=\"icon\"", 1)

    # Normalize fonts block
    text = re.sub(
        r'\s*<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*'
        r'<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\s*'
        r'(?:<link rel="(?:preload|stylesheet)" href="https://fonts\.googleapis\.com/css2\?[^"]+"[^>]*>\s*'
        r'<noscript><link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]+"></noscript>\s*)+',
        "\n" + async_fonts_block(),
        text,
        count=1,
    )
    text = OLD_FONTS.sub(FONTS_URL.split("?")[1].replace("family=", "family="), text)
    # Fix any remaining JetBrains URLs inline
    text = text.replace(
        "family=Inter:wght@400;500;700&family=JetBrains+Mono:wght@500&family=Montserrat:wght@600;700",
        "family=Inter:wght@400;500;700&family=Montserrat:wght@600;700",
    )
    text = re.sub(r"\n{3,}", "\n\n", text)

    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = []
    for path in sorted(ROOT.rglob("*.html")):
        if "node_modules" in path.parts:
            continue
        if patch_file(path):
            changed.append(str(path.relative_to(ROOT)))
    print(f"Updated {len(changed)} HTML files")


if __name__ == "__main__":
    main()
