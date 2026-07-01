"""Fix WCAG heading-order: no level skips (h1→h2→h3)."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

FOOTER_H4 = re.compile(
    r'<h4 class="font-label-caps text-label-caps uppercase text-white mb-6 md:mb-8">'
    r'(Hızlı Linkler|Kategoriler|İletişim)'
    r'</h4>'
)
FOOTER_H4_REP = r'<h2 class="font-label-caps text-label-caps uppercase text-white mb-6 md:mb-8">\1</h2>'

SIDEBAR_H3 = (
    '<h3 class="font-label-caps text-on-surface-variant mb-6 flex items-center gap-2">'
)
SIDEBAR_H2 = (
    '<h2 class="font-label-caps text-on-surface-variant mb-6 flex items-center gap-2">'
)

DETAIL_SECTION_H3 = re.compile(
    r'<h3 class="font-label-caps text-label-caps text-steel-gray mb-4 uppercase">'
    r'(Teknik Özellikler|Avantajlar|Uygulama Alanları|Güvenlik Talimatları)'
    r'</h3>'
)
DETAIL_SECTION_H2_REP = (
    r'<h2 class="font-label-caps text-label-caps text-steel-gray mb-4 uppercase">\1</h2>'
)


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text

    text = FOOTER_H4.sub(FOOTER_H4_REP, text)

    if path.name == "urunler.html":
        text = text.replace(SIDEBAR_H3, SIDEBAR_H2)
        text = re.sub(
            r"(KATEGORİ|UYGULAMA ALANI)\s*</h3>",
            r"\1</h2>",
            text,
        )

    if "page-product-detail" in text or "product-detail-noir" in path.name:
        text = DETAIL_SECTION_H3.sub(DETAIL_SECTION_H2_REP, text)

    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    n = 0
    for path in ROOT.rglob("*.html"):
        if "node_modules" in path.parts:
            continue
        if patch_file(path):
            print(path.relative_to(ROOT))
            n += 1
    print(f"Updated {n} files")


if __name__ == "__main__":
    main()
