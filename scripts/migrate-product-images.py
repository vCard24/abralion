# -*- coding: utf-8 -*-
"""
Eski ürün görsel klasörlerini yeni slug yapısına taşır, katalog path'lerini günceller.
"""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "images" / "products"
CATALOG_PATH = ROOT / "assets" / "js" / "products-data.js"
ROOT_CATALOG = ROOT / "products-data.js"

# Eski klasör → yeni klasör (dosyalar taşınır, eski klasör silinir)
FOLDER_MIGRATIONS = {
    "asfalt-icin-elmas-kesme-diski": "asfalt-elmas-kesme-diski",
    "guclendirilmis-beton-icin-elmas-kesme-diski": "beton-elmas-kesme-diski",
    "granit-ve-mermer-segmentli-taslama-diski": "granit-mermer-segmentli-taslama-diski",
    "cok-fonksiyonlu-cam-ve-seramik-matkap-ucu-4-kesicili": "cam-seramik-matkap-ucu",
    "sds-max-burc-aleti-tarakli-murc": "sds-max-burc-aleti",
    "sds-plus-4-kesicili-beton-matkap-ucu-quadro": "sds-plus-4-kesicili-beton-matkap-ucu",
    "miknatisli-anahtar-ucu-manyetik-somun-adaptoru": "miknatisli-anahtar-ucu",
    "duz-keski-sds-plus": "duz-keski",
    "duz-keski-sds-max": "duz-keski",
    "sivri-uclu-keski-murc-sds-plus": "sivri-uclu-keski-murc",
    "sivri-uclu-keski-murc-sds-max": "sivri-uclu-keski-murc",
    "profesyonel-plastik-maket-bicagi": "profesyonel-maket-bicagi",
    "profesyonel-metal-maket-bicagi": "profesyonel-maket-bicagi",
    "maket-bicagi-yedek-ucu": "profesyonel-maket-bicagi",
}

