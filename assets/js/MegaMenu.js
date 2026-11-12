function escapeHtml(text) {
  const d = document.createElement('div');
  d.textContent = text;
  return d.innerHTML;
}

const CHISEL_MENU_SUFFIX = {
  'duz-keski-sds-plus': 'SDS Plus',
  'duz-keski-sds-max': 'SDS Max',
  'sivri-uclu-keski-murc-sds-plus': 'SDS Plus',
  'sivri-uclu-keski-murc-sds-max': 'SDS Max',
};

const KIRICI_MENU_ORDER = [
  'sds-plus-2-kesicili-beton-matkap-ucu',
  'sds-plus-4-kesicili-beton-matkap-ucu',
  'hss-matkap-ucu',
  'miknatisli-anahtar-ucu',
  'ph2-manyetik-bits-uc',
  'sds-max-burc-aleti',
  'duz-keski-sds-plus',
  'cam-seramik-matkap-ucu',
  'sivri-uclu-keski-murc-sds-plus',
  'genis-agizli-keski',
  'duz-keski-sds-max',
  'sivri-uclu-keski-murc-sds-max',
];

function menuProductLabel(product) {
  const suffix = CHISEL_MENU_SUFFIX[product.slug];
  const name = suffix ? `${product.name} · ${suffix}` : product.name;
  const limit = suffix ? 56 : 42;
  return name.length > limit ? `${name.slice(0, limit - 1)}…` : name;
}

function orderMenuProducts(categoryId, items) {
  if (categoryId !== 'kirici-delici') return items;
  const rank = new Map(KIRICI_MENU_ORDER.map((slug, index) => [slug, index]));
  return [...items].sort((a, b) => (rank.get(a.slug) ?? 100) - (rank.get(b.slug) ?? 100));
}

function columnCount(itemLen) {
  if (itemLen > 5) return 3;
  if (itemLen > 2) return 2;
  return 1;
}

function buildProductColumns(base, items) {
  const cols = columnCount(items.length);
  const links = items
    .map((p) => {
      const thumb =
        typeof productMenuThumbUrl === 'function'
          ? productMenuThumbUrl(base, p)
          : productThumbUrl(base, p);
      const featureSrc =
        typeof productFeatureImageUrl === 'function'
          ? productFeatureImageUrl(base, p)
          : productThumbUrl(base, p);
      const featureCandidates =
        typeof productFeatureImageCandidates === 'function'
          ? productFeatureImageCandidates(base, p)
          : [featureSrc].filter(Boolean);
      const label = menuProductLabel(p);
      return `<li>
            <a href="${productUrl(p.slug)}" class="mega-menu-product-link"
              data-feature-src="${featureSrc}"
              data-feature-candidates="${encodeURIComponent(JSON.stringify(featureCandidates))}"
              data-feature-name="${escapeHtml(label)}">
              <span class="mega-menu-product-thumb">
                <img src="${thumb}" alt="" width="32" height="32" loading="lazy">
              </span>
              <span class="mega-menu-product-name">${escapeHtml(label)}</span>
            </a>
          </li>`;
    })
    .join('');
  return `<ul class="mega-menu-col" style="display:grid;grid-column:1 / -1;grid-template-columns:repeat(${cols},minmax(0,1fr));gap:4px 20px;align-items:start">${links}</ul>`;
}

function setPanelFeature(panel, src, href, name, candidates) {
  const feature = panel?.querySelector('.mega-menu-feature');
  const img = feature?.querySelector('img');
  if (!feature || !img || !src) return;
  if (href) feature.href = href;
  if (name) {
    img.alt = name;
    feature.setAttribute('aria-label', name);
  }
  feature.classList.remove('is-missing');
  const list = Array.isArray(candidates) && candidates.length ? candidates : [src];
  if (window.ABRALION_IMAGE?.bindImageFallbackChain) {
    img.removeAttribute('data-image-fallback-bound');
    window.ABRALION_IMAGE.bindImageFallbackChain(img, list);
    img.src = list[0];
    return;
  }
  if (img.src !== src) img.src = src;
}

