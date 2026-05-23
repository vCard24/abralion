const NOIR_BADGE_COLUMNS = new Set([
  'malzeme', 'asindirici_kodu', 'asindirici_tipi', 'urun_tipi', 'baglanti_tipi',
  'bicak_malzemesi', 'kasa_malzemesi', 'kullanim_yeri', 'govde_kizak_tipi',
]);

function formatTableCellHtml(cell, col) {
  const raw = cell == null ? '' : String(cell);
  if (!raw) return '';
  const colId = col.key || col.compute;
  if (colId && NOIR_BADGE_COLUMNS.has(colId)) {
    return `<span class="noir-spec-badge">${escapeHtml(raw)}</span>`;
  }
  return escapeHtml(raw);
}

function productThumbForCard(base, product) {
  const slug = product.slug;
  const kart = `${base}assets/images/products/${slug}/${slug}-kart.webp`;
  if (product.images?.[0]?.src) {
    const src = product.images[0].src;
    return src.startsWith('assets') ? `${base}${src}` : src;
  }
  return kart;
}

function renderRelatedProducts(product, pm) {
  const grid = document.getElementById('related-products-grid');
  if (!grid || !pm) return;

  const base = getBasePath();
  const related = pm.getAllProducts()
    .filter((p) => p.categoryId === product.categoryId && p.slug !== product.slug)
    .slice(0, 3);

  if (!related.length) {
    grid.innerHTML = '<p class="col-span-full font-technical-data text-steel-gray">Katalogdan diğer ürün ailelerini inceleyebilirsiniz.</p>';
    return;
  }

  grid.innerHTML = related.map((p) => {
    const url = `${base}urun/${p.slug}.html`;
    const thumb = productThumbForCard(base, p);
    const code = (p.variants?.[0]?.urun_kodu || p.slug).toUpperCase();
    const descRaw = (p.description || '').slice(0, 90);
    const desc = escapeHtml(descRaw);
    const name = escapeHtml(p.name);
    return `<a href="${url}" class="noir-related-card group block overflow-hidden rounded-lg">
      <div class="noir-related-card__media relative flex items-center justify-center p-8 overflow-hidden">
        <img class="h-full max-h-full object-contain transition-transform duration-500 group-hover:scale-110 opacity-80" src="${thumb}" alt="" loading="lazy" width="400" height="300">
        <span class="noir-related-card__code absolute top-4 left-4 font-technical-data text-[10px] text-white px-2 py-1">${escapeHtml(code)}</span>
      </div>
      <div class="p-6">
        <h4 class="font-label-caps text-label-caps text-white mb-2 uppercase leading-snug">${name}</h4>
        <p class="text-[12px] text-steel-gray mb-4 line-clamp-2">${desc}${descRaw.length >= 90 ? '…' : ''}</p>
        <span class="text-abrasive-red font-label-caps text-[11px] inline-flex items-center gap-2 uppercase">
          Detayları İncele
          <span class="material-symbols-outlined text-[14px]" data-icon="chevron_right">chevron_right</span>
        </span>
      </div>
    </a>`;
  }).join('');
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
          <span class="material-symbols-outlined text-abrasive-red text-lg shrink-0" data-icon="check_circle">check_circle</span>
          <span class="text-body-md text-on-surface">${text}</span>
        </li>`;
      }
      return `<li class="text-on-surface-variant">${text}</li>`;
    })
    .join('');
}

function renderGallery(product, container) {
  const base = getBasePath();
  const images = (product.images && product.images.length)
    ? product.images
    : [{ src: 'assets/images/placeholder/gorsel.jpg', alt: product.name }];

  const slides = images
    .map((img, i) => {
      const src = img.src.startsWith('assets') ? `${base}${img.src}` : img.src;
      return `<img src="${src}" alt="${escapeHtml(img.alt || product.name)}" class="slider-image w-4/5 h-4/5 object-contain transition-transform duration-700 group-hover:scale-110${i === 0 ? ' active' : ''}">`;
    })
    .join('');

  const thumbs = images
    .map((img, i) => {
      const src = img.src.startsWith('assets') ? `${base}${img.src}` : img.src;
      const active = i === 0;
      return `<button type="button" class="gallery-thumb-btn aspect-square bg-surface-elevation border p-2 cursor-pointer transition-colors${active ? ' border-abrasive-red' : ' border-steel-gray/10 hover:border-abrasive-red/50'}" aria-label="Görsel ${i + 1}" aria-selected="${active ? 'true' : 'false'}" data-index="${i}">
          <img src="${src}" alt="" class="gallery-thumb w-full h-full object-contain">
        </button>`;
    })
    .join('');

  container.innerHTML = `
    <div class="product-gallery-gradient aspect-square flex items-center justify-center border border-steel-gray/10 relative shimmer-effect group overflow-hidden product-image-slider gallery-main">
      <button type="button" class="slider-btn prev absolute left-4 top-1/2 z-20 -translate-y-1/2 flex h-12 w-12 items-center justify-center border border-white/10 bg-carbon-black/60 text-white transition-colors hover:bg-abrasive-red sr-only" aria-label="Önceki görsel">‹</button>
      <div class="slider-container relative flex h-full w-full items-center justify-center z-10">${slides}</div>
      <button type="button" class="slider-btn next absolute right-4 top-1/2 z-20 -translate-y-1/2 flex h-12 w-12 items-center justify-center border border-white/10 bg-carbon-black/60 text-white transition-colors hover:bg-abrasive-red sr-only" aria-label="Sonraki görsel">›</button>
      <div class="absolute bottom-6 left-6 flex gap-3 z-20">
        <button type="button" class="gallery-lightbox-trigger w-12 h-12 bg-carbon-black/60 border border-white/10 flex items-center justify-center hover:bg-abrasive-red transition-colors" aria-label="Yakınlaştır">
          <span class="material-symbols-outlined text-white" data-icon="zoom_in">zoom_in</span>
        </button>
      </div>
    </div>
    <div class="gallery-thumbs grid grid-cols-4 gap-4" role="tablist" aria-label="Ürün görselleri">${thumbs}</div>`;

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
  if (galleryController && typeof galleryController.showSlide === 'function') {
    const originalShow = galleryController.showSlide.bind(galleryController);
    galleryController.showSlide = (index) => {
      originalShow(index);
      syncTransformOrigin();
    };
  }
  if (typeof initGalleryLightbox === 'function') {
    initGalleryLightbox(galleryController);
  }
}

function techSummaryItem(label, value, options = {}) {
  if (value == null || value === '') return '';
  const valueClass = options.red ? 'font-technical-data text-abrasive-red' : 'font-technical-data text-on-surface';
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
    wrap.innerHTML = '<p class="col-span-2 text-steel-gray text-[12px]">Varyasyon tablosundan model detaylarını inceleyebilirsiniz.</p>';
    return;
  }
  const rpm = variant.max_hiz_rpm != null
    ? `${Number(variant.max_hiz_rpm).toLocaleString('tr-TR')} RPM`
    : variant.max_hiz_ms != null
      ? `${variant.max_hiz_ms} m/s`
      : '';
  wrap.innerHTML = [
    techSummaryItem('Malzeme', variant.asindirici_kodu || variant.asindirici_tipi || product.categoryName),
    techSummaryItem('Çap', variant.daire_capi_mm != null ? `${variant.daire_capi_mm} mm` : ''),
    techSummaryItem('Kalınlık', variant.kalinlik_mm != null ? `${variant.kalinlik_mm} mm` : ''),
    techSummaryItem('Delik Çapı', variant.gobek_capi_mm != null ? `${variant.gobek_capi_mm} mm` : ''),
    techSummaryItem('Max RPM', rpm, { red: Boolean(rpm) }),
    techSummaryItem('Sertifika', 'EN 12413 / oSa'),
  ].filter(Boolean).join('');
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
      extraEl.innerHTML = parts.length > 1
        ? parts.slice(1).map((part) => `<p>${escapeHtml(part.trim())}</p>`).join('')
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
    <li><a class="hover:text-on-surface transition-colors" href="${base}index.html">Ana Sayfa</a></li>
    <li class="flex items-center gap-2" aria-hidden="true"><span class="material-symbols-outlined text-[14px]">chevron_right</span></li>
    <li><a class="hover:text-on-surface transition-colors" href="${base}urunler.html">Ürünlerimiz</a></li>
    <li class="flex items-center gap-2" aria-hidden="true"><span class="material-symbols-outlined text-[14px]">chevron_right</span></li>
    <li><a class="hover:text-on-surface transition-colors" href="${base}urunler.html?kategori=${encodeURIComponent(product.categoryId)}">${escapeHtml(product.categoryName)}</a></li>
    <li class="flex items-center gap-2" aria-hidden="true"><span class="material-symbols-outlined text-[14px]">chevron_right</span></li>
    <li class="text-abrasive-red" aria-current="page">${escapeHtml(product.name)}</li>`;
}

