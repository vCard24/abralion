# -*- coding: utf-8 -*-
"""Site geneli HTML sayfa denetimi."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = [
    "index.html", "urunler.html", "hakkimizda.html", "dokumanlar.html",
    "iletisim.html", "karsilastir.html",
]
PRODUCT_DIR = ROOT / "urun"
LATEST_NOIR = "20260525e"

issues = []
ok = []


def check(path: Path, kind: str):
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8")

    if "noir-migration.css" not in text:
        issues.append((rel, "noir-migration.css eksik"))
    else:
        m = re.search(r"noir-migration\.css\?v=([^\"']+)", text)
        ver = m.group(1) if m else "?"
        if ver != LATEST_NOIR and kind == "product":
            issues.append((rel, f"eski noir cache: {ver} (beklenen {LATEST_NOIR})"))
        elif kind == "site" and ver != LATEST_NOIR:
            issues.append((rel, f"eski noir cache: {ver} (site sayfalari guncellenmeli)"))

    if kind == "product":
        for req in (
            "page-product-detail-stitch",
            "page-product-detail",
            "bg-carbon-black",
            "tailwind-config.js",
            "product-detail.js",
            'id="product-gallery"',
            'id="variant-specs-table"',
            'id="product-title"',
        ):
            if req not in text:
                issues.append((rel, f"eksik: {req}"))

        if "tailwind-config" in text and 'id="tailwind-config"' in text:
            issues.append((rel, "inline tailwind-config (harici olmali)"))

        if "</main>er" in text or "<motion" in text:
            issues.append((rel, "bozuk HTML etiketi"))

    if kind == "site":
        if "tailwind-config.js" not in text and 'id="tailwind-config"' not in text:
            issues.append((rel, "tailwind config eksik"))
        body = re.search(r"<body[^>]*class=\"([^\"]*)\"", text)
        if body and "bg-carbon-black" not in body.group(1) and "page-about" not in body.group(1):
            if rel not in ("dokumanlar.html", "iletisim.html", "karsilastir.html"):
                issues.append((rel, f"body'de carbon-black/page-about yok: {body.group(1)[:80]}"))

    if not issues or all(i[0] != rel for i in issues):
        ok.append(rel)


for name in PUBLIC:
    p = ROOT / name
    if p.exists():
        check(p, "site")

products = sorted({p.name: p for p in PRODUCT_DIR.glob("*.html")}.values(), key=lambda x: x.name)
for p in products:
    check(p, "product")

print(f"=== Denetim: {len(PUBLIC)} site + {len(products)} urun sayfasi ===\n")
if issues:
    by_file = {}
    for rel, msg in issues:
        by_file.setdefault(rel, []).append(msg)
    print(f"SORUN ({len(by_file)} dosya):\n")
    for rel in sorted(by_file):
        for msg in by_file[rel]:
            print(f"  {rel}: {msg}")
else:
    print("Tum dosyalar temel kontrollerden gecti.\n")

print(f"\nOK: {len(products)} urun + site sayfalari tarandi.")
