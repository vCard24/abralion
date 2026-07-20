const NOIR_BADGE_COLUMNS = new Set([
  'malzeme',
  'asindirici_kodu',
  'asindirici_tipi',
  'urun_tipi',
  'baglanti_tipi',
  'bicak_malzemesi',
  'kasa_malzemesi',
  'kullanim_yeri',
  'govde_kizak_tipi',
]);

function iconSvg(name, extraClass = '') {
  return window.AbralionIcons && typeof window.AbralionIcons.iconSvg === 'function'
    ? window.AbralionIcons.iconSvg(name, extraClass)
    : '';
}

function formatTableCellHtml(cell, col) {
  const raw = cell == null ? '' : String(cell);
  if (!raw) return '';
  const colId = col.key || col.compute;
  if (colId && NOIR_BADGE_COLUMNS.has(colId)) {
    return `<span class="noir-spec-badge">${escapeHtml(raw)}</span>`;
  }
  return escapeHtml(raw);
}

function kartImageSrc(base, slug) {
  return `${base}assets/images/products/${slug}/${slug}-kart.jpg`;
}

/** Uygulama görseli kutusu — yeni şablon veya eski img yapısı */
function resolveApplicationVisualRoot() {
  const tab = document.querySelector('#tab-description');
  if (!tab) return null;

  const existing = tab.querySelector('.product-application-visual');
  if (existing) return existing;

  const legacyImg = document.getElementById('product-application-image');
  const wrap = legacyImg?.closest('.relative') || tab.querySelector('.relative.overflow-hidden');
  if (!wrap) return null;

  wrap.classList.add(
    'product-application-visual',
    'isolate',
    'bg-surface-container',
    'bg-contain',
    'bg-center',
    'bg-no-repeat'
  );
  legacyImg?.remove();
  return wrap;
}

/** Her ürün sayfasında kart görseli; applicationImage veya kart yoksa galerinin ilk görseli */
function setProductApplicationVisual(base, slug, productName, product) {
  const visual = resolveApplicationVisualRoot();
  if (!visual || !slug) return;

  const apply = (url) => {
    visual.style.backgroundImage = `url("${url}")`;
    visual.setAttribute('role', 'img');
    visual.setAttribute(
      'aria-label',
      productName ? t('product.applicationImageAria', { productName }) : t('product.applicationImage')
    );
  };

  const tryCandidates = (candidates) => {
    let idx = 0;
    const tryNext = () => {
      if (idx >= candidates.length) return;
      const probe = new Image();
      probe.onload = () => apply(candidates[idx]);
      probe.onerror = () => {
        idx += 1;
        tryNext();
      };
      probe.src = candidates[idx];
    };
    tryNext();
  };

  const custom = product?.applicationImage;
  if (custom) {
    const candidates =
      typeof buildSingleImageCandidates === 'function'
        ? buildSingleImageCandidates(custom, base)
        : [custom.startsWith('assets') ? `${base}${custom}` : custom];
    tryCandidates(candidates);
    return;
  }

  const candidates =
    typeof buildProductImageCandidates === 'function'
      ? buildProductImageCandidates(product || { slug }, base)
      : [kartImageSrc(base, slug)];
  tryCandidates(candidates);
}

function productThumbForCard(base, product) {
  if (typeof primaryProductImageSrc === 'function') {
    return primaryProductImageSrc(product, base);
  }
  const slug = product.slug;
  return kartImageSrc(base, slug);
}

