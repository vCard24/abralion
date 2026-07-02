#!/usr/bin/env python3
"""Stage 1: legal pages, footer links, kart.jpg gaps."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "hakkimizda.html"

DRAFT_NOTE = (
    '<p class="mt-12 p-4 border border-steel-gray/30 rounded-lg text-sm text-steel-gray">'
    "<strong>Not:</strong> Bu metin taslaktır, hukuki incelemeden geçirilecektir."
    "</p>"
)

PAGES = [
    {
        "file": "gizlilik-politikasi.html",
        "title": "Gizlilik Politikası | Abralion",
        "meta_description": "Abralion gizlilik politikası: EKS-PLAST LLC veri sorumlusu, iletişim ve teklif formlarında işlenen kişisel veriler.",
        "og_title": "Gizlilik Politikası - Abralion",
        "h1": "Gizlilik Politikası",
        "intro": "Bu politika, abralion.com üzerinden sunulan hizmetler kapsamında kişisel verilerin nasıl işlendiğini açıklar.",
        "sections": [
            (
                "Veri sorumlusu",
                "<p><strong>EKS-PLAST LLC</strong> (ticari marka: <strong>Abralion</strong>) bu web sitesi kapsamında veri sorumlusudur. "
                "Rusya Federasyonu’nda faaliyet gösteren şirket, Türk firmalarına endüstriyel kesim ve taşlama ürünleri tedarik etmektedir.</p>"
                "<p>İletişim: <a class=\"footer-nav-link\" href=\"mailto:info@abralion.com\">info@abralion.com</a></p>",
            ),
            (
                "Toplanan veriler",
                "<p>İletişim ve fiyat teklifi formları aracılığıyla aşağıdaki bilgiler toplanabilir:</p>"
                "<ul class=\"list-disc pl-6 space-y-2 text-on-surface-variant\">"
                "<li>Ad soyad</li>"
                "<li>E-posta adresi</li>"
                "<li>Telefon numarası</li>"
                "<li>Konu / şirket / ülke / şehir (form alanlarına bağlı olarak)</li>"
                "<li>Mesaj ve teklif detayları (ürün seçimi, miktar, uygulama alanı vb.)</li>"
                "</ul>",
            ),
            (
                "Kullanım amacı",
                "<p>Toplanan veriler yalnızca teklif ve iletişim taleplerinizi değerlendirmek, size dönüş yapmak ve "
                "talep ettiğiniz ürün veya hizmet hakkında bilgi sağlamak amacıyla işlenir. Pazarlama amaçlı "
                "profil oluşturma veya üçüncü taraflara satış yapılmaz.</p>",
            ),
            (
                "Saklama süresi",
                "<p>Form kayıtları, talebin sonuçlandırılması ve meşru ticari kayıt yükümlülükleri için gerekli süre "
                "boyunca saklanır; daha uzun süre gerekmediği ölçüde arşivlenir veya silinir.</p>",
            ),
            (
                "Çerezler",
                "<p>Bu web sitesinde ziyaretçi davranışını izlemek veya reklam amaçlı <strong>çerez kullanılmamaktadır</strong>. "
                "Tarayıcınızın yerel depolama alanı yalnızca form taslakları veya ürün karşılaştırma listesi gibi "
                "işlevsel amaçlarla (ör. sessionStorage) sınırlı şekilde kullanılabilir.</p>",
            ),
            (
                "Haklarınız",
                "<p>Kişisel verilerinize erişim, düzeltme veya silme taleplerinizi "
                "<a class=\"footer-nav-link\" href=\"mailto:info@abralion.com\">info@abralion.com</a> adresine iletebilirsiniz.</p>",
            ),
        ],
        "current": "gizlilik-politikasi.html",
    },
    {
        "file": "kullanim-kosullari.html",
        "title": "Kullanım Koşulları | Abralion",
        "meta_description": "Abralion web sitesi kullanım koşulları: site içeriği, sorumluluk sınırları ve iletişim.",
        "og_title": "Kullanım Koşulları - Abralion",
        "h1": "Kullanım Koşulları",
        "intro": "abralion.com sitesini kullanarak aşağıdaki koşulları kabul etmiş sayılırsınız.",
        "sections": [
            (
                "Site sahibi",
                "<p>Bu site <strong>EKS-PLAST LLC</strong> (Abralion) tarafından işletilir. "
                "İletişim: <a class=\"footer-nav-link\" href=\"mailto:info@abralion.com\">info@abralion.com</a></p>",
            ),
            (
                "İçerik ve fikri mülkiyet",
                "<p>Sitedeki metinler, görseller, ürün bilgileri ve teknik dökümanlar EKS-PLAST LLC’ye veya lisans verenlerine aittir. "
                "Yazılı izin olmadan ticari amaçla kopyalanamaz veya yeniden yayımlanamaz.</p>",
            ),
            (
                "Ürün bilgileri",
                "<p>Ürün özellikleri ve teknik veriler bilgilendirme amaçlıdır. Kesin uygulama ve uygunluk için "
                "teknik dökümanları incelemeniz ve gerekirse uzman ekibimizle iletişime geçmeniz önerilir.</p>",
            ),
            (
                "Sorumluluk sınırı",
                "<p>Site “olduğu gibi” sunulur. Erişim kesintileri, üçüncü taraf bağlantıları veya sitedeki bilgilerin "
                "kullanımından doğan dolaylı zararlardan EKS-PLAST LLC sorumlu tutulamaz; yürürlükteki zorunlu "
                "hukuk hükümleri saklıdır.</p>",
            ),
            (
                "Değişiklikler",
                "<p>Bu koşullar önceden bildirim yapılmaksızın güncellenebilir. Güncel metin her zaman bu sayfada yayımlanır.</p>",
            ),
        ],
        "current": "kullanim-kosullari.html",
    },
    {
        "file": "kvkk.html",
        "title": "KVKK Aydınlatma Metni | Abralion",
        "meta_description": "Abralion KVKK aydınlatma metni: kişisel verilerin işlenmesi, hukuki sebep ve başvuru yolları.",
        "og_title": "KVKK Aydınlatma Metni - Abralion",
        "h1": "KVKK Aydınlatma Metni",
        "intro": "6698 sayılı Kişisel Verilerin Korunması Kanunu (“KVKK”) kapsamında veri sorumlusu sıfatıyla bilgilendirme.",
        "sections": [
            (
                "Veri sorumlusu",
                "<p><strong>EKS-PLAST LLC</strong> (Abralion) — İletişim: "
                "<a class=\"footer-nav-link\" href=\"mailto:info@abralion.com\">info@abralion.com</a></p>",
            ),
            (
                "İşlenen kişisel veriler",
                "<p>İletişim ve teklif formları üzerinden: ad soyad, e-posta, telefon, konu, mesaj ve formda "
                "gönüllü olarak paylaştığınız diğer ticari bilgiler (şirket, ülke, şehir, ürün tercihleri).</p>",
            ),
            (
                "İşleme amaçları",
                "<ul class=\"list-disc pl-6 space-y-2 text-on-surface-variant\">"
                "<li>Teklif ve iletişim taleplerini yanıtlamak</li>"
                "<li>Müşteri ilişkileri ve satış öncesi destek süreçlerini yürütmek</li>"
                "<li>Yasal yükümlülüklerin yerine getirilmesi</li>"
                "</ul>",
            ),
            (
                "Hukuki sebep",
                "<p>Verileriniz; bir sözleşmenin kurulması veya ifası, meşru menfaat ve açık rızanızın bulunduğu "
                "hallerde KVKK m. 5 ve 6 kapsamında işlenir.</p>",
            ),
            (
                "Aktarım",
                "<p>Verileriniz yalnızca talebinizi yerine getirmek için gerekli hizmet sağlayıcılarına (ör. e-posta "
                "altyapısı) ve kanunen yetkili kurumlara, gerekli güvenlik önlemleri alınarak aktarılabilir.</p>",
            ),
            (
                "Haklarınız (KVKK m. 11)",
                "<p>Kişisel verilerinizin işlenip işlenmediğini öğrenme, bilgi talep etme, düzeltilmesini veya "
                "silinmesini isteme haklarına sahipsiniz. Başvurularınızı "
                "<a class=\"footer-nav-link\" href=\"mailto:info@abralion.com\">info@abralion.com</a> üzerinden iletebilirsiniz.</p>",
            ),
            (
                "Çerezler",
                "<p>Reklam veya analitik amaçlı <strong>çerez kullanılmamaktadır</strong>.</p>",
            ),
        ],
        "current": "kvkk.html",
    },
]


def build_main(page: dict) -> str:
    parts = [
        f'    <section class="py-section-gap border-b border-steel-gray/10" aria-labelledby="legal-title">',
        '      <div class="max-w-3xl mx-auto px-margin-mobile lg:px-margin-desktop space-y-8">',
        f'        <h1 id="legal-title" class="font-headline-lg text-headline-lg text-white m-0">{page["h1"]}</h1>',
        f'        <p class="text-on-surface-variant text-body-lg leading-relaxed m-0">{page["intro"]}</p>',
    ]
    for heading, body in page["sections"]:
        parts.append(f'        <div class="space-y-3">')
        parts.append(f'          <h2 class="font-headline-md text-headline-md text-white m-0">{heading}</h2>')
        parts.append(f'          <div class="text-on-surface-variant font-body-md text-body-md leading-relaxed space-y-3">{body}</div>')
        parts.append("        </div>")
    parts.append(f"        {DRAFT_NOTE}")
    parts.append("      </div>")
    parts.append("    </section>")
    return "\n".join(parts)


def legal_footer_links(current: str, prefix: str = "") -> str:
    items = [
        ("gizlilik-politikasi.html", "Gizlilik Politikası"),
        ("kullanim-kosullari.html", "Kullanım Koşulları"),
        ("kvkk.html", "KVKK"),
    ]
    lines = []
    for href, label in items:
        full = f"{prefix}{href}"
        if href == current:
            lines.append(
                f'<a class="footer-nav-link text-on-surface font-semibold" href="{full}" aria-current="page">{label}</a>'
            )
        else:
            lines.append(f'<a class="footer-nav-link" href="{full}">{label}</a>')
    return "\n        ".join(lines)


def patch_footer_block(html: str, prefix: str = "") -> str:
    new_links = legal_footer_links("", prefix)
    return re.sub(
        r'<a class="footer-nav-link" href="#">Gizlilik Politikası</a>\s*'
        r'<a class="footer-nav-link" href="#">Kullanım Koşulları</a>\s*'
        r'<a class="footer-nav-link" href="#">KVKK</a>',
        new_links,
        html,
    )


def generate_legal_page(page: dict, template: str) -> str:
    slug = page["file"]
    url = f"https://abralion.com/{slug}"
    head = template.split("<body", 1)[0]
    body_tail = "<body" + template.split("<body", 1)[1]
    header_end = body_tail.find("<main id=\"main-content\">")
    footer_start = body_tail.find("  <footer class=\"footer")
    header = body_tail[:header_end]
    footer_and_scripts = body_tail[footer_start:]

    head = re.sub(r"<title>[^<]+</title>", f"<title>{page['title']}</title>", head)
    head = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{page["meta_description"]}">',
        head,
    )
    head = re.sub(
        r'<link rel="canonical" href="[^"]+">',
        f'<link rel="canonical" href="{url}">',
        head,
    )
    head = re.sub(
        r'<meta property="og:url" content="[^"]+">',
        f'<meta property="og:url" content="{url}">',
        head,
    )
    head = re.sub(
        r'<meta property="og:title" content="[^"]+">',
        f'<meta property="og:title" content="{page["og_title"]}">',
        head,
    )
    head = re.sub(
        r'<meta property="og:description" content="[^"]+">',
        f'<meta property="og:description" content="{page["meta_description"]}">',
        head,
    )
    head = re.sub(
        r'<meta name="twitter:title" content="[^"]+">',
        f'<meta name="twitter:title" content="{page["og_title"]}">',
        head,
    )
    head = re.sub(
        r'<meta name="twitter:description" content="[^"]+">',
        f'<meta name="twitter:description" content="{page["meta_description"]}">',
        head,
    )
    head = head.replace(
        'class="page-about bg-carbon-black',
        'class="page-legal bg-carbon-black',
    )
    header = re.sub(
        r'<li><a class="footer-nav-link[^"]*" href="hakkimizda\.html"[^>]*>Hakkımızda</a></li>',
        '<li><a class="footer-nav-link" href="hakkimizda.html">Hakkımızda</a></li>',
        header,
    )
    header = re.sub(
        r' href="hakkimizda\.html" class="[^"]*" aria-current="page"',
        ' href="hakkimizda.html"',
        header,
    )

    main = build_main(page)
    footer_and_scripts = re.sub(
        r'(<div class="flex flex-wrap justify-center gap-6[^>]*>)\s*'
        r'<a class="footer-nav-link" href="#">Gizlilik Politikası</a>\s*'
        r'<a class="footer-nav-link" href="#">Kullanım Koşulları</a>\s*'
        r'<a class="footer-nav-link" href="#">KVKK</a>',
        r"\1\n        " + legal_footer_links(page["current"]),
        footer_and_scripts,
        count=1,
    )

    return head + header + f"\n  <main id=\"main-content\">\n{main}\n  </main>\n\n" + footer_and_scripts


def patch_all_footers() -> int:
    n = 0
    for path in ROOT.rglob("*.html"):
        if not path.is_file() or "scripts" in path.parts or "node_modules" in path.parts:
            continue
        if path.name in ("product-detail-noir.html", "product-detail-main-stitch.html"):
            continue
        prefix = "../" if path.parent.name == "urun" else ""
        text = path.read_text(encoding="utf-8")
        new = patch_footer_block(text, prefix)
        if new != text:
            path.write_text(new, encoding="utf-8")
            n += 1
    return n


def create_kart_jpg(slug: str) -> bool:
    folder = ROOT / "assets/images/products" / slug
    dest = folder / f"{slug}-kart.jpg"
    if dest.is_file():
        return False
    sources = sorted(folder.glob("*card*.webp")) + sorted(folder.glob("*kart*.webp"))
    if not sources:
        return False
    try:
        from PIL import Image
    except ImportError:
        return False
    img = Image.open(sources[0])
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(dest, "JPEG", quality=85, optimize=True)
    return True


def main() -> None:
    template = TEMPLATE.read_text(encoding="utf-8")
    for page in PAGES:
        out = ROOT / page["file"]
        out.write_text(generate_legal_page(page, template), encoding="utf-8")
        print("wrote", out.name)
    print("footers patched:", patch_all_footers())
    for slug in ("genel-amacli-elmas-kesme-diski", "sds-plus-2-kesicili-beton-matkap-ucu"):
        if create_kart_jpg(slug):
            print("created kart.jpg for", slug)


if __name__ == "__main__":
    main()
