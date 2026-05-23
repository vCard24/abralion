# -*- coding: utf-8 -*-
"""Fix product-detail-noir.html: footer, tabs main block."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHELL = ROOT / "scripts" / "templates" / "product-detail-noir.html"
MAIN = ROOT / "scripts" / "templates" / "product-detail-main-stitch.html"

text = SHELL.read_text(encoding="utf-8")
text = text.replace('  </main>er class="footer', '  </main>\n\n  <footer class="footer')

main_block = MAIN.read_text(encoding="utf-8").strip() + "\n"

start = text.index('  <main id="main-content">')
# Find footer (after fixing corruption)
footer_idx = text.index('<footer class="footer', start)

text = (
    text[: start + len('  <main id="main-content">\n')]
    + main_block
    + "  </main>\n\n  "
    + text[footer_idx:]
)

SHELL.write_text(text, encoding="utf-8")
print("Patched", SHELL)