function resetPanelFeature(panel) {
  const feature = panel?.querySelector('.mega-menu-feature');
  if (!feature) return;
  let candidates = [];
  try {
    candidates = JSON.parse(decodeURIComponent(feature.dataset.defaultCandidates || '%5B%5D'));
  } catch {
    candidates = [];
  }
  setPanelFeature(
    panel,
    feature.dataset.defaultSrc,
    feature.dataset.defaultHref,
    feature.dataset.defaultName,
    candidates
  );
  panel.querySelectorAll('.mega-menu-product-link.is-featured').forEach((el) => {
    el.classList.remove('is-featured');
  });
  const first = panel.querySelector('.mega-menu-product-link');
  if (first) first.classList.add('is-featured');
}

function initPanelProductPreview(panel) {
  if (!panel || panel.dataset.previewBound) return;
  panel.dataset.previewBound = '1';

  panel.querySelectorAll('.mega-menu-product-link').forEach((link) => {
    const show = () => {
      panel.querySelectorAll('.mega-menu-product-link.is-featured').forEach((el) => {
        el.classList.remove('is-featured');
      });
      link.classList.add('is-featured');
      let candidates = [];
      try {
        candidates = JSON.parse(decodeURIComponent(link.dataset.featureCandidates || '%5B%5D'));
      } catch {
        candidates = [];
      }
      setPanelFeature(
        panel,
        link.dataset.featureSrc || candidates[0] || link.querySelector('img')?.src,
        link.href,
        link.dataset.featureName || link.querySelector('.mega-menu-product-name')?.textContent,
        candidates
      );
    };
    link.addEventListener('mouseenter', show);
    link.addEventListener('focus', show);
  });
}

