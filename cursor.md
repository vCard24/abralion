# Abralion B2B Katalog — Proje Bağlamı (Cursor)

> Bu dosya yarın ve sonraki oturumlarda bağlam kaybını önlemek içindir.  
> Son güncelleme: **21 Mayıs 2026**

---

## Proje özeti

- **Tür:** Statik HTML/CSS/JS B2B ürün kataloğu (build aracı yok)
- **Dil:** Türkçe arayüz; Rusça katalog PDF’si mevcut
- **Firma:** Abralion — EKS-PLAST LLC (Rusya’daki Türk firmalarına endüstriyel kesim/taşlama ürünleri)
- **Test:** `file://` ile yerel açılıyor → **`products-data.js` zorunlu** (fetch CORS sorunu)
- **Referans proje:** `C:\Users\mosta\Desktop\abralion\` (orijinal tasarım kaynağı)

**Ölçek:** 5 kategori, **24 ürün** (alt ürün varyantları JSON içinde)

---

## Dizin yapısı

```
abralion-cursor/
├── index.html              # Ana sayfa
├── urunler.html            # Ürün listesi + kategori filtreleri
├── karsilastir.html        # Ürün karşılaştırma (max 4 slot)
├── dokumanlar.html         # PDF kataloglar + güvenlik rehberleri
├── hakkimizda.html
├── iletisim.html           # Form + FormValidator.js
├── urunler.json            # Kaynak veri (Excel/PDF’den türetilmiş)
├── data/
│   └── products.json       # Normalize edilmiş katalog (fetch hedefi)
├── urun/
│   └── {slug}.html         # 24 ürün detay sayfası (JS ile doldurulur)
├── assets/
│   ├── css/
│   │   ├── main.css
│   │   ├── components.css  # Header, mega menü, kartlar
│   │   ├── responsive.css
│   │   ├── dark-theme.css
│   │   ├── site-extra.css  # Proje özel düzeltmeler (öncelikli)
│   │   ├── compare.css
│   │   └── product-detail-page.css
│   ├── js/
│   │   ├── site.js         # getBasePath(), productUrl()
│   │   ├── products-data.js # window.ABRALION_CATALOG (file:// için)
│   │   ├── ProductManager.js, ProductCard.js, CompareManager.js
│   │   ├── MegaMenu.js, Header.js, ThemeToggle.js
│   │   ├── product-detail.js, product-gallery.js, VariantDisplay.js
│   │   └── pages/          # home.js, urunler.js, karsilastir.js, contact.js
│   ├── images/
│   │   ├── logo.svg, logo-beyaz.svg, arma.svg
│   │   └── products/{slug}/  # Ürün galeri görselleri
│   └── documents/          # PDF dosyaları
└── scripts/
    ├── normalize.py        # urunler.json → products.json + products-data.js
    ├── update_layout.py    # Tüm HTML header/footer güncelle
    ├── generate-product-pages.py
    ├── fix_encoding.py, fix_html_body.py, fix_dokumanlar_ru.py
    └── extract_pdf_tables.py
```

---

## Veri akışı

```
urunler.json  ──normalize.py──►  data/products.json
                              └──►  assets/js/products-data.js