# normalize.py CUSTOM_IMAGES — yeni slug anahtarlarıyla
LEGACY_GALLERY = {
    "metal-inox-kesme-tasi": [
        {"src": "assets/images/products/metal-inox-kesme-tasi/metal-inox-kesme-tasi-genel.png", "alt": "Metal / Inox Kesme Taşı - Genel görünüm"},
        {"src": "assets/images/products/metal-inox-kesme-tasi/metal-inox-kesme-tasi-115x1.png", "alt": "Metal / Inox Kesme Taşı - Ø115 × 1,0 mm"},
        {"src": "assets/images/products/metal-inox-kesme-tasi/metal-inox-kesme-tasi-125x1.png", "alt": "Metal / Inox Kesme Taşı - Ø125 × 1,0 mm"},
        {"src": "assets/images/products/metal-inox-kesme-tasi/metal-inox-kesme-tasi-125x16.png", "alt": "Metal / Inox Kesme Taşı - Ø125 × 1,6 mm"},
        {"src": "assets/images/products/metal-inox-kesme-tasi/metal-inox-kesme-tasi-125x25.png", "alt": "Metal / Inox Kesme Taşı - Ø125 × 2,5 mm"},
        {"src": "assets/images/products/metal-inox-kesme-tasi/metal-inox-kesme-tasi-150x3.png", "alt": "Metal / Inox Kesme Taşı - Ø150 × 3,0 mm"},
        {"src": "assets/images/products/metal-inox-kesme-tasi/metal-inox-kesme-tasi-180x25.png", "alt": "Metal / Inox Kesme Taşı - Ø180 × 2,5 mm"},
        {"src": "assets/images/products/metal-inox-kesme-tasi/metal-inox-kesme-tasi-180x3.png", "alt": "Metal / Inox Kesme Taşı - Ø180 × 3,0 mm"},
        {"src": "assets/images/products/metal-inox-kesme-tasi/metal-inox-kesme-tasi-230x2.png", "alt": "Metal / Inox Kesme Taşı - Ø230 × 2,0 mm"},
        {"src": "assets/images/products/metal-inox-kesme-tasi/metal-inox-kesme-tasi-230x25.png", "alt": "Metal / Inox Kesme Taşı - Ø230 × 2,5 mm"},
    ],
    "355mm-metal-sabit-tezgah-kesme-diski": [
        {"src": "assets/images/products/355mm-metal-sabit-tezgah-kesme-diski/355mm-metal-sabit-tezgah-kesme-diski-ana.png", "alt": "355mm Metal Sabit Tezgah Kesme Diski ana ürün görseli"},
        {"src": "assets/images/products/355mm-metal-sabit-tezgah-kesme-diski/355mm-metal-sabit-tezgah-kesme-diski-detay.png", "alt": "355mm Kesme Diski detay görseli"},
    ],
    "metal-inox-taslama-diski": [
        {"src": "assets/images/products/metal-inox-taslama-diski/metal-inox-taslama-diski-genel.png", "alt": "Metal / Inox Taşlama Diski - Genel görünüm"},
        {"src": "assets/images/products/metal-inox-taslama-diski/metal-inox-taslama-diski-125x6.png", "alt": "Metal / Inox Taşlama Diski - Ø125 × 6,0 mm"},
        {"src": "assets/images/products/metal-inox-taslama-diski/metal-inox-taslama-diski-150x6.png", "alt": "Metal / Inox Taşlama Diski - Ø150 × 6,0 mm"},
        {"src": "assets/images/products/metal-inox-taslama-diski/metal-inox-taslama-diski-180x6.png", "alt": "Metal / Inox Taşlama Diski - Ø180 × 6,0 mm"},
        {"src": "assets/images/products/metal-inox-taslama-diski/metal-inox-taslama-diski-180x6-2.png", "alt": "Metal / Inox Taşlama Diski - Ø180 × 6,0 mm (görünüm 2)"},
        {"src": "assets/images/products/metal-inox-taslama-diski/metal-inox-taslama-diski-230x6.png", "alt": "Metal / Inox Taşlama Diski - Ø230 × 6,0 mm"},
        {"src": "assets/images/products/metal-inox-taslama-diski/metal-inox-taslama-diski-detay.png", "alt": "Metal / Inox Taşlama Diski - Detay"},
    ],
    "zr-zirkon-flap-disk": [
        {"src": "assets/images/products/zr-zirkon-flap-disk/zr-zirkon-flap-disk-genel.png", "alt": "ZR Zirkon Flap Disk - Genel görünüm"},
        {"src": "assets/images/products/zr-zirkon-flap-disk/zr-zirkon-flap-disk-125x22.png", "alt": "ZR Zirkon Flap Disk - Ø125 × 22 mm · 40#"},
        {"src": "assets/images/products/zr-zirkon-flap-disk/zr-zirkon-flap-disk-kullanim.png", "alt": "ZR Zirkon Flap Disk - Kullanım"},
    ],
    "ao-aluminyum-oksit-flap-disk": [
        {"src": "assets/images/products/ao-aluminyum-oksit-flap-disk/ao-aluminyum-oksit-flap-disk-genel.png", "alt": "AO Alüminyum Oksit Flap Disk - Genel görünüm"},
        {"src": "assets/images/products/ao-aluminyum-oksit-flap-disk/ao-aluminyum-oksit-flap-disk-125x22.png", "alt": "AO Alüminyum Oksit Flap Disk - Ø125 × 22 mm · 40#"},
        {"src": "assets/images/products/ao-aluminyum-oksit-flap-disk/ao-aluminyum-oksit-flap-disk-kullanim.png", "alt": "AO Alüminyum Oksit Flap Disk - Kullanım"},
    ],
    "segmentli-standart-elmas-kesici": [
        {"src": "assets/images/products/segmentli-standart-elmas-kesici/segmentli-standart-elmas-kesici-125.png", "alt": "Segmentli Standart Elmas Kesici - Ø125 mm"},
        {"src": "assets/images/products/segmentli-standart-elmas-kesici/segmentli-standart-elmas-kesici-kutu.png", "alt": "Segmentli Standart Elmas Kesici - Ø230 mm kutu"},
        {"src": "assets/images/products/segmentli-standart-elmas-kesici/segmentli-standart-elmas-kesici-kullanim.png", "alt": "Segmentli Standart Elmas Kesici - Kullanım"},
    ],
    "ultra-ince-elmas-disk": [
        {"src": "assets/images/products/ultra-ince-elmas-disk/ultra-ince-elmas-disk-125.png", "alt": "Ultra İnce Elmas Disk - Ø125 mm"},
        {"src": "assets/images/products/ultra-ince-elmas-disk/ultra-ince-elmas-disk-kutu.png", "alt": "Ultra İnce Elmas Disk - Blister kutu"},
        {"src": "assets/images/products/ultra-ince-elmas-disk/ultra-ince-elmas-disk-kullanim.png", "alt": "Ultra İnce Elmas Disk - Kullanım"},
    ],
    "granit-mermer-segmentli-taslama-diski": [
        {"src": "assets/images/products/granit-mermer-segmentli-taslama-diski/granit-ve-mermer-segmentli-taslama-diski-125.png", "alt": "Granit Mermer Segmentli Taşlama Diski - Ø125 mm"},
        {"src": "assets/images/products/granit-mermer-segmentli-taslama-diski/granit-ve-mermer-segmentli-taslama-diski-ust.png", "alt": "Granit Mermer Segmentli Taşlama Diski - Üst görünüm"},
        {"src": "assets/images/products/granit-mermer-segmentli-taslama-diski/granit-ve-mermer-segmentli-taslama-diski-kutu.png", "alt": "Granit Mermer Segmentli Taşlama Diski - Ambalaj"},
        {"src": "assets/images/products/granit-mermer-segmentli-taslama-diski/granit-ve-mermer-segmentli-taslama-diski-kullanim.png", "alt": "Granit Mermer Segmentli Taşlama Diski - Kullanım"},
    ],
    "asfalt-elmas-kesme-diski": [
        {"src": "assets/images/products/asfalt-elmas-kesme-diski/asfalt-icin-elmas-kesme-diski-350.png", "alt": "Asfalt Elmas Kesme Diski - Ø350 mm"},
        {"src": "assets/images/products/asfalt-elmas-kesme-diski/asfalt-icin-elmas-kesme-diski-kullanim.png", "alt": "Asfalt Elmas Kesme Diski - Kullanım"},
    ],
    "beton-elmas-kesme-diski": [
        {"src": "assets/images/products/beton-elmas-kesme-diski/guclendirilmis-beton-icin-elmas-kesme-diski-400.png", "alt": "Beton Elmas Kesme Diski - Ø400 mm"},
        {"src": "assets/images/products/beton-elmas-kesme-diski/guclendirilmis-beton-icin-elmas-kesme-diski-kullanim.png", "alt": "Beton Elmas Kesme Diski - Kullanım"},
    ],
    "sds-max-burc-aleti": [
        {"src": "assets/images/products/sds-max-burc-aleti/sds-max-burc-aleti-tarakli-murc-ana.png", "alt": "SDS MAX Burç Aleti - Ana görsel"},
        {"src": "assets/images/products/sds-max-burc-aleti/sds-max-burc-aleti-tarakli-murc-bas.png", "alt": "SDS MAX Burç Aleti - 4×4 tarak başı"},
        {"src": "assets/images/products/sds-max-burc-aleti/sds-max-burc-aleti-tarakli-murc-kullanim.png", "alt": "SDS MAX Burç Aleti - Kullanım"},
    ],
    "hss-matkap-ucu": [
        {"src": "assets/images/products/hss-matkap-ucu/hss-matkap-ucu-ana.png", "alt": "HSS Matkap Ucu ana ürün görseli"},
        {"src": "assets/images/products/hss-matkap-ucu/hss-matkap-ucu-kullanim.png", "alt": "HSS Matkap Ucu aktif kullanım"},
    ],
    "sds-plus-4-kesicili-beton-matkap-ucu": [
        {"src": "assets/images/products/sds-plus-4-kesicili-beton-matkap-ucu/sds-plus-4-kesicili-beton-matkap-ucu-quadro-ana.png", "alt": "SDS Plus 4 Kesicili Beton Matkap Ucu ana ürün görseli"},
        {"src": "assets/images/products/sds-plus-4-kesicili-beton-matkap-ucu/sds-plus-4-kesicili-beton-matkap-ucu-quadro-kullanim.png", "alt": "SDS Plus 4 Kesicili Beton Matkap Ucu aktif kullanım"},
    ],
    "miknatisli-anahtar-ucu": [
        {"src": "assets/images/products/miknatisli-anahtar-ucu/miknatisli-anahtar-ucu-manyetik-somun-adaptoru-ana.png", "alt": "Mıknatıslı Anahtar Ucu ana ürün görseli"},
        {"src": "assets/images/products/miknatisli-anahtar-ucu/miknatisli-anahtar-ucu-manyetik-somun-adaptoru-kullanim.png", "alt": "Mıknatıslı Anahtar Ucu aktif kullanım"},
    ],
    "ph2-manyetik-bits-uc": [
        {"src": "assets/images/products/ph2-manyetik-bits-uc/ph2-manyetik-bits-uc-ana.png", "alt": "PH2 Manyetik Bits Uç ana ürün görseli"},
        {"src": "assets/images/products/ph2-manyetik-bits-uc/ph2-manyetik-bits-uc-kullanim.png", "alt": "PH2 Manyetik Bits Uç aktif kullanım"},
    ],
    "duz-keski": [
        {"src": "assets/images/products/duz-keski/duz-keski-sds-plus-ana.png", "alt": "Düz Keski SDS Plus - Ana görsel"},
        {"src": "assets/images/products/duz-keski/duz-keski-sds-plus-kullanim.png", "alt": "Düz Keski SDS Plus - Kullanım"},
        {"src": "assets/images/products/duz-keski/duz-keski-sds-max-ana.png", "alt": "Düz Keski SDS Max - Ana görsel"},
        {"src": "assets/images/products/duz-keski/duz-keski-sds-max-kullanim.png", "alt": "Düz Keski SDS Max - Kullanım"},
    ],
    "sivri-uclu-keski-murc": [
        {"src": "assets/images/products/sivri-uclu-keski-murc/sivri-uclu-keski-murc-sds-plus-ana.png", "alt": "Sivri Uçlu Keski / Murç SDS Plus - Ana görsel"},
        {"src": "assets/images/products/sivri-uclu-keski-murc/sivri-uclu-keski-murc-sds-plus-kullanim.png", "alt": "Sivri Uçlu Keski / Murç SDS Plus - Kullanım"},
        {"src": "assets/images/products/sivri-uclu-keski-murc/sivri-uclu-keski-murc-sds-max-ana.png", "alt": "Sivri Uçlu Keski / Murç SDS Max - Ana görsel"},
        {"src": "assets/images/products/sivri-uclu-keski-murc/sivri-uclu-keski-murc-sds-max-kullanim.png", "alt": "Sivri Uçlu Keski / Murç SDS Max - Kullanım"},
    ],
    "cam-seramik-matkap-ucu": [
        {"src": "assets/images/products/cam-seramik-matkap-ucu/cok-fonksiyonlu-cam-ve-seramik-matkap-ucu-4-kesicili-ana.png", "alt": "Cam Seramik Matkap Ucu ana ürün görseli"},
        {"src": "assets/images/products/cam-seramik-matkap-ucu/cok-fonksiyonlu-cam-ve-seramik-matkap-ucu-4-kesicili-kutu.png", "alt": "Cam Seramik Matkap Ucu ambalaj"},
        {"src": "assets/images/products/cam-seramik-matkap-ucu/cok-fonksiyonlu-cam-ve-seramik-matkap-ucu-4-kesicili-kullanim.png", "alt": "Cam Seramik Matkap Ucu aktif kullanım"},
    ],
    "profesyonel-maket-bicagi": [
        {"src": "assets/images/products/profesyonel-maket-bicagi/profesyonel-plastik-maket-bicagi-ana.png", "alt": "Profesyonel Plastik Maket Bıçağı - Ana görsel"},
        {"src": "assets/images/products/profesyonel-maket-bicagi/profesyonel-plastik-maket-bicagi-detay.png", "alt": "Profesyonel Plastik Maket Bıçağı - Detay"},
        {"src": "assets/images/products/profesyonel-maket-bicagi/profesyonel-plastik-maket-bicagi-kutu.png", "alt": "Profesyonel Plastik Maket Bıçağı - Ambalaj"},
        {"src": "assets/images/products/profesyonel-maket-bicagi/profesyonel-metal-maket-bicagi-ana.png", "alt": "Profesyonel Metal Maket Bıçağı - Ana görsel"},
        {"src": "assets/images/products/profesyonel-maket-bicagi/profesyonel-metal-maket-bicagi-detay.png", "alt": "Profesyonel Metal Maket Bıçağı - Detay"},
        {"src": "assets/images/products/profesyonel-maket-bicagi/maket-bicagi-yedek-ucu-ana.png", "alt": "Maket Bıçağı Yedek Ucu - Ana görsel"},
        {"src": "assets/images/products/profesyonel-maket-bicagi/maket-bicagi-yedek-ucu-detay.png", "alt": "Maket Bıçağı Yedek Ucu - Detay"},
    ],
    "abs-govdeli-profesyonel-serit-metre": [
        {"src": "assets/images/products/abs-govdeli-profesyonel-serit-metre/abs-govdeli-profesyonel-serit-metre-ana.png", "alt": "ABS Gövdeli Profesyonel Şerit Metre ana ürün görseli"},
        {"src": "assets/images/products/abs-govdeli-profesyonel-serit-metre/abs-govdeli-profesyonel-serit-metre-detay.png", "alt": "Profesyonel Şerit Metre detay"},
        {"src": "assets/images/products/abs-govdeli-profesyonel-serit-metre/abs-govdeli-profesyonel-serit-metre-serit.png", "alt": "Profesyonel Şerit Metre şerit"},
        {"src": "assets/images/products/abs-govdeli-profesyonel-serit-metre/abs-govdeli-profesyonel-serit-metre-kutu.png", "alt": "Profesyonel Şerit Metre ambalaj"},
        {"src": "assets/images/products/abs-govdeli-profesyonel-serit-metre/abs-govdeli-profesyonel-serit-metre-display.png", "alt": "Profesyonel Şerit Metre teşhir kutusu"},
        {"src": "assets/images/products/abs-govdeli-profesyonel-serit-metre/abs-govdeli-profesyonel-serit-metre-kullanim.png", "alt": "Profesyonel Şerit Metre aktif kullanım"},
    ],
}

