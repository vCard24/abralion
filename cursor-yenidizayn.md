# Abralion — Stitch Noir Yeniden Tasarım Bağlamı

> Son güncelleme: 2026-05-23  
> Son push: `685ad3b` — `feat: Stitch Noir redesign for Abralion site` (`main`)

Bu dosya, Cursor oturumları arasında bağlam kaybını önlemek için önemli kararları, dosya haritasını ve yeniden üretim komutlarını özetler.

---

## Hedef

Eski Abralion sitesini **Stitch “Precision Industrial Noir”** tasarımına taşımak. Referans dosyalar genelde şu klasörde:

```
c:\Users\mosta\Desktop\abralion-doneler\indirilenler-abralion\stitch_abralion_website_redesign\stitch_abralion_website_redesign\
```

Örnek sayfalar:
| Sayfa | Referans |
|-------|----------|
| Ana sayfa / header | `ana_sayfa_abralion_1\code.html` |
| Ürünler | `urunler_abralion\code.html` (veya benzeri) |
| Karşılaştır | `urun_karsilastirma_abralion\urun-karsilastir.html` |
| İletişim | `i_leti_im_abralion\code.html` |
| Dökümanlar | `d_k_manlar_abralion\dokumanlar.html` |

---

## Mimari (kısa)

- **Tailwind CDN** + `assets/js/tailwind-config.js` — Stitch renk/spacing/font token’ları
- **`assets/css/noir-migration.css`** — Sayfa arka planları, header, footer, hero, karşılaştırma tablosu, öne çıkan carousel; legacy CSS sıfırlamaları
- **Eski CSS hâlâ yükleniyor:** `main.css`, `components.css`, `dark-theme.css`, `site-extra.css` — çakışmalar `noir-migration.css` ile `header.header`, `footer.footer` gibi yüksek özgüllükle giderildi
- **Body sınıfı:** `page-noir-site bg-carbon-black text-on-surface font-body-md`
- **Erken tema:** `assets/js/theme-init.js` — `dark-theme` + footer `[data-logo]` (kare logo: `logo-beyaz.svg`)

---

## Tamamlanan ana işler

### 1. Sayfa migrasyonları (Noir shell)
| Dosya | Not |
|-------|-----|
| `index.html` | Hero, bento, öne çıkan carousel |
| `urunler.html` | Katalog grid, filtreler |
| `dokumanlar.html` | Katalog / güvenlik PDF’leri |
| `iletisim.html` | Form korundu (`contact-form`, `contact.js`); yalnızca Rusya ofisi |
| `hakkimizda.html` | |
| `karsilastir.html` | Dinamik tablo: `assets/js/pages/karsilastir.js` |
| `urun/*.html` (24 ürün) | Şablon: `scripts/templates/product-detail-noir.html` |

### 2. Header (Stitch TopNavBar)
- **Logo:** `assets/images/logo-beyaz-yatay.svg` (yatay; header’da `data-logo` kullanılmıyor)
- **Yapı:** logo + menü solda; sağda Karşılaştır + **Teklif Al** (`iletisim.html`)
- **Arama kutusu** header’dan kaldırıldı (Stitch’te yok)
- **Kaynak şablonlar:** `scripts/includes/header-root.html`, `scripts/includes/header-subdir.html`
- **Toplu güncelleme:** `python scripts/patch_header_stitch.py`
- **Mobil menü:** `assets/js/Header.js` — nav `.header-brand-nav` içine geri yerleştirilir
- **Font:** Inter 16px / 400; aktif link kırmızı + alt çizgi — `dark-theme.css` override’ları `noir-migration.css` ile ezildi

### 3. Footer
- Sosyal ikon satırı (globe/mail) kaldırıldı
- Abralion logosu + EKS-PLAST metni; sertifikalar `site.js` → `initFooterCerts()`
- **Kritik fix:** `footer.footer` üzerinde `all: unset` kullanılmamalı — Tailwind renklerini siliyordu, metin görünmez oluyordu
- Footer logo: `logo-beyaz.svg` + `footer-logo-link`

### 4. Ana sayfa — Öne Çıkan Çözümler
- Carousel: masaüstü **3 kart**, tablet 2, mobil 1
- **`ProductCard` `compact: true`** — açıklama, ölçü (mm), DETAYLAR satırı HTML’de üretilmiyor
- JS: `assets/js/pages/home.js` → `renderProductCards(grid, featured, { compact: true })`
- CSS yedek: `#featured-products-grid .product-card-actions { display: none }`

### 5. Mega menü — hover önizleme
- Ürün listesinde gezinince sağdaki büyük görsel (`mega-menu-feature`) eşleşen ürünle güncellenir
- **Dosya:** `assets/js/MegaMenu.js` — `setPanelFeature`, `initPanelProductPreview`
- Kategori sekmesi değişince görsel o kategorinin ilk ürününe döner

