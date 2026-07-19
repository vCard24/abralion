#!/usr/bin/env python3
"""Replace Google Fonts with self-hosted fonts.css on all HTML pages."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from asset_cache_version import content_hash

FONTS_CSS = ROOT / "assets" / "css" / "fonts.css"
FONT_V = content_hash(FONTS_CSS) if FONTS_CSS.is_file() else "dev"

GOOGLE_BLOCK = re.compile(
    r"\s*<link rel=\"preconnect\" href=\"https://fonts\.googleapis\.com\">\s*"
    r"<link rel=\"preconnect\" href=\"https://fonts\.gstatic\.com\" crossorigin>\s*"
    r"<link rel=\"stylesheet\" href=\"https://fonts\.googleapis\.com/css2\?[^\"]+\" "
    r"media=\"print\" onload=\"this\.media='all'\">\s*"
    r"<noscript><link rel=\"stylesheet\" href=\"https://fonts\.googleapis\.com/css2\?[^\"]+\"></noscript>\s*",
    re.I,
)

GOOGLE_BLOCK_ALT = re.compile(
    r"\s*<link rel=\"preconnect\" href=\"https://fonts\.googleapis\.com\">\s*"
    r"<link rel=\"preconnect\" href=\"https://fonts\.gstatic\.com\" crossorigin>\s*"
    r"<link rel=\"stylesheet\" href=\"https://fonts\.googleapis\.com/css2\?[^\"]+\">\s*",
    re.I,
)

FONT_PRELOADS = re.compile(
    r'\s*<link rel="preload" href="(?:\.\./)?assets/fonts/[^"]+\.woff2" '
    r'as="font" type="font/woff2" crossorigin>\s*',
    re.I,
)


def asset_prefix(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("urun/") or rel.startswith("scripts/templates/"):
        return "../"
    return ""


def fonts_block(prefix: str, *, hero_preload: bool) -> str:
    lines = []
    if hero_preload:
        lines.extend(
            [
                f'  <link rel="preload" href="{prefix}assets/fonts/inter-tr-400-normal.woff2" as="font" type="font/woff2" crossorigin>',
                f'  <link rel="preload" href="{prefix}assets/fonts/montserrat-tr-700-normal.woff2" as="font" type="font/woff2" crossorigin>',
            ]
        )
    lines.append(
        f'  <link rel="stylesheet" href="{prefix}assets/css/fonts.css?v={FONT_V}">'
    )
    return "\n".join(lines) + "\n"


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text
    prefix = asset_prefix(path)
    is_home = path.name == "index.html" and path.parent == ROOT

    text = FONT_PRELOADS.sub("\n", text)
    replacement = fonts_block(prefix, hero_preload=is_home)

    if "fonts.css" in text:
        text = re.sub(
            rf'(?m)^[ \t]*<link rel="stylesheet" href="{re.escape(prefix)}assets/css/fonts\.css\?v=[a-f0-9]+">\s*$',
            replacement.rstrip(),
            text,
            count=1,
        )
    elif GOOGLE_BLOCK.search(text):
        text = GOOGLE_BLOCK.sub("\n" + replacement, text, count=1)
    elif GOOGLE_BLOCK_ALT.search(text):
        text = GOOGLE_BLOCK_ALT.sub("\n" + replacement, text, count=1)
    elif "fonts.css" not in text and "fonts.googleapis.com" in text:
        text = re.sub(
            r"\s*<link rel=\"preconnect\" href=\"https://fonts\.googleapis\.com\">.*?fonts\.googleapis\.com/css2\?[^\"]+\"[^>]*>\s*",
            "\n" + replacement,
            text,
            count=1,
            flags=re.S,
        )

    text = re.sub(r"\n{3,}", "\n\n", text)
    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    if not FONTS_CSS.is_file():
        raise SystemExit("Run scripts/download_local_fonts.py first")
    changed = []
    for path in sorted(ROOT.rglob("*.html")):
        if "node_modules" in path.parts or "scripts/includes" in path.parts:
            continue
        if patch_file(path):
            changed.append(path.relative_to(ROOT).as_posix())
    print(f"fonts.css ?v={FONT_V}")
    print(f"Updated {len(changed)} HTML files")


if __name__ == "__main__":
    main()
