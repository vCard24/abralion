# -*- coding: utf-8 -*-
import re, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets/images/products"
raw = (ROOT / "assets/js/products-data.js").read_text(encoding="utf-8")
data = json.loads(re.search(r"window\.ABRALION_CATALOG\s*=\s*(\{.*\})\s*;?\s*$", raw, re.S).group(1))

issues = []
rows = []
for p in sorted(data["products"], key=lambda x: x["slug"]):
    slug = p["slug"]
    folder = IMG / slug
    files = [f for f in folder.iterdir() if f.is_file() and f.name != ".gitkeep"] if folder.is_dir() else []
    karts = [f.name for f in files if "-kart." in f.name.lower()]
    gallery = p.get("images") or []
    missing = [Path(img["src"]).name for img in gallery if not (ROOT / img["src"].replace("/", "\\")).is_file()]
    note = ""
    if not folder.is_dir():
        note = "KLASOR YOK"
        issues.append(f"{slug}: klasor yok")
    elif not files:
        note = "BOS"
        issues.append(f"{slug}: bos klasor")
    elif not karts:
        note = "KART YOK (galeri yedegi var)"
        issues.append(f"{slug}: kart yok")
    elif missing:
        note = f"KIRIK: {', '.join(missing)}"
        issues.append(f"{slug}: kirik path")
    rows.append((slug, len(files), len(gallery), len(karts), note))

print(f"{'URUN':<42} {'DOSYA':>5} {'GALERI':>6} {'KART':>4}")
print("-" * 62)
for slug, nf, ng, nk, note in rows:
    line = f"{slug:<42} {nf:>5} {ng:>6} {nk:>4}"
    if note:
        line += f"  ! {note}"
    print(line)
print()
print(f"Toplam: {len(rows)} urun | Sorun: {len(issues)}")
for i in issues:
    print(f"  - {i}")
