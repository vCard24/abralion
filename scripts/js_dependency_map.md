# JS global bağımlılık haritası

Otomatik üretim: `python scripts/js_dependency_audit.py`

## Sembol → tanımlayan dosya

| Global | Dosya |
|--------|-------|
| `ABRALION_CATALOG` | `products-data.min.js` |
| `ABRALION_IMAGE` | `product-image-utils.js` |
| `AbralionIcons` | `icons.js` |
| `CompareManager` | `CompareManager.js` |
| `FormValidator` | `FormValidator.js` |
| `GalleryLightbox` | `gallery-lightbox.js` |
| `Header` | `Header.js` |
| `MegaMenu` | `MegaMenu.js` |
| `ProductCard` | `ProductCard.js` |
| `ProductManager` | `ProductManager.js` |
| `QuoteManager` | `QuoteManager.js` |
| `bindGalleryImageFallback` | `product-image-utils.js` |
| `bindProductImageFallback` | `product-image-utils.js` |
| `buildProductImageCandidates` | `product-image-utils.js` |
| `buildQuotePageUrl` | `site.js` |
| `collectCompareKeysForQuote` | `site.js` |
| `compareManager` | `CompareManager.js` |
| `documentDownloadFilename` | `site.js` |
| `encodeCompareKeysForUrl` | `site.js` |
| `ensureAbralionPdfLogoDataUrl` | `quote-pdf-logo.js` |
| `getBasePath` | `site.js` |
| `getCompareKeysForPrefill` | `site.js` |
| `getSpecColumnClass` | `VariantDisplay.js` |
| `getTableColumns` | `VariantDisplay.js` |
| `initGalleryLightbox` | `gallery-lightbox.js` |
| `initPdfDownloadLinks` | `site.js` |
| `initPdfLinks` | `site.js` |
| `initProductGallery` | `product-gallery.js` |
| `isQuoteFromCompare` | `site.js` |
| `navigateToQuotePage` | `site.js` |
| `parseModelsFromUrl` | `site.js` |
| `primaryProductImageSrc` | `product-image-utils.js` |
| `productImageRelForFetch` | `product-image-utils.js` |
| `productMenuThumbUrl` | `site.js` |
| `productOgImage` | `og-meta.js` |
| `productThumbUrl` | `site.js` |
| `productUrl` | `site.js` |
| `quoteManager` | `QuoteManager.js` |
| `readCompareListFromStorage` | `site.js` |
| `readComparePrefillForQuote` | `site.js` |
| `resolveCatalogKeys` | `site.js` |
| `sanitizeDownloadLabel` | `site.js` |
| `saveComparePrefillForQuote` | `site.js` |
| `sendFormMail` | `site.js` |
| `setPageSocialMeta` | `og-meta.js` |
| `variantLabel` | `VariantDisplay.js` |
| `variantRowCells` | `VariantDisplay.js` |
| `variantSpecLines` | `VariantDisplay.js` |

## Dosya → tükettiği globaller (tarama)

