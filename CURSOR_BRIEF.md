# ABRALION — Cursor Görev Paketi
## Haziran 2026 Katalog Güncellemesi

---

## ÖNCE OKU — SİSTEM NASIL ÇALIŞIYOR

JS mimarisi şu şekilde:
- `products-data.js` → `window.ABRALION_CATALOG` global objesini tanımlar
- `ProductManager.js` → bu objeyi okur, ürünleri yönetir
- `product-detail.js` → `body[data-product-id]`'den slug okur, ürünü bulur, tüm sayfayı JS ile doldurur
- `MegaMenu.js` → kategorileri ve ürünleri `ABRALION_CATALOG`'dan okur
- `VariantDisplay.js` → `PRODUCT_TABLE_COLUMNS` objesiyle hangi sayfada hangi sütunların gösterileceğini bilir

**HTML sayfaları sadece iskelet.** İçerik tamamen JS tarafından doldurulur.

---

## GÖREV 1 — ESKİ DOSYALARI SİL

Şu dosyaları sil:

```
urun/ao-aluminyum-oksit-flap-disk.html
urun/355mm-metal-sabit-tezgah-kesme-diski.html
urun/abs-govdeli-profesyonel-serit-metre.html
urun/hss-matkap-ucu.html
urun/maket-bicagi-yedek-ucu.html
urun/metal-inox-kesme-tasi.html
urun/metal-inox-taslama-diski.html
urun/sivri-uclu-keski-murc-sds-max.html
urun/sivri-uclu-keski-murc-sds-plus.html
```

---

## GÖREV 2 — products-data.js'yi DEĞİŞTİR

`assets/js/products-data.js` dosyasını bu paketteki `products-data.js` ile tamamen değiştir.

Bu dosya `window.ABRALION_CATALOG` objesini içerir. Yeni katalogda 4 kategori ve 22 ürün var.

---

## GÖREV 3 — VariantDisplay.js'e YENİ ÜRÜN SATIRLARI EKLE

`assets/js/VariantDisplay.js` içindeki `PRODUCT_TABLE_COLUMNS` objesine şu yeni ürün slug'larını ekle. Mevcut satırları silme, sadece yenilerini ekle:

