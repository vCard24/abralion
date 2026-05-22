/**
 * Open Graph & Twitter Card — paylaşım önizlemesi
 */
(function () {
  const SITE_ORIGIN = 'https://abralion.com';
  const DEFAULT_IMAGE = `${SITE_ORIGIN}/assets/images/abralion-disc.webp`;

  function toAbsoluteUrl(path, base) {
    if (!path) return DEFAULT_IMAGE;
    if (/^https?:\/\//i.test(path)) return path;
    const b = base != null ? base : (typeof getBasePath === 'function' ? getBasePath() : '');
    const normalized = path.replace(/^\//, '');
    const combined = `${b}${normalized}`.replace(/\/+/g, '/');
    try {
      return new URL(combined, `${SITE_ORIGIN}/`).href;
    } catch {
      return DEFAULT_IMAGE;
    }
  }

  function setMeta(attr, key, value) {
    if (value == null || value === '') return;
    let el = document.querySelector(`meta[${attr}="${key}"]`);
    if (!el) {
      el = document.createElement('meta');
      el.setAttribute(attr, key);
      document.head.appendChild(el);
    }
    el.setAttribute('content', String(value));
  }

  function productOgImage(product, base) {
    const slug = product.slug;
    const candidates = [];
    if (product.images?.[0]?.src) candidates.push(product.images[0].src);
    candidates.push(`assets/images/products/${slug}/${slug}-kart.jpg`);
    candidates.push(`assets/images/products/${slug}/${slug}-kart.png`);
    for (const src of candidates) {
      const url = toAbsoluteUrl(src, base);
      if (url && url !== DEFAULT_IMAGE) return url;
    }
    return toAbsoluteUrl(candidates[0], base);
  }

  /**
   * @param {Object} opts
   * @param {string} opts.title — og:title
   * @param {string} [opts.description]
   * @param {string} [opts.image] — site-relative or absolute
   * @param {string} [opts.imageAlt]
   * @param {string} [opts.url] — canonical / og:url
   * @param {string} [opts.type] — website | product
   * @param {string} [opts.base] — getBasePath()
   */
  function setPageSocialMeta(opts) {
    const base = opts.base != null ? opts.base : (typeof getBasePath === 'function' ? getBasePath() : '');
    const title = opts.title || document.title;
    const description =
      opts.description ||
      document.querySelector('meta[name="description"]')?.getAttribute('content') ||
      '';
    const image = opts.image ? toAbsoluteUrl(opts.image, base) : DEFAULT_IMAGE;
    const url = opts.url || window.location.href;
    const type = opts.type || 'website';
    const imageAlt = opts.imageAlt || title;

    document.title = title;

    setMeta('name', 'description', description);
    setMeta('property', 'og:type', type);
    setMeta('property', 'og:site_name', 'Abralion');
    setMeta('property', 'og:locale', 'tr_TR');
    setMeta('property', 'og:url', url);
    setMeta('property', 'og:title', title);
    setMeta('property', 'og:description', description);
    setMeta('property', 'og:image', image);
    setMeta('property', 'og:image:alt', imageAlt);

    setMeta('name', 'twitter:card', 'summary_large_image');
    setMeta('name', 'twitter:title', title);
    setMeta('name', 'twitter:description', description);
    setMeta('name', 'twitter:image', image);
    setMeta('name', 'twitter:image:alt', imageAlt);
  }

  window.OG_SITE_ORIGIN = SITE_ORIGIN;
  window.OG_DEFAULT_IMAGE = DEFAULT_IMAGE;
  window.absolutizeSiteUrl = toAbsoluteUrl;
  window.productOgImage = productOgImage;
  window.setPageSocialMeta = setPageSocialMeta;
})();