function renderRelatedProducts(product, pm) {
  const grid = document.getElementById('related-products-grid');
  if (!grid || !pm) return;

  const base = getBasePath();
  const related = pm
    .getAllProducts()
    .filter((p) => p.categoryId === product.categoryId && p.slug !== product.slug)
    .slice(0, 3);

  if (!related.length) {
    grid.innerHTML =
      `<p class="col-span-full font-technical-data text-steel-gray">${t('product.relatedEmpty')}</p>`;
    return;
  }

  grid.innerHTML = related
    .map((p) => {
      const url = `${base}urun/${p.slug}.html`;
      const thumb = productThumbForCard(base, p);
      const code = (p.variants?.[0]?.urun_kodu || p.slug).toUpperCase();
      const descRaw = (p.description || '').slice(0, 90);
      const desc = escapeHtml(descRaw);
      const name = escapeHtml(p.name);
      return `<a href="${url}" class="noir-related-card group block overflow-hidden rounded-lg" data-related-product-id="${escapeHtml(p.id)}">
      <div class="noir-related-card__media relative flex items-center justify-center p-8 overflow-hidden">
        <img class="noir-related-card__img h-full max-h-full object-contain transition-transform duration-500 group-hover:scale-110 opacity-80" src="${thumb}" alt="" loading="lazy" width="400" height="300" data-related-slug="${escapeHtml(p.slug)}">
        <span class="noir-related-card__code absolute top-4 left-4 font-technical-data text-[10px] text-white px-2 py-1">${escapeHtml(code)}</span>
      </div>
      <div class="p-6">
        <h3 class="font-label-caps text-label-caps text-white mb-2 uppercase leading-snug">${name}</h3>
        <p class="text-[12px] text-steel-gray mb-4 line-clamp-2">${desc}${descRaw.length >= 90 ? '…' : ''}</p>
        <span class="text-abrasive-red font-label-caps text-[11px] inline-flex items-center gap-2 uppercase">
          ${t('product.viewDetails')}
          ${iconSvg('chevron_right', 'text-[14px]')}
        </span>
      </div>
    </a>`;
    })
    .join('');

  if (typeof bindProductImageFallback === 'function') {
    grid.querySelectorAll('[data-related-product-id]').forEach((link) => {
      const p = related.find((item) => item.id === link.dataset.relatedProductId);
      const img = link.querySelector('img');
      if (p && img) bindProductImageFallback(img, p, base);
    });
  }
}

function escapeHtml(text) {
  const d = document.createElement('div');
  d.textContent = text;
  return d.innerHTML;
}

function fillList(ul, items, options = {}) {
  if (!ul) return;
  const styled = Boolean(options.styled);
  ul.innerHTML = (items || [])
    .map((item) => {
      const text = escapeHtml(item.replace(/^✓\s*/, ''));
      if (styled) {
        return `<li class="flex items-start gap-3">
          ${iconSvg('check_circle', 'text-abrasive-red text-lg shrink-0')}
          <span class="text-body-md text-on-surface">${text}</span>
        </li>`;
      }
      return `<li class="text-on-surface-variant">${text}</li>`;
    })
    .join('');
}

