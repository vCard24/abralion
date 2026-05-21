# -*- coding: utf-8 -*-
import json
import re
import unicodedata
from pathlib import Path

def slugify(text):
    text = text.lower().strip()
    tr = str.maketrans("çğıöşü", "cgiosu")
    text = text.translate(tr)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

CATEGORY_IDS = {
    "Kesici - Taşlama - Flap Disk": "kesici-taslama-flap-disk",
    "Elmas Kesici": "elmas-kesici",
    "Kırıcı & Delici": "uclar",
    "Maket Bıçakları": "maket-bicaklari",
    "Metreler": "metreler",
}

SCHEMA_MAP = {
    "Kesici - Taşlama - Flap Disk": "disk-kesici-taslama",
    "Elmas Kesici": "disk-elmas",
    "Kırıcı & Delici": "matkap-uc",
    "Maket Bıçakları": "maket",
    "Metreler": "metre",
}

# Ürün görselleri (slug → images); normalize sırasında korunur
CUSTOM_IMAGES = {
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
        {"src": "assets/images/products/355mm-metal-sabit-tezgah-kesme-diski/355mm-metal-sabit-tezgah-kesme-diski-ana.png", "alt": "355mm Metal Sabit Tezgah Kesme Diski - Ana görsel"},
        {"src": "assets/images/products/355mm-metal-sabit-tezgah-kesme-diski/355mm-metal-sabit-tezgah-kesme-diski-detay.png", "alt": "355mm Metal Sabit Tezgah Kesme Diski - Detay görsel"},
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
    "granit-ve-mermer-segmentli-taslama-diski": [
        {"src": "assets/images/products/granit-ve-mermer-segmentli-taslama-diski/granit-ve-mermer-segmentli-taslama-diski-125.png", "alt": "Granit ve Mermer Segmentli Taşlama Diski - Ø125 mm"},
        {"src": "assets/images/products/granit-ve-mermer-segmentli-taslama-diski/granit-ve-mermer-segmentli-taslama-diski-ust.png", "alt": "Granit ve Mermer Segmentli Taşlama Diski - Üst görünüm"},
        {"src": "assets/images/products/granit-ve-mermer-segmentli-taslama-diski/granit-ve-mermer-segmentli-taslama-diski-kutu.png", "alt": "Granit ve Mermer Segmentli Taşlama Diski - Ambalaj"},
        {"src": "assets/images/products/granit-ve-mermer-segmentli-taslama-diski/granit-ve-mermer-segmentli-taslama-diski-kullanim.png", "alt": "Granit ve Mermer Segmentli Taşlama Diski - Kullanım"},
    ],
    "asfalt-icin-elmas-kesme-diski": [
        {"src": "assets/images/products/asfalt-icin-elmas-kesme-diski/asfalt-icin-elmas-kesme-diski-350.png", "alt": "Asfalt İçin Elmas Kesme Diski - Ø350 mm"},
        {"src": "assets/images/products/asfalt-icin-elmas-kesme-diski/asfalt-icin-elmas-kesme-diski-kullanim.png", "alt": "Asfalt İçin Elmas Kesme Diski - Kullanım"},
    ],
    "guclendirilmis-beton-icin-elmas-kesme-diski": [
        {"src": "assets/images/products/guclendirilmis-beton-icin-elmas-kesme-diski/guclendirilmis-beton-icin-elmas-kesme-diski-400.png", "alt": "Güçlendirilmiş Beton İçin Elmas Kesme Diski - Ø400 mm"},
        {"src": "assets/images/products/guclendirilmis-beton-icin-elmas-kesme-diski/guclendirilmis-beton-icin-elmas-kesme-diski-kullanim.png", "alt": "Güçlendirilmiş Beton İçin Elmas Kesme Diski - Kullanım"},
    ],
    "sds-max-burc-aleti-tarakli-murc": [
        {"src": "assets/images/products/sds-max-burc-aleti-tarakli-murc/sds-max-burc-aleti-tarakli-murc-ana.png", "alt": "SDS MAX Burç Aleti (Taraklı Murç) - Ana görsel"},
        {"src": "assets/images/products/sds-max-burc-aleti-tarakli-murc/sds-max-burc-aleti-tarakli-murc-bas.png", "alt": "SDS MAX Burç Aleti (Taraklı Murç) - 4×4 tarak başı"},
        {"src": "assets/images/products/sds-max-burc-aleti-tarakli-murc/sds-max-burc-aleti-tarakli-murc-kullanim.png", "alt": "SDS MAX Burç Aleti (Taraklı Murç) - Kullanım"},
    ],
    "hss-matkap-ucu": [
        {"src": "assets/images/products/hss-matkap-ucu/hss-matkap-ucu-ana.png", "alt": "HSS Matkap Ucu - Ana görsel"},
        {"src": "assets/images/products/hss-matkap-ucu/hss-matkap-ucu-kullanim.png", "alt": "HSS Matkap Ucu - Kullanım"},
    ],
    "sds-plus-4-kesicili-beton-matkap-ucu-quadro": [
        {"src": "assets/images/products/sds-plus-4-kesicili-beton-matkap-ucu-quadro/sds-plus-4-kesicili-beton-matkap-ucu-quadro-ana.png", "alt": "SDS Plus 4 Kesicili Beton Matkap Ucu (Quadro) - Ana görsel"},
        {"src": "assets/images/products/sds-plus-4-kesicili-beton-matkap-ucu-quadro/sds-plus-4-kesicili-beton-matkap-ucu-quadro-kullanim.png", "alt": "SDS Plus 4 Kesicili Beton Matkap Ucu (Quadro) - Betonarme delme"},
    ],
    "miknatisli-anahtar-ucu-manyetik-somun-adaptoru": [
        {"src": "assets/images/products/miknatisli-anahtar-ucu-manyetik-somun-adaptoru/miknatisli-anahtar-ucu-manyetik-somun-adaptoru-ana.png", "alt": "Mıknatıslı Anahtar Ucu (Manyetik Somun Adaptörü) - Ana görsel"},
        {"src": "assets/images/products/miknatisli-anahtar-ucu-manyetik-somun-adaptoru/miknatisli-anahtar-ucu-manyetik-somun-adaptoru-kullanim.png", "alt": "Mıknatıslı Anahtar Ucu (Manyetik Somun Adaptörü) - Kullanım"},
    ],
    "ph2-manyetik-bits-uc": [
        {"src": "assets/images/products/ph2-manyetik-bits-uc/ph2-manyetik-bits-uc-ana.png", "alt": "PH2 Manyetik Bits Uç - Ana görsel"},
        {"src": "assets/images/products/ph2-manyetik-bits-uc/ph2-manyetik-bits-uc-kullanim.png", "alt": "PH2 Manyetik Bits Uç - Kullanım"},
    ],
    "duz-keski-sds-plus": [
        {"src": "assets/images/products/duz-keski-sds-plus/duz-keski-sds-plus-ana.png", "alt": "Düz Keski SDS Plus - Ana görsel"},
        {"src": "assets/images/products/duz-keski-sds-plus/duz-keski-sds-plus-kullanim.png", "alt": "Düz Keski SDS Plus - Kullanım"},
    ],
    "duz-keski-sds-max": [
        {"src": "assets/images/products/duz-keski-sds-max/duz-keski-sds-max-ana.png", "alt": "Düz Keski SDS Max - Ana görsel"},
        {"src": "assets/images/products/duz-keski-sds-max/duz-keski-sds-max-kullanim.png", "alt": "Düz Keski SDS Max - Kullanım"},
    ],
    "sivri-uclu-keski-murc-sds-plus": [
        {"src": "assets/images/products/sivri-uclu-keski-murc-sds-plus/sivri-uclu-keski-murc-sds-plus-ana.png", "alt": "Sivri Uçlu Keski / Murç (SDS Plus) - Ana görsel"},
        {"src": "assets/images/products/sivri-uclu-keski-murc-sds-plus/sivri-uclu-keski-murc-sds-plus-kullanim.png", "alt": "Sivri Uçlu Keski / Murç (SDS Plus) - Kullanım"},
    ],
    "sivri-uclu-keski-murc-sds-max": [
        {"src": "assets/images/products/sivri-uclu-keski-murc-sds-max/sivri-uclu-keski-murc-sds-max-ana.png", "alt": "Sivri Uçlu Keski / Murç (SDS Max) - Ana görsel"},
        {"src": "assets/images/products/sivri-uclu-keski-murc-sds-max/sivri-uclu-keski-murc-sds-max-kullanim.png", "alt": "Sivri Uçlu Keski / Murç (SDS Max) - Kullanım"},
    ],
    "cok-fonksiyonlu-cam-ve-seramik-matkap-ucu-4-kesicili": [
        {"src": "assets/images/products/cok-fonksiyonlu-cam-ve-seramik-matkap-ucu-4-kesicili/cok-fonksiyonlu-cam-ve-seramik-matkap-ucu-4-kesicili-ana.png", "alt": "Çok Fonksiyonlu Cam ve Seramik Matkap Ucu (4 Kesicili) - Ana görsel"},
        {"src": "assets/images/products/cok-fonksiyonlu-cam-ve-seramik-matkap-ucu-4-kesicili/cok-fonksiyonlu-cam-ve-seramik-matkap-ucu-4-kesicili-kutu.png", "alt": "Çok Fonksiyonlu Cam ve Seramik Matkap Ucu (4 Kesicili) - Ambalaj"},
        {"src": "assets/images/products/cok-fonksiyonlu-cam-ve-seramik-matkap-ucu-4-kesicili/cok-fonksiyonlu-cam-ve-seramik-matkap-ucu-4-kesicili-kullanim.png", "alt": "Çok Fonksiyonlu Cam ve Seramik Matkap Ucu (4 Kesicili) - Kullanım"},
    ],
    "profesyonel-plastik-maket-bicagi": [
        {"src": "assets/images/products/profesyonel-plastik-maket-bicagi/profesyonel-plastik-maket-bicagi-ana.png", "alt": "Profesyonel Plastik Maket Bıçağı - Ana görsel"},
        {"src": "assets/images/products/profesyonel-plastik-maket-bicagi/profesyonel-plastik-maket-bicagi-detay.png", "alt": "Profesyonel Plastik Maket Bıçağı - Detay"},
        {"src": "assets/images/products/profesyonel-plastik-maket-bicagi/profesyonel-plastik-maket-bicagi-kutu.png", "alt": "Profesyonel Plastik Maket Bıçağı - Ambalaj"},
        {"src": "assets/images/products/profesyonel-plastik-maket-bicagi/profesyonel-plastik-maket-bicagi-kutu-arka.png", "alt": "Profesyonel Plastik Maket Bıçağı - Ambalaj arka"},
        {"src": "assets/images/products/profesyonel-plastik-maket-bicagi/profesyonel-plastik-maket-bicagi-kullanim.png", "alt": "Profesyonel Plastik Maket Bıçağı - Kullanım"},
    ],
    "profesyonel-metal-maket-bicagi": [
        {"src": "assets/images/products/profesyonel-metal-maket-bicagi/profesyonel-metal-maket-bicagi-ana.png", "alt": "Profesyonel Metal Maket Bıçağı - Ana görsel"},
        {"src": "assets/images/products/profesyonel-metal-maket-bicagi/profesyonel-metal-maket-bicagi-detay.png", "alt": "Profesyonel Metal Maket Bıçağı - Detay"},
        {"src": "assets/images/products/profesyonel-metal-maket-bicagi/profesyonel-metal-maket-bicagi-kutu.png", "alt": "Profesyonel Metal Maket Bıçağı - Ambalaj"},
        {"src": "assets/images/products/profesyonel-metal-maket-bicagi/profesyonel-metal-maket-bicagi-kutu-arka.png", "alt": "Profesyonel Metal Maket Bıçağı - Ambalaj arka"},
        {"src": "assets/images/products/profesyonel-metal-maket-bicagi/profesyonel-metal-maket-bicagi-kullanim.png", "alt": "Profesyonel Metal Maket Bıçağı - Kullanım"},
    ],
    "abs-govdeli-profesyonel-serit-metre": [
        {"src": "assets/images/products/abs-govdeli-profesyonel-serit-metre/abs-govdeli-profesyonel-serit-metre-ana.png", "alt": "ABS Gövdeli Profesyonel Şerit Metre - Ana görsel"},
        {"src": "assets/images/products/abs-govdeli-profesyonel-serit-metre/abs-govdeli-profesyonel-serit-metre-detay.png", "alt": "ABS Gövdeli Profesyonel Şerit Metre - Detay"},
        {"src": "assets/images/products/abs-govdeli-profesyonel-serit-metre/abs-govdeli-profesyonel-serit-metre-serit.png", "alt": "ABS Gövdeli Profesyonel Şerit Metre - Şerit"},
        {"src": "assets/images/products/abs-govdeli-profesyonel-serit-metre/abs-govdeli-profesyonel-serit-metre-kutu.png", "alt": "ABS Gövdeli Profesyonel Şerit Metre - Ambalaj"},
        {"src": "assets/images/products/abs-govdeli-profesyonel-serit-metre/abs-govdeli-profesyonel-serit-metre-display.png", "alt": "ABS Gövdeli Profesyonel Şerit Metre - Teşhir kutusu"},
        {"src": "assets/images/products/abs-govdeli-profesyonel-serit-metre/abs-govdeli-profesyonel-serit-metre-kullanim.png", "alt": "ABS Gövdeli Profesyonel Şerit Metre - Kullanım"},
    ],
    "maket-bicagi-yedek-ucu": [
        {"src": "assets/images/products/maket-bicagi-yedek-ucu/maket-bicagi-yedek-ucu-ana.png", "alt": "Maket Bıçağı Yedek Ucu - Ana görsel"},
        {"src": "assets/images/products/maket-bicagi-yedek-ucu/maket-bicagi-yedek-ucu-detay.png", "alt": "Maket Bıçağı Yedek Ucu - Detay"},
        {"src": "assets/images/products/maket-bicagi-yedek-ucu/maket-bicagi-yedek-ucu-kutu.png", "alt": "Maket Bıçağı Yedek Ucu - Ambalaj"},
        {"src": "assets/images/products/maket-bicagi-yedek-ucu/maket-bicagi-yedek-ucu-kutu-dikey.png", "alt": "Maket Bıçağı Yedek Ucu - Ambalaj dikey"},
    ],
}

