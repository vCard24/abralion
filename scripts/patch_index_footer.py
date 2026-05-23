"""Remove about-preview and replace footer with Precision Industrial Noir."""
from pathlib import Path
import re

INDEX = Path(__file__).resolve().parents[1] / "index.html"

ABOUT_PATTERN = re.compile(
    r"\n    <section class=\"about-preview section\">.*?</section>\n",
    re.DOTALL,
)

NEW_FOOTER = r"""  <footer class="footer bg-carbon-black border-t border-white/5">
    <div class="max-w-7xl mx-auto px-margin-mobile lg:px-margin-desktop py-section-gap grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-gutter">
      <motion class="space-y-6">
        <a href="index.html" class="inline-block" aria-label="Abralion Ana Sayfa">
          <img src="assets/images/logo.svg" alt="Abralion Logo" class="footer-logo h-14 w-auto" data-logo>
        </a>
        <p class="font-body-md text-body-md text-on-surface-variant leading-relaxed">
          Rusya'da faaliyet gösteren EKS-PLAST LLC bünyesinde, Türk firmalarına endüstriyel kesim ve taşlama ürünleri sunan güvenilir çözüm ortağınız.
        </p>
        <div class="flex gap-4">
          <a class="flex h-10 w-10 items-center justify-center rounded-full bg-surface-elevation text-secondary transition-colors hover:text-abrasive-red" href="https://www.abralion.com" target="_blank" rel="noopener noreferrer" aria-label="Web sitesi">
            <span class="material-symbols-outlined" data-icon="language">language</span>
          </a>
          <a class="flex h-10 w-10 items-center justify-center rounded-full bg-surface-elevation text-secondary transition-colors hover:text-abrasive-red" href="mailto:info@abralion.com" aria-label="E-posta">
            <span class="material-symbols-outlined" data-icon="mail">mail</span>
          </a>
        </div>
      </div>
      <div>
        <h4 class="font-label-caps text-label-caps uppercase text-white mb-6 md:mb-8">Hızlı Linkler</h4>
        <ul class="space-y-4 font-body-md text-body-md text-on-surface-variant">
          <li><a class="transition-colors hover:text-abrasive-red" href="index.html">Ana Sayfa</a></li>
          <li><a class="transition-colors hover:text-abrasive-red" href="urunler.html">Ürünlerimiz</a></li>
          <li><a class="transition-colors hover:text-abrasive-red" href="dokumanlar.html">Dökümanlar</a></li>
          <li><a class="transition-colors hover:text-abrasive-red" href="hakkimizda.html">Hakkımızda</a></li>
          <li><a class="transition-colors hover:text-abrasive-red" href="iletisim.html">İletişim</a></li>
        </ul>
      </div>
      <div>
        <h4 class="font-label-caps text-label-caps uppercase text-white mb-6 md:mb-8">Kategoriler</h4>
        <ul class="space-y-4 font-body-md text-body-md text-on-surface-variant">
          <li><a class="transition-colors hover:text-abrasive-red" href="urunler.html?kategori=kesici-taslama-flap-disk">Kesici - Taşlama - Flap Disk</a></li>
          <li><a class="transition-colors hover:text-abrasive-red" href="urunler.html?kategori=elmas-kesici">Elmas Kesici</a></li>
          <li><a class="transition-colors hover:text-abrasive-red" href="urunler.html?kategori=uclar">Kırıcı &amp; Delici</a></li>
          <li><a class="transition-colors hover:text-abrasive-red" href="urunler.html?kategori=maket-bicaklari">Maket Bıçakları</a></li>
          <li><a class="transition-colors hover:text-abrasive-red" href="urunler.html?kategori=metreler">Metreler</a></li>
          <li><a class="transition-colors hover:text-abrasive-red" href="karsilastir.html">Ürün Karşılaştırma</a></li>
        </ul>
      </motion>
      <div>
        <h4 class="font-label-caps text-label-caps uppercase text-white mb-6 md:mb-8">İletişim</h4>
        <ul class="space-y-6 font-body-md text-body-md text-on-surface-variant">
          <li class="flex items-start gap-3">
            <span class="material-symbols-outlined shrink-0 text-abrasive-red" data-icon="call">call</span>
            <span>
              <a class="transition-colors hover:text-abrasive-red" href="tel:+74951424267">8 (495) 142-42-67</a><br>
              <a class="transition-colors hover:text-abrasive-red" href="tel:+79857896062">+7 985 789-60-62</a>
            </span>
          </li>
          <li class="flex items-start gap-3">
            <span class="material-symbols-outlined shrink-0 text-abrasive-red" data-icon="mail">mail</span>
            <a class="transition-colors hover:text-abrasive-red" href="mailto:info@abralion.com">info@abralion.com</a>
          </li>
          <li class="flex items-start gap-3">
            <span class="material-symbols-outlined shrink-0 text-abrasive-red" data-icon="language">language</span>
            <a class="transition-colors hover:text-abrasive-red" href="https://www.abralion.com" target="_blank" rel="noopener noreferrer">www.abralion.com</a>
          </li>
          <li class="flex items-start gap-3">
            <span class="material-symbols-outlined shrink-0 text-abrasive-red" data-icon="location_on">location_on</span>
            <span>Rusya — EKS-PLAST LLC<br><span class="text-xs opacity-60">Endüstriyel tedarik operasyon merkezi</span></span>
          </li>
        </ul>
      </motion>
    </motion>
    <div class="max-w-7xl mx-auto px-margin-mobile lg:px-margin-desktop py-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4">
      <p class="font-body-md text-sm text-on-surface-variant">&copy; 2026 Abralion — EKS-PLAST LLC. Tüm hakları saklıdır.</p>
      <div class="flex flex-wrap justify-center gap-6 font-body-md text-sm text-on-surface-variant">
        <a class="transition-colors hover:text-abrasive-red" href="#">Gizlilik Politikası</a>
        <a class="transition-colors hover:text-abrasive-red" href="#">Kullanım Koşulları</a>
        <a class="transition-colors hover:text-abrasive-red" href="#">KVKK</a>
      </motion>
    </motion>
  </footer>"""


def main() -> None:
    footer = NEW_FOOTER.replace("<motion class=", "<div class=").replace("<motion>", "<div>")
    footer = footer.replace("</motion>", "</div>")

    text = INDEX.read_text(encoding="utf-8")

    new_text, count = ABOUT_PATTERN.subn("\n", text)
    if count != 1:
        raise SystemExit(f"about-preview removal failed (matches={count})")

    footer_start = new_text.find('  <footer class="footer">')
    footer_end = new_text.find("  </footer>", footer_start)
    if footer_start == -1 or footer_end == -1:
        raise SystemExit("footer block not found")

    footer_end += len("  </footer>")
    new_text = new_text[:footer_start] + footer + "\n" + new_text[footer_end:]

    INDEX.write_text(new_text, encoding="utf-8", newline="\n")
    print("index.html: about-preview removed, footer updated")


if __name__ == "__main__":
    main()