function renderGallery(product, container) {
  const base = getBasePath();
  const images =
    product.images && product.images.length
      ? product.images
      : [{ src: 'assets/images/home/hero-bg.jpg', alt: product.name }];

  const slides = images
    .map((img, i) => {
      const src =
        typeof buildSingleImageCandidates === 'function'
          ? buildSingleImageCandidates(img.src, base)[0]
          : img.src.startsWith('assets')
            ? `${base}${img.src}`
            : img.src;
      return `<img src="${src}" alt="${escapeHtml(img.alt || product.name)}" class="slider-image max-w-full max-h-full w-auto h-auto object-contain p-2 transition-transform duration-700 group-hover:scale-110${i === 0 ? ' active' : ''}" data-gallery-src="${escapeHtml(img.src)}">`;
    })
    .join('');

  const thumbs = images
    .map((img, i) => {
      const src =
        typeof buildSingleImageCandidates === 'function'
          ? buildSingleImageCandidates(img.src, base)[0]
          : img.src.startsWith('assets')
            ? `${base}${img.src}`
            : img.src;
      const active = i === 0;
      return `<button type="button" class="gallery-thumb-btn aspect-square bg-surface-elevation border p-2 cursor-pointer transition-colors${active ? ' border-abrasive-red' : ' border-steel-gray/10 hover:border-abrasive-red/50'}" aria-label="${t('gallery.imageN', { n: i + 1 })}" aria-selected="${active ? 'true' : 'false'}" data-index="${i}">
          <img src="${src}" alt="" class="gallery-thumb w-full h-full object-contain" data-gallery-src="${escapeHtml(img.src)}">
        </button>`;
    })
    .join('');

  container.innerHTML = `
    <div class="product-gallery-gradient w-full h-[min(420px,90vw)] max-h-[420px] flex items-center justify-center border border-steel-gray/10 relative shimmer-effect group overflow-hidden product-image-slider gallery-main bg-gradient-to-b from-surface-container to-carbon-black">
      <button type="button" class="slider-btn prev absolute left-4 top-1/2 z-20 -translate-y-1/2 flex h-12 w-12 items-center justify-center border border-white/10 bg-carbon-black/60 text-white transition-colors hover:bg-abrasive-red sr-only" aria-label="${t('gallery.previous')}">‹</button>
      <div class="slider-container relative flex h-full w-full max-h-[420px] items-center justify-center z-10 p-8 md:p-10 ![aspect-ratio:auto]">${slides}</div>
      <button type="button" class="slider-btn next absolute right-4 top-1/2 z-20 -translate-y-1/2 flex h-12 w-12 items-center justify-center border border-white/10 bg-carbon-black/60 text-white transition-colors hover:bg-abrasive-red sr-only" aria-label="${t('gallery.next')}">›</button>
      <div class="absolute bottom-6 left-6 flex gap-3 z-20">
        <button type="button" class="gallery-lightbox-trigger w-12 h-12 bg-carbon-black/60 border border-white/10 flex items-center justify-center hover:bg-abrasive-red transition-colors" aria-label="${t('gallery.zoom')}">
          ${iconSvg('zoom_in', 'text-white')}
        </button>
      </div>
    </div>
    <div class="gallery-thumbs grid grid-cols-4 gap-4" role="tablist" aria-label="${t('gallery.thumbnails')}">${thumbs}</div>`;

  const mainSlider = container.querySelector('.gallery-main');
  const syncTransformOrigin = () => {
    const activeImg = container.querySelector('.slider-image.active');
    if (!activeImg || !mainSlider) return;
    mainSlider.onmousemove = (e) => {
      const rect = mainSlider.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      activeImg.style.transformOrigin = `${x}% ${y}%`;
    };
  };
  syncTransformOrigin();

  const galleryController = initProductGallery();
  if (galleryController && typeof galleryController.show === 'function') {
    const originalShow = galleryController.show.bind(galleryController);
    galleryController.show = (index) => {
      originalShow(index);
      syncTransformOrigin();
    };
  }
  if (typeof initGalleryLightbox === 'function') {
    initGalleryLightbox(galleryController);
  }

  if (typeof bindGalleryImageFallback === 'function') {
    container.querySelectorAll('[data-gallery-src]').forEach((img) => {
      bindGalleryImageFallback(img, img.dataset.gallerySrc, base);
    });
  }
}

function techSummaryItem(label, value, options = {}) {
  if (value == null || value === '') return '';
  const valueClass = options.red
    ? 'font-technical-data text-abrasive-red'
    : 'font-technical-data text-on-surface';
  return `<div>
    <p class="text-steel-gray text-[12px] uppercase">${escapeHtml(label)}</p>
    <p class="${valueClass}">${escapeHtml(String(value))}</p>
  </div>`;
}

function renderTechSummary(product) {
  const wrap = document.getElementById('product-tech-summary');
  if (!wrap) return;
  const variant = (product.variants || [])[0];
  if (!variant) {
    wrap.innerHTML =
      `<p class="col-span-2 text-steel-gray text-[12px]">${t('product.techSummaryHint')}</p>`;
    return;
  }
  const rpm =
    variant.max_hiz_rpm != null
      ? `${typeof formatNumber === 'function' ? formatNumber(variant.max_hiz_rpm) : Number(variant.max_hiz_rpm).toLocaleString(typeof getIntlLocale === 'function' ? getIntlLocale() : 'ru-RU')} об/мин`
      : variant.max_hiz_ms != null
        ? `${variant.max_hiz_ms} м/с`
        : '';
  wrap.innerHTML = [
    techSummaryItem(
      t('product.techSummary.material'),
      variant.asindirici_kodu || variant.asindirici_tipi || product.categoryName
    ),
    techSummaryItem(t('product.techSummary.diameter'), variant.daire_capi_mm != null ? `${variant.daire_capi_mm} mm` : ''),
    techSummaryItem(t('product.techSummary.thickness'), variant.kalinlik_mm != null ? `${variant.kalinlik_mm} mm` : ''),
    techSummaryItem(
      t('product.techSummary.bore'),
      variant.gobek_capi_mm != null ? `${variant.gobek_capi_mm} mm` : ''
    ),
    techSummaryItem(t('product.techSummary.maxRpm'), rpm, { red: Boolean(rpm) }),
    techSummaryItem(
      t('product.techSummary.certificate'),
      t('product.techSummary.certificateValue')
    ),
  ]
    .filter(Boolean)
    .join('');
}

