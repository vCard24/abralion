"""Patch index.html featured products section — Precision Industrial Noir."""
from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / "index.html"

DETAIL_ICON = """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="M12 5l7 7-7 7"/></svg>"""

CARD = """          <article class="product-card product-card--noir product-card--static group flex flex-col overflow-hidden rounded-lg border border-steel-gray/20 bg-surface-elevation transition-colors duration-300 hover:border-abrasive-red/50" data-category-id="{cat}">
            <a href="{url}" class="product-card-media block aspect-[4/3] overflow-hidden bg-carbon-black p-4">
              <img class="product-card-image mx-auto max-h-full w-full object-contain transition-transform duration-500 group-hover:scale-105" src="{img}" alt="{name}" loading="lazy" width="400" height="300" data-fallback="{fallback}">
            </a>
            <div class="product-card-content flex flex-1 flex-col gap-3 p-5">
              <h3 class="product-card-title font-headline-md text-headline-md leading-snug">
                <a href="{url}" class="text-white transition-colors hover:text-abrasive-red">{name}</a>
              </h3>
              <div class="product-card-footer mt-auto flex items-end justify-between gap-3 border-t border-steel-gray/20 pt-4">
                <p class="product-card-spec font-technical-data text-technical-data uppercase text-steel-gray">{spec}</p>
                <a href="{url}" class="product-card-detail flex h-10 w-10 shrink-0 items-center justify-center rounded text-abrasive-red transition-colors hover:bg-abrasive-red/10" aria-label="{name} detayları">{icon}</a>
              </div>
            </div>
          </article>"""

PRODUCTS = [
    {
        "cat": "kesici-taslama-flap-disk",
        "url": "urun/metal-inox-kesme-tasi.html",
        "img": "assets/images/products/metal-inox-kesme-tasi/metal-inox-kesme-tasi-kart.png",
        "fallback": "assets/images/products/metal-inox-kesme-tasi/metal-inox-kesme-tasi-kart.png",
        "name": "Metal / Inox Kesme Taşı",
        "spec": "Ø115 × 1,0 mm · 13300 RPM",
    },
    {
        "cat": "kesici-taslama-flap-disk",
        "url": "urun/355mm-metal-sabit-tezgah-kesme-diski.html",
        "img": "assets/images/products/355mm-metal-sabit-tezgah-kesme-diski/355mm-metal-sabit-tezgah-kesme-diski-kart.jpg",
        "fallback": "assets/images/products/355mm-metal-sabit-tezgah-kesme-diski/355mm-metal-sabit-tezgah-kesme-diski-kart.png",
        "name": "355mm Metal Sabit Tezgah Kesme Diski",
        "spec": "Ø355 × 3,0 mm · 4400 RPM",
    },
    {
        "cat": "kesici-taslama-flap-disk",
        "url": "urun/metal-inox-taslama-diski.html",
        "img": "assets/images/products/metal-inox-taslama-diski/metal-inox-taslama-diski-kart.jpg",
        "fallback": "assets/images/products/metal-inox-taslama-diski/metal-inox-taslama-diski-kart.png",
        "name": "Metal / Inox Taşlama Diski",
        "spec": "Ø125 × 6,0 mm · 12200 RPM",
    },
    {
        "cat": "kesici-taslama-flap-disk",
        "url": "urun/zr-zirkon-flap-disk.html",
        "img": "assets/images/products/zr-zirkon-flap-disk/zr-zirkon-flap-disk-kart.jpg",
        "fallback": "assets/images/products/zr-zirkon-flap-disk/zr-zirkon-flap-disk-kart.png",
        "name": "ZR Zirkon Flap Disk",
        "spec": "Ø115 mm · 40# · 13300 RPM",
    },
    {
        "cat": "kesici-taslama-flap-disk",
        "url": "urun/ao-aluminyum-oksit-flap-disk.html",
        "img": "assets/images/products/ao-aluminyum-oksit-flap-disk/ao-aluminyum-oksit-flap-disk-kart.jpg",
        "fallback": "assets/images/products/ao-aluminyum-oksit-flap-disk/ao-aluminyum-oksit-flap-disk-kart.png",
        "name": "AO Alüminyum Oksit Flap Disk",
        "spec": "Ø115 mm · 40# · 12200 RPM",
    },
    {
        "cat": "elmas-kesici",
        "url": "urun/segmentli-standart-elmas-kesici.html",
        "img": "assets/images/products/segmentli-standart-elmas-kesici/segmentli-standart-elmas-kesici-kart.jpg",
        "fallback": "assets/images/products/segmentli-standart-elmas-kesici/segmentli-standart-elmas-kesici-kart.png",
        "name": "Segmentli Standart Elmas Kesici",
        "spec": "Ø125 mm · 12200 RPM",
    },
]

SECTION = """    <section class="featured-products bg-background py-section-gap" id="featured-products-section">
      <div class="mx-auto max-w-site px-margin-mobile lg:px-margin-desktop">
        <header class="featured-products__header mb-10 md:mb-12">
          <h2 class="font-headline-lg text-headline-lg text-white">Öne Çıkan Çözümler</h2>
          <p class="mt-3 max-w-2xl font-body-md text-body-md text-steel-gray">PDF kataloğumuzdan seçilmiş endüstriyel kesim ve taşlama ürünleri — teknik verilerle hızlı karar.</p>
        </header>
        <div class="product-grid grid grid-cols-1 gap-gutter md:grid-cols-2 lg:grid-cols-4" id="featured-products-grid">
          <!-- CATALOG_STATIC_START -->
{cards}          <!-- CATALOG_STATIC_END -->
        </div>
        <div class="mt-10 md:mt-12">
          <a href="urunler.html" class="inline-flex items-center rounded bg-abrasive-red px-8 py-4 font-label-caps text-label-caps uppercase text-on-primary-container transition-all hover:brightness-110 active:scale-95">Tüm Ürünleri Gör</a>
        </div>
      </div>
    </section>"""

OLD_START = '    <section class="featured-products section">'
OLD_END = '    </section>\n  </main>'


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")
    start = text.find(OLD_START)
    end = text.find(OLD_END)
    if start == -1 or end == -1:
        raise SystemExit(f"featured section markers not found (start={start}, end={end})")

    cards = "\n".join(CARD.format(icon=DETAIL_ICON, **p) for p in PRODUCTS) + "\n"
    new_section = SECTION.format(cards=cards)
    text = text[:start] + new_section + "\n\n" + text[end:]
    INDEX.write_text(text, encoding="utf-8", newline="\n")
    print("featured products section patched")


if __name__ == "__main__":
    main()
