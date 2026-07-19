#!/usr/bin/env python3
"""Keep layout and font stylesheets deterministic across generated HTML pages."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {"node_modules", ".git"}

BUNDLE_ASYNC = re.compile(
    r'(?P<indent>[ \t]*)<link rel="stylesheet" '
    r'href="(?P<href>(?:\.\./)?assets/css/bundle\.min\.css\?v=[a-f0-9]+)" '
    r'media="print" onload="this\.media=\'all\'">\s*'
    r'<noscript><link rel="stylesheet" href="(?P=href)"></noscript>',
)
FONTS_ASYNC = re.compile(
    r'(?P<indent>[ \t]*)<link rel="stylesheet" '
    r'href="(?P<href>(?:\.\./)?assets/css/fonts\.css\?v=[a-f0-9]+)" '
    r'media="print" onload="this\.media=\'all\'">\s*'
    r'<noscript>\s*<link rel="stylesheet" href="(?P=href)">\s*</noscript>',
)


def normalize(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")

    def replace(match: re.Match[str]) -> str:
        return f'{match.group("indent")}<link rel="stylesheet" href="{match.group("href")}">'

    updated = BUNDLE_ASYNC.sub(replace, text)
    updated = FONTS_ASYNC.sub(replace, updated)
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    changed = []
    for path in ROOT.rglob("*.html"):
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if normalize(path):
            changed.append(path.relative_to(ROOT).as_posix())
    print(f"Normalized stylesheet loading in {len(changed)} HTML files")


if __name__ == "__main__":
    main()
