# A1b — seri görsel aktarımı

Pilot `86c8d8b` onaylandı. Kaynak klasör `C:\Users\mosta\Desktop\abralion-kasim-2026-fotograflar` salt okundu. `miknatisli-anahtar-ucu` bu turda yeniden üretilmedi.

Script: `scripts/ingest_kasim2026_photos.py --remaining`. Kartlar rembg `u2net` ile yeniden kesildi (eşik maskesi yok). Katalog: `scripts/sync_catalog.py`, önbellek: `scripts/asset_cache_version.py`. `audit_links.py`: 3247 referans, 0 kırık.

Dört yeni ürünün `images[]` kaydı açılmadı. Dosyalar diskte; bağlama A2/A3. Audit referanssız dosyayı öksüz saymıyor, bu klasörler hata değil.

## Ürün tablosu

Baytlar galeri üretiminin hemen sonrası. Yeni ürünlerin kart dosyaları bu satırdan sonra eklendi; kart boyutları aşağıdaki kart bölümünde.

| Ürün | Kare | Ana foto | Yazılan | Önce | Silinen | Sonra | Katalog |
| --- | ---: | --- | ---: | ---: | --- | ---: | --- |
| cam-seramik-matkap-ucu | 20 | DSC_9327 | 125 | 416019 | 9 / 350471 | 2232725 | evet |
| hss-matkap-ucu | 33 | DSC_8892 | 203 | 446192 | 8 / 389911 | 2608989 | evet |
| sds-plus-2-kesicili-beton-matkap-ucu | 40 | DSC_9233 | 245 | 910474 | 12 / 898123 | 3801139 | evet |
| sds-plus-4-kesicili-beton-matkap-ucu | 29 | DSC_9170 | 179 | 772996 | 8 / 645590 | 2863974 | evet |
| sds-max-burc-aleti | 4 | DSC_9189 | 29 | 751235 | 11 / 628689 | 529352 | evet |
| ph2-manyetik-bits-uc | 14 | DSC_9045 | 89 | 884341 | 8 / 827534 | 1480896 | evet |
| duz-keski-sds-max | 3 | DSC_8950 | 23 | 967974 | 8 / 890363 | 375671 | evet |
| sivri-uclu-keski-murc-sds-plus | 3 | DSC_8944 | 23 | 1099822 | 6 / 1027252 | 363746 | evet |
| canak-firca-sacakli | 12 | DSC_8984 | 77 | 0 | 0 | 1909823 | hayır |
| canak-firca-burgulu | 12 | DSC_8974 | 77 | 0 | 0 | 1631454 | hayır |
| plastik-sapli-celik-tel-firca | 4 | DSC_8926 | 29 | 0 | 0 | 1070460 | hayır |
| genis-agizli-keski | 2 | DSC_9114 | 17 | 0 | 0 | 266414 | hayır |

Sekiz mevcut klasör: önce 6.25 MB, silinen 5.66 MB, sonra 14.26 MB. Dört yeni galeri (kart hariç) 4.66 MB. Her kare için tam boy 1600 (avif/webp/jpg) ve küçük resim 480, artı `{slug}.webp`, `-cover.jpg`, `-og.jpg`, `-wa.jpg` (`#0A0A0A`, 1200×630) ve `-menu-thumb.webp`. `{slug}-kart.jpg` ve `{slug}-kart-card.*` silinmedi.

## Ana foto

Ürünü tek başına gösteren kare. Ambalaj ve aksiyon kareleri seçilmedi. Kart karesi galeri ana fotosundan ayrı duruyor.

| Ürün | Seçim | Neden |
| --- | --- | --- |
| cam-seramik-matkap-ucu | DSC_9327 | En büyük çıplak uç. Çoğu kare blister. |
| hss-matkap-ucu | DSC_8892 | Dikey, tek matkap. Tüp ve kutu değil. |
| sds-plus-2 | DSC_9233 | Tam boy çıplak uç. Diğer karelerde askı kartı var. |
| sds-plus-4 | DSC_9170 | Tam boy çıplak uç. DSC_8918 uç makrosu seçilmedi. |
| sds-max-burc-aleti | DSC_9189 | Ambalajsız dişli baş. Tam boy DSC_9116 neredeyse beyaz zemin. |
| ph2-manyetik-bits-uc | DSC_9045 | Tek uç, tam boy. |
| duz-keski-sds-max | DSC_8950 | Tam keski, askı kartı yok. |
| sivri-uclu-keski-murc-sds-plus | DSC_8944 | Tüm alet, en küçük askı etiketi. Tam boy karelerin hepsinde etiket var; etiketsiz tek kare uç detayı DSC_9301. |
| canak-firca-sacakli | DSC_8984 | Tek fırça, cepheden. Kart karesi DSC_9025 (çift). |
| canak-firca-burgulu | DSC_8974 | Tek fırça. Kart karesi DSC_8978 (çift). |
| plastik-sapli-celik-tel-firca | DSC_8926 | Tek fırça, tam boy. Aynı kare kartta da kullanıldı. |
| genis-agizli-keski | DSC_9114 | Geniş ağız, blister yok. Aynı kare kartta da kullanıldı. |

## Silinenler

Kart dosyaları durdu. Eski `-card` (kart değil), cover/og/wa, menu-thumb, `{slug}.webp` ve kullanım/uygulama kareleri silinip yenisi yazıldı. Ayrıntı: `scripts/raporlar/a1b-run.json`.

