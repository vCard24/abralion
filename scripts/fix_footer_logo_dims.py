#!/usr/bin/env python3
"""Footer logo-beyaz.svg img öğelerine width/height ekler."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = 'class="footer-logo h-14 w-auto" data-logo>'
NEW = 'class="footer-logo h-14 w-auto" width="168" height="132" decoding="async" data-logo>'

count = 0
for path in ROOT.rglob("*.html"):
    text = path.read_text(encoding="utf-8")
    if OLD not in text:
        continue
    path.write_text(text.replace(OLD, NEW), encoding="utf-8", newline="\n")
    count += 1
    print(path.relative_to(ROOT))

print(f"\nGüncellenen dosya: {count}")
