/** Site kök yolu — alt klasörlerde body[data-base="../"] */
window.getBasePath = function () {
  return document.body.getAttribute('data-base') || '';
};

window.productUrl = function (slug) {
  const base = getBasePath();
  return `${base}urun/${slug}.html`;
};

/** Karşılaştırma → teklif aktarımı (file:// dahil güvenilir) */
window.ABRALION_COMPARE_PREFILL_KEY = 'abralion_compare_prefill';

window.saveComparePrefillForQuote = function (keys) {
  if (!Array.isArray(keys)) return;
  const list = keys.filter((k) => typeof k === 'string' && k.length > 0).slice(0, 4);
  try {
    sessionStorage.setItem(window.ABRALION_COMPARE_PREFILL_KEY, JSON.stringify(list));
  } catch {
    /* ignore */
  }
  if (window.quoteManager?.setList) {
    window.quoteManager.setList(list);
  }
};

window.readComparePrefillForQuote = function () {
  try {
    const raw = sessionStorage.getItem(window.ABRALION_COMPARE_PREFILL_KEY);
    const list = raw ? JSON.parse(raw) : [];
    return Array.isArray(list) ? list.filter((k) => typeof k === 'string' && k.length > 0) : [];
  } catch {
    return [];
  }
};

window.readCompareListFromStorage = function () {
  try {
    const raw = localStorage.getItem('abralion_compare_list');
    const list = raw ? JSON.parse(raw) : [];
    return Array.isArray(list) ? list.filter((k) => typeof k === 'string' && k.length > 0) : [];
  } catch {
    return [];
  }
};

window.resolveCatalogKeys = function (keys, products) {
  if (!Array.isArray(keys) || !Array.isArray(products)) return [];
  return keys.map((key) => {
    let productId = key;
    let variantId = key;
    if (typeof key === 'string' && key.includes('::')) {
      const sep = key.indexOf('::');
      productId = key.slice(0, sep);
      variantId = key.slice(sep + 2);
    }
    const product = products.find((p) => p.id === productId || p.slug === productId);
    if (!product) return { key, product: null, variant: null };
    let variant = product.variants?.find(
      (v) =>
        v.id === variantId ||
        v.urun_kodu === variantId ||
        String(v.id) === String(variantId)
    );
    if (!variant && product.variants?.length) {
      variant = product.variants[0];
    }
    return {
      key,
      product,
      variant: variant || { id: variantId, urun_kodu: variantId },
    };
  });
};

window.collectCompareKeysForQuote = function () {
  if (window.compareManager?.getCompareList) {
    const live = window.compareManager.getCompareList();
    if (live.length) return live;
  }
  return readCompareListFromStorage();
};

/** URL'de model taşıma — file:// için en güvenilir yol */
window.encodeCompareKeysForUrl = function (keys) {
  if (!Array.isArray(keys) || !keys.length) return '';
  return keys
    .slice(0, 4)
    .map((key) => {
      let productId = key;
      let variantId = key;
      if (key.includes('::')) {
        const parts = key.split('::');
        productId = parts[0];
        variantId = parts.slice(1).join('::');
      }
      return `${encodeURIComponent(productId)}~${encodeURIComponent(variantId)}`;
    })
    .join(',');
};

window.parseModelsFromUrl = function (search) {
  const raw = new URLSearchParams(search || window.location.search).get('models');
  if (!raw) return [];
  return raw
    .split(',')
    .map((part) => {
      const sep = part.indexOf('~');
      if (sep === -1) {
        const id = decodeURIComponent(part);
        return `${id}::${id}`;
      }
      const productId = decodeURIComponent(part.slice(0, sep));
      const variantId = decodeURIComponent(part.slice(sep + 1));
      return `${productId}::${variantId || productId}`;
    })
    .filter(Boolean);
};

window.buildQuotePageUrl = function (keys, base) {
  const root = base != null ? base : getBasePath();
  const list = Array.isArray(keys) ? keys.filter(Boolean).slice(0, 4) : [];
  if (!list.length) return `${root}fiyat-teklifi.html?kaynak=karsilastir&from=compare`;
  const models = encodeCompareKeysForUrl(list);
  return `${root}fiyat-teklifi.html?kaynak=karsilastir&from=compare&models=${models}`;
};

