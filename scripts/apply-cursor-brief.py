# -*- coding: utf-8 -*-
"""CURSOR_BRIEF.md görev 1, 4, 5, 6 yardımcı scripti."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URUN = ROOT / "urun"
IMAGES = ROOT / "assets" / "images" / "products"

NEW_IMAGE_DIRS = [
    "zr-zirkon-flap-disk",
    "segmentli-standart-elmas-kesici",
    "ultra-ince-elmas-disk",
    "granit-mermer-segmentli-taslama-diski",
    "asfalt-elmas-kesme-diski",
    "beton-elmas-kesme-diski",
    "genel-amacli-elmas-kesme-diski",
    "sds-plus-2-kesicili-beton-matkap-ucu",
    "sds-plus-4-kesicili-beton-matkap-ucu",
    "duz-keski",
    "sivri-uclu-keski-murc",
    "cam-seramik-matkap-ucu",
    "sds-max-burc-aleti",
    "miknatisli-anahtar-ucu",
    "ph2-manyetik-bits-uc",
    "profesyonel-maket-bicagi",
]

ROOT_HTML = [
    "index.html",
    "urunler.html",
    "hakkimizda.html",
    "dokumanlar.html",
    "iletisim.html",
    "karsilastir.html",
]

FOOTER_OLD = """          <li><a class="transition-colors hover:text-abrasive-red" href="urunler.html?kategori=uclar">Kırıcı &amp; Delici</a></li>
          <li><a class="transition-colors hover:text-abrasive-red" href="urunler.html?kategori=maket-bicaklari">Maket Bıçakları</a></li>
          <li><a class="transition-colors hover:text-abrasive-red" href="urunler.html?kategori=metreler">Metreler</a></li>"""

FOOTER_NEW = """          <li><a class="transition-colors hover:text-abrasive-red" href="urunler.html?kategori=kirici-delici">Kırıcı &amp; Delici</a></li>
          <li><a class="transition-colors hover:text-abrasive-red" href="urunler.html?kategori=olcum-kesim">Metreler &amp; Maket Bıçakları</a></li>"""


def delete_old_urun_pages():
    removed = 0
    for f in URUN.glob("*.html"):
        f.unlink()
        removed += 1
    print(f"Silindi: {removed} urun/*.html")


def create_image_dirs():
    for slug in NEW_IMAGE_DIRS:
        d = IMAGES / slug
        d.mkdir(parents=True, exist_ok=True)
        keep = d / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")
    print(f"Oluşturuldu: {len(NEW_IMAGE_DIRS)} görsel klasörü")


def update_root_footers():
    for name in ROOT_HTML:
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        if FOOTER_OLD in text:
            text = text.replace(FOOTER_OLD, FOOTER_NEW)
        text = text.replace('href="urunler.html?kategori=uclar"', 'href="urunler.html?kategori=kirici-delici"')
        text = text.replace('href="urunler.html?kategori=metreler"', 'href="urunler.html?kategori=olcum-kesim"')
        text = text.replace('href="urunler.html?kategori=maket-bicaklari"', 'href="urunler.html?kategori=olcum-kesim"')
        path.write_text(text, encoding="utf-8")
    print("Güncellendi: kök sayfa footer + hakkimizda linkleri")


def generate_pages():
    subprocess.check_call(["python", str(ROOT / "scripts" / "generate-product-pages.py")], cwd=ROOT)


def main():
    delete_old_urun_pages()
    create_image_dirs()
    update_root_footers()
    generate_pages()
    print("Tamamlandı.")


if __name__ == "__main__":
    main()
