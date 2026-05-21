# -*- coding: utf-8 -*-
"""urunler.html ve index.html icine taranabilir statik urun kartlari enjekte eder."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "products.json"
MARKER_START = "<!-- CATALOG_STATIC_START -->"
MARKER_END = "<!-- CATALOG_STATIC_END -->"


def kart_src(slug: str, base: str) -> str:
    ext = "png" if slug == "metal-inox-kesme-tasi" else "jpg"
    return f"{base}assets/images/products/{slug}/{slug}-kart.{ext}"


def desc_snippet(text: str, limit: int = 120) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "…"


def card_html(product: dict, base: str = "") -> str:
    slug = product["slug"]
    name = html.escape(product["name"])
    cat = html.escape(product.get("categoryName") or "")
    desc = html.escape(desc_snippet(product.get("description", "")))
    cat_id = html.escape(product.get("categoryId") or "")
    img = html.escape(kart_src(slug, base))
    url = html.escape(f"{base}urun/{slug}.html")
    png_fb = html.escape(f"{base}assets/images/products/{slug}/{slug}-kart.png")
    return f"""          <div class="product-card product-card--static" data-category-id="{cat_id}">
            <div class="product-card-image-container product-card-image-container--static-hero">
              <a href="{url}">
                <img class="product-card-image product-card-image--hero" src="{img}" alt="{name}" loading="lazy" width="400" height="300" data-fallback="{png_fb}">
              </a>
            </div>
            <div class="product-card-content">
              <div class="product-card-category">{cat}</div>
              <h3 class="product-card-title"><a href="{url}">{name}</a></h3>
              <p class="product-card-description">{desc}</p>
              <div class="product-card-actions">
                <a href="{url}" class="btn btn-primary btn-small">Detaylar</a>
              </div>
            </div>
          </div>"""


def inject_file(path: Path, inner_html: str) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER_START not in text or MARKER_END not in text:
        raise SystemExit(f"Markers missing in {path}")
    before, rest = text.split(MARKER_START, 1)
    _, after = rest.split(MARKER_END, 1)
    new_text = before + MARKER_START + "\n" + inner_html + "\n          " + MARKER_END + after
    path.write_text(new_text, encoding="utf-8")
    print(f"Updated {path.name}")


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    products = sorted(data["products"], key=lambda p: (p.get("categoryId", ""), p.get("name", "")))
    featured = [p for p in data["products"] if p.get("featured")][:6]

    all_cards = "\n".join(card_html(p) for p in products)
    featured_cards = "\n".join(card_html(p) for p in featured)

    inject_file(ROOT / "urunler.html", all_cards)

    index_path = ROOT / "index.html"
    inject_file(index_path, featured_cards)

    count_line = f'        <p id="products-count">{len(products)} ürün</p>'
    index_text = index_path.read_text(encoding="utf-8")
    urunler_path = ROOT / "urunler.html"
    urunler_text = urunler_path.read_text(encoding="utf-8")
    urunler_text = urunler_text.replace(
        '<p id="products-count">Yükleniyor…</p>',
        count_line.replace("        ", "        ", 1),
    )
    urunler_path.write_text(urunler_text, encoding="utf-8")

    print(f"Injected {len(products)} catalog cards, {len(featured)} featured.")


if __name__ == "__main__":
    main()
