from pathlib import Path
p = Path(__file__).resolve().parents[1] / "assets" / "js" / "product-detail.js"
t = p.read_text(encoding="utf-8")
t = t.replace("<motion", "<MOTION_TAG").replace("</motion>", "</MOTION_TAG>")
t = t.replace("MOTION_TAG", "div")
p.write_text(t, encoding="utf-8")
print("fixed", p)
