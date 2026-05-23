function escapeHtml(text) {
  const d = document.createElement('div');
  d.textContent = text;
  return d.innerHTML;
}

function columnCount(itemLen) {
  if (itemLen > 8) return 4;
  if (itemLen > 5) return 3;
  if (itemLen > 2) return 2;
  return 1;
}

function buildProductColumns(base, items) {
  const cols = columnCount(items.length);
  const buckets = Array.from({ length: cols }, () => []);
  items.forEach((p, i) => buckets[i % cols].push(p));

  return buckets
    .map((bucket) => {
      const links = bucket
        .map((p) => {
          const thumb = productThumbUrl(base, p);
          const short = p.name.length > 42 ? `${p.name.slice(0, 40)}…` : p.name;
          return `<li>
            <a href="${productUrl(p.slug)}" class="mega-menu-product-link"
              data-feature-src="${thumb}"
              data-feature-name="${escapeHtml(p.name)}">
              <span class="mega-menu-product-thumb">
                <img src="${thumb}" alt="" width="32" height="32" loading="lazy">
              </span>
              <span class="mega-menu-product-name">${escapeHtml(short)}</span>
            </a>
          </li>`;
        })
        .join('');
      return `<ul class="mega-menu-col">${links}</ul>`;
    })
    .join('');
}

function setPanelFeature(panel, src, href, name) {
  const feature = panel?.querySelector('.mega-menu-feature');
  const img = feature?.querySelector('img');
  if (!feature || !img || !src) return;
  if (href) feature.href = href;
  if (name) {
    img.alt = name;
    feature.setAttribute('aria-label', name);
  }
  if (img.src !== src) {
    img.src = src;
    feature.classList.remove('is-missing');
  }
}

function resetPanelFeature(panel) {
  const feature = panel?.querySelector('.mega-menu-feature');
  if (!feature) return;
  setPanelFeature(
    panel,
    feature.dataset.defaultSrc,
    feature.dataset.defaultHref,
    feature.dataset.defaultName
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
      setPanelFeature(
        panel,
        link.dataset.featureSrc || link.querySelector('img')?.src,
        link.href,
        link.dataset.featureName || link.querySelector('.mega-menu-product-name')?.textContent
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

  if (window.innerWidth > 768) {
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
    const firstId = categories[0]?.id || '';

    let tabsHtml = '';
    let panelsHtml = '';

    categories.forEach((cat, index) => {
      const isFirst = index === 0;
      const items = data.products.filter((p) => p.categoryId === cat.id);
      const catHref = `${base}urunler.html?kategori=${encodeURIComponent(cat.id)}`;
      const featured = items[0];
      const featuredThumb = featured ? productThumbUrl(base, featured) : '';
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
                  data-default-href="${featuredHref}"
                  data-default-name="${escapeHtml(featured.name)}"
                  aria-label="${escapeHtml(featured.name)}">
                  <img src="${featuredThumb}" alt="${escapeHtml(featured.name)}" loading="lazy">
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

    container.querySelectorAll('.mega-menu-product-thumb img, .mega-menu-feature img').forEach((img) => {
      img.addEventListener('error', () => {
        const wrap = img.closest('.mega-menu-product-thumb') || img.closest('.mega-menu-feature');
        wrap?.classList.add('is-missing');
      });
    });

    initMegaMenuInteraction(container);

    container.querySelectorAll('.mega-menu-panel.is-active').forEach((panel) => {
      resetPanelFeature(panel);
    });
  } catch (e) {
    console.error('Mega menü yüklenemedi', e);
  }
}

document.addEventListener('DOMContentLoaded', buildMegaMenu);
