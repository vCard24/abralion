/** Site kök yolu — alt klasörlerde body[data-base="../"] */
window.getBasePath = function () {
  return document.body.getAttribute('data-base') || '';
};

window.productUrl = function (slug) {
  const base = getBasePath();
  return `${base}urun/${slug}.html`;
};

/** Ürün sayfası galerisinden menü küçük görseli (slug → katalog yolu) */
const PRODUCT_MENU_THUMB = {
  'metal-inox-taslama-diski':
    'assets/images/products/metal-inox-taslama-diski/metal-inox-taslama-diski-detay.png',
};

/** Mega menü — ürün küçük görseli (katalog → kart dosyası) */
window.productThumbUrl = function (base, product) {
  const slug = product.slug;
  const menuThumb = PRODUCT_MENU_THUMB[slug];
  if (menuThumb) {
    return `${base}${menuThumb}`;
  }
  if (product.images?.[0]?.src) {
    const src = product.images[0].src;
    return src.startsWith('assets') ? `${base}${src}` : src;
  }
  if (slug === 'metal-inox-kesme-tasi') {
    return `${base}assets/images/products/${slug}/${slug}-kart.png`;
  }
  return `${base}assets/images/products/${slug}/${slug}-kart.jpg`;
};
