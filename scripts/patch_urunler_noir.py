"""Replace urunler.html main with Stitch urunlerimiz.html layout (Noir)."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
REF = Path(
    r"c:\Users\mosta\Desktop\abralion-doneler\indirilenler-abralion"
    r"\stitch_abralion_website_redesign\stitch_abralion_website_redesign"
    r"\r_nlerimiz_abralion_1\urunlerimiz.html"
)
INDEX = ROOT / "index.html"
TARGET = ROOT / "urunler.html"


def extract_block(html: str, start_marker: str, end_marker: str) -> str:
    start = html.index(start_marker)
    end = html.index(end_marker, start)
    return html[start:end]


def reindent(block: str, base: int = 2) -> str:
    lines = block.splitlines()
    if not lines:
        return ""
    min_indent = min(
        len(line) - len(line.lstrip())
        for line in lines
        if line.strip()
    )
    pad = " " * base
    out = []
    for line in lines:
        if not line.strip():
            out.append("")
            continue
        stripped = line[min_indent:] if len(line) >= min_indent else line.lstrip()
        out.append(pad + stripped)
    return "\n".join(out)


def patch_main(ref_html: str) -> str:
    main_raw = extract_block(ref_html, "<main class=", "</main>")
    main_raw = main_raw.replace(
        '<main class="max-w-7xl mx-auto px-margin-desktop py-16">',
        '<main id="main-content" class="max-w-7xl mx-auto px-margin-mobile lg:px-margin-desktop py-16">',
        1,
    )
    main_raw = main_raw.replace(
        '<div class="product-grid-asymmetric">',
        '<div class="product-grid-asymmetric" id="products-grid">',
        1,
    )
    main_raw = main_raw.replace(
        '<span class="text-on-surface">24 Ürün Ailesi</span>',
        '<span class="text-on-surface" id="products-count">24 Ürün Ailesi</span>',
        1,
    )
    return reindent(main_raw, 2)


def patch_cta(ref_html: str) -> str:
    cta_raw = extract_block(
        ref_html,
        "<!-- Technical Support CTA -->",
        "</section>\n<!-- Footer -->",
    )
    cta_raw = cta_raw.replace(
        '<button class="bg-abrasive-red text-white px-8 py-4 font-label-caps hover:bg-inverse-primary transition-all">MÜHENDİSE DANIŞ</button>',
        '<a href="iletisim.html" class="inline-flex items-center bg-abrasive-red text-white px-8 py-4 font-label-caps hover:bg-inverse-primary transition-all">MÜHENDİSE DANIŞ</a>',
        1,
    )
    cta_raw = cta_raw.replace(
        '<button class="bg-transparent border border-white px-8 py-4 font-label-caps hover:bg-white hover:text-carbon-black transition-all">KATALOG İNDİR (.PDF)</button>',
        '<a href="dokumanlar.html" class="inline-flex items-center bg-transparent border border-white px-8 py-4 font-label-caps hover:bg-white hover:text-carbon-black transition-all">KATALOG İNDİR (.PDF)</a>',
        1,
    )
    return reindent(cta_raw, 2)


def noir_head_snippet() -> str:
    return """  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=JetBrains+Mono:wght@500&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&family=Montserrat:wght@600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com?plugins=forms"></script>
  <script src="assets/js/tailwind-config.js"></script>
  <link rel="stylesheet" href="assets/css/noir-migration.css?v=20260523">
"""


def extract_header_footer(index_html: str):
    header = extract_block(index_html, '  <header class="header', "  </header>\n")
    header = "  <header class=\"header" + header
    footer = extract_block(index_html, '  <footer class="footer', "  </footer>\n")
    footer = "  <footer class=\"footer" + footer
    return header, footer


def main():
    ref_html = REF.read_text(encoding="utf-8")
    index_html = INDEX.read_text(encoding="utf-8")
    target = TARGET.read_text(encoding="utf-8")

    new_main = patch_main(ref_html)
    new_cta = patch_cta(ref_html)
    header, footer = extract_header_footer(index_html)

    # Head: insert Noir assets after compare.css
    if "noir-migration.css" not in target:
        target = target.replace(
            '  <link rel="stylesheet" href="assets/css/compare.css">\n</head>',
            '  <link rel="stylesheet" href="assets/css/compare.css">\n'
            + noir_head_snippet()
            + "</head>",
            1,
        )

    # Body class
    target = re.sub(
        r"<body[^>]*>",
        '<body class="bg-background text-on-surface font-body-md antialiased">',
        target,
        count=1,
    )

    # Skip link
    target = target.replace(
        '<a href="#main-content" class="sr-only">İçeriğe atla</a>',
        '<a href="#main-content" class="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[2000] focus:px-4 focus:py-2 focus:bg-abrasive-red focus:text-white focus:rounded">İçeriğe atla</a>',
        1,
    )

    # Header
    old_header = extract_block(target, '  <header class="header', "  </header>\n")
    old_header = "  <header class=\"header" + old_header
    target = target.replace(old_header, header, 1)

    # Main + CTA
    old_main = extract_block(target, '  <main id="main-content"', "  </main>\n")
    old_main = "  <main id=\"main-content\"" + old_main[len('  <main id="main-content"'):]
    # old_main might have class="products-page - use regex
    target = re.sub(
        r"  <main id=\"main-content\"[\s\S]*?  </main>\n",
        new_main + "\n\n" + new_cta + "\n",
        target,
        count=1,
    )

    # Footer
    old_footer = extract_block(target, '  <footer class="footer', "  </footer>\n")
    old_footer = "  <footer class=\"footer" + old_footer
    target = target.replace(old_footer, footer, 1)

    TARGET.write_text(target, encoding="utf-8")
    print("Updated", TARGET)


if __name__ == "__main__":
    main()