```javascript
// --- YENİ ÜRÜNLER (Haziran 2026 Kataloğu) ---

'zr-zirkon-flap-disk': [
  { key: 'urun_kodu',      label: 'Ürün Kodu' },
  { key: 'daire_capi_mm',  label: 'Daire Çapı Ø' },
  { key: 'gobek_capi_mm',  label: 'Göbek Çapı Ø' },
  { key: 'asindirici_tipi',label: 'Aşındırıcı Tipi' },
  { compute: 'max_hiz_flap_rpm', label: 'Maksimum Hız (Rpm)' },
  { key: 'grit',           label: 'Grit' },
  { key: 'kutu_adet',      label: 'Kutu' },
  { key: 'koli_adet',      label: 'Koli' },
],

'segmentli-standart-elmas-kesici': [
  { key: 'urun_kodu',     label: 'Ürün Kodu' },
  { key: 'daire_capi_mm', label: 'Daire Çapı Ø' },
  { key: 'gobek_capi_mm', label: 'Göbek Çapı Ø' },
  { compute: 'max_hiz_rpm_only', label: 'Maksimum Hız (Rpm)' },
  { key: 'kutu_adet',     label: 'Kutu' },
  { key: 'koli_adet',     label: 'Koli' },
],

'ultra-ince-elmas-disk': [
  { key: 'urun_kodu',     label: 'Ürün Kodu' },
  { key: 'daire_capi_mm', label: 'Daire Çapı Ø' },
  { key: 'gobek_capi_mm', label: 'Göbek Çapı Ø' },
  { compute: 'max_hiz_rpm_only', label: 'Maksimum Hız (Rpm)' },
  { key: 'kutu_adet',     label: 'Kutu' },
  { key: 'koli_adet',     label: 'Koli' },
],

'granit-mermer-segmentli-taslama-diski': [
  { key: 'urun_kodu',     label: 'Ürün Kodu' },
  { key: 'daire_capi_mm', label: 'Daire Çapı Ø' },
  { key: 'gobek_capi_mm', label: 'Göbek Çapı Ø' },
  { compute: 'max_hiz_rpm_only', label: 'Maksimum Hız (Rpm)' },
  { key: 'kutu_adet',     label: 'Kutu' },
  { key: 'koli_adet',     label: 'Koli' },
],

'asfalt-elmas-kesme-diski': [
  { key: 'urun_kodu',     label: 'Ürün Kodu' },
  { key: 'daire_capi_mm', label: 'Daire Çapı Ø' },
  { key: 'gobek_capi_mm', label: 'Göbek Çapı Ø' },
  { compute: 'max_hiz_ms_only', label: 'Maksimum Hız (m/s)' },
  { key: 'kutu_adet',     label: 'Kutu' },
  { key: 'koli_adet',     label: 'Koli' },
],

'beton-elmas-kesme-diski': [
  { key: 'urun_kodu',     label: 'Ürün Kodu' },
  { key: 'daire_capi_mm', label: 'Daire Çapı Ø' },
  { key: 'gobek_capi_mm', label: 'Göbek Çapı Ø' },
  { compute: 'max_hiz_ms_only', label: 'Maksimum Hız (m/s)' },
  { key: 'kutu_adet',     label: 'Kutu' },
  { key: 'koli_adet',     label: 'Koli' },
],

'genel-amacli-elmas-kesme-diski': [
  { key: 'daire_capi_mm', label: 'Daire Çapı Ø' },
  { key: 'gobek_capi_mm', label: 'Göbek Çapı Ø' },
  { compute: 'max_hiz_ms_only', label: 'Maksimum Hız (m/s)' },
  { key: 'kutu_adet',     label: 'Kutu' },
  { key: 'koli_adet',     label: 'Koli' },
],

'sds-plus-2-kesicili-beton-matkap-ucu': [
  { key: 'urun_tipi',          label: 'Ürün Tipi' },
  { key: 'cap_mm',             label: 'Çap (mm)' },
  { key: 'toplam_uzunluk_mm',  label: 'Toplam Uzunluk (mm)' },
  { key: 'baglanti_tipi',      label: 'Bağlantı Tipi' },
  { key: 'kutu_adet',          label: 'Kutu' },
  { key: 'koli_adet',          label: 'Koli' },
],

'sds-plus-4-kesicili-beton-matkap-ucu': [
  { key: 'urun_tipi',          label: 'Ürün Tipi' },
  { key: 'cap_mm',             label: 'Çap (mm)' },
  { key: 'toplam_uzunluk_mm',  label: 'Toplam Uzunluk (mm)' },
  { key: 'baglanti_tipi',      label: 'Bağlantı Tipi' },
  { key: 'kutu_adet',          label: 'Kutu' },
  { key: 'koli_adet',          label: 'Koli' },
],

'duz-keski': [
  { key: 'urun_tipi',                   label: 'Ürün Tipi' },
  { compute: 'olcu_saft_uzunluk_uc',    label: 'Ölçü (Şaft x Uzunluk x Uç)' },
  { key: 'baglanti_tipi',               label: 'Bağlantı Tipi' },
  { key: 'malzeme',                     label: 'Malzeme' },
  { key: 'kutu_adet',                   label: 'Kutu' },
  { key: 'koli_adet',                   label: 'Koli' },
],

'sivri-uclu-keski-murc': [
  { key: 'urun_tipi',               label: 'Ürün Tipi' },
  { compute: 'olcu_saft_uzunluk',   label: 'Ölçü (Şaft x Uzunluk)' },
  { key: 'baglanti_tipi',           label: 'Bağlantı Tipi' },
  { key: 'malzeme',                 label: 'Malzeme' },
  { key: 'kutu_adet',               label: 'Kutu' },
  { key: 'koli_adet',               label: 'Koli' },
],

'cam-seramik-matkap-ucu': [
  { key: 'cap_mm',        label: 'Çap (mm)' },
  { key: 'saft_tipi',     label: 'Şaft Tipi' },
  { key: 'kutu_ici_adet', label: 'Kutu İçi Adet' },
  { key: 'koli_adet',     label: 'Koli' },
],

'sds-max-burc-aleti': [
  { key: 'baglanti_tipi',  label: 'Bağlantı Tipi' },
  { key: 'kafa_olcusu_mm', label: 'Kafa Ölçüsü' },
  { key: 'uzunluk_mm',     label: 'Uzunluk' },
  { key: 'kutu_adet',      label: 'Kutu' },
  { key: 'koli_adet',      label: 'Koli' },
],

'miknatisli-anahtar-ucu': [
  { key: 'urun_tipi',       label: 'Ürün Tipi' },
  { compute: 'olcu_cap_uzunluk', label: 'Ölçü (Çap x Uzunluk)' },
  { key: 'malzeme',         label: 'Malzeme' },
  { key: 'kutu_ici_adet',   label: 'Kutu İçi Adet' },
  { key: 'koli_adet',       label: 'Koli' },
],

'ph2-manyetik-bits-uc': [
  { key: 'urun_tipi',     label: 'Ürün Tipi' },
  { key: 'uc_tipi',       label: 'Uç Tipi' },
  { key: 'uzunluk_mm',    label: 'Uzunluk' },
  { key: 'malzeme',       label: 'Malzeme' },
  { key: 'kutu_ici_adet', label: 'Kutu İçi Adet' },
  { key: 'koli_adet',     label: 'Koli' },
],

'profesyonel-maket-bicagi': [
  { key: 'urun_tipi',         label: 'Ürün Tipi' },
  { key: 'bicak_genisligi_mm',label: 'Bıçak Genişliği' },
  { key: 'govde_kizak_tipi',  label: 'Gövde / Kızak Tipi' },
  { key: 'bicak_malzemesi',   label: 'Bıçak Malzemesi' },
  { key: 'kutu_ici_adet',     label: 'Kutu İçi' },
  { key: 'koli_adet',         label: 'Koli' },
],
```

