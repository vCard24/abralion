# -*- coding: utf-8 -*-
"""A2: dört yeni ürün kaydı, 12200 rpm, TR Aluminum. Dokuz güncelleme ürününe dokunmaz."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

from structured_data import inject, product_schema

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import sync_catalog  # noqa: E402

TODAY = "2026-11-11"
CATALOG_RE = re.compile(
    r"window\.ABRALION_CATALOG\s*=\s*(\{.*\})\s*;?\s*$",
    re.S,
)
SCHEMA_BLOCK = re.compile(
    r"<!-- STRUCTURED_DATA_START -->.*?<!-- STRUCTURED_DATA_END -->",
    re.S,
)

SIZES = (
    (65, 'Ø 65 mm (2,5")'),
    (75, 'Ø 75 mm (3")'),
    (100, 'Ø 100 mm (4")'),
)


def esc(value: str) -> str:
    return (value or "").replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def load_js(path: Path) -> tuple[str, dict]:
    raw = path.read_text(encoding="utf-8")
    match = CATALOG_RE.search(raw)
    if not match:
        raise SystemExit(f"katalog yok: {path}")
    return raw[: match.start(1)], json.loads(match.group(1))


def write_js(path: Path, prefix: str, catalog: dict) -> None:
    body = json.dumps(catalog, ensure_ascii=False, indent=2)
    suffix = ";\n"
    path.write_text(prefix + body + suffix, encoding="utf-8")


def write_json(path: Path, catalog: dict) -> None:
    path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def gallery(slug: str, name: str, alt_pattern: str) -> list[dict]:
    folder = ROOT / "assets" / "images" / "products" / slug
    frames = sorted(
        p
        for p in folder.glob(f"{slug}-galeri-*.jpg")
        if "-thumb" not in p.name
    )
    if not frames:
        raise SystemExit(f"galeri yok: {slug}")
    images = []
    for path in frames:
        nn = path.stem.rsplit("-galeri-", 1)[-1]
        images.append(
            {
                "src": f"assets/images/products/{slug}/{path.name}",
                "alt": alt_pattern.format(name=name, nn=nn),
            }
        )
    return images


def insert_after(products: list[dict], after_slug: str, items: list[dict]) -> None:
    index = next(i for i, product in enumerate(products) if product["slug"] == after_slug)
    for offset, item in enumerate(items):
        products.insert(index + 1 + offset, item)


def apply_fixes(catalog: dict, *, aluminum: bool) -> None:
    for product in catalog["products"]:
        if product["slug"] == "ultra-ince-elmas-disk":
            for variant in product["variants"]:
                if variant.get("daire_capi_mm") == 125 and variant.get("max_hiz_rpm") == 2500:
                    variant["max_hiz_rpm"] = 12200
        if aluminum and product["slug"] == "ao-aluminyum-oksit-flap-disk":
            for variant in product["variants"]:
                if variant.get("asindirici_tipi") == "AO Alumnum Oxide":
                    variant["asindirici_tipi"] = "AO Aluminum Oxide"


def cup_variants(prefix: str, wire: str, speed_label: str) -> list[dict]:
    rows = []
    for diameter, label in SIZES:
        rows.append(
            {
                "id": f"{prefix}-{diameter}",
                "urun_kodu": f"{prefix}-{diameter}",
                "daire_capi_mm": diameter,
                "daire_etiket": label,
                "tel_tipi": wire,
                "max_hiz_rpm": 13300,
                "max_hiz_ms": 80,
                "max_hiz_etiket": speed_label,
                "baglanti_tipi": "M14",
                "kutu_adet": 1,
                "koli_adet": None,
            }
        )
    return rows


def product_record(
    slug: str,
    name: str,
    category_id: str,
    category_name: str,
    featured: bool,
    description: str,
    features: list[str],
    applications: list[str],
    variants: list[dict],
    alt_pattern: str,
) -> dict:
    return {
        "id": slug,
        "slug": slug,
        "name": name,
        "categoryId": category_id,
        "categoryName": category_name,
        "featured": featured,
        "description": description,
        "features": features,
        "applications": applications,
        "images": gallery(slug, name, alt_pattern),
        "variants": variants,
    }


def tr_products() -> list[dict]:
    kesici = "Kesici - Taşlama - Flap Disk"
    kirici = "Kırıcı & Delici"
    alt = "{name} - galeri {nn}"
    speed = "13.300 rpm / 80 m/s"
    return [
        product_record(
            "canak-firca-sacakli",
            "Çanak Fırça Saçaklı",
            "kesici-taslama-flap-disk",
            kesici,
            True,
            "Esnek tel yapısı sayesinde işlenecek yüzeye mükemmel uyum sağlayarak üstün bir temizlik ve yüzey hazırlama performansı sunan genel amaçlı saçaklı çanak fırçalardır. Geniş metal levhaların ve profillerin temizliğinde işçilik zamanından tasarruf sağlar. M14 bağlantısı ile pratik ve güvenli bir kullanım sunar.",
            [
                "Dalgalı (saçaklı) tel geometrisi sayesinde geniş yüzeylerde daha homojen ve esnek fırçalama hareketi",
                "Yüksek devirli spiral taşlama makinelerine tam uyum sağlayan ve balans yapmayan dayanıklı yapı",
                "Yüzeydeki ana metali oymadan veya çizmeden, sadece pas, boya ve tortuyu kaldıran hassas temizlik yeteneği",
                "Esnek telleri sayesinde girintili, çıkıntılı ve düzensiz formlara sahip yüzeylere kolay adaptasyon",
                "Kopmalara ve deformasyona karşı dirençli, yüksek mukavemetli çelik tel dokusu ile uzun kullanım ömrü",
            ],
            [
                "Geniş metal sac ve profillerdeki pas, oksitlenme, eski boya ve inatçı kirlerin temizlenmesi",
                "Kaynak sonrasında metal yüzeyde kalan cüruf ve kaynak tortularının fırçalanması",
                "Boya, yalıtım, kaplama ve yapıştırma işlemleri öncesinde hızlı ve profesyonel yüzey hazırlığı",
                "Kesim sonrası hafif çapak alma ve keskin köşelerin yuvarlatılması",
                "Ahşap, metal ve taş yüzeylerde hafif toz alma, esnek dokulandırma ve cilalama/parlatma işlemleri",
            ],
            cup_variants("cfs", "Saçaklı tel", speed),
            alt,
        ),
        product_record(
            "canak-firca-burgulu",
            "Çanak Fırça Burgulu (Ağır Hizmet Tipi)",
            "kesici-taslama-flap-disk",
            kesici,
            True,
            "Zorlu temizlik, derinlemesine pas sökme ve ağır yüzey aşındırma işlemleri için özel olarak tasarlanmış, ekstra dayanıklı burgulu (düğümlü) tel fırçadır. Agresif yapısı sayesinde metal, beton ve doğal taş gibi sert yüzeylere sıkıca tutunmuş inatçı katmanları hızla kazır.",
            [
                "Zorlu katmanları hızla kazımak için tasarlanmış agresif ve sertleştirilmiş burgulu (düğümlü) tel teknolojisi",
                "Sürtünme ve kopmalara karşı yüksek direnç gösteren ekstra dayanıklı çelik tel yapısı",
                "Geniş yüzeylerde zaman kazandıran ve fırçalama verimini artıran özel çanak (cup) tasarımı",
                "Ağır hizmet şartlarında (Heavy Duty) maksimum stabilite ve uzun ömürlü kullanım garantisi",
                "Pazardaki tüm M14 vidalı elektrikli ve havalı spiral taşlama makineleriyle tam uyumluluk",
            ],
            [
                "Endüstriyel kaynak işlemlerinde oluşan kalın cüruf, tortu ve yanık izlerinin derinlemesine temizliği",
                "Geniş metal yüzeylerdeki ağır pas, korozyon, kalıplaşmış kir ve eski boyaların sökülmesi",
                "Metal, beton ve doğal taş yüzeylerdeki keskin çapakların, pürüzlerin ve kalıntıların giderilmesi",
                "Ağır sanayi, çelik konstrüksiyon, dökümhane, tersane ve otomotiv sektörlerindeki yüzey hazırlama işlemleri",
                "İnşaat ve restorasyon (renovasyon) projelerinde yapısal temizlik uygulamaları",
            ],
            cup_variants("cfb", "Burgulu tel", speed),
            alt,
        ),
        product_record(
            "plastik-sapli-celik-tel-firca",
            "Plastik Saplı Çelik Tel Fırça (El Fırçası)",
            "kesici-taslama-flap-disk",
            kesici,
            False,
            "Dar açılı bölgeler, köşeler ve boru yüzeyleri gibi ulaşılması zor alanlar için tasarlanmış profesyonel çelik tel el fırçasıdır. Yüksek mukavemetli çelik telleri sayesinde ağır pas, kaynak tortusu ve inatçı kirleri hızla söker. Atölyelerdeki mekanik temizliklerden bahçe ve tesisat bakımlarına kadar geniş bir yelpazede pratik çözümler sunar.",
            [
                "Ulaşılması zor köşelere ve dar açılı yüzeylere kolay erişim sağlayan ince ve fonksiyonel fırça profili",
                "Uzun süreli çalışmalarda eli yormayan ve konfor sunan ergonomik tasarımlı plastik sap",
                "En zorlu kirleri, pası ve eski boyayı kolayca kazıyan dayanıklı çelik tel dokusu",
                "Ekstra hafif yapısı sayesinde yüksek manevra kabiliyeti ve rahat kullanım deneyimi",
                "Endüstriyel kullanımdan günlük genel bakıma kadar her alanda pırıl pırıl yüzeyler bırakan üstün temizlik performansı",
            ],
            [
                "Kaynak öncesi yüzey hazırlığı ve kaynak sonrası çapak, tortu temizliği",
                "Metal boru, profil ve köşeli parçalardaki pas, korozyon ve boyaların sökülmesi",
                "Atölye, şantiye ve sanayi tesislerinde dar alanlardaki inatçı kirlerin aşındırılması",
                "Bahçe aletleri, barbekü ızgaraları, tesisat parçaları gibi ev ve dış mekan ekipmanlarının bakımı",
                "Banyo, seramik derzleri veya sert zeminlerdeki ağır kirliliklerin manuel olarak kazınması",
            ],
            [
                {
                    "id": "pstf-25",
                    "urun_kodu": "pstf-25",
                    "toplam_uzunluk": "25 cm",
                    "sap_uzunlugu": "15 cm",
                    "tel_sayisi": "400+",
                    "tel_tipi": "Çelik",
                    "kutu_adet": 1,
                    "koli_adet": None,
                }
            ],
            alt,
        ),
        product_record(
            "genis-agizli-keski",
            "Geniş Ağız Keski",
            "kirici-delici",
            kirici,
            False,
            "Şantiyelerde, tadilat ve restorasyon projelerinde geniş yüzeylerin sökülmesi için özel olarak geliştirilmiş profesyonel kırıcı keski ucudur. Yüksek mukavemetli K28 alaşımlı alet çeliği yapısı ile darbelere karşı maksimum direnç gösterir ve geniş ağız formu sayesinde yüzey temizliğini hızlandırarak iş verimliliğini artırır.",
            [
                "Genişletilmiş ağız yapısı ile darbe gücünü geniş alana yayarak hızlı yüzey sökümü",
                "Yüksek darbe dayanımı ve uzun kullanım ömrü sunan K28 alaşımlı alet çeliği (Tool Steel) gövde",
                "Zorlu şantiye koşullarında bükülmeye ve erken aşınmaya karşı özel ısıl işlem direnci",
                "Hafif ve orta sınıf tüm SDS-PLUS girişli kırıcı-delici makinelerle tam uyumluluk",
            ],
            [
                "Duvar ve zeminlerdeki eski sıva, şap ve harç kalıntılarının temizlenmesi",
                "Seramik, fayans ve yer karolarının yüzeye zarar vermeden sökülmesi",
                "Beton, tuğla ve doğal taş yüzeylerde kanal açma ve yüzey düzeltme işlemleri",
                "Genel inşaat yıkım, kırım ve tadilat uygulamaları",
            ],
            [
                {
                    "id": "gak-14-250-40",
                    "urun_kodu": "gak-14-250-40",
                    "urun_tipi": "Geniş ağız keski",
                    "saft_mm": 14,
                    "uzunluk_mm": 250,
                    "uc_genisligi_mm": 40,
                    "baglanti_tipi": "SDS Plus",
                    "malzeme": "Çelik",
                    "kutu_adet": 1,
                    "koli_adet": None,
                }
            ],
            alt,
        ),
    ]


def ru_products() -> list[dict]:
    kesici = "Отрезные и шлифовальные круги"
    kirici = "Буры и зубила"
    alt = "{name} — галерея {nn}"
    speed = "13 300 об/мин / 80 м/с"
    return [
        product_record(
            "canak-firca-sacakli",
            "Чашечная щётка с гофрированной проволокой",
            "kesici-taslama-flap-disk",
            kesici,
            True,
            "Чашечные щётки с гофрированной проволокой повторяют форму поверхности и дают равномерную очистку. На широких листах и профилях сокращают время ручной зачистки. Посадка M14 обеспечивает быструю и надёжную установку на угловую шлифовальную машину.",
            [
                "Волнистая проволока даёт равномерное и гибкое движение по широкой поверхности",
                "Сбалансированная конструкция для высокооборотных угловых шлифовальных машин",
                "Снимает ржавчину, краску и налёт, не врезаясь в основной металл",
                "Гибкая проволока повторяет впадины и неровный профиль",
                "Прочная стальная проволока держит форму и служит дольше",
            ],
            [
                "Очистка широкого листа и профиля от ржавчины, окислов, старой краски и стойких загрязнений",
                "Снятие шлака и сварочного налёта после сварки",
                "Подготовка поверхности перед окраской, изоляцией, покрытием и склеиванием",
                "Лёгкое снятие заусенцев и скругление острых кромок после резки",
                "Лёгкое обеспыливание, текстурирование и полировка дерева, металла и камня",
            ],
            cup_variants("cfs", "Гофрированная проволока", speed),
            alt,
        ),
        product_record(
            "canak-firca-burgulu",
            "Чашечная щётка жгутовая (усиленная)",
            "kesici-taslama-flap-disk",
            kesici,
            True,
            "Усиленная чашечная щётка со жгутовой проволокой для тяжёлой очистки, глубокого снятия ржавчины и агрессивной обработки. Жёсткая проволока быстро снимает слои, въевшиеся в металл, бетон и природный камень.",
            [
                "Жгутовая проволока повышенной жёсткости для быстрого снятия плотных слоёв",
                "Стальная проволока устойчива к истиранию и обрыву",
                "Чашечная форма ускоряет обработку широких поверхностей",
                "Стабильная работа в тяжёлом режиме и увеличенный ресурс",
                "Посадка M14 для электрических и пневматических угловых шлифовальных машин",
            ],
            [
                "Глубокая очистка толстого шлака, нагара и следов сварки",
                "Снятие тяжёлой ржавчины, коррозии, спёкшейся грязи и старой краски с металла",
                "Удаление острых заусенцев и остатков с металла, бетона и природного камня",
                "Подготовка поверхности в тяжёлой промышленности, металлоконструкциях, литье, судостроении и автосервисе",
                "Конструкционная очистка на стройке и при реставрации",
            ],
            cup_variants("cfb", "Жгутовая проволока", speed),
            alt,
        ),
        product_record(
            "plastik-sapli-celik-tel-firca",
            "Ручная стальная щётка с пластиковой ручкой",
            "kesici-taslama-flap-disk",
            kesici,
            False,
            "Ручная стальная щётка для углов, кромок и труб, куда не проходит машинная щётка. Проволока высокой прочности быстро снимает плотную ржавчину, сварочный налёт и стойкую грязь. Подходит и для слесарной зачистки, и для ухода за инструментом и арматурой.",
            [
                "Узкий профиль достаёт до углов и труднодоступных поверхностей",
                "Эргономичная пластиковая ручка не утомляет при долгой работе",
                "Стальная проволока счищает грязь, ржавчину и старую краску",
                "Малый вес даёт свободный ход и точное ведение",
                "Одинаково уместна в цехе и при повседневном уходе",
            ],
            [
                "Подготовка поверхности до сварки и снятие заусенцев и налёта после сварки",
                "Очистка труб, профиля и угловых деталей от ржавчины, коррозии и краски",
                "Зачистка стойких загрязнений в узких местах мастерской и на объекте",
                "Уход за садовым инструментом, решётками гриля и сантехническими деталями",
                "Ручное удаление сильных загрязнений со швов плитки и твёрдых полов",
            ],
            [
                {
                    "id": "pstf-25",
                    "urun_kodu": "pstf-25",
                    "toplam_uzunluk": "25 см",
                    "sap_uzunlugu": "15 см",
                    "tel_sayisi": "400+",
                    "tel_tipi": "Сталь",
                    "kutu_adet": 1,
                    "koli_adet": None,
                }
            ],
            alt,
        ),
        product_record(
            "genis-agizli-keski",
            "Широкое зубило",
            "kirici-delici",
            kirici,
            False,
            "Профессиональное зубило для снятия широких слоёв на стройке, при ремонте и реставрации. Корпус из инструментальной стали K28 держит удар, а широкая кромка ускоряет очистку поверхности.",
            [
                "Расширенная кромка распределяет удар и быстрее снимает слой",
                "Корпус из инструментальной стали K28 с высокой ударной стойкостью",
                "Термообработка против изгиба и раннего износа на объекте",
                "Посадка SDS Plus для лёгких и средних перфораторов",
            ],
            [
                "Снятие старой штукатурки, стяжки и остатков раствора со стен и пола",
                "Демонтаж керамики, плитки и напольных плит без лишнего повреждения основания",
                "Штробление и выравнивание бетона, кирпича и природного камня",
                "Общестроительный демонтаж, скол и ремонт",
            ],
            [
                {
                    "id": "gak-14-250-40",
                    "urun_kodu": "gak-14-250-40",
                    "urun_tipi": "Широкое зубило",
                    "saft_mm": 14,
                    "uzunluk_mm": 250,
                    "uc_genisligi_mm": 40,
                    "baglanti_tipi": "SDS Plus",
                    "malzeme": "Сталь",
                    "kutu_adet": 1,
                    "koli_adet": None,
                }
            ],
            alt,
        ),
    ]


def add_products(catalog: dict, records: list[dict]) -> None:
    existing = {product["slug"] for product in catalog["products"]}
    brushes = [record for record in records if record["categoryId"] == "kesici-taslama-flap-disk"]
    chisels = [record for record in records if record["slug"] == "genis-agizli-keski"]
    brushes = [record for record in brushes if record["slug"] not in existing]
    chisels = [record for record in chisels if record["slug"] not in existing]
    if brushes:
        insert_after(catalog["products"], "ao-aluminyum-oksit-flap-disk", brushes)
    if chisels:
        insert_after(catalog["products"], "sivri-uclu-keski-murc-sds-max", chisels)


def write_tr_pages(catalog: dict) -> None:
    template = (ROOT / "scripts" / "templates" / "product-detail-noir.html").read_text(encoding="utf-8")
    wanted = {record["slug"] for record in tr_products()}
    for product in catalog["products"]:
        if product["slug"] not in wanted:
            continue
        slug = product["slug"]
        html = template
        description = esc((product.get("description") or "")[:160])
        og_image = f"https://abralion.com/assets/images/products/{slug}/{slug}-cover.jpg"
        for key, value in {
            "slug": slug,
            "name": esc(product["name"]),
            "konu": quote(product["name"], safe=""),
            "description": description,
            "canonical": f"https://abralion.com/urun/{slug}.html",
            "og_title": esc(f'{product["name"]} - Abralion'),
            "og_image": og_image,
            "og_image_alt": esc(product["name"]),
            "technical_catalog_href": "../dokumanlar.html",
        }.items():
            html = html.replace("{" + key + "}", value)
        html = inject(html, product_schema(product))
        (ROOT / "urun" / f"{slug}.html").write_text(html, encoding="utf-8")
        print(f"TR page {slug}")


def write_ru_pages(catalog: dict) -> None:
    donor_path = ROOT / "ru" / "urun" / "duz-keski-sds-plus.html"
    donor = donor_path.read_text(encoding="utf-8")
    old_name = re.search(r'<h1 id="product-title"[^>]*>([^<]*)</h1>', donor).group(1)
    old_desc = re.search(r'<meta name="description" content="([^"]*)"', donor).group(1)
    by_slug = {product["slug"]: product for product in catalog["products"]}
    for record in ru_products():
        product = by_slug[record["slug"]]
        slug = product["slug"]
        meta = (product.get("description") or "")[:160]
        html = donor.replace("duz-keski-sds-plus", slug)
        html = html.replace(old_desc, esc(meta))
        html = html.replace(old_name, esc(product["name"]))
        html = html.replace(
            f"../assets/documents/products/{slug}.pdf",
            "../dokumenty.html",
        )
        url = f"https://abralion.com/ru/urun/{slug}.html"
        images = [
            f"https://abralion.com/{image['src'].lstrip('/')}"
            for image in product.get("images") or []
            if image.get("src")
        ][:4]
        payload = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Product",
                    "@id": f"{url}#product",
                    "name": product["name"],
                    "description": product.get("description", ""),
                    "url": url,
                    "brand": {"@type": "Brand", "name": "Abralion"},
                    "category": product.get("categoryName", ""),
                    "image": images,
                },
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Главная", "item": "https://abralion.com/ru/"},
                        {"@type": "ListItem", "position": 2, "name": "Продукция", "item": "https://abralion.com/ru/produkty.html"},
                        {"@type": "ListItem", "position": 3, "name": product["name"], "item": url},
                    ],
                },
            ],
        }
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        block = (
            "<!-- STRUCTURED_DATA_START -->\n"
            f'  <script type="application/ld+json">{encoded}</script>\n'
            "  <!-- STRUCTURED_DATA_END -->"
        )
        html = SCHEMA_BLOCK.sub(block, html, count=1)
        (ROOT / "ru" / "urun" / f"{slug}.html").write_text(html, encoding="utf-8")
        print(f"RU page {slug}")


def ru_collection(products: list[dict]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Каталог продукции Abralion",
        "url": "https://abralion.com/ru/produkty.html",
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(products),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": index,
                    "url": f"https://abralion.com/ru/urun/{product['slug']}.html",
                    "name": product["name"],
                }
                for index, product in enumerate(products, 1)
            ],
        },
        "inLanguage": "ru",
    }


def append_sitemap(path: Path, locs: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for loc in locs:
        if loc in text:
            continue
        block = (
            "  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{TODAY}</lastmod>\n"
            "    <changefreq>monthly</changefreq>\n"
            "    <priority>0.7</priority>\n"
            "  </url>\n"
        )
        text = text.replace("</urlset>", block + "</urlset>")
    path.write_text(text, encoding="utf-8")


def fix_ru_catalog_script_quote() -> None:
    pattern = re.compile(r"(products-data-ru\.js\?v=[0-9a-fA-F]+)>(</script>)")
    for path in (ROOT / "ru").rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        updated = pattern.sub(r'\1">\2', text)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            print(f"quote {path.relative_to(ROOT)}")


def main() -> None:
    tr_json_path = ROOT / "data" / "products.json"
    tr_js_path = ROOT / "assets" / "js" / "products-data.js"
    ru_json_path = ROOT / "ru" / "data" / "products-ru.json"
    ru_js_path = ROOT / "ru" / "assets" / "js" / "products-data-ru.js"

    tr_catalog = json.loads(tr_json_path.read_text(encoding="utf-8"))
    apply_fixes(tr_catalog, aluminum=True)
    add_products(tr_catalog, tr_products())
    write_json(tr_json_path, tr_catalog)

    prefix, js_catalog = load_js(tr_js_path)
    apply_fixes(js_catalog, aluminum=True)
    add_products(js_catalog, tr_products())
    write_js(tr_js_path, prefix, js_catalog)
    sync_catalog.ROOT_COPY.write_text(tr_js_path.read_text(encoding="utf-8"), encoding="utf-8")

    ru_catalog = json.loads(ru_json_path.read_text(encoding="utf-8"))
    apply_fixes(ru_catalog, aluminum=False)
    add_products(ru_catalog, ru_products())
    write_json(ru_json_path, ru_catalog)

    ru_prefix, ru_js = load_js(ru_js_path)
    apply_fixes(ru_js, aluminum=False)
    add_products(ru_js, ru_products())
    write_js(ru_js_path, ru_prefix, ru_js)

    write_tr_pages(js_catalog)
    write_ru_pages(ru_js)

    from structured_data import collection_schema

    urunler = ROOT / "urunler.html"
    urunler.write_text(inject(urunler.read_text(encoding="utf-8"), collection_schema(js_catalog["products"])), encoding="utf-8")
    produkty = ROOT / "ru" / "produkty.html"
    produkty.write_text(inject(produkty.read_text(encoding="utf-8"), ru_collection(ru_js["products"])), encoding="utf-8")

    slugs = [record["slug"] for record in tr_products()]
    append_sitemap(ROOT / "sitemap.xml", [f"https://abralion.com/urun/{slug}.html" for slug in slugs])
    append_sitemap(ROOT / "ru" / "sitemap.xml", [f"https://abralion.com/ru/urun/{slug}.html" for slug in slugs])
    fix_ru_catalog_script_quote()
    print(f"products {len(js_catalog['products'])}")


if __name__ == "__main__":
    main()
    raise SystemExit(subprocess.call([sys.executable, str(ROOT / "scripts" / "sync_catalog.py")], cwd=ROOT))
