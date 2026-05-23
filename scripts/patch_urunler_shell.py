from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
index = (ROOT / "index.html").read_text(encoding="utf-8")
target = (ROOT / "urunler.html").read_text(encoding="utf-8")


def block(html: str, start: str, end: str) -> str:
    s = html.index(start)
    e = html.index(end, s) + len(end)
    return html[s:e]


hdr = block(index, '  <header class="header sticky', "  </header>\n")
ftr = block(index, '  <footer class="footer bg-carbon-black', "  </footer>\n")

hs = target.index('  <header class="header')
he = target.index("  </header>\n", hs) + len("  </header>\n")
target = target[:hs] + hdr + target[he:]

fs = target.index('  <footer class="footer')
fe = target.index("  </footer>\n", fs) + len("  </footer>\n")
target = target[:fs] + ftr + target[fe:]

# Close CTA section if missing
if "  </section>\n\n  <footer" not in target:
    target = target.replace(
        "  </div>\n\n  <footer class=\"footer",
        "  </div>\n  </section>\n\n  <footer class=\"footer",
        1,
    )

(ROOT / "urunler.html").write_text(target, encoding="utf-8")
print("Done")