---

## GÖREV 4 — YENİ HTML SAYFALARI OLUŞTUR

`urun/` klasöründe şu 22 dosyayı oluştur. Her biri aynı iskelet yapıda olacak.

### Oluşturulacak dosyalar:
```
urun/metal-inox-kesme-tasi.html
urun/355mm-metal-sabit-tezgah-kesme-diski.html
urun/metal-inox-taslama-diski.html
urun/zr-zirkon-flap-disk.html
urun/ao-aluminyum-oksit-flap-disk.html
urun/segmentli-standart-elmas-kesici.html
urun/ultra-ince-elmas-disk.html
urun/granit-mermer-segmentli-taslama-diski.html
urun/asfalt-elmas-kesme-diski.html
urun/beton-elmas-kesme-diski.html
urun/genel-amacli-elmas-kesme-diski.html
urun/sds-plus-2-kesicili-beton-matkap-ucu.html
urun/sds-plus-4-kesicili-beton-matkap-ucu.html
urun/hss-matkap-ucu.html
urun/duz-keski.html
urun/sivri-uclu-keski-murc.html
urun/cam-seramik-matkap-ucu.html
urun/sds-max-burc-aleti.html
urun/miknatisli-anahtar-ucu.html
urun/ph2-manyetik-bits-uc.html
urun/profesyonel-maket-bicagi.html
urun/abs-govdeli-profesyonel-serit-metre.html
```

### HTML iskelet (mevcut metal-inox-kesme-tasi.html'i referans al):

Her dosya için mevcut herhangi bir ürün sayfasından kopyala ve şu değerleri değiştir:

| Değiştirilecek | Yeni değer |
|---|---|
| `data-product-id="metal-inox-kesme-tasi"` | `data-product-id="{slug}"` |
| `<title>Metal / Inox Kesme Taşı - Abralion</title>` | `<title>{ürün adı} - Abralion</title>` |
| `<meta name="description" content="...">` | Ürüne uygun kısa açıklama |
| `<link rel="canonical" href="...">` | `https://abralion.com/urun/{slug}.html` |
| `og:title`, `og:description`, `og:image` | Ürüne uygun değerler |
| `og:image` URL'si | `https://abralion.com/assets/images/products/{slug}/{slug}.webp` |

**Tüm `../` path'leri korunacak** — sayfalar `urun/` altında olduğu için `../assets/...` doğru.

**Script listesi her sayfada aynı** — mevcut sayfadan kopyala, değiştirme.

---

## GÖREV 5 — GÖRSEL KLASÖRÜ YAPISI

Şu klasörleri oluştur (içleri şimdilik boş olabilir — görseller sonra yüklenecek):

