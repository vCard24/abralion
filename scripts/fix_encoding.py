#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UTF-8 metnin yanlışlıkla cp1252/latin-1 okunmasından kaynaklanan mojibake düzeltmesi."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOJIBAKE_MARKERS = ("Ã", "Ä", "Å", "â€", "â€™", "â€œ", "â€")


def line_needs_fix(line: str) -> bool:
    return any(m in line for m in MOJIBAKE_MARKERS)


def fix_line(line: str) -> str:
    if not line_needs_fix(line):
        return line
    for encoding in ("cp1252", "latin-1"):
        try:
            return line.encode(encoding).decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            continue
    return line


def fix_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    if not any(m in original for m in MOJIBAKE_MARKERS):
        return False
    lines = original.splitlines(keepends=True)
    fixed = "".join(fix_line(line) for line in lines)
    if fixed != original:
        path.write_text(fixed, encoding="utf-8", newline="")
        return True
    return False


def main():
    patterns = ("*.html",)
    changed = 0
    for pattern in patterns:
        for path in sorted(ROOT.rglob(pattern)):
            if fix_file(path):
                print(f"OK: {path.relative_to(ROOT)}")
                changed += 1
    print(f"\n{changed} dosya düzeltildi.")


if __name__ == "__main__":
    main()
