# -*- coding: utf-8 -*-
"""Kaynak PDF'leri slug adiyla assets/documents/products/ altina kopyalar, katalogu gunceller."""
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(r"c:\Users\mosta\Desktop\Yeni klasör")
DEST = ROOT / "assets" / "documents" / "products"
CATALOG_PATH = ROOT / "assets" / "js" / "products-data.js"
ROOT_CATALOG = ROOT / "products-data.js"

# Kaynak dosya adi (kismi eslesme, kucuk harf) -> urun slug(lari)
CATALOG_MAP = [
    ("metal_inox_kesme_tasi", ["metal-inox-kesme-tasi"]),
    ("355mm-metal-sabit-tezgah", ["355mm-metal-sabit-tezgah-kesme-diski"]),
    ("metal-inox--taslama", ["metal-inox-taslama-diski"]),
    ("metal-inox-taslama", ["metal-inox-taslama-diski"]),
    ("zr_zirkon_flap", ["zr-zirkon-flap-disk"]),
    ("ao al", ["ao-aluminyum-oksit-flap-disk"]),
    ("segmentli standart elmas", ["segmentli-standart-elmas-kesici"]),
    ("ultra", ["ultra-ince-elmas-disk"]),
    ("granit ve mermer", ["granit-mermer-segmentli-taslama-diski"]),
    ("asfalt icin", ["asfalt-elmas-kesme-diski"]),
    ("asfalt i", ["asfalt-elmas-kesme-diski"]),
    ("güçlendirilmiş beton", ["beton-elmas-kesme-diski"]),
    ("guclendirilmis beton", ["beton-elmas-kesme-diski"]),
    ("genel amaçlı", ["genel-amacli-elmas-kesme-diski"]),
    ("genel amacli", ["genel-amacli-elmas-kesme-diski"]),
    ("sds plus 2", ["sds-plus-2-kesicili-beton-matkap-ucu"]),
    ("sds plus 4", ["sds-plus-4-kesicili-beton-matkap-ucu"]),
    ("hss matkap", ["hss-matkap-ucu"]),
    ("düz keski", ["duz-keski-sds-plus", "duz-keski-sds-max"]),
    ("duz keski", ["duz-keski-sds-plus", "duz-keski-sds-max"]),
    ("sivri uçlu", ["sivri-uclu-keski-murc-sds-plus", "sivri-uclu-keski-murc-sds-max"]),
    ("sivri uclu", ["sivri-uclu-keski-murc-sds-plus", "sivri-uclu-keski-murc-sds-max"]),
    ("cam ve seramik", ["cam-seramik-matkap-ucu"]),
    ("sds max bur", ["sds-max-burc-aleti"]),
    ("mıknatıslı", ["miknatisli-anahtar-ucu"]),
    ("miknatisli", ["miknatisli-anahtar-ucu"]),
    ("ph2 manyetik", ["ph2-manyetik-bits-uc"]),
    ("profesyonel maket", ["profesyonel-maket-bicagi"]),
    ("abs g", ["abs-govdeli-profesyonel-serit-metre"]),
]


def normalize_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.lower().replace("_", " ").replace("-", " ")).strip()


def find_source_file(key: str) -> Path | None:
    key_n = normalize_name(key)
    for pdf in SRC.glob("*.pdf"):
        stem_n = normalize_name(pdf.stem)
        if key_n in stem_n or stem_n.startswith(key_n):
            return pdf
    return None


def load_catalog():
    raw = CATALOG_PATH.read_text(encoding="utf-8")
    match = re.search(r"window\.ABRALION_CATALOG\s*=\s*(\{.*\})\s*;?\s*$", raw, re.S)
    return json.loads(match.group(1)), raw


def save_catalog(data, template_raw):
    body = json.dumps(data, ensure_ascii=False, indent=2)
    new_raw = re.sub(
        r"window\.ABRALION_CATALOG\s*=\s*\{.*\}\s*;?\s*$",
        f"window.ABRALION_CATALOG = {body};",
        template_raw,
        flags=re.S,
    )
    CATALOG_PATH.write_text(new_raw, encoding="utf-8")
    if ROOT_CATALOG.exists():
        ROOT_CATALOG.write_text(new_raw, encoding="utf-8")


def main():
    if not SRC.is_dir():
        raise SystemExit(f"Kaynak klasor yok: {SRC}")

    DEST.mkdir(parents=True, exist_ok=True)
    data, raw = load_catalog()
    slug_to_product = {p["slug"]: p for p in data["products"]}

    used_sources: set[Path] = set()
    copied: list[str] = []
    missing: list[str] = []

    for key, slugs in CATALOG_MAP:
        src = find_source_file(key)
        if not src:
            missing.append(key)
            continue
        if src in used_sources:
            continue
        used_sources.add(src)

        for slug in slugs:
            if slug not in slug_to_product:
                print(f"UYARI: katalogda slug yok: {slug}")
                continue
            dest = DEST / f"{slug}.pdf"
            shutil.copy2(src, dest)
            rel = f"assets/documents/products/{slug}.pdf"
            slug_to_product[slug]["technicalCatalog"] = rel
            copied.append(f"{src.name} -> {dest.name}")

    save_catalog(data, raw)

    gen = ROOT / "scripts" / "generate-product-pages.py"
    if gen.exists():
        subprocess.run(["python", str(gen)], check=True, cwd=ROOT)

    print(f"Kopyalandi: {len(copied)} dosya")
    for line in copied:
        print(f"  {line}")
    if missing:
        print("Bulunamadi:", ", ".join(missing))


if __name__ == "__main__":
    main()
