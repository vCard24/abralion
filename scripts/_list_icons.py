import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
icons = set()
for p in root.rglob("*"):
    if p.suffix.lower() not in {".html", ".js"}:
        continue
    if "node_modules" in p.parts:
        continue
    t = p.read_text(encoding="utf-8", errors="ignore")
    icons.update(re.findall(r'data-icon="([^"]+)"', t))
for name in sorted(icons):
    print(name)
print("TOTAL", len(icons))
