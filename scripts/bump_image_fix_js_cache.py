#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUMPS = {
    r"MegaMenu\.js\?v=[^\"']+": "MegaMenu.js?v=20260705",
    r"product-detail\.js\?v=[^\"']+": "product-detail.js?v=20260705",
    r"Header\.js\?v=[^\"']+": "Header.js?v=20260705",
}

def main() -> None:
    for path in ROOT.rglob("*.html"):
        if "node_modules" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        orig = text
        for pattern, rep in BUMPS.items():
            text = re.sub(pattern, rep, text)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            print(path.relative_to(ROOT))

if __name__ == "__main__":
    main()
