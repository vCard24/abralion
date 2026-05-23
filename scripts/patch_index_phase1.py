"""Phase 1: patch index.html header + hero for Precision Industrial Noir."""
from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / "index.html"

HEADER_INNER_OLD = """        <a href="index.html" class="header-logo-link" aria-label="Abralion Ana Sayfa">
          <img src="assets/images/logo.svg" alt="Abralion Logo" class="header-logo" data-logo>
        </a>
        <nav class="header-nav" aria-label="Ana navigasyon">
          <ul class="header-nav-list">
            <li><a href="index.html" class="header-nav-link">Ana Sayfa</a></li>
            <li class="header-nav-dropdown">
              <a href="urunler.html" class="header-nav-link">
                Ürünlerimiz
                <span class="dropdown-arrow">▼</span>
              </a>
              <ul class="dropdown-menu mega-menu" id="mega-menu"></ul>
            </li>
            <li>
              <a href="karsilastir.html" class="header-nav-link">
                Karşılaştır
                <span class="compare-badge" style="display: none;">0</span>
              </a>
            </li>
            <li><a href="dokumanlar.html" class="header-nav-link">Dökümanlar</a></li>
            <li><a href="hakkimizda.html" class="header-nav-link">Hakkımızda</a></li>
            <li><a href="iletisim.html" class="header-nav-link">İletişim</a></li>
          </ul>
          <div class="header-search">
            <input type="search" class="header-search-input" placeholder="Ürün ara..." aria-label="Ürün ara" id="header-search-input">
            <button type="button" class="header-search-btn" aria-label="Ara" id="header-search-btn">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <circle cx="11" cy="11" r="8"/>
                <path d="m21 21-4.35-4.35"/>
              </svg>
            </button>
          </div>
        </nav>
        <button type="button" class="mobile-menu-toggle" aria-label="Menüyü aç/kapat" aria-expanded="false">
          <span></span>
          <span></span>
          <span></span>
        </button>"""

HEADER_INNER_NEW = """        <a href="index.html" class="header-logo-link flex shrink-0 items-center" aria-label="Abralion Ana Sayfa">
          <img src="assets/images/logo.svg" alt="Abralion Logo" class="header-logo h-[50px] w-auto transition-opacity hover:opacity-80" data-logo>
        </a>
        <nav class="header-nav flex flex-grow items-center justify-end gap-4 lg:gap-6" aria-label="Ana navigasyon">
          <ul class="header-nav-list flex items-center gap-1 lg:gap-2">
            <li><a href="index.html" class="header-nav-link font-body-md text-body-md transition-colors">Ana Sayfa</a></li>
            <li class="header-nav-dropdown relative">
              <a href="urunler.html" class="header-nav-link font-body-md text-body-md transition-colors">
                Ürünlerimiz
                <span class="dropdown-arrow" aria-hidden="true">▼</span>
              </a>
              <ul class="dropdown-menu mega-menu" id="mega-menu"></ul>
            </li>
            <li>
              <a href="karsilastir.html" class="header-nav-link font-body-md text-body-md transition-colors inline-flex items-center">
                Karşılaştır
                <span class="compare-badge" style="display: none;">0</span>
              </a>
            </li>
            <li><a href="dokumanlar.html" class="header-nav-link font-body-md text-body-md transition-colors">Dökümanlar</a></li>
            <li><a href="hakkimizda.html" class="header-nav-link font-body-md text-body-md transition-colors">Hakkımızda</a></li>
            <li><a href="iletisim.html" class="header-nav-link font-body-md text-body-md transition-colors">İletişim</a></li>
          </ul>
          <div class="header-search hidden lg:flex items-center gap-2">
            <input type="search" class="header-search-input font-body-md text-body-md px-3 py-2" placeholder="Ürün ara..." aria-label="Ürün ara" id="header-search-input">
            <button type="button" class="header-search-btn flex min-h-[44px] min-w-[44px] items-center justify-center px-4 text-white transition-all hover:brightness-110" aria-label="Ara" id="header-search-btn">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-5 w-5" aria-hidden="true">
                <circle cx="11" cy="11" r="8"/>
                <path d="m21 21-4.35-4.35"/>
              </svg>
            </button>
          </div>
        </nav>
        <button type="button" class="mobile-menu-toggle flex flex-col items-center justify-center gap-1.5 p-2.5 lg:hidden" aria-label="Menüyü aç/kapat" aria-expanded="false">
          <span class="block h-0.5 w-6 rounded-sm transition-all"></span>
          <span class="block h-0.5 w-6 rounded-sm transition-all"></span>
          <span class="block h-0.5 w-6 rounded-sm transition-all"></span>
        </button>"""