- **CompareManager.js**: `CompareManager`, `compareManager`, `getBasePath`, `navigateToQuotePage`
- **FormValidator.js**: `FormValidator`
- **Header.js**: `Header`, `getBasePath`
- **MegaMenu.js**: `ABRALION_CATALOG`, `ABRALION_IMAGE`, `bindGalleryImageFallback`, `bindProductImageFallback`, `getBasePath`, `productMenuThumbUrl`, `productThumbUrl`, `productUrl`
- **ProductCard.js**: `AbralionIcons`, `ProductCard`, `bindProductImageFallback`, `compareManager`, `getBasePath`, `primaryProductImageSrc`, `productUrl`
- **ProductManager.js**: `ABRALION_CATALOG`, `ProductManager`, `getBasePath`
- **QuoteManager.js**: `QuoteManager`, `compareManager`, `quoteManager`
- **VariantDisplay.js**: `getSpecColumnClass`, `getTableColumns`, `variantLabel`, `variantRowCells`, `variantSpecLines`
- **contact.js**: `FormValidator`, `sendFormMail`
- **fiyat-teklifi.js**: `ABRALION_CATALOG`, `ProductManager`, `bindProductImageFallback`, `ensureAbralionPdfLogoDataUrl`, `getBasePath`, `getCompareKeysForPrefill`, `isQuoteFromCompare`, `primaryProductImageSrc`, `productImageRelForFetch`, `productUrl`, `quoteManager`, `resolveCatalogKeys`, `sendFormMail`, `variantLabel`, `variantSpecLines`
- **gallery-lightbox.js**: `GalleryLightbox`, `initGalleryLightbox`
- **home.bundle.min.js**: `ABRALION_CATALOG`, `ABRALION_IMAGE`, `AbralionIcons`, `CompareManager`, `Header`, `bindGalleryImageFallback`, `bindProductImageFallback`, `buildProductImageCandidates`, `buildQuotePageUrl`, `collectCompareKeysForQuote`, `compareManager`, `documentDownloadFilename`, `encodeCompareKeysForUrl`, `getBasePath`, `getCompareKeysForPrefill`, `initPdfDownloadLinks`, `initPdfLinks`, `isQuoteFromCompare`, `navigateToQuotePage`, `parseModelsFromUrl`, `primaryProductImageSrc`, `productImageRelForFetch`, `productMenuThumbUrl`, `productThumbUrl`, `productUrl`, `quoteManager`, `readCompareListFromStorage`, `readComparePrefillForQuote`, `resolveCatalogKeys`, `sanitizeDownloadLabel`, `saveComparePrefillForQuote`, `sendFormMail`
- **icons.js**: `AbralionIcons`
- **karsilastir.js**: `AbralionIcons`, `ProductManager`, `bindProductImageFallback`, `buildQuotePageUrl`, `compareManager`, `ensureAbralionPdfLogoDataUrl`, `getBasePath`, `navigateToQuotePage`, `primaryProductImageSrc`, `productImageRelForFetch`, `productUrl`, `quoteManager`, `variantSpecLines`
- **main.js**: `Header`, `compareManager`
- **og-meta.js**: `getBasePath`, `productOgImage`, `setPageSocialMeta`
- **product-detail.js**: `AbralionIcons`, `ProductManager`, `bindGalleryImageFallback`, `bindProductImageFallback`, `buildProductImageCandidates`, `compareManager`, `getBasePath`, `getSpecColumnClass`, `getTableColumns`, `initGalleryLightbox`, `initProductGallery`, `primaryProductImageSrc`, `setPageSocialMeta`, `variantLabel`, `variantRowCells`
- **product-gallery.js**: `GalleryLightbox`, `initProductGallery`
- **product-image-utils.js**: `ABRALION_IMAGE`, `bindGalleryImageFallback`, `bindProductImageFallback`, `buildProductImageCandidates`, `getBasePath`, `primaryProductImageSrc`, `productImageRelForFetch`
- **quote-pdf-logo.js**: `ensureAbralionPdfLogoDataUrl`
- **site.js**: `buildQuotePageUrl`, `collectCompareKeysForQuote`, `compareManager`, `documentDownloadFilename`, `encodeCompareKeysForUrl`, `getCompareKeysForPrefill`, `initPdfDownloadLinks`, `initPdfLinks`, `isQuoteFromCompare`, `navigateToQuotePage`, `parseModelsFromUrl`, `primaryProductImageSrc`, `productMenuThumbUrl`, `productThumbUrl`, `productUrl`, `quoteManager`, `readCompareListFromStorage`, `readComparePrefillForQuote`, `resolveCatalogKeys`, `sanitizeDownloadLabel`, `saveComparePrefillForQuote`, `sendFormMail`
- **urunler.js**: `ProductCard`, `ProductManager`, `getBasePath`, `productUrl`

## Sayfa script sırası

### `scripts/templates/product-detail-noir.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/355mm-metal-sabit-tezgah-kesme-diski.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/abs-govdeli-profesyonel-serit-metre.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/ao-aluminyum-oksit-flap-disk.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/asfalt-elmas-kesme-diski.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/beton-elmas-kesme-diski.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/cam-seramik-matkap-ucu.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/duz-keski-sds-max.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/duz-keski-sds-plus.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/genel-amacli-elmas-kesme-diski.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/granit-mermer-segmentli-taslama-diski.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/hss-matkap-ucu.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/metal-inox-kesme-tasi.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/metal-inox-taslama-diski.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/miknatisli-anahtar-ucu.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/ph2-manyetik-bits-uc.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/profesyonel-maket-bicagi.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/sds-max-burc-aleti.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/sds-plus-2-kesicili-beton-matkap-ucu.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/sds-plus-4-kesicili-beton-matkap-ucu.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/segmentli-standart-elmas-kesici.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/sivri-uclu-keski-murc-sds-max.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/sivri-uclu-keski-murc-sds-plus.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/ultra-ince-elmas-disk.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

### `urun/zr-zirkon-flap-disk.html`

1. `icons.js`
2. `product-image-utils.js`
3. `site.js`
4. `og-meta.js`
5. `products-data.min.js`
6. `VariantDisplay.js`
7. `CompareManager.js`
8. `ProductManager.js`
9. `Header.js`
10. `MegaMenu.js`
11. `product-gallery.js`
12. `gallery-lightbox.js`
13. `product-detail.js`
14. `main.js`

## Önerilen temel sıra (ürün / liste sayfaları)

1. `icons.js`
2. `product-image-utils.js` (site.js öncesi)
3. `site.js`
4. `products-data.min.js` (senkron, defer yok)
5. `VariantDisplay.js` (ürün detay / karşılaştır / teklif)
6. `CompareManager.js` → `QuoteManager.js` (gerektiğinde)
7. `ProductManager.js` → `ProductCard.js` (gerektiğinde)
8. `FormValidator.js` (form sayfaları)
9. `Header.js` → `MegaMenu.js`
10. `product-gallery.js` → `gallery-lightbox.js` (ürün detay)
11. `og-meta.js` (ürün detay)
12. `main.js` → sayfa modülü
