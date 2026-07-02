(function () {
  'use strict';

  /** Her tarayıcıda yüklenebilen yedek görsel */
  const PLACEHOLDER_REL = 'assets/images/home/hero-bg.jpg';

  function normalizeRelPath(src) {
    return String(src || '').replace(/^\//, '');
  }

  function isWebpUrl(url) {
    return /\.webp(\?|#|$)/i.test(String(url || ''));
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

  function normalizeUrl(url) {
    try {
      return new URL(url, window.location.href).href;
    } catch {
      return String(url || '');
    }
  }

  function pushUnique(list, seen, url) {
    if (!url || seen.has(url)) return;
    seen.add(url);
    list.push(url);
  }

  /** WebP için her zaman webp + png + jpg adaylarını döndür (Safari canvas testi güvenilmez). */
  function rasterRelVariants(rel) {
    const path = normalizeRelPath(rel);
    if (!path) return [];
    if (!isWebpUrl(path)) return [path];

    const png = path.replace(/\.webp$/i, '.png');
    const jpg = path.replace(/\.webp$/i, '.jpg');
    const out = [path];
    if (png !== path && !out.includes(png)) out.push(png);
    if (jpg !== path && !out.includes(jpg)) out.push(jpg);
    return out;
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
      rasterRelVariants(img?.src).forEach((rel) => {
        if (rel && !out.includes(rel)) out.push(rel);
      });
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
      rasterRelVariants(product.applicationImage).forEach((rel) => {
        pushUnique(urls, seen, withBase(base, rel));
      });
    }

    pushUnique(urls, seen, withBase(base, PLACEHOLDER_REL));
    return urls;
  }

  function primaryProductImageSrc(product, base) {
    const list = buildProductImageCandidates(product, base);
    return list[0] || withBase(base, PLACEHOLDER_REL);
  }

  function productImageRelForFetch(product) {
    const candidates = buildProductImageCandidates(product, '');
    const raster = candidates.find(
      (u) => !isWebpUrl(u) && !u.includes('placeholder') && !u.includes('hero-bg')
    );
    const webp = candidates.find((u) => isWebpUrl(u));
    const pick = raster || webp || candidates[0] || PLACEHOLDER_REL;
    return pick.replace(/^(\.\.\/)+/, '');
  }

  function buildSingleImageCandidates(relPath, base) {
    const seen = new Set();
    const urls = [];
    rasterRelVariants(relPath).forEach((rel) => {
      pushUnique(urls, seen, withBase(base, rel));
    });
    pushUnique(urls, seen, withBase(base, PLACEHOLDER_REL));
    return urls;
  }

  function advanceImageFallback(img) {
    let list = [];
    try {
      list = JSON.parse(img.dataset.imageCandidates || '[]');
    } catch {
      return false;
    }
    if (!list.length) return false;

    const current = normalizeUrl(img.currentSrc || img.src);
    let idx = parseInt(img.dataset.imageCandidateIndex || '0', 10);

    while (idx < list.length - 1) {
      idx += 1;
      const next = list[idx];
      if (!next) continue;
      if (normalizeUrl(next) === current) continue;
      img.dataset.imageCandidateIndex = String(idx);
      img.src = next;
      return true;
    }
    return false;
  }

  function bindImageFallbackChain(img, candidates) {
    if (!img || !candidates?.length) return;

    const list = candidates.filter(Boolean);
    img.dataset.imageCandidates = JSON.stringify(list);
    img.dataset.imageCandidateIndex = '0';

    if (!img.getAttribute('src')) {
      img.src = list[0];
    }

    if (img.dataset.imageFallbackBound === '1') return;
    img.dataset.imageFallbackBound = '1';

    const verifyLoaded = () => {
      if (img.complete && !img.naturalWidth) advanceImageFallback(img);
    };

    img.addEventListener('error', () => {
      advanceImageFallback(img);
    });

    img.addEventListener('load', verifyLoaded, { once: true });

    if (img.complete) {
      requestAnimationFrame(verifyLoaded);
    }
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

  /** Eski API — e-posta/PDF için WebP tercihi (canvas testi kullanılmaz) */
  function detectWebpSupport() {
    return true;
  }

  window.ABRALION_IMAGE = {
    detectWebpSupport,
    isWebpUrl,
    withBase,
    rasterRelVariants,
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
