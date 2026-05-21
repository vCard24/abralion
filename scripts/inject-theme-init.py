# -*- coding: utf-8 -*-
"""Tüm HTML sayfalarına theme-init.js ekler (body hemen sonrası)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNIPPET_ROOT = '  <script src="assets/js/theme-init.js"></script>\n'
SNIPPET_URUN = '  <script src="../assets/js/theme-init.js"></script>\n'
MARKER = 'theme-init.js'


def inject(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    snippet = SNIPPET_URUN if path.parent.name == "urun" else SNIPPET_ROOT
    new_text, n = re.subn(
        r"(<body[^>]*>)\s*",
        r"\1\n" + snippet,
        text,
        count=1,
        flags=re.IGNORECASE,
    )
    if n:
        path.write_text(new_text, encoding="utf-8")
        print(f"OK: {path.relative_to(ROOT)}")
        return True
    print(f"SKIP: {path.relative_to(ROOT)}")
    return False


def main():
    files = sorted(ROOT.glob("*.html")) + sorted((ROOT / "urun").glob("*.html"))
    n = sum(inject(f) for f in files)
    print(f"\n{n} dosya güncellendi.")


if __name__ == "__main__":
    main()