# Yeni slug → kart kaynağı (taşıma sonrası kopyalanacak)
KART_SOURCES = {
    "asfalt-elmas-kesme-diski": "asfalt-icin-elmas-kesme-diski-kart.jpg",
    "beton-elmas-kesme-diski": "guclendirilmis-beton-icin-elmas-kesme-diski-kart.jpg",
    "granit-mermer-segmentli-taslama-diski": "granit-ve-mermer-segmentli-taslama-diski-kart.jpg",
    "cam-seramik-matkap-ucu": "cok-fonksiyonlu-cam-ve-seramik-matkap-ucu-4-kesicili-kart.jpg",
    "sds-max-burc-aleti": "sds-max-burc-aleti-tarakli-murc-kart.jpg",
    "sds-plus-4-kesicili-beton-matkap-ucu": "sds-plus-4-kesicili-beton-matkap-ucu-quadro-kart.jpg",
    "miknatisli-anahtar-ucu": "miknatisli-anahtar-ucu-manyetik-somun-adaptoru-kart.jpg",
    "duz-keski": "duz-keski-sds-plus-kart.jpg",
    "sivri-uclu-keski-murc": "sivri-uclu-keski-murc-sds-plus-kart.jpg",
    "profesyonel-maket-bicagi": "profesyonel-plastik-maket-bicagi-kart.jpg",
}