def load_existing_images():
    path = Path("data/products.json")
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {p["slug"]: p.get("images") for p in data.get("products", []) if p.get("images")}

def detect_uclar_schema(alt):
    if "Keski" in alt or "Murç" in alt:
        return "keski-murc"
    if "Manyetik" in alt and "Bits" not in alt:
        return "aksesuar"
    if "Bits" in alt:
        return "aksesuar"
    return "matkap-uc"

with open("urunler.json", encoding="utf-8") as f:
    raw = json.load(f)

existing_images = load_existing_images()

categories = []
products = []
seen_cats = {}

for item in raw["urunler"]:
    cat_name = item["kategori"]
    cat_id = CATEGORY_IDS.get(cat_name, slugify(cat_name))
    if cat_id not in seen_cats:
        seen_cats[cat_id] = {
            "id": cat_id,
            "name": cat_name,
            "order": len(seen_cats) + 1,
        }
        categories.append(seen_cats[cat_id])

    alt = item["alt_kategori"]
    pid = slugify(alt)
    schema = SCHEMA_MAP.get(cat_name, "generic")
    if cat_name == "Kırıcı & Delici":
        schema = detect_uclar_schema(alt)

    variants = []
    for i, v in enumerate(item.get("urunler", [])):
        vid = v.get("urun_kodu") or f"{pid}-v{i+1}"
        variants.append({"id": str(vid), **v})

    products.append({
        "id": pid,
        "slug": pid,
        "name": alt,
        "categoryId": cat_id,
        "categoryName": cat_name,
        "description": item.get("aciklama", ""),
        "features": item.get("ozellikler", []),
        "applications": item.get("uygulama_alanlari", []),
        "variantSchema": schema,
        "variants": variants,
        "images": CUSTOM_IMAGES.get(pid)
        or existing_images.get(pid)
        or [
            {"src": "assets/images/placeholder/gorsel.jpg", "alt": f"{alt} - Ana görsel"},
            {"src": "assets/images/placeholder/gorsel.jpg", "alt": f"{alt} - Detay"},
        ],
        "featured": cat_name in ("Elmas Kesici", "Kesici - Taşlama - Flap Disk") and len(products) < 6,
    })

out = {"categories": categories, "products": products}
with open("data/products.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

bundle = "window.ABRALION_CATALOG = " + json.dumps(out, ensure_ascii=False) + ";\n"
with open("assets/js/products-data.js", "w", encoding="utf-8") as f:
    f.write(bundle)

print(f"OK: {len(categories)} kategori, {len(products)} urun")