function initMegaMenuInteraction(root) {
  const dropdown = root.closest('.header-nav-dropdown');
  if (!dropdown) return;

  const tabs = root.querySelectorAll('.mega-menu-tab');
  const panels = root.querySelectorAll('.mega-menu-panel');
  const desktopHover = window.matchMedia('(min-width: 769px)');

  const activate = (catId) => {
    tabs.forEach((tab) => {
      const on = tab.dataset.category === catId;
      tab.classList.toggle('is-active', on);
      tab.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    panels.forEach((panel) => {
      const on = panel.dataset.category === catId;
      panel.classList.toggle('is-active', on);
      if (on) resetPanelFeature(panel);
    });
  };

  panels.forEach((panel) => initPanelProductPreview(panel));

  tabs.forEach((tab) => {
    tab.addEventListener('mouseenter', () => activate(tab.dataset.category));
    tab.addEventListener('focus', () => activate(tab.dataset.category));
  });

  if (desktopHover.matches) {
    let closeTimer;
    const open = () => {
      clearTimeout(closeTimer);
      dropdown.classList.add('is-open');
    };
    const scheduleClose = () => {
      closeTimer = setTimeout(() => dropdown.classList.remove('is-open'), 220);
    };
    dropdown.addEventListener('mouseenter', open);
    dropdown.addEventListener('mouseleave', scheduleClose);
    dropdown.addEventListener('focusin', open);
    dropdown.addEventListener('focusout', (e) => {
      if (!dropdown.contains(e.relatedTarget)) scheduleClose();
    });
  }
}

async function buildMegaMenu() {
  const container = document.getElementById('mega-menu');
  if (!container) return;
  const base = getBasePath();
  try {
    let data = window.ABRALION_CATALOG;
    if (!data?.products) {
      const res = await fetch(new URL(`${base}data/products.json`, window.location.href).href);
      if (!res.ok) throw new Error('fetch failed');
      data = await res.json();
    }

    const categories = [...data.categories].sort((a, b) => a.order - b.order);

    let tabsHtml = '';
    let panelsHtml = '';

    categories.forEach((cat, index) => {
      const isFirst = index === 0;
      const items = orderMenuProducts(
        cat.id,
        data.products.filter((p) => p.categoryId === cat.id)
      );
      const catHref = `${base}urunler.html?kategori=${encodeURIComponent(cat.id)}`;
      const featured = items[0];
      const featuredThumb = featured
        ? typeof productFeatureImageUrl === 'function'
          ? productFeatureImageUrl(base, featured)
          : productThumbUrl(base, featured)
        : '';
      const featuredCandidates = featured
        ? typeof productFeatureImageCandidates === 'function'
          ? productFeatureImageCandidates(base, featured)
          : [featuredThumb].filter(Boolean)
        : [];
      const featuredHref = featured ? productUrl(featured.slug) : catHref;

      tabsHtml += `<li>
        <a href="${catHref}" class="mega-menu-tab${isFirst ? ' is-active' : ''}"
          data-category="${cat.id}" aria-selected="${isFirst ? 'true' : 'false'}">
          ${escapeHtml(cat.name)}
        </a>
      </li>`;

      panelsHtml += `<div class="mega-menu-panel${isFirst ? ' is-active' : ''}" data-category="${cat.id}" role="tabpanel">
        <div class="mega-menu-panel-inner">
          <div class="mega-menu-columns">${buildProductColumns(base, items)}</div>
          ${
            featured
              ? `<a href="${featuredHref}" class="mega-menu-feature"
                  data-default-src="${featuredThumb}"
                  data-default-candidates="${encodeURIComponent(JSON.stringify(featuredCandidates))}"
                  data-default-href="${featuredHref}"
                  data-default-name="${escapeHtml(featured.name)}"
                  aria-label="${escapeHtml(featured.name)}">
                  <img src="${featuredThumb}" alt="${escapeHtml(featured.name)}" width="400" height="200" loading="lazy">
                </a>`
              : ''
          }
        </div>
      </div>`;
    });

    container.innerHTML = `<li class="mega-menu-root">
      <div class="mega-menu-layout">
        <ul class="mega-menu-tabs" role="tablist" aria-label="Ürün kategorileri">${tabsHtml}</ul>
        <div class="mega-menu-panels">${panelsHtml}</div>
      </div>
    </li>`;

    const bindMegaMenuAfterPaint = () => {
      const root = base != null ? base : typeof getBasePath === 'function' ? getBasePath() : '';

      container.querySelectorAll('.mega-menu-product-thumb img').forEach((img) => {
        const link = img.closest('.mega-menu-product-link');
        const slugMatch = link?.getAttribute('href')?.match(/\/([^/]+)\.html$/);
        const slug = slugMatch?.[1];
        const product = slug ? data.products.find((p) => p.slug === slug) : null;
        if (!product) return;
        const menuRel = `assets/images/products/${product.slug}/${product.slug}-menu-thumb.webp`;
        if (typeof bindGalleryImageFallback === 'function') {
          bindGalleryImageFallback(img, menuRel, base);
          return;
        }
        if (window.ABRALION_IMAGE?.bindImageFallbackChain) {
          const kartRel = `assets/images/products/${product.slug}/${product.slug}-kart.jpg`;
          const candidates = [`${root}${menuRel}`, `${root}${kartRel}`].map((u) =>
            u.replace(/([^:]\/)\/+/g, '$1')
          );
          window.ABRALION_IMAGE.bindImageFallbackChain(img, candidates);
        }
      });

      container.querySelectorAll('.mega-menu-feature img').forEach((img) => {
        const feature = img.closest('.mega-menu-feature');
        const slugMatch = feature?.getAttribute('href')?.match(/\/([^/]+)\.html$/);
        const slug = slugMatch?.[1];
        const product = slug ? data.products.find((p) => p.slug === slug) : null;
        if (!product) return;
        const candidates =
          typeof productFeatureImageCandidates === 'function'
            ? productFeatureImageCandidates(base, product)
            : [
                typeof productFeatureImageUrl === 'function'
                  ? productFeatureImageUrl(base, product)
                  : productThumbUrl(base, product),
              ].filter(Boolean);
        if (window.ABRALION_IMAGE?.bindImageFallbackChain) {
          img.removeAttribute('data-image-fallback-bound');
          window.ABRALION_IMAGE.bindImageFallbackChain(img, candidates);
          if (candidates[0]) img.src = candidates[0];
        } else if (candidates[0]) {
          img.src = candidates[0];
        }
      });

      initMegaMenuInteraction(container);

      container.querySelectorAll('.mega-menu-panel.is-active').forEach((panel) => {
        resetPanelFeature(panel);
      });
    };

    requestAnimationFrame(bindMegaMenuAfterPaint);
  } catch (e) {
    console.error('Mega menü yüklenemedi', e);
  }
}

let megaMenuPromise = null;

function ensureMegaMenu() {
  if (!megaMenuPromise) megaMenuPromise = buildMegaMenu();
  return megaMenuPromise;
}

document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('mega-menu');
  const trigger = container?.closest('.header-nav-dropdown');
  if (!trigger) return;
  const load = () => {
    ensureMegaMenu();
  };
  trigger.addEventListener('pointerenter', load, { once: true });
  trigger.addEventListener('focusin', load, { once: true });
  trigger.addEventListener('pointerdown', load, { once: true });
});
