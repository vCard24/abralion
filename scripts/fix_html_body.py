# -*- coding: utf-8 -*-
"""body etiketi ile sr-only arasına satır sonu ekler."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAT = re.compile(r'(<body[^>]*>)\s*<a href="#main-content"', re.IGNORECASE)

for path in ROOT.rglob("*.html"):
    text = path.read_text(encoding="utf-8")
    new = PAT.sub(r'\1\n  <a href="#main-content"', text)
    if new != text:
        path.write_text(new, encoding="utf-8")
        print(path.relative_to(ROOT))