def migrate_folders():
    moved = 0
    for old_slug, new_slug in FOLDER_MIGRATIONS.items():
        src_dir = IMG / old_slug
        if not src_dir.is_dir():
            continue
        dst_dir = IMG / new_slug
        dst_dir.mkdir(parents=True, exist_ok=True)
        for f in src_dir.iterdir():
            if f.name == ".gitkeep":
                continue
            target = dst_dir / f.name
            if target.exists():
                continue
            shutil.move(str(f), str(target))
            moved += 1
        shutil.rmtree(src_dir, ignore_errors=True)
        print(f"  {old_slug} -> {new_slug}")
    print(f"Taşındı: {moved} dosya")


def ensure_kart_images():
    for slug, kart_name in KART_SOURCES.items():
        folder = IMG / slug
        if not folder.is_dir():
            continue
        target = folder / f"{slug}-kart.jpg"
        source = folder / kart_name
        if target.exists():
            continue
        if source.is_file():
            shutil.copy2(source, target)
            print(f"  kart: {slug}-kart.jpg")


def load_catalog():
    raw = CATALOG_PATH.read_text(encoding="utf-8")
    match = re.search(r"window\.ABRALION_CATALOG\s*=\s*(\{.*\})\s*;?\s*$", raw, re.S)
    return json.loads(match.group(1)), raw


