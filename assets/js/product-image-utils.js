(function () {
  'use strict';

  const PLACEHOLDER_REL = 'assets/images/placeholder/gorsel.jpg';
  let webpSupported = null;

  function detectWebpSupport() {
    if (webpSupported !== null) return webpSupported;
    try {
      const canvas = document.createElement('canvas');
      canvas.width = 1;
      canvas.height = 1;
      webpSupported = canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    } catch {
      webpSupported = false;
    }
    return webpSupported;
  }

  function isWebpUrl(url) {
    return /\.webp(\?|#|$)/i.test(String(url || ''));
  }

  function normalizeRelPath(src) {
    return String(src || '').replace(/^\//, '');
  }

  function resolveBase(base) {
    if (base != null) return base;
    return typeof getBasePath === 'function' ? getBasePath() : '';
  }

  function withBase(base, rel) {
    if (!rel) return '';
    if (/^https?:\/\//i.test(rel) || rel.startsWith('data:')) return rel;
    const root = resolveBase(base);
    return `${root}${normalizeRelPath(rel)}`.replace(/([^:]\/)\/+/g, '$1');
  }

  function pushUnique(list, seen, url) {
    if (!url || seen.has(url)) return;
    seen.add(url);
    list.push(url);
  }

  function kartRelPaths(slug) {
    const s = slug || '';
    const jpg = `assets/images/products/${s}/${s}-kart.jpg`;
    const png = `assets/images/products/${s}/${s}-kart.png`;
    return s === 'metal-inox-kesme-tasi' ? [png, jpg] : [jpg, png];
  }

  function galleryRelPaths(product) {
    const out = [];
    (product?.images || []).forEach((img) => {
      const rel = normalizeRelPath(img?.src);
      if (!rel) return;
      if (isWebpUrl(rel) && !detectWebpSupport()) {
        const png = rel.replace(/\.webp$/i, '.png');
        const jpg = rel.replace(/\.webp$/i, '.jpg');
        if (png !== rel) out.push(png);
        if (jpg !== rel && jpg !== png) out.push(jpg);
        return;
      }
      if (!out.includes(rel)) out.push(rel);
    });
    return out;
  }

  function buildProductImageCandidates(product, base) {
    const slug = product?.slug || product?.id || '';
    const seen = new Set();
    const urls = [];

    kartRelPaths(slug).forEach((rel) => pushUnique(urls, seen, withBase(base, rel)));
    galleryRelPaths(product).forEach((rel) => pushUnique(urls, seen, withBase(base, rel)));

    if (product?.applicationImage) {
      const rel = normalizeRelPath(product.applicationImage);
      if (!isWebpUrl(rel) || detectWebpSupport()) {
        pushUnique(urls, seen, withBase(base, rel));
      }
    }

    pushUnique(urls, seen, withBase(base, PLACEHOLDER_REL));
    return urls;
  }

  function primaryProductImageSrc(product, base) {
    const list = buildProductImageCandidates(product, base);
    return list[0] || withBase(base, PLACEHOLDER_REL);
  }

  /** E-posta / PDF — mevcut dosyayı tercih et (WebP destekleniyorsa galeri WebP) */
  function productImageRelForFetch(product) {
    const candidates = buildProductImageCandidates(product, '');
    const webp = candidates.find(
      (u) => isWebpUrl(u) && !u.includes('placeholder')
    );
    if (webp && detectWebpSupport()) return webp.replace(/^(\.\.\/)+/, '');
    const raster = candidates.find(
      (u) => !isWebpUrl(u) && !u.includes('placeholder')
    );
    return (raster || candidates[0] || PLACEHOLDER_REL).replace(/^(\.\.\/)+/, '');
  }

  function buildSingleImageCandidates(relPath, base) {
    const rel = normalizeRelPath(relPath);
    const seen = new Set();
    const urls = [];
    const abs = withBase(base, rel);

    if (!isWebpUrl(rel) || detectWebpSupport()) {
      pushUnique(urls, seen, abs);
    }
    if (isWebpUrl(rel)) {
      pushUnique(urls, seen, withBase(base, rel.replace(/\.webp$/i, '.png')));
      pushUnique(urls, seen, withBase(base, rel.replace(/\.webp$/i, '.jpg')));
    }
    pushUnique(urls, seen, withBase(base, PLACEHOLDER_REL));
    return urls;
  }

  function bindImageFallbackChain(img, candidates) {
    if (!img || !candidates?.length) return;
    img.dataset.imageCandidates = JSON.stringify(candidates);
    img.dataset.imageCandidateIndex = '0';
    if (!img.getAttribute('src')) img.src = candidates[0];

    if (img.dataset.imageFallbackBound === '1') return;
    img.dataset.imageFallbackBound = '1';

    img.addEventListener('error', () => {
      let list = candidates;
      try {
        const parsed = JSON.parse(img.dataset.imageCandidates || '[]');
        if (parsed.length) list = parsed;
      } catch {
        /* use candidates */
      }

      let idx = parseInt(img.dataset.imageCandidateIndex || '0', 10) + 1;
      while (idx < list.length) {
        if (list[idx] && img.src !== list[idx]) {
          img.dataset.imageCandidateIndex = String(idx);
          img.src = list[idx];
          return;
        }
        idx += 1;
      }
    });
  }

  function bindProductImageFallback(img, product, base) {
    bindImageFallbackChain(img, buildProductImageCandidates(product, base));
  }

  function bindGalleryImageFallback(img, relPath, base) {
    bindImageFallbackChain(img, buildSingleImageCandidates(relPath, base));
  }

  function initProductImageFallbacks(root) {
    const scope = root && root.querySelectorAll ? root : document;
    scope.querySelectorAll('img[data-product-id][data-product-slug]').forEach((img) => {
      const slug = img.dataset.productSlug;
      const product = { slug, id: img.dataset.productId, images: [] };
      try {
        const raw = img.dataset.productImages;
        if (raw) product.images = JSON.parse(raw);
      } catch {
        /* ignore */
      }
      bindProductImageFallback(img, product, img.dataset.imageBase || null);
    });
  }

  window.ABRALION_IMAGE = {
    detectWebpSupport,
    isWebpUrl,
    withBase,
    buildProductImageCandidates,
    primaryProductImageSrc,
    productImageRelForFetch,
    buildSingleImageCandidates,
    bindProductImageFallback,
    bindGalleryImageFallback,
    bindImageFallbackChain,
    initProductImageFallbacks,
    PLACEHOLDER_REL,
  };

  window.buildProductImageCandidates = buildProductImageCandidates;
  window.primaryProductImageSrc = primaryProductImageSrc;
  window.productImageRelForFetch = productImageRelForFetch;
  window.bindProductImageFallback = bindProductImageFallback;
  window.bindGalleryImageFallback = bindGalleryImageFallback;
})();
