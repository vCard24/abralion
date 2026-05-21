# -*- coding: utf-8 -*-
import json
import fitz
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
doc = fitz.open(ROOT / "abralion-web.pdf")

with open(ROOT / "data/products.json", encoding="utf-8") as f:
    products = json.load(f)["products"]


def find_headers(page_text):
    lines = [l.strip() for l in page_text.split("\n") if l.strip()]
    for i, line in enumerate(lines):
        if "rün Kodu" in line:
            block = lines[i : i + 14]
            cols = []
            for b in block:
                if any(
                    k in b
                    for k in (
                        "rün Kodu",
                        "Daire",
                        "Göbek",
                        "Kalın",
                        "Maksimum",
                        "Aşındır",
                        "Grit",
                        "Kutu",
                        "Koli",
                        "Çap",
                        "Uzunluk",
                        "Bağlant",
                        "Şaft",
                        "Malzeme",
                        "Kullanım",
                        "Tip",
                        "Kafa",
                        "Geniş",
                        "Gövde",
                        "Bıçak",
                        "Şerit",
                        "Kasa",
                        "Paket",
                    )
                ):
                    cols.append(b)
                elif cols and b[0].isdigit() or (cols and "/" in b[:6]):
                    break
            return cols
    return None


for p in products:
    headers = None
    search = p["name"]
    for i in range(doc.page_count):
        t = doc[i].get_text()
        if search in t:
            h = find_headers(t)
            if h:
                headers = h
                break
    print(f"{p['slug']}: {headers}")
