/**
 * Open Graph & Twitter Card — paylaşım önizlemesi
 */
(function () {
  function resolveSiteOrigin() {
    if (window.ABRALION_SITE_ORIGIN) return window.ABRALION_SITE_ORIGIN.replace(/\/$/, '');
    if (
      typeof getLocale === 'function'
        ? getLocale() === 'ru'
        : document.documentElement.lang?.toLowerCase().startsWith('ru')
    ) {
      return 'https://abralion.com/ru';
    }
    return 'https://abralion.com';
  }

  function resolveOgLocale() {
    if (typeof getOgLocale === 'function') return getOgLocale();
    if (window.ABRALION_OG_LOCALE) return window.ABRALION_OG_LOCALE;
    return document.documentElement.lang?.toLowerCase().startsWith('ru') ? 'ru_RU' : 'tr_TR';
  }

  const SITE_ORIGIN = resolveSiteOrigin();
  const DEFAULT_IMAGE = 'https://abralion.com/assets/images/og-cover.jpg';

  function toAbsoluteUrl(path, base) {
    if (!path) return DEFAULT_IMAGE;
    if (/^https?:\/\//i.test(path)) return path;
    const b = base != null ? base : typeof getBasePath === 'function' ? getBasePath() : '';
    const normalized = path.replace(/^\.\.\//, '').replace(/^\//, '');
    // Product/share assets live at site root, not under /ru/
    const rootOrigin = 'https://abralion.com';
    const combined = `${b}${normalized}`.replace(/\/+/g, '/').replace(/^\//, '');
    try {
      if (normalized.startsWith('assets/images/')) {
        return new URL(normalized, `${rootOrigin}/`).href;
      }
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
    candidates.push(`assets/images/products/${slug}/${slug}-cover.jpg`);
    candidates.push(`assets/images/products/${slug}/${slug}-kart.jpg`);
    if (product.images?.[0]?.src) candidates.push(product.images[0].src);
    candidates.push(`assets/images/products/${slug}/${slug}.jpg`);
    candidates.push(`assets/images/products/${slug}/${slug}.png`);
    candidates.push(`assets/images/products/${slug}/${slug}.webp`);
    for (const src of candidates) {
      const url = toAbsoluteUrl(src, base);
      if (url && url !== DEFAULT_IMAGE) return url;
    }
    return DEFAULT_IMAGE;
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
    const base =
      opts.base != null ? opts.base : typeof getBasePath === 'function' ? getBasePath() : '';
    const title = opts.title || document.title;
    const description =
      opts.description ||
      document.querySelector('meta[name="description"]')?.getAttribute('content') ||
      '';
    const image = opts.image ? toAbsoluteUrl(opts.image, base) : DEFAULT_IMAGE;
    const url = opts.url || window.location.href;
    const type = opts.type || 'website';
    const imageAlt = opts.imageAlt || title;
    const ogLocale = resolveOgLocale();

    document.title = title;

    setMeta('name', 'description', description);
    setMeta('property', 'og:type', type);
    setMeta('property', 'og:site_name', 'Abralion');
    setMeta('property', 'og:locale', ogLocale);
    setMeta('property', 'og:url', url);
    setMeta('property', 'og:title', title);
    setMeta('property', 'og:description', description);
    setMeta('property', 'og:image', image);
    setMeta('property', 'og:image:alt', imageAlt);

    if (ogLocale === 'ru_RU') {
      setMeta('property', 'og:locale:alternate', 'tr_TR');
    }

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