HERO_OLD = """        <div class="home-hero" id="home-hero">
          <div class="home-hero__layout">
            <div class="home-hero__content">
              <p class="home-hero__badge">
                <span class="home-hero__badge-dot" aria-hidden="true"></span>
                Rusya'da Endüstriyel Tedarik
              </p>
              <h1 class="home-hero__title">
                Endüstriyel <span class="home-hero__accent">Kesim ve Taşlama</span> Çözümleri
              </h1>
              <p class="home-hero__subtitle">
                Rusya'daki Türk firmalarına yüksek kaliteli kesici diskler, elmas kesiciler, flap diskler ve profesyonel uçlar sunuyoruz.
              </p>
              <div class="home-hero__actions">
                <a href="urunler.html" class="btn btn-primary">Ürün Kataloğunu İncele</a>
                <a href="iletisim.html" class="btn home-hero__btn-ghost">İletişime Geç</a>
              </div>
              <div class="home-hero__stats">
                <div class="home-hero__stat">
                  <span class="home-hero__stat-value">24</span>
                  <span class="home-hero__stat-label">Ürün Ailesi</span>
                </div>
                <div class="home-hero__stat">
                  <span class="home-hero__stat-value">90+</span>
                  <span class="home-hero__stat-label">Varyasyon</span>
                </div>
                <div class="home-hero__stat">
                  <span class="home-hero__stat-value">5</span>
                  <span class="home-hero__stat-label">Kategori</span>
                </div>
              </div>
            </div>
            <div class="home-hero__deco-wrap" aria-hidden="true">
              <img
                class="home-hero__deco"
                src="assets/images/abralion-disc.webp"
                alt=""
                width="312"
                height="312"
                loading="lazy"
                decoding="async">
            </div>
          </div>
        </div>"""

HERO_NEW = """        <div class="home-hero relative flex min-h-[520px] items-center overflow-hidden hero-glow px-6 py-12 md:min-h-[560px] md:px-10 md:py-16 lg:min-h-[600px] lg:px-12 lg:py-20" id="home-hero">
          <div class="home-hero__layout relative z-20 grid w-full grid-cols-1 items-center gap-gutter lg:grid-cols-2">
            <div class="home-hero__content space-y-8">
              <p class="home-hero__badge flex items-center gap-2">
                <span class="home-hero__badge-dot h-2 w-2 shrink-0 animate-pulse rounded-full" aria-hidden="true"></span>
                <span class="font-label-caps text-label-caps uppercase tracking-widest text-abrasive-red">Rusya'da Endüstriyel Tedarik</span>
              </p>
              <h1 class="home-hero__title font-headline-display text-headline-lg-mobile md:text-headline-lg lg:text-headline-display tracking-tight text-white">
                Endüstriyel <span class="home-hero__accent text-abrasive-red">Kesim ve Taşlama</span> Çözümleri
              </h1>
              <p class="home-hero__subtitle font-body-lg text-body-lg max-w-xl text-secondary">
                Rusya'daki Türk firmalarına yüksek kaliteli kesici diskler, elmas kesiciler, flap diskler ve profesyonel uçlar sunuyoruz.
              </p>
              <div class="home-hero__actions flex flex-wrap gap-4 pt-2">
                <a href="urunler.html" class="inline-flex items-center rounded bg-abrasive-red px-8 py-4 font-label-caps text-label-caps uppercase text-on-primary-container transition-all hover:brightness-110 active:scale-95">Ürün Kataloğunu İncele</a>
                <a href="iletisim.html" class="home-hero__btn-ghost inline-flex items-center rounded px-8 py-4 font-label-caps text-label-caps uppercase transition-all">İletişime Geç</a>
              </div>
              <div class="home-hero__stats flex flex-wrap gap-8">
                <div class="home-hero__stat flex flex-col">
                  <span class="home-hero__stat-value font-headline-md text-headline-md text-white">24</span>
                  <span class="home-hero__stat-label font-technical-data text-technical-data uppercase text-steel-gray">Ürün Ailesi</span>
                </div>
                <div class="home-hero__stat flex flex-col">
                  <span class="home-hero__stat-value font-headline-md text-headline-md text-white">90+</span>
                  <span class="home-hero__stat-label font-technical-data text-technical-data uppercase text-steel-gray">Varyasyon</span>
                </div>
                <div class="home-hero__stat flex flex-col">
                  <span class="home-hero__stat-value font-headline-md text-headline-md text-white">5</span>
                  <span class="home-hero__stat-label font-technical-data text-technical-data uppercase text-steel-gray">Kategori</span>
                </div>
              </div>
            </div>
            <div class="home-hero__deco-wrap flex items-center justify-center lg:justify-end" aria-hidden="true">
              <img
                class="home-hero__deco"
                src="assets/images/abralion-disc.webp"
                alt=""
                width="312"
                height="312"
                loading="lazy"
                decoding="async">
            </div>
          </div>
        </div>"""

CONTAINER_OLD = """    <section class="home-hero-section section" id="home-hero-wrap">
      <div class="container">"""

CONTAINER_NEW = """    <section class="home-hero-section section" id="home-hero-wrap">
      <div class="container max-w-site mx-auto px-margin-mobile lg:px-margin-desktop">"""


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")
    if HEADER_INNER_OLD not in text:
        raise SystemExit("header block not found")
    if HERO_OLD not in text:
        raise SystemExit("hero block not found")
    text = text.replace(HEADER_INNER_OLD, HEADER_INNER_NEW, 1)
    text = text.replace(HERO_OLD, HERO_NEW, 1)
    text = text.replace(CONTAINER_OLD, CONTAINER_NEW, 1)
    INDEX.write_text(text, encoding="utf-8", newline="\n")
    print("index.html patched (header + hero)")


if __name__ == "__main__":
    main()
