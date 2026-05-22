#!/usr/bin/env python3
"""Tüm HTML sayfalarında header ve footer şablonunu günceller."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SR_ONLY = '  <a href="#main-content" class="sr-only">İçeriğe atla</a>\n\n'


def header_html(base: str) -> str:
    return f"""  <header class="header">
    <div class="container">
      <div class="header-container">
        <a href="{base}index.html" class="header-logo-link" aria-label="Abralion Ana Sayfa">
          <img src="{base}assets/images/logo.svg" alt="Abralion Logo" class="header-logo" data-logo>
        </a>
        <nav class="header-nav" aria-label="Ana navigasyon">
          <ul class="header-nav-list">
            <li><a href="{base}index.html" class="header-nav-link">Ana Sayfa</a></li>
            <li class="header-nav-dropdown">
              <a href="{base}urunler.html" class="header-nav-link">
                Ürünlerimiz
                <span class="dropdown-arrow">▼</span>
              </a>
              <ul class="dropdown-menu mega-menu" id="mega-menu"></ul>
            </li>
            <li>
              <a href="{base}karsilastir.html" class="header-nav-link">
                Karşılaştır
                <span class="compare-badge" style="display: none;">0</span>
              </a>
            </li>
            <li><a href="{base}dokumanlar.html" class="header-nav-link">Dökümanlar</a></li>
            <li><a href="{base}hakkimizda.html" class="header-nav-link">Hakkımızda</a></li>
            <li><a href="{base}iletisim.html" class="header-nav-link">İletişim</a></li>
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
        </button>
      </div>
    </div>
  </header>"""


def footer_html(base: str) -> str:
    return f"""  <footer class="footer">
    <div class="container">
      <div class="footer-container">
        <div class="footer-section">
          <img src="{base}assets/images/logo.svg" alt="Abralion Logo" class="footer-logo" data-logo>
          <p class="footer-description">
            Rusya'da faaliyet gösteren EKS-PLAST LLC bünyesinde, Türk firmalarına endüstriyel kesim ve taşlama ürünleri sunan güvenilir çözüm ortağınız.
          </p>
        </div>
        <div class="footer-section">
          <h3>Hızlı Linkler</h3>
          <ul class="footer-links">
            <li><a href="{base}index.html">Ana Sayfa</a></li>
            <li><a href="{base}urunler.html">Ürünlerimiz</a></li>
            <li><a href="{base}dokumanlar.html">Dökümanlar</a></li>
            <li><a href="{base}hakkimizda.html">Hakkımızda</a></li>
            <li><a href="{base}iletisim.html">İletişim</a></li>
          </ul>
        </div>
        <div class="footer-section">
          <h3>Kategoriler</h3>
          <ul class="footer-links">
            <li><a href="{base}urunler.html?kategori=kesici-taslama-flap-disk">Kesici - Taşlama - Flap Disk</a></li>
            <li><a href="{base}urunler.html?kategori=elmas-kesici">Elmas Kesici</a></li>
            <li><a href="{base}urunler.html?kategori=uclar">Kırıcı & Delici</a></li>
            <li><a href="{base}urunler.html?kategori=maket-bicaklari">Maket Bıçakları</a></li>
            <li><a href="{base}urunler.html?kategori=metreler">Metreler</a></li>
            <li><a href="{base}karsilastir.html">Ürün Karşılaştırma</a></li>
          </ul>
        </div>
        <div class="footer-section">
          <h3>İletişim</h3>
          <ul class="footer-links">
            <li><a href="{base}iletisim.html">İletişim Formu</a></li>
            <li><a href="mailto:info@abralion.com">info@abralion.com</a></li>
            <li><a href="https://www.abralion.com" target="_blank" rel="noopener noreferrer">www.abralion.com</a></li>
            <li><a href="tel:+74951424267">8 (495) 142-42-67</a></li>
            <li><a href="tel:+79857896062">+7 985 789-60-62</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2026 Abralion — EKS-PLAST LLC. Tüm hakları saklıdır.</p>
      </div>
    </div>
  </footer>"""


HEADER_RE = re.compile(r"<header class=\"header\">.*?</header>", re.DOTALL)
FOOTER_RE = re.compile(r"<footer class=\"footer\">.*?</footer>", re.DOTALL)
SR_RE = re.compile(r"\s*<a href=\"#main-content\" class=\"sr-only\">.*?</a>\s*\n?", re.DOTALL)


def update_file(path: Path) -> bool:
    base = "../" if path.parent.name == "urun" else ""
    text = path.read_text(encoding="utf-8")
    original = text

    if not HEADER_RE.search(text) or not FOOTER_RE.search(text):
        print(f"SKIP (no header/footer): {path.relative_to(ROOT)}")
        return False

    text = HEADER_RE.sub(header_html(base), text, count=1)
    text = FOOTER_RE.sub(footer_html(base), text, count=1)

    if SR_RE.search(text):
        text = SR_RE.sub(SR_ONLY, text, count=1)
    else:
        text = re.sub(r"(<body[^>]*>)\s*", r"\1\n" + SR_ONLY, text, count=1)

    text = text.replace("    <header class=\"header\">", "  <header class=\"header\">")
    text = text.replace("    <footer class=\"footer\">", "  <footer class=\"footer\">")
    text = re.sub(
        r"(<body[^>]*>)\s*<a href=\"#main-content\"",
        r"\1\n  <a href=\"#main-content\"",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"</a>\s*<header", "</a>\n\n  <header", text)
    text = re.sub(r"</main>\s*<footer", "</main>\n\n  <footer", text)

    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"OK: {path.relative_to(ROOT)}")
        return True
    print(f"UNCHANGED: {path.relative_to(ROOT)}")
    return False


def main():
    files = sorted(ROOT.glob("*.html")) + sorted((ROOT / "urun").glob("*.html"))
    n = sum(1 for f in files if update_file(f))
    print(f"\n{n} dosya güncellendi.")


if __name__ == "__main__":
    main()
