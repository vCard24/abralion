# -*- coding: utf-8 -*-
"""Ürün linklerini Excel için CSV olarak dışa aktarır."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
OUT = ROOT / "urun-kart-gorselleri-sablon.csv"
FILE_BASE = "file:///C:/Users/mosta/Desktop/abralion-cursor/"

rows = []
for i, pr in enumerate(DATA["products"], 1):
    slug = pr["slug"]
    img0 = (pr.get("images") or [{}])[0].get("src", "") if pr.get("images") else ""
    rows.append({
        "sira": i,
        "kategori": pr.get("categoryName", ""),
        "urun_adi": pr.get("name", ""),
        "slug": slug,
        "detay_sayfa": f"urun/{slug}.html",
        "detay_tam_link": f"{FILE_BASE}urun/{slug}.html",
        "kategori_liste": f"urunler.html?kategori={pr.get('categoryId', '')}",
        "onerilen_kart_dosyasi": f"{slug}-kart.png",
        "onerilen_kart_yolu": f"assets/images/products/{slug}/{slug}-kart.png",
        "mevcut_katalog_gorseli": img0,
        "yeni_gorsel_notu": "",
    })

fieldnames = list(rows[0].keys())
with OUT.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)

print(f"OK: {len(rows)} urun -> {OUT}")