```

| Dosya | Rol |
|--------|-----|
| `urunler.json` | Ham kaynak; `kategori`, `alt_kategori`, `urunler[]` |
| `data/products.json` | `categories[]` + `products[]` (slug, variants, images, schema) |
| `products-data.js` | Aynı JSON, `window.ABRALION_CATALOG` — **file:// test** |

### Kategoriler

| Görünen ad | `id` (URL: `?kategori=`) | Ürün sayısı (yaklaşık) |
|------------|-------------------------|-------------------------|
| Kesici - Taşlama - Flap Disk | `kesici-taslama-flap-disk` | 5 |
| Elmas Kesici | `elmas-kesici` | 5 |
| **Kırıcı & Delici** | `uclar` | 10 |
| Maket Bıçakları | `maket-bicaklari` | 3 |
| Metreler | `metreler` | 1 |

> **Not:** Eski ad “Uçlar” idi; görünen ad **Kırıcı & Delici** olarak değiştirildi. URL parametresi hâlâ `uclar` (geri uyumluluk).

### Ürün slug listesi (24)

`metal-inox-kesme-tasi`, `355mm-metal-sabit-tezgah-kesme-diski`, `metal-inox-taslama-diski`, `zr-zirkon-flap-disk`, `ao-aluminyum-oksit-flap-disk`, `segmentli-standart-elmas-kesici`, `ultra-ince-elmas-disk`, `granit-ve-mermer-segmentli-taslama-diski`, `asfalt-icin-elmas-kesme-diski`, `guclendirilmis-beton-icin-elmas-kesme-diski`, `sds-max-burc-aleti-tarakli-murc`, `hss-matkap-ucu`, `sds-plus-4-kesicili-beton-matkap-ucu-quadro`, `miknatisli-anahtar-ucu-manyetik-somun-adaptoru`, `ph2-manyetik-bits-uc`, `duz-keski-sds-plus`, `duz-keski-sds-max`, `sivri-uclu-keski-murc-sds-plus`, `sivri-uclu-keski-murc-sds-max`, `cok-fonksiyonlu-cam-ve-seramik-matkap-ucu-4-kesicili`, `profesyonel-plastik-maket-bicagi`, `profesyonel-metal-maket-bicagi`, `maket-bicagi-yedek-ucu`, `abs-govdeli-profesyonel-serit-metre`

---

## Sayfalar ve JS

| Sayfa | Sayfa JS | Özel not |
|-------|----------|----------|
| `index.html` | `pages/home.js` | Öne çıkan ürünler |
| `urunler.html` | `pages/urunler.js` | `?kategori=` filtre, sidebar butonları |
| `urun/*.html` | `product-detail.js`, `product-gallery.js` | `body[data-product-id]`, `data-base="../"` |
| `karsilastir.html` | `pages/karsilastir.js` | Matris tablo, boş hücre: ` - `, max 4 |
| `dokumanlar.html` | — | Statik kartlar |
| `iletisim.html` | `pages/contact.js` | `FormValidator.js` |

**Ortak script sırası (kök sayfalar):**  
`site.js` → `products-data.js` → `CompareManager` → `ProductManager` → `ProductCard` → `Header` → `MegaMenu` → `ThemeToggle` → `main.js` → sayfa JS

**Mega menü:** `MegaMenu.js` → `#mega-menu` içine kategorileri ve ürün linklerini dinamik yazar.

---

## CSS katmanları (yüklenme sırası)

1. `main.css` — genel layout, döküman sayfası temel stilleri  
2. `components.css` — header, dropdown, mega menü, kartlar  
3. `responsive.css` — breakpoint’ler (768px mobil menü)  
4. `dark-theme.css`  
5. `site-extra.css` — **proje özel düzeltmeler** (grid, dokümanlar, ürün kartı butonları)  
6. Sayfa özel: `compare.css`, `product-detail-page.css`

---

## Python scriptleri (sık kullanılan)

```powershell
cd c:\Users\mosta\Desktop\abralion-cursor

# Veri güncelle (urunler.json değiştiyse)
python scripts/normalize.py

# Header/footer tüm HTML’lere uygula
python scripts/update_layout.py

# Ürün detay sayfalarını yeniden üret
python scripts/generate-product-pages.py
```

### `normalize.py` önemli sabitler

- `CATEGORY_IDS` — kategori adı → `id`
- `SCHEMA_MAP` — varyant tablo şeması (`disk-kesici-taslama`, `matkap-uc`, …)
- `CUSTOM_IMAGES` — slug bazlı galeri; normalize sırasında **korunur**

**Yeni ürün galerisi ekleme akışı:**

1. Görselleri `assets/images/products/{slug}/` altına koy  
2. `CUSTOM_IMAGES` içine ekle  
3. `python scripts/normalize.py`  
4. Gerekirse `generate-product-pages.py`

---

## Dökümanlar (`dokumanlar.html`)

| PDF | Açıklama |
|-----|----------|
| `abralion_turkce_katalog.pdf` | Türkçe katalog |
| `abralion_russian_cataloque.pdf` | Rusça katalog |
| `guvenlik-asindirici-urunler.pdf` | Aşındırıcı güvenlik |
| `delici-ve-kirici-urunler-guvenlik-rehberi.pdf` | Delici/kırıcı güvenlik |

Her kartta **İndir** + **Tarayıcıda Aç** (`target="_blank"`).

---

## Bu oturumda yapılanlar (20–21 Mayıs 2026)

### Tamamlanan

1. **Dökümanlar sayfası** — Referans `documents.html` ile hizalandı; güvenlik bölümü grid’de `auto-fit` + 2 sütun (`site-extra.css`); Rusça kart HTML düzeltildi.  
2. **Kategori yeniden adlandırma** — “Uçlar” → **“Kırıcı & Delici”** (`urunler.json`, `normalize.py`, 30 HTML footer, `urunler.html` sidebar). URL: `?kategori=uclar` aynı kaldı.  
3. **Mega menü** — Taşma sorunu: 3 sütunlu grid, `max-height: min(85vh, 680px)`, `overflow-y: auto`, sticky “Tüm Ürünleri Gör”, nav altında ortalama (`components.css` + `site-extra.css` scrollbar).

### Önceki oturumlardan (özet)

- 24 ürün sayfası, karşılaştırma matrisi, iletişim formu, ürün galerileri (`CUSTOM_IMAGES`), encoding fix scriptleri, mobilde kart butonları `width:100%` düzeltmesi, `file://` için `products-data.js`.

---

## Kullanıcı tercihleri

- Minimal kapsam; gereksiz refactor yok  
- `file://` test; değişiklikten sonra **Ctrl+F5**  
- Karşılaştırma: kategoriler arası OK, boş hücre ` - `, 4 slot  
- Ürün galerisi: `aspect-ratio: 1/1`, `object-fit: contain`  
- Git commit yalnızca istenirse

---

## Bilinen / isteğe bağlı iyileştirmeler

- [ ] Mega menüde kategori başına max 6 ürün + “Tümünü gör” (daha kısa menü)  
- [ ] Kalan mojibake taraması (`Ã`, `ğŸ` vb.)  
- [ ] `index.html` satır 17: `href=\"#main-content\"` kaçış hatası (görsel sorun yoksa düşük öncelik)  
- [ ] Canlı sunucuda `products-data.js` yerine yalnızca `data/products.json` fetch yeterli olabilir

---

## Hızlı referans — önemli dosyalar

| Konu | Dosya |
|------|--------|
| Kategori / ürün verisi | `urunler.json`, `data/products.json` |
| Mega menü JS | `assets/js/MegaMenu.js` |
| Mega menü CSS | `assets/css/components.css` (`.mega-menu`) |
| Footer şablonu | `scripts/update_layout.py` |
| Karşılaştırma | `assets/js/pages/karsilastir.js`, `assets/css/compare.css` |
| Proje özel CSS | `assets/css/site-extra.css` |

---

## Cursor’a not

Yeni oturumda bu dosyayı okuyun veya kullanıcıya “`cursor.md`’ye göre devam et” deyin. Veri değişikliğinde önce `normalize.py`, layout değişikliğinde `update_layout.py` çalıştırılmalı.