Öne çıkanlar:

- `sds-plus-2`: `-card-440.avif`, `-card.avif`, `-card.webp`, kullanım ve uygulama dosyaları. Ana sayfa (`index.html`, `ru/index.html`) artık duran `sds-plus-2-kesicili-beton-matkap-ucu-kart.jpg` dosyasına bakıyor. `applicationImage` `...-galeri-01.jpg`.
- `sds-max-burc-aleti`: `sds-max-burc-aleti2-*` ve taraklı murç kullanım karesi.
- `cam-seramik`: eski kutu ve kullanım jpg'leri.
- Kardeş klasörlerdeki eski slug dosyaları aşağıdaki bağlama adımında silindi. Kartlar durdu.

## Kardeş bağlama

Galeri kopyalanmadı. `images[]` kaynak slug'ın `-galeri-NN.jpg` yollarını kullanıyor.

| Hedef | Kaynak | Galeri | Kopyalanan |
| --- | --- | ---: | --- |
| duz-keski-sds-plus | duz-keski-sds-max | 3 | webp, cover, og, wa, menu-thumb |
| sivri-uclu-keski-murc-sds-max | sivri-uclu-keski-murc-sds-plus | 3 | webp, cover, og, wa, menu-thumb |

Beşinci dosya menü küçük resmi: `site.js` onu slug'a göre arıyor. Dört paylaşım dosyası da (`webp`, `cover`, `og`, `wa`) şablon slug'a göre baktığı için kardeş klasöre fiziksel kopyalandı. TR ve RU kataloglardaki `images[]` aynı yolları gösteriyor.

`duz-keski-sds-plus` klasöründen silinenler: cover, og, wa, webp, menu-thumb, kullanim.jpg (860975 bayt). `sivri-uclu-keski-murc-sds-max` klasöründen silinenler: card.avif, card.webp, cover, og, wa, webp, menu-thumb, kullanim.webp (840694 bayt). `-kart.jpg` ve `-kart-card.*` durdu.

## Yeni ürün kartları

Stil B, pilot `koyu-kompozit.jpg` reçetesi: rembg `u2net`, zemin `#0A0A0A`, altta yumuşak yansıma. `kart.jpg` 190×110, `kart-card.webp` / `kart-card.avif` 600×316.

Tel fırçalara 2 px koyu kenar tüyü uygulandı. 2× kenar kontrolünde beyaz hale kalmadı. Geniş ağızlı keski tüysüz.

| Ürün | Kaynak | kart.jpg | webp | avif | Önizleme |
| --- | --- | ---: | ---: | ---: | --- |
| canak-firca-sacakli | DSC_9025 | 3590 | 13598 | 9142 | `scripts/raporlar/a1b-kartlar/canak-firca-sacakli.jpg` |
| canak-firca-burgulu | DSC_8978 | 3234 | 9858 | 7083 | `scripts/raporlar/a1b-kartlar/canak-firca-burgulu.jpg` |
| plastik-sapli-celik-tel-firca | DSC_8926 | 1506 | 2472 | 1792 | `scripts/raporlar/a1b-kartlar/plastik-sapli-celik-tel-firca.jpg` |
| genis-agizli-keski | DSC_9114 | 1369 | 1328 | 1256 | `scripts/raporlar/a1b-kartlar/genis-agizli-keski.jpg` |

Üretilen galeri yolları (katalog kaydı A2'de):

- `assets/images/products/canak-firca-sacakli/` — 12 kare, ana `canak-firca-sacakli.webp` (DSC_8984)
- `assets/images/products/canak-firca-burgulu/` — 12 kare, ana `canak-firca-burgulu.webp` (DSC_8974)
- `assets/images/products/plastik-sapli-celik-tel-firca/` — 4 kare, ana `plastik-sapli-celik-tel-firca.webp` (DSC_8926)
- `assets/images/products/genis-agizli-keski/` — 2 kare, ana `genis-agizli-keski.webp` (DSC_9114)

Her klasörde `-galeri-NN.{avif,webp,jpg}`, `-galeri-NN-thumb.{avif,webp,jpg}`, cover/og/wa ve menu-thumb de var. Tam liste `a1b-run.json` içindeki `images` alanlarında.

## Lightbox

Tam boy artık WebP öncelikli. `product-detail.js` küçük resme `data-full-webp` yazıyor. `gallery-lightbox.js` aday listesini `ABRALION_IMAGE.buildSingleImageCandidates` ile kuruyor (webp, sonra png, sonra jpg). Aynı değişiklik RU kopyasında.

Pilot sayfa (`urun/miknatisli-anahtar-ucu.html`): ilk yüklemede 8 küçük webp, tam boy dosya yok. Lightbox `miknatisli-anahtar-ucu-galeri-01.webp` (1064×1600) açtı, sonraki kare `...-galeri-02.webp`. Pilot galeride webp, jpg'ye göre %53–65 küçük (örnek 01: 15278 / 40017, %62).

## Kapanış

- `products-data.min.js` ve kök `products-data.js` senkron.
- Önbellek sorgu anahtarları yenilendi. Pilot sayfa `gallery-lightbox.js?v=3bc452f3`.
- Audit: 0 kırık. Dört yeni klasör HTML'den henüz bağlı değil; A2/A3 bağlayacak.
- A2 (katalog metni, `data/katalog-kasim2026-icerik.json`) bu turda başlamadı. Onay bekliyor.
