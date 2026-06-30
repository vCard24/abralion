# -*- coding: utf-8 -*-
"""PDF ic metadata Title alanini urun/dokuman adiyla gunceller."""
import json
import re
import tempfile
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "assets" / "documents"
CATALOG_PATH = ROOT / "assets" / "js" / "products-data.js"

EXTRA_TITLES = {
    "abralion_turkce_katalog.pdf": "Türkçe Ürün Kataloğu teknik döküman",
    "abralion_russian_cataloque.pdf": "Каталог Продукции teknik döküman",
    "guvenlik-asindirici-urunler.pdf": "Aşındırıcı Ürünlerin Kullanımı İçin Güvenlik Tavsiyeleri teknik döküman",
    "delici-ve-kirici-urunler-guvenlik-rehberi.pdf": "Delici ve Kırıcı Ürünlerin Kullanımı İçin Güvenlik Tavsiyeleri teknik döküman",
}


def load_catalog():
    raw = CATALOG_PATH.read_text(encoding="utf-8")
    match = re.search(r"window\.ABRALION_CATALOG\s*=\s*(\{.*\})\s*;?\s*$", raw, re.S)
    return json.loads(match.group(1))


def title_for_product(name: str) -> str:
    return f"{name} teknik döküman"


def patch_pdf(path: Path, title: str) -> bool:
    doc = fitz.open(path)
    old = doc.metadata.get("title") or ""
    if old == title:
        doc.close()
        return False

    doc.set_metadata(
        {
            "title": title,
            "subject": title,
            "author": "Abralion",
            "producer": "Abralion",
        }
    )

    fd, tmp_name = tempfile.mkstemp(suffix=".pdf")
    import os

    os.close(fd)
    tmp = Path(tmp_name)
    try:
        doc.save(tmp, garbage=4, deflate=True)
        doc.close()
        tmp.replace(path)
        return True
    except Exception:
        doc.close()
        if tmp.exists():
            tmp.unlink()
        raise


def main():
    titles: dict[str, str] = {}

    for product in load_catalog()["products"]:
        rel = product.get("technicalCatalog")
        if not rel:
            continue
        fname = Path(rel).name
        titles[fname] = title_for_product(product["name"])

    titles.update(EXTRA_TITLES)

    updated = 0
    for fname, title in sorted(titles.items()):
        for base in (DOCS, DOCS / "products"):
            path = base / fname
            if not path.is_file():
                continue
            if patch_pdf(path, title):
                print(f"OK: {path.relative_to(ROOT)}")
                updated += 1
            else:
                print(f"SKIP: {path.relative_to(ROOT)}")

    print(f"\nGuncellenen: {updated} PDF")


if __name__ == "__main__":
    main()