function renderDescriptionContent(product) {
  const desc = (product.description || '').trim();
  const descEl = document.getElementById('product-description');
  const extraEl = document.getElementById('product-description-extra');
  const quoteEl = document.getElementById('product-description-quote');

  if (descEl) {
    const parts = desc.split(/(?<=[.!?])\s+/);
    descEl.textContent = parts[0] || desc;
    if (extraEl) {
      extraEl.innerHTML =
        parts.length > 1
          ? parts
              .slice(1)
              .map((part) => `<p>${escapeHtml(part.trim())}</p>`)
              .join('')
          : '';
    }
  }

  const quoteSource = product.applications?.[0] || product.features?.[0];
  if (quoteEl && quoteSource) {
    quoteEl.textContent = `"${quoteSource.replace(/^✓\s*/, '').trim()}"`;
    quoteEl.classList.remove('hidden');
  } else if (quoteEl) {
    quoteEl.classList.add('hidden');
  }
}

function renderBreadcrumb(product) {
  const base = getBasePath();
  const ol = document.getElementById('product-breadcrumb');
  if (!ol) return;
  ol.innerHTML = `
    <li><a class="hover:text-on-surface transition-colors" href="${base}index.html">${t('product.breadcrumb.home')}</a></li>
    <li class="flex items-center gap-2" aria-hidden="true">${iconSvg('chevron_right', 'text-[14px]')}</li>
    <li><a class="hover:text-on-surface transition-colors" href="${base}produkty.html">${t('product.breadcrumb.products')}</a></li>
    <li class="flex items-center gap-2" aria-hidden="true">${iconSvg('chevron_right', 'text-[14px]')}</li>
    <li><a class="hover:text-on-surface transition-colors" href="${base}produkty.html?kategori=${encodeURIComponent(product.categoryId)}">${escapeHtml(product.categoryName)}</a></li>
    <li class="flex items-center gap-2" aria-hidden="true">${iconSvg('chevron_right', 'text-[14px]')}</li>
    <li class="text-abrasive-red" aria-current="page">${escapeHtml(product.name)}</li>`;
}