```
assets/images/products/zr-zirkon-flap-disk/
assets/images/products/segmentli-standart-elmas-kesici/
assets/images/products/ultra-ince-elmas-disk/
assets/images/products/granit-mermer-segmentli-taslama-diski/
assets/images/products/asfalt-elmas-kesme-diski/
assets/images/products/beton-elmas-kesme-diski/
assets/images/products/genel-amacli-elmas-kesme-diski/
assets/images/products/sds-plus-2-kesicili-beton-matkap-ucu/
assets/images/products/sds-plus-4-kesicili-beton-matkap-ucu/
assets/images/products/duz-keski/
assets/images/products/sivri-uclu-keski-murc/
assets/images/products/cam-seramik-matkap-ucu/
assets/images/products/sds-max-burc-aleti/
assets/images/products/miknatisli-anahtar-ucu/
assets/images/products/ph2-manyetik-bits-uc/
assets/images/products/profesyonel-maket-bicagi/
```

Her klasörde `.gitkeep` veya boş bir placeholder dosyası bırak.

---

## GÖREV 6 — KATEGORİ ID GÜNCELLEMESİ

Yeni `products-data.js`'de kategori ID'leri değişti. Eski ve yeni karşılaştırması:

| Eski ID | Yeni ID |
|---|---|
| `kesici-taslama-flap-disk` | `kesici-taslama-flap-disk` *(aynı)* |
| `elmas-kesici` | `elmas-kesici` *(aynı)* |
| `uclar` | `kirici-delici` *(değişti!)* |
| `maket-bicaklari` | `olcum-kesim` *(değişti!)* |
| `metreler` | `olcum-kesim` *(birleşti!)* |

`urunler.html` içindeki category filter butonlarını kontrol et. `data-category="uclar"` veya `data-category="maket-bicaklari"` veya `data-category="metreler"` geçen yerleri yeni ID'lerle güncelle.

Footer'daki kategori linklerini de güncelle:
```html
<!-- ESKİ -->
<a href="../urunler.html?kategori=uclar">Kırıcı &amp; Delici</a>
<a href="../urunler.html?kategori=maket-bicaklari">Maket Bıçakları</a>
<a href="../urunler.html?kategori=metreler">Metreler</a>

<!-- YENİ -->
<a href="../urunler.html?kategori=kirici-delici">Kırıcı &amp; Delici</a>
<a href="../urunler.html?kategori=olcum-kesim">Metreler &amp; Maket Bıçakları</a>
```

---

## GÖREV 7 — GÖRSEL PATH KURALI

Görsel path'leri `products-data.js`'de tanımlı. Format:

```
assets/images/products/{slug}/{slug}.webp           ← ana ürün (800x800)
assets/images/products/{slug}/{slug}-etiket.webp    ← etiket detay (800x800)
assets/images/products/{slug}/{slug}-kullanim.webp  ← aktif kullanım (800x800)
assets/images/products/{slug}/{slug}-varyasyon.webp ← grup görseli (800x800, bazı ürünlerde yok)
```

Görseller henüz yüklenmemiş. `product-detail.js` `images[]` dizisinden okuyarak galeriyi oluşturur, dosya olmasa da hata vermez.

---

## ÖZET — NE DEĞİŞİYOR

| Dosya | İşlem |
|---|---|
| `assets/js/products-data.js` | **Tamamen değiştir** (paketteki dosyayla) |
| `assets/js/VariantDisplay.js` | **Yeni satırlar ekle** (PRODUCT_TABLE_COLUMNS'a) |
| `urun/*.html` (9 eski dosya) | **Sil** |
| `urun/*.html` (22 yeni dosya) | **Oluştur** |
| `assets/images/products/*/` (16 yeni klasör) | **Oluştur** |
| `urunler.html` | **Kategori ID'lerini güncelle** |
| Tüm sayfalardaki footer | **Kategori linklerini güncelle** |

---

## KRİTİK NOTLAR

1. `productUrl()` fonksiyonu `site.js`'de tanımlı: `${base}urun/${slug}.html` — yani tüm ürün sayfaları `urun/` altında, alt klasör yok.

2. `product-detail.js` sayfayı tamamen JS ile dolduruyor — HTML sadece `data-product-id` attribute'unu taşıyor, içerik boş olabilir.

3. `products-data.js` değiştiğinde mega menü, ürünler sayfası, ilgili ürünler — hepsi otomatik güncellenir.

4. Mevcut ürünlerin `id` ve `slug`'ları değişmedi — sadece kategori ID'leri güncellendi.
