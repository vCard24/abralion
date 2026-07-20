"""Replace site header with Stitch ana_sayfa layout (logo + nav + Teklif Al)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEADER_ROOT = (ROOT / "scripts/includes/header-root.html").read_text(encoding="utf-8")
HEADER_SUB = (ROOT / "scripts/includes/header-subdir.html").read_text(encoding="utf-8")
PATTERN = re.compile(r"<header class=\"header[\s\S]*?</header>", re.MULTILINE)

TR_TO_RU = {
    "index.html": "https://abralion.com/ru/",
    "urunler.html": "https://abralion.com/ru/produkty.html",
    "dokumanlar.html": "https://abralion.com/ru/dokumenty.html",
    "hakkimizda.html": "https://abralion.com/ru/o-kompanii.html",
    "iletisim.html": "https://abralion.com/ru/kontakty.html",
    "fiyat-teklifi.html": "https://abralion.com/ru/zapros-tseny.html",
    "karsilastir.html": "https://abralion.com/ru/sravnenie.html",
    "gizlilik-politikasi.html": "https://abralion.com/ru/politika-konfidentsialnosti.html",
    "kullanim-kosullari.html": "https://abralion.com/ru/usloviya-ispolzovaniya.html",
    "kvkk.html": "https://abralion.com/ru/zashhita-dannykh.html",
    "teklif-tesekkur.html": "https://abralion.com/ru/spasibo.html",
}

RU_HREF_RE = re.compile(
    r'(<a href=")https://abralion\.com/ru/[^"]*(" class="lang-btn" hreflang="ru")'
)


def ru_url_for(path: Path) -> str:
    if path.parent.name == "urun":
        return f"https://abralion.com/ru/urun/{path.name}"
    return TR_TO_RU.get(path.name, "https://abralion.com/ru/")


def with_ru_href(snippet: str, ru_url: str) -> str:
    return RU_HREF_RE.sub(rf"\1{ru_url}\2", snippet, count=1)


updated = 0
for path in ROOT.rglob("*.html"):
    if "scripts" in path.parts and path.name != "product-detail-noir.html":
        continue
    if "ru" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    if '<header class="header' not in text:
        continue
    base = HEADER_SUB if path.parent.name == "urun" else HEADER_ROOT
    snippet = with_ru_href(base.strip(), ru_url_for(path))
    new_text, n = PATTERN.subn(snippet, text, count=1)
    if n:
        path.write_text(new_text, encoding="utf-8")
        updated += 1
        print(path.relative_to(ROOT))

print(f"\nUpdated {updated} files")
