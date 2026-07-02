#!/usr/bin/env python3
"""Inject icons.js before other deferred scripts on all pages."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKER = "assets/js/icons.js"
SNIPPET_ROOT = '  <script defer src="assets/js/icons.js?v=20260525"></script>\n'
SNIPPET_URUN = '  <script defer src="../assets/js/icons.js?v=20260525"></script>\n'


def prefix_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("urun/"):
        return "../"
    return ""


def patch(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    snippet = SNIPPET_URUN if prefix_for(path) == "../" else SNIPPET_ROOT
  # Insert before first deferred script
    needle = '<script defer src="'
    idx = text.find(needle)
    if idx == -1:
        return False
    new_text = text[:idx] + snippet + text[idx:]
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    n = 0
    for path in sorted(ROOT.rglob("*.html")):
        if "node_modules" in path.parts:
            continue
        if patch(path):
            n += 1
    print(f"Injected icons.js into {n} HTML files")


if __name__ == "__main__":
    main()
