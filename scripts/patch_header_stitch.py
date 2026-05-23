"""Replace site header with Stitch ana_sayfa layout (logo + nav + Teklif Al)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEADER_ROOT = (ROOT / "scripts/includes/header-root.html").read_text(encoding="utf-8")
HEADER_SUB = (ROOT / "scripts/includes/header-subdir.html").read_text(encoding="utf-8")
PATTERN = re.compile(r"<header class=\"header[\s\S]*?</header>", re.MULTILINE)

updated = 0
for path in ROOT.rglob("*.html"):
    if "scripts" in path.parts and path.name != "product-detail-noir.html":
        continue
    text = path.read_text(encoding="utf-8")
    if "<header class=\"header" not in text:
        continue
    snippet = HEADER_SUB if path.parent.name == "urun" else HEADER_ROOT
    new_text, n = PATTERN.subn(snippet.strip(), text, count=1)
    if n:
        path.write_text(new_text, encoding="utf-8")
        updated += 1
        print(path.relative_to(ROOT))

print(f"\nUpdated {updated} files")