function renderVariantTable(product, tableWrap) {
  const columns = getTableColumns(product);
  if (!columns.length) {
    tableWrap.innerHTML = '<p class="no-products-message p-4">Bu ürün için tablo yapılandırması bulunamadı.</p>';
    return;
  }

  let thead = '<thead><tr class="bg-surface-container-high border-b border-steel-gray/20">';
  thead += '<th class="compare-col spec-col--compare p-4 font-label-caps text-[12px] text-steel-gray" scope="col"><span class="sr-only">Karşılaştır</span></th>';
  thead += columns.map((c) => {
    const colClass = getSpecColumnClass(c);
    return `<th class="spec-col ${colClass} p-4 font-label-caps text-[12px] text-steel-gray uppercase" scope="col">${escapeHtml(c.label)}</th>`;
  }).join('');
  thead += '</tr></thead>';

  let tbody = '<tbody class="font-technical-data text-[14px]">';
  (product.variants || []).forEach((variant, index) => {
    const vid = variant.urun_kodu || variant.id || `v${index + 1}`;
    const cells = variantRowCells(variant, columns);
    const label = variantLabel(variant, product.name).replace(/"/g, '&quot;');
    const stripe = index % 2 === 1 ? ' bg-surface-container-low/30' : '';
    tbody += `<tr class="border-b border-steel-gray/10 hover:bg-surface-elevation/50 transition-colors${stripe}" data-variant-id="${vid}">`;
    tbody += `<td class="compare-cell spec-col--compare p-4">
      <label class="compare-check" title="Karşılaştırmaya ekle">
        <input type="checkbox" class="compare-row-input"
          data-product-id="${product.id}"
          data-variant-id="${vid}"
          aria-label="${label} karşılaştır">
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
    tableWrap.innerHTML = '<p class="no-products-message p-4">Bu ürün için varyant verisi bulunamadı.</p>';
    return;
  }

  tableWrap.innerHTML = `<table class="w-full text-left border-collapse specs-table specs-table--stitch">${thead}${tbody}</table>`;

  tableWrap.querySelectorAll('.compare-row-input').forEach((input) => {
    input.addEventListener('change', () => {
      const result = window.compareManager.toggle(
        input.dataset.productId,
        input.dataset.variantId
      );
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
  const pageUrl = `${window.OG_SITE_ORIGIN || 'https://abralion.com'}/urun/${slug}.html`;
  const shareImage =
    product.images?.[0]?.src || `assets/images/products/${slug}/${slug}-kart.jpg`;
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
    catEl.textContent = series ? `Seri: ${series}` : '';
    catEl.classList.add('uppercase');
  }
  if (titleEl) titleEl.textContent = product.name || '';

  renderDescriptionContent(product);
  renderTechSummary(product);

  fillList(
    document.querySelector('#product-features-short ul'),
    product.features,
    { styled: true }
  );
  fillList(
    document.querySelector('#product-applications ul'),
    product.applications,
    { styled: true }
  );

  const appImg = document.getElementById('product-application-image');
  if (appImg && product.images?.[0]?.src) {
    const imgSrc = product.images[0].src.startsWith('assets')
      ? `${base}${product.images[0].src}`
      : product.images[0].src;
    appImg.src = imgSrc;
    appImg.alt = product.images[0].alt || product.name;
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
  const variantId =
    firstVariant?.urun_kodu || firstVariant?.id || product.id || product.slug;
  btn.dataset.variantId = variantId;

  if (btn.dataset.compareBound === 'true') return;
  btn.dataset.compareBound = 'true';

  btn.addEventListener('click', () => {
    const result = window.compareManager.toggle(
      btn.dataset.productId,
      btn.dataset.variantId
    );
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
  const tabPanels = document.querySelectorAll('.product-detail-tabs-section .tab-content[id^="tab-"]:not(#tab-variant-section)');
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
      document.getElementById('product-variant-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
        main.innerHTML = `<section class="max-w-7xl mx-auto px-margin-mobile lg:px-margin-desktop py-16"><p class="no-products-message">${escapeHtml(productId)} — ürün bulunamadı.</p></section>`;
      }
      return;
    }
    renderProductPage(product, pm);
  } catch (e) {
    console.error(e);
    const tableWrap = document.getElementById('variant-specs-table');
    if (tableWrap) {
      tableWrap.innerHTML = `<p class="no-products-message p-4">${escapeHtml(e.message || 'Sayfa yüklenemedi.')}</p>`;
    }
  }
});