window.isQuoteFromCompare = function (search) {
  const params = new URLSearchParams(search || window.location.search);
  return params.get('from') === 'compare' || params.get('kaynak') === 'karsilastir';
};

window.getCompareKeysForPrefill = function () {
  const fromCompare = isQuoteFromCompare();
  const fromUrl = parseModelsFromUrl();
  if (fromUrl.length) return fromUrl;

  if (fromCompare) {
    const fromStorage = readCompareListFromStorage();
    if (fromStorage.length) return fromStorage;

    const fromSession = readComparePrefillForQuote();
    if (fromSession.length) return fromSession;
  }

  const fromSession = readComparePrefillForQuote();
  if (fromSession.length) return fromSession;

  const fromCompareList = collectCompareKeysForQuote();
  if (fromCompareList.length) return fromCompareList;

  if (window.quoteManager?.getQuoteList) {
    const fromQuote = window.quoteManager.getQuoteList();
    if (fromQuote.length) return fromQuote;
  }

  return [];
};

window.navigateToQuotePage = function (keys, base) {
  const list = Array.isArray(keys) ? keys : collectCompareKeysForQuote();
  saveComparePrefillForQuote(list);
  window.location.href = buildQuotePageUrl(list, base != null ? base : getBasePath());
};

/** PDF indirme dosya adi — ic metadata yerine okunabilir ad */
window.sanitizeDownloadLabel = function (label) {
  return (label || 'Dokuman')
    .replace(/[\\/:*?"<>|]/g, '-')
    .replace(/\s+/g, ' ')
    .trim();
};

window.documentDownloadFilename = function (label, suffix = 'teknik döküman') {
  return `${sanitizeDownloadLabel(label)} ${suffix}.pdf`;
};

/** Tum PDF linklerini yeni sekmede ac */
window.initPdfLinks = function (root = document) {
  root.querySelectorAll('a[href*=".pdf"]').forEach((link) => {
    link.removeAttribute('download');
    link.setAttribute('target', '_blank');
    link.setAttribute('rel', 'noopener noreferrer');
  });
};

/** @deprecated initPdfLinks kullanin */
window.initPdfDownloadLinks = window.initPdfLinks;

/** Mega menü — ürün küçük görseli (katalog → kart dosyası) */
window.productThumbUrl = function (base, product) {
  const slug = product.slug;
  if (product.images?.[0]?.src) {
    const src = product.images[0].src;
    return src.startsWith('assets') ? `${base}${src}` : src;
  }
  if (slug === 'metal-inox-kesme-tasi') {
    return `${base}assets/images/products/${slug}/${slug}-kart.png`;
  }
  return `${base}assets/images/products/${slug}/${slug}-kart.jpg`;
};

/** Footer sosyal — +7 985 789-60-62 */
const FOOTER_SOCIAL_PHONE = '79857896062';

const FOOTER_SOCIAL_SVGS = {
  telegram:
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12.12 12.12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>',
  whatsapp:
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.435 9.884-9.881 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z"/></svg>',
  instagram:
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>',
};

function initFooterCerts() {
  const brandCol = document.querySelector('.footer .space-y-6');
  const desc =
    document.querySelector('.footer .footer-description') ||
    (brandCol && brandCol.querySelector('p'));
  if (!desc || desc.parentElement.querySelector('.footer-cert')) {
    return;
  }

  const base = getBasePath();
  const wrap = document.createElement('div');
  wrap.className = 'footer-cert';
  wrap.setAttribute('role', 'group');
  wrap.setAttribute('aria-label', 'Sertifikasyon işaretleri');

  [
    { src: 'mpa-logo.png', alt: 'MPA Hannover' },
    { src: 'eac-logo.png', alt: 'EAC uygunluk işareti' },
  ].forEach(({ src, alt }) => {
    const img = document.createElement('img');
    img.src = `${base}assets/images/${src}`;
    img.alt = alt;
    img.loading = 'lazy';
    img.decoding = 'async';
    wrap.appendChild(img);
  });

  desc.insertAdjacentElement('afterend', wrap);
}

function findFooterContactSection() {
  const sections = document.querySelectorAll('.footer .footer-section');
  for (const section of sections) {
    const h3 = section.querySelector('h3');
    if (h3 && h3.textContent.trim() === 'İletişim') {
      return section;
    }
  }
  return null;
}

function initFooterSocial() {
  const contact = findFooterContactSection();
  if (!contact || contact.querySelector('.footer-social')) {
    return;
  }

  const links = contact.querySelector('.footer-links');
  if (!links) {
    return;
  }

  const base = getBasePath();
  const items = [
    {
      id: 'telegram',
      label: 'Telegram — 8 (985) 789-60-62',
      href: `https://t.me/+${FOOTER_SOCIAL_PHONE}`,
      external: true,
    },
    {
      id: 'whatsapp',
      label: 'WhatsApp — 8 (985) 789-60-62',
      href: `https://wa.me/${FOOTER_SOCIAL_PHONE}`,
      external: true,
    },
    {
      id: 'instagram',
      label: 'Instagram',
      href: `${base}index.html`,
      external: false,
    },
  ];

  const ul = document.createElement('ul');
  ul.className = 'footer-social';

  items.forEach(({ id, label, href, external }) => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = href;
    a.setAttribute('aria-label', label);
    a.innerHTML = FOOTER_SOCIAL_SVGS[id];
    if (external) {
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
    }
    li.appendChild(a);
    ul.appendChild(li);
  });

  links.insertAdjacentElement('afterend', ul);
}

function ensureWhatsAppFloatStyles() {
  if (document.getElementById('whatsapp-float-styles')) {
    return;
  }

  const style = document.createElement('style');
  style.id = 'whatsapp-float-styles';
  style.textContent = `
    #whatsapp-float {
      position: fixed !important;
      right: max(1rem, env(safe-area-inset-right, 0px));
      bottom: max(1.25rem, env(safe-area-inset-bottom, 0px));
      z-index: 10050;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 3.5rem;
      height: 3.5rem;
      margin: 0;
      padding: 0;
      border: 0;
      border-radius: 50%;
      background: #25d366;
      color: #fff;
      box-shadow: 0 4px 18px rgba(0, 0, 0, 0.35);
      text-decoration: none;
      box-sizing: border-box;
      pointer-events: auto;
    }
    #whatsapp-float svg {
      width: 1.65rem;
      height: 1.65rem;
      max-width: 1.65rem;
      max-height: 1.65rem;
      display: block;
      flex-shrink: 0;
    }
    body.has-compare-bar #whatsapp-float {
      bottom: max(5.25rem, calc(env(safe-area-inset-bottom, 0px) + 4.5rem));
    }
    @media (max-width: 640px) {
      #whatsapp-float {
        width: 3.25rem;
        height: 3.25rem;
        right: max(0.75rem, env(safe-area-inset-right, 0px));
        bottom: max(1rem, env(safe-area-inset-bottom, 0px));
      }
      body.has-compare-bar #whatsapp-float {
        bottom: max(5rem, calc(env(safe-area-inset-bottom, 0px) + 4.25rem));
      }
    }
  `;
  document.head.appendChild(style);
}

function initWhatsAppFloat() {
  if (document.getElementById('whatsapp-float')) {
    return;
  }

  ensureWhatsAppFloatStyles();

  const link = document.createElement('a');
  link.id = 'whatsapp-float';
  link.className = 'whatsapp-float';
  link.href = `https://wa.me/${FOOTER_SOCIAL_PHONE}`;
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  link.setAttribute('aria-label', 'WhatsApp — +7 985 789-60-62');
  link.innerHTML = FOOTER_SOCIAL_SVGS.whatsapp;
  document.body.appendChild(link);
}

function initFooter() {
  initFooterCerts();
  initFooterSocial();
  initPdfLinks();
  initWhatsAppFloat();
}

function bootSiteFooter() {
  try {
    initFooter();
  } catch (err) {
    console.error('Footer init:', err);
    initWhatsAppFloat();
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootSiteFooter);
} else {
  bootSiteFooter();
}

initWhatsAppFloat();
