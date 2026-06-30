# -*- coding: utf-8 -*-
"""Proje tutarlilik denetimi."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "images" / "products"
CATALOG_PATH = ROOT / "assets" / "js" / "products-data.js"
URUN = ROOT / "urun"
ISSUES = []


def issue(severity, area, msg):
    ISSUES.append((severity, area, msg))


def load_catalog():
    raw = CATALOG_PATH.read_text(encoding="utf-8")
    m = re.search(r"window\.ABRALION_CATALOG\s*=\s*(\{.*\})\s*;?\s*$", raw, re.S)
    return json.loads(m.group(1))


def check_images(data):
    for p in data["products"]:
        slug = p["slug"]
        for i, img in enumerate(p.get("images") or []):
            rel = img.get("src", "")
            path = ROOT / rel.replace("/", "\\") if "\\" not in rel else ROOT / rel
            if not path.is_file():
                issue("ERROR", "gorsel", f"{slug}: eksik dosya -> {rel}")
        folder = IMG / slug
        if folder.is_dir():
            karts = [f for f in folder.iterdir() if f.is_file() and "-kart." in f.name.lower()]
            if not karts:
                issue("WARN", "gorsel", f"{slug}: *-kart.jpg yok (urun karti bos kalabilir)")
        if not p.get("images"):
            issue("WARN", "gorsel", f"{slug}: galeri bos")


def check_html_pages(data):
    slugs = {p["slug"] for p in data["products"]}
    html_files = {f.stem for f in URUN.glob("*.html")}
    for s in slugs - html_files:
        issue("ERROR", "sayfa", f"Eksik HTML: urun/{s}.html")
    for h in html_files - slugs:
        issue("WARN", "sayfa", f"Yetim HTML: urun/{h}.html")
    for f in URUN.glob("*.html"):
        text = f.read_text(encoding="utf-8")
        pid = re.search(r'data-product-id="([^"]+)"', text)
        if pid and pid.group(1) != f.stem:
            issue("ERROR", "sayfa", f"{f.name}: data-product-id={pid.group(1)} slug uyumsuz")


def check_variant_display(data):
    vd = (ROOT / "assets/js/VariantDisplay.js").read_text(encoding="utf-8")
    m = re.search(r"PRODUCT_TABLE_COLUMNS\s*=\s*\{", vd)
    if not m:
        issue("ERROR", "tablo", "PRODUCT_TABLE_COLUMNS bulunamadi")
        return
    # extract keys like 'slug-name':
    keys = set(re.findall(r"'([a-z0-9-]+)'\s*:", vd))
    for p in data["products"]:
        if p["slug"] not in keys:
            issue("WARN", "tablo", f"{p['slug']}: VariantDisplay PRODUCT_TABLE_COLUMNS tanimi yok")


def check_categories(data):
    cat_ids = {c["id"] for c in data["categories"]}
    old = {"uclar", "maket-bicaklari", "metreler"}
    for p in data["products"]:
        if p.get("categoryId") not in cat_ids:
            issue("ERROR", "kategori", f"{p['slug']}: gecersiz categoryId={p.get('categoryId')}")
        if p.get("categoryId") in old:
            issue("ERROR", "kategori", f"{p['slug']}: eski categoryId={p.get('categoryId')}")


def grep_old_refs():
    patterns = [
        (r"kategori=(uclar|maket-bicaklari|metreler)", "eski kategori linki"),
        (r"duz-keski\.html", "birlesik duz-keski sayfasi"),
        (r"sivri-uclu-keski-murc\.html(?!-)", "birlesik sivri sayfasi"),
        (r"22 ana ürün|22 ürün", "eski urun sayisi metni"),
        (r"24 ana ürün|24 ürün", None),
    ]
    skip_dirs = {".git", "node_modules", "agent-transcripts"}
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(s in path.parts for s in skip_dirs):
            continue
        if path.suffix.lower() not in {".html", ".js", ".css", ".xml", ".md", ".py", ".json"}:
            continue
        if "sync-catalog-images" in path.name or "audit-project" in path.name:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pat, label in patterns:
            if label is None:
                continue
            if re.search(pat, text):
                rel = path.relative_to(ROOT)
                issue("WARN", "referans", f"{rel}: {label}")


def check_urunler_meta(data):
    n = len(data["products"])
    nc = len(data["categories"])
    text = (ROOT / "urunler.html").read_text(encoding="utf-8")
    if f"{n} ana ürün" not in text and f"{n} ürün" not in text:
        issue("WARN", "metin", f"urunler.html meta {n} urun ile uyumsuz olabilir")
    if f"{nc} kategori" not in text:
        issue("WARN", "metin", f"urunler.html meta {nc} kategori ile uyumsuz olabilir")


def check_product_card_heroes(data):
    css = (ROOT / "assets/css/product-card-heroes.css").read_text(encoding="utf-8")
    slugs = {p["slug"] for p in data["products"]}
    hero_slugs = set(re.findall(r'data-product-id="([^"]+)"', css))
    for s in hero_slugs - slugs:
        issue("WARN", "kart", f"product-card-heroes.css: katalogda olmayan {s}")
    for s in slugs:
        if s in hero_slugs:
            folder = IMG / s
            kart = list(folder.glob("*-kart.jpg")) if folder.is_dir() else []
            if not kart:
                issue("WARN", "kart", f"{s}: hero CSS var ama kart gorseli yok")


def check_sitemap(data):
    sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    slugs = {p["slug"] for p in data["products"]}
    for s in slugs:
        if f"/urun/{s}.html" not in sm:
            issue("WARN", "sitemap", f"Eksik: urun/{s}.html")
    old_urls = re.findall(r"/urun/([a-z0-9-]+)\.html", sm)
    for u in old_urls:
        if u not in slugs:
            issue("WARN", "sitemap", f"Yetim URL: urun/{u}.html")


def main():
    data = load_catalog()
    print(f"Katalog: {len(data['products'])} urun, {len(data['categories'])} kategori\n")
    check_images(data)
    check_html_pages(data)
    check_variant_display(data)
    check_categories(data)
    check_urunler_meta(data)
    check_product_card_heroes(data)
    check_sitemap(data)
    grep_old_refs()

    by_sev = {"ERROR": [], "WARN": []}
    for sev, area, msg in ISSUES:
        by_sev[sev].append((area, msg))

    for sev in ("ERROR", "WARN"):
        items = by_sev[sev]
        print(f"=== {sev} ({len(items)}) ===")
        for area, msg in items:
            print(f"  [{area}] {msg}")
        print()

    if not ISSUES:
        print("Kritik sorun bulunamadi.")
    return len(by_sev["ERROR"])


if __name__ == "__main__":
    raise SystemExit(main())