### 6. Ürün kartları / görseller
- Katalog kartlarında görsel: `object-cover`, tam alan (`ProductCard.js`)
- Kart görseli yolu: `assets/images/products/{slug}/{slug}-kart.jpg` (istisna: `metal-inox-kesme-tasi` → png)

### 7. Karşılaştırma sayfası
- Siyah okunamaz metin: `compare.css` + `noir-migration.css` renk override’ları
- Hook’lar korundu: `#compare-content`, `compare-matrix-remove`, `clear-compare`

---

## Önemli dosyalar

| Dosya | Rol |
|-------|-----|
| `assets/css/noir-migration.css` | Noir sayfa + header/footer/carousel/compare |
| `assets/js/tailwind-config.js` | Tailwind tema |
| `assets/js/Header.js` | Mobil menü, aktif sayfa, arama (artık DOM’da yok) |
| `assets/js/MegaMenu.js` | Kategori mega menü + hover önizleme |
| `assets/js/ProductCard.js` | Katalog kartı; `compact`, `noir` seçenekleri |
| `assets/js/pages/home.js` | Öne çıkan carousel |
| `assets/js/pages/karsilastir.js` | Karşılaştırma tablosu |
| `assets/js/site.js` | Footer sertifikalar, `productUrl`, thumb URL |
| `scripts/templates/product-detail-noir.html` | Ürün sayfası shell |
| `scripts/generate-product-pages.py` | Ürün HTML üretimi |

---

## Yardımcı script’ler

```bash
# Header’ı tüm HTML’lere uygula
python scripts/patch_header_stitch.py

# Ürün sayfalarını şablondan yeniden üret
python scripts/generate-product-pages.py
```

Diğer patch script’leri (`patch_index_phase1.py`, `patch_urunler_noir.py`, …) tek seferlik migrasyon için kullanıldı; gerekirse referans olarak duruyor.

---

## Önbellek (cache bust) — güncellenince HTML’de artır

| Asset | Örnek sürüm (index.html) |
|-------|---------------------------|
| `noir-migration.css` | `?v=20260526b` |
| `Header.js` | `?v=20260526a` |
| `MegaMenu.js` | `?v=20260526c` |
| `home.js` | `?v=20260525m` |
| `ProductCard.js` | `?v=20260525m` |

CSS/JS değişince ilgili sayfalardaki `?v=` değerini artırın veya toplu replace script kullanın.

---

## Bilinen tuzaklar

1. **`all: unset` on footer/header** — Tailwind metin renklerini siler; kullanmayın.
2. **`dark-theme.css` header linkleri** — font-weight 600 / Segoe etkisi; header için `noir-migration.css` ile ezilmeli.
3. **`<motion>` etiketleri** — geçmişte HTML’e yanlışlıkla girmişti; `scripts/fix_motion_typos.py` ile düzeltildi.
4. **Header logo vs footer logo** — Header yatay SVG; footer kare `logo-beyaz.svg` (`data-logo`).
5. **İletişim** — İstanbul ofisi / harita kaldırıldı; yalnızca Moskova.
6. **PowerShell `&&` / karmaşık `python -c`** — Windows’ta script dosyası tercih edin.

---

## Korunması gereken hook’lar

- İletişim: `#contact-form`, alan id’leri, `assets/js/pages/contact.js`
- Karşılaştır: `#compare-content`, `CompareManager`, rozet `.compare-badge`
- Mega menü: `#mega-menu`
- Öne çıkan: `#featured-products-grid`, `[data-featured-carousel]`
- Ürün detay: varyant bölümü, galeri — `product-detail.js`, `VariantDisplay.js`

---

## Olası sonraki adımlar (backlog)

- [ ] Header / mega menü layout’unu Stitch referansıyla piksel düzeyinde son kontrol
- [ ] Büyük önizleme görselini mega menüde **sola** almak (şu an grid: liste sol, görsel sağ)
- [ ] `noir-migration.css` cache sürümlerini tüm sayfalarda eşitle
- [ ] Statik katalog fallback (`CATALOG_STATIC_*` index’te boş) — istenirse inject script
- [ ] Eski `main.css` / `dark-theme.css` bağımlılığını kademeli azaltma
- [ ] `scripts/` içindeki tek seferlik patch dosyalarını temizleme veya `scripts/README.md`

---

## Git

```bash
git log -1 --oneline   # 685ad3b feat: Stitch Noir redesign for Abralion site
git remote -v          # origin → github.com/vCard24/abralion.git
```

Yeni oturumda: bu dosyayı + ilgili HTML/JS/CSS dosyasını `@` ile referans verin.
