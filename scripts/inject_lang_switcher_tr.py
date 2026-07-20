"""Inject TR/RU header language switcher into Turkish pages (skip ru/)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

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

SWITCHER_RE = re.compile(
    r'<div class="lang-switcher"[^>]*>[\s\S]*?</div>\s*',
    re.MULTILINE,
)
ACTIONS_RE = re.compile(
    r'(<div class="header-actions[^"]*"[^>]*>)\s*',
)


def ru_url_for(path: Path) -> str | None:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("ru/"):
        return None
    if path.parent.name == "urun":
        return f"https://abralion.com/ru/urun/{path.name}"
    return TR_TO_RU.get(path.name)


def switcher_html(ru_url: str) -> str:
    return (
        '<div class="lang-switcher" role="navigation" aria-label="Dil seçimi">'
        '<span class="lang-btn lang-btn--active" aria-current="page">TR</span>'
        f'<a href="{ru_url}" class="lang-btn" hreflang="ru" lang="ru" aria-label="Русская версия">RU</a>'
        "</div>"
    )


def child_indent(text: str, actions_match: re.Match[str]) -> str:
    after = text[actions_match.end() : actions_match.end() + 80]
    m = re.match(r"\n([ \t]+)", after)
    if m:
        return m.group(1)
    # Product headers use 10 spaces; root pages use 8.
    return "          " if 'gap-3 lg:gap-4"' in actions_match.group(1) else "        "


def inject(text: str, ru_url: str) -> tuple[str, bool]:
    block = switcher_html(ru_url)
    if SWITCHER_RE.search(text):
        match = ACTIONS_RE.search(text)
        indent = child_indent(text, match) if match else "        "
        return SWITCHER_RE.sub(block + "\n" + indent, text, count=1), True
    match = ACTIONS_RE.search(text)
    if not match:
        return text, False
    indent = child_indent(text, match)
    return ACTIONS_RE.sub(rf"\1\n{indent}{block}\n{indent}", text, count=1), True


def main() -> None:
    updated = 0
    skipped = 0
    for path in sorted(ROOT.rglob("*.html")):
        if "scripts" in path.parts or "ru" in path.parts:
            continue
        ru_url = ru_url_for(path)
        if not ru_url:
            skipped += 1
            continue
        text = path.read_text(encoding="utf-8")
        if 'class="header' not in text and "header-actions" not in text:
            skipped += 1
            continue
        new_text, ok = inject(text, ru_url)
        if ok and new_text != text:
            path.write_text(new_text, encoding="utf-8", newline="\n")
            updated += 1
            print(path.relative_to(ROOT))
        elif not ok:
            print(f"SKIP (no header-actions): {path.relative_to(ROOT)}")
            skipped += 1
    print(f"\nUpdated {updated} files; skipped {skipped}")


if __name__ == "__main__":
    main()
