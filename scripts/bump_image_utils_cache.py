#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAT = re.compile(r"product-image-utils\.js\?v=[^\"']+")
REP = "product-image-utils.js?v=20260708"

def main() -> None:
    n = 0
    for path in ROOT.rglob("*.html"):
        if "node_modules" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        new_text = PAT.sub(REP, text)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            n += 1
    print(f"Updated {n} files")

if __name__ == "__main__":
    main()
