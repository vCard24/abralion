#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAT = re.compile(r"noir-migration\.css\?v=[^\"']+")
REP = "noir-migration.css?v=20260703"


def main() -> None:
    count = 0
    for path in ROOT.rglob("*.html"):
        if "node_modules" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        new_text = PAT.sub(REP, text)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            count += 1
            print(path.relative_to(ROOT))
    print(f"Updated {count} files")


if __name__ == "__main__":
    main()