def save_catalog(data, template_raw):
    body = json.dumps(data, ensure_ascii=False, indent=2)
    new_raw = re.sub(
        r"window\.ABRALION_CATALOG\s*=\s*\{.*\}\s*;?\s*$",
        f"window.ABRALION_CATALOG = {body};",
        template_raw,
        flags=re.S,
    )
    CATALOG_PATH.write_text(new_raw, encoding="utf-8")
    if ROOT_CATALOG.exists():
        ROOT_CATALOG.write_text(new_raw, encoding="utf-8")


def sync_catalog_images():
    data, raw = load_catalog()
    updated = 0
    for product in data["products"]:
        slug = product["slug"]
        if slug not in LEGACY_GALLERY:
            continue
        product["images"] = LEGACY_GALLERY[slug]
        updated += 1
    save_catalog(data, raw)
    print(f"Katalog güncellendi: {updated} ürün galerisi")


def list_remaining_folders():
    valid = {p["slug"] for p in load_catalog()[0]["products"]}
    extra = []
    for d in sorted(IMG.iterdir()):
        if not d.is_dir():
            continue
        if d.name not in valid:
            extra.append(d.name)
    if extra:
        print("Beklenmeyen klasörler (manuel kontrol):", ", ".join(extra))
    else:
        print("Klasör listesi temiz: yalnızca 22 aktif slug.")


def main():
    print("1) Eski klasörler taşınıyor...")
    migrate_folders()
    print("2) Kart görselleri eşleniyor...")
    ensure_kart_images()
    print("3) products-data.js güncelleniyor...")
    sync_catalog_images()
    print("4) Kontrol...")
    list_remaining_folders()


if __name__ == "__main__":
    main()
