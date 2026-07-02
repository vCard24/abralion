#!/usr/bin/env python3
"""Replace material-symbols-outlined spans with inline SVG in HTML files."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from icon_paths import svg_for  # noqa: E402

SPAN_RE = re.compile(
    r'<span\s+class="([^"]*\bmaterial-symbols-outlined\b[^"]*)"'
    r'(?:\s+data-icon="([^"]+)")?[^>]*>([^<]*)</span>',
    re.IGNORECASE,
)


def clean_classes(raw: str) -> str:
    parts = []
    for part in raw.split():
        if part == "material-symbols-outlined":
            continue
        parts.append(part)
    return " ".join(parts).strip()


def replace_span(match: re.Match[str]) -> str:
    classes = clean_classes(match.group(1))
    name = (match.group(2) or match.group(3) or "").strip()
    if not name or name not in __import__("icon_paths", fromlist=["ICON_PATHS"]).ICON_PATHS:
        return match.group(0)
    return svg_for(name, classes)


def patch_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    new_text, n = SPAN_RE.subn(replace_span, text)
    if n:
        path.write_text(new_text, encoding="utf-8")
    return n


def main() -> None:
    total = 0
    for path in sorted(ROOT.rglob("*.html")):
        if "node_modules" in path.parts:
            continue
        n = patch_file(path)
        if n:
            print(f"{path.relative_to(ROOT)}: {n}")
            total += n
    print(f"Replaced {total} icon spans in HTML")


if __name__ == "__main__":
    main()