function renderVariantTable(product, tableWrap) {
  const columns = getTableColumns(product);
  if (!columns.length) {
    tableWrap.innerHTML =
      `<p class="no-products-message p-4">${t('product.noTableConfig')}</p>`;
    return;
  }

  let thead = '<thead><tr class="bg-surface-container-high border-b border-steel-gray/20">';
  thead +=
    `<th class="compare-col spec-col--compare p-4 font-label-caps text-[12px] text-steel-gray" scope="col"><span class="sr-only">${t('compare.column')}</span></th>`;
  thead += columns
    .map((c) => {
      const colClass = getSpecColumnClass(c);
      return `<th class="spec-col ${colClass} p-4 font-label-caps text-[12px] text-steel-gray uppercase" scope="col">${escapeHtml(c.label)}</th>`;
    })
    .join('');
  thead += '</tr></thead>';

  let tbody = '<tbody class="font-technical-data text-[14px]">';
  (product.variants || []).forEach((variant, index) => {
    const vid = variant.urun_kodu || variant.id || `v${index + 1}`;
    const cells = variantRowCells(variant, columns);
    const label = variantLabel(variant, product.name).replace(/"/g, '&quot;');
    const stripe = index % 2 === 1 ? ' bg-surface-container-low/30' : '';
    tbody += `<tr class="border-b border-steel-gray/10 hover:bg-surface-elevation/50 transition-colors${stripe}" data-variant-id="${vid}">`;
    tbody += `<td class="compare-cell spec-col--compare p-4">
      <label class="compare-check" title="${t('compare.addTitle')}">
        <input type="checkbox" class="compare-row-input"
          data-product-id="${product.id}"
          data-variant-id="${vid}"
          aria-label="${t('compare.compareAria', { label })}">
        <span class="compare-check-box" aria-hidden="true"></span>
      </label>
    </td>`;
    cells.forEach((cell, cellIndex) => {
      const colClass = getSpecColumnClass(columns[cellIndex]);
      tbody += `<td class="spec-col ${colClass} p-4 text-on-surface">${formatTableCellHtml(cell, columns[cellIndex])}</td>`;
    });
    tbody += '</tr>';
  });
  tbody += '</tbody>';

  if (!(product.variants || []).length) {
    tableWrap.innerHTML =
      `<p class="no-products-message p-4">${t('product.noVariants')}</p>`;
    return;
  }

  tableWrap.innerHTML = `<table class="w-full text-left border-collapse specs-table specs-table--stitch">${thead}${tbody}</table>`;

  tableWrap.querySelectorAll('.compare-row-input').forEach((input) => {
    input.addEventListener('change', () => {
      const result = window.compareManager.toggle(input.dataset.productId, input.dataset.variantId);
      if (!result.success && input.checked) {
        input.checked = false;
        if (result.message) {
          const toast = document.createElement('div');
          toast.className = 'compare-toast';
          toast.textContent = result.message;
          document.body.appendChild(toast);
          requestAnimationFrame(() => toast.classList.add('show'));
          setTimeout(() => toast.remove(), 2500);
        }
      }
    });
  });

  window.compareManager?.syncCheckboxes();
}

function renderProductPage(product, pm) {
  const base = getBasePath();
  const slug = product.slug;
  const description = (product.description || '').slice(0, 160);
  const pageUrl = `${window.ABRALION_SITE_ORIGIN || window.OG_SITE_ORIGIN || 'https://abralion.com/ru'}/urun/${slug}.html`;
  const shareImage =
    typeof buildProductImageCandidates === 'function'
      ? (() => {
          const relCandidates = buildProductImageCandidates(product, '');
          const pick =
            relCandidates.find((u) => !/\.webp(\?|#|$)/i.test(u) && !u.includes('placeholder')) ||
            relCandidates[0];
          if (!pick) return `assets/images/products/${slug}/${slug}-kart.jpg`;
          const match = pick.match(/assets\/images\/[^\s"']+/);
          return match
            ? match[0]
            : product.images?.[0]?.src || `assets/images/products/${slug}/${slug}-kart.jpg`;
        })()
      : product.images?.[0]?.src || `assets/images/products/${slug}/${slug}-kart.jpg`;
  const shareImageAlt = product.images?.[0]?.alt || product.name;

  if (typeof setPageSocialMeta === 'function') {
    setPageSocialMeta({
      title: `${product.name} - Abralion`,
      description,
      image: shareImage,
      imageAlt: shareImageAlt,
      url: pageUrl,
      type: 'product',
      base,
    });
  } else {
    document.title = `${product.name} - Abralion`;
    const metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc && description) metaDesc.setAttribute('content', description);
  }

  renderBreadcrumb(product);

  const catEl = document.getElementById('product-category');
  const titleEl = document.getElementById('product-title');
  if (catEl) {
    const series = product.categoryName || '';
    catEl.textContent = series ? t('product.seriesPrefix', { series }) : '';
    catEl.classList.add('uppercase');
  }
  if (titleEl) titleEl.textContent = product.name || '';

  renderDescriptionContent(product);
  renderTechSummary(product);

  fillList(document.querySelector('#product-features-short ul'), product.features, {
    styled: true,
  });
  fillList(document.querySelector('#product-applications ul'), product.applications, {
    styled: true,
  });

  setProductApplicationVisual(base, slug, product.name, product);

  const catalogLink = document.getElementById('product-technical-catalog-link');
  if (catalogLink) {
    const catalog = product.technicalCatalog;
    if (catalog) {
      catalogLink.href = catalog.startsWith('assets') ? `${base}${catalog}` : catalog;
      catalogLink.removeAttribute('download');
      catalogLink.setAttribute('target', '_blank');
      catalogLink.setAttribute('rel', 'noopener noreferrer');
    } else {
      catalogLink.href = `${base}dokumenty.html`;
      catalogLink.removeAttribute('download');
      catalogLink.removeAttribute('target');
      catalogLink.removeAttribute('rel');
    }
  }

  const gallery = document.getElementById('product-gallery');
  if (gallery) renderGallery(product, gallery);

  const tableWrap = document.getElementById('variant-specs-table');
  if (tableWrap) renderVariantTable(product, tableWrap);

  initProductDetailCompareButton(product);
  renderRelatedProducts(product, pm);
}

function initProductDetailCompareButton(product) {
  const btn = document.querySelector('.page-product-detail .btn-icon-compare');
  if (!btn || !window.compareManager) return;

  const firstVariant = (product.variants || [])[0];
  const variantId = firstVariant?.urun_kodu || firstVariant?.id || product.id || product.slug;
  btn.dataset.variantId = variantId;

  if (btn.dataset.compareBound === 'true') return;
  btn.dataset.compareBound = 'true';

  btn.addEventListener('click', () => {
    const result = window.compareManager.toggle(btn.dataset.productId, btn.dataset.variantId);
    if (!result.success && result.message) {
      const toast = document.createElement('div');
      toast.className = 'compare-toast';
      toast.textContent = result.message;
      document.body.appendChild(toast);
      requestAnimationFrame(() => toast.classList.add('show'));
      setTimeout(() => toast.remove(), 2500);
    }
  });

  window.compareManager.syncCheckboxes();
}

function initProductDetailTabs() {
  const tabButtons = document.querySelectorAll('.product-detail-tabs [data-target]');
  const tabPanels = document.querySelectorAll(
    '.product-detail-tabs-section .tab-content[id^="tab-"]:not(#tab-variant-section)'
  );
  if (!tabButtons.length) return;

  function setActiveButton(targetId) {
    tabButtons.forEach((btn) => {
      const active = btn.getAttribute('data-target') === targetId;
      btn.setAttribute('aria-selected', active ? 'true' : 'false');
      btn.classList.toggle('border-b-2', active);
      btn.classList.toggle('border-abrasive-red', active);
      btn.classList.toggle('text-on-surface', active);
      btn.classList.toggle('text-steel-gray', !active);
    });
  }

  function activateTab(targetId) {
    if (targetId === 'tab-variant-section') {
      document
        .getElementById('product-variant-section')
        ?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setActiveButton(targetId);
      return;
    }
    tabPanels.forEach((panel) => {
      const show = panel.id === targetId;
      panel.hidden = !show;
      panel.classList.toggle('hidden', !show);
    });
    setActiveButton(targetId);
  }

  tabButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const target = btn.getAttribute('data-target');
      if (target) activateTab(target);
    });
  });

  activateTab('tab-description');
}

document.addEventListener('DOMContentLoaded', async () => {
  initProductDetailTabs();

  const productId = document.body.dataset.productId;
  if (!productId) return;

  const pm = new ProductManager();
  try {
    await pm.loadProducts();
    const product = pm.getProductById(productId);
    if (!product) {
      const main = document.getElementById('main-content');
      if (main) {
        main.innerHTML = `<section class="max-w-7xl mx-auto px-margin-mobile lg:px-margin-desktop py-16"><p class="no-products-message">${escapeHtml(t('product.notFound', { id: productId }))}</p></section>`;
      }
      return;
    }
    renderProductPage(product, pm);
  } catch (e) {
    console.error(e);
    const tableWrap = document.getElementById('variant-specs-table');
    if (tableWrap) {
      tableWrap.innerHTML = `<p class="no-products-message p-4">${escapeHtml(e.message || t('product.loadError'))}</p>`;
    }
  }
});
