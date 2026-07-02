const CATEGORY_FILTERS = {
  'kesici-taslama': (p) =>
    p.categoryId === 'kesici-taslama-flap-disk' && !/flap-disk/i.test(p.slug || ''),
  'flap-disk': (p) =>
    p.categoryId === 'kesici-taslama-flap-disk' && /flap-disk/i.test(p.slug || ''),
  'elmas-kesici': (p) => p.categoryId === 'elmas-kesici',
  'kirici-delici': (p) => p.categoryId === 'kirici-delici',
};

const URL_CATEGORY_TO_FILTERS = {
  'kesici-taslama-flap-disk': ['kesici-taslama', 'flap-disk'],
  'elmas-kesici': ['elmas-kesici'],
  'kirici-delici': ['kirici-delici'],
};

const APPLICATION_BTN_ON =
  'application-filter-btn bg-abrasive-red px-3 py-1 text-technical-data text-white transition-colors';
const APPLICATION_BTN_OFF =
  'application-filter-btn bg-surface-elevation technical-border px-3 py-1 text-technical-data hover:bg-secondary-container transition-colors';

let catalogProducts = [];
let urlCategoryId = null;
let searchQuery = '';

function createSkeletonCard() {
  const card = document.createElement('div');
  card.className = 'product-card product-card--skeleton';
  card.setAttribute('aria-hidden', 'true');
  card.innerHTML = `
    <div class="product-card-skeleton-image"></div>
    <div class="product-card-skeleton-body">
      <div class="product-card-skeleton-line product-card-skeleton-line--short"></div>
      <div class="product-card-skeleton-line"></div>
      <div class="product-card-skeleton-line product-card-skeleton-line--medium"></div>
      <div class="product-card-skeleton-btn"></div>
    </div>`;
  return card;
}

function initStaticCardImages(root) {
  root.querySelectorAll('.product-card-image--hero[data-fallback]').forEach((img) => {
    img.addEventListener('error', () => {
      if (img.dataset.fallbackDone) return;
      const fallback = img.dataset.fallback;
      if (fallback && img.src !== fallback) {
        img.dataset.fallbackDone = '1';
        img.src = fallback;
      }
    });
  });
}

function filterStaticCards(grid, categoryId) {
  grid.querySelectorAll('.product-card--static').forEach((card) => {
    if (!categoryId || categoryId === 'all') {
      card.hidden = false;
    } else {
      card.hidden = card.dataset.categoryId !== categoryId;
    }
  });
}

function updateStaticCount(grid, countEl, categoryId) {
  if (!countEl) return;
  const cards = grid.querySelectorAll('.product-card--static');
  const visible =
    categoryId && categoryId !== 'all'
      ? grid.querySelectorAll('.product-card--static:not([hidden])').length
      : cards.length;
  countEl.textContent = `${visible || cards.length} ürün`;
}

function renderProductCards(grid, products) {
  if (typeof ProductCard === 'undefined') {
    return false;
  }
  const fragment = document.createDocumentFragment();
  let count = 0;
  products.forEach((product) => {
    try {
      fragment.appendChild(new ProductCard(product).render());
      count += 1;
    } catch (err) {
      console.error('Kart oluşturulamadı:', product?.slug, err);
    }
  });
  if (!count) {
    grid.innerHTML = '<p class="no-products-message">Seçilen filtrelere uygun ürün bulunamadı.</p>';
    return true;
  }
  grid.innerHTML = '';
  grid.appendChild(fragment);
  return true;
}

function productSearchHaystack(product) {
  return [
    product.name,
    product.description,
    product.categoryName,
    ...(product.features || []),
    ...(product.applications || []),
  ]
    .join(' ')
    .toLowerCase();
}

function getProductApplications(product) {
  const hay = productSearchHaystack(product);
  const areas = new Set();

  if (/metal|çelik|demir|profil|\bsac\b|lama/.test(hay)) areas.add('metal');
  if (/inox|paslanmaz/.test(hay)) areas.add('inox');
  if (/beton|tuğla|asfalt|şantiye|inşaat|kırıcı|delici|sds|matkap/.test(hay)) areas.add('beton');
  if (/mermer|granit|seramik|doğal taş/.test(hay)) areas.add('mermer');
  if (/ahşap|marangoz|maket|tre\b|wood/.test(hay)) areas.add('ahsap');

  if (!areas.size) {
    if (product.categoryId === 'elmas-kesici') {
      areas.add('beton');
      areas.add('mermer');
    } else if (product.categoryId === 'kirici-delici') {
      areas.add('beton');
    } else if (product.categoryId === 'kesici-taslama-flap-disk') {
      areas.add('metal');
    } else if (product.categoryId === 'olcum-kesim') {
      areas.add('ahsap');
    }
  }

  return [...areas];
}

function getSelectedCategoryFilters() {
  return [...document.querySelectorAll('.category-filter-input:checked')].map(
    (input) => input.dataset.filter
  );
}

function getSelectedApplicationFilters() {
  return [...document.querySelectorAll('.application-filter-btn.active')].map(
    (btn) => btn.dataset.application
  );
}

function matchesCategoryFilter(product, selectedCategories) {
  if (urlCategoryId) {
    return product.categoryId === urlCategoryId;
  }
  if (!selectedCategories.length) {
    return true;
  }
  return selectedCategories.some((key) => CATEGORY_FILTERS[key]?.(product));
}

function matchesApplicationFilter(product, selectedApplications) {
  if (!selectedApplications.length) {
    return true;
  }
  const apps = getProductApplications(product);
  return selectedApplications.some((area) => apps.includes(area));
}

function filterProducts(products) {
  const categories = getSelectedCategoryFilters();
  const applications = getSelectedApplicationFilters();
  let list = products.filter(
    (p) => matchesCategoryFilter(p, categories) && matchesApplicationFilter(p, applications)
  );

  if (searchQuery && typeof ProductManager !== 'undefined') {
    const pm = new ProductManager();
    pm.products = list;
    list = pm.search(searchQuery);
  }

  return list;
}

function updateCategoryLabelStyles() {
  document.querySelectorAll('.category-filter-input').forEach((input) => {
    const label = input.closest('label');
    const text = label?.querySelector('span');
    if (!text) return;
    text.classList.toggle('text-on-surface', input.checked);
    text.classList.toggle('text-on-surface-variant', !input.checked);
    text.classList.toggle('group-hover:text-abrasive-red', input.checked);
  });
}

function setApplicationButtonState(btn, active) {
  btn.className = active ? APPLICATION_BTN_ON : APPLICATION_BTN_OFF;
  btn.classList.toggle('active', active);
}

function syncFiltersFromUrl(kategori) {
  if (!kategori) return;

  if (kategori === 'olcum-kesim') {
    urlCategoryId = kategori;
    return;
  }

  const filterKeys = URL_CATEGORY_TO_FILTERS[kategori];
  if (!filterKeys) {
    urlCategoryId = kategori;
    return;
  }

  document.querySelectorAll('.category-filter-input').forEach((input) => {
    input.checked = filterKeys.includes(input.dataset.filter);
  });
  updateCategoryLabelStyles();
}

function clearUrlCategoryParam() {
  urlCategoryId = null;
  const url = new URL(window.location.href);
  if (!url.searchParams.has('kategori')) return;
  url.searchParams.delete('kategori');
  const next = url.searchParams.toString();
  window.history.replaceState({}, '', next ? `${url.pathname}?${next}` : url.pathname);
}

function applyCatalogFilters() {
  const grid = document.getElementById('products-grid');
  const countEl = document.getElementById('products-count');
  if (!grid || !catalogProducts.length) return;

  const list = filterProducts(catalogProducts);
  renderProductCards(grid, list);
  if (countEl) {
    countEl.textContent = `${list.length} Ürün Ailesi`;
  }
}

function clearAllFilters() {
  document.querySelectorAll('.category-filter-input').forEach((input) => {
    input.checked = false;
  });
  document.querySelectorAll('.application-filter-btn').forEach((btn) => {
    setApplicationButtonState(btn, false);
  });
  updateCategoryLabelStyles();
  clearUrlCategoryParam();
  applyCatalogFilters();
}

function initSidebarFilters() {
  document.querySelectorAll('.category-filter-input').forEach((input) => {
    input.addEventListener('change', () => {
      updateCategoryLabelStyles();
      clearUrlCategoryParam();
      applyCatalogFilters();
    });
  });

  document.querySelectorAll('.application-filter-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const next = !btn.classList.contains('active');
      setApplicationButtonState(btn, next);
      applyCatalogFilters();
    });
  });

  document.getElementById('clear-filters-btn')?.addEventListener('click', clearAllFilters);
}

function filterCategory(cat) {
  const base = getBasePath();
  if (!cat || cat === 'all') {
    window.location.href = `${base}urunler.html`;
  } else {
    window.location.href = `${base}urunler.html?kategori=${encodeURIComponent(cat)}`;
  }
}

function syncCategoryFilters(activeCategory) {
  const cat = activeCategory || 'all';
  document.querySelectorAll('.category-btn, .category-chip').forEach((el) => {
    el.classList.toggle('active', el.dataset.category === cat);
  });
}

function initCategoryChips() {
  document.querySelectorAll('.category-chip').forEach((chip) => {
    chip.addEventListener('click', () => {
      filterCategory(chip.dataset.category);
    });
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  const grid = document.getElementById('products-grid');
  if (!grid) return;

  const countEl = document.getElementById('products-count');
  const fallbackMsg = document.getElementById('products-grid-fallback-msg');
  const params = new URLSearchParams(window.location.search);
  const kategori = params.get('kategori');
  const search = params.get('search');
  const urun = params.get('urun');
  if (urun) {
    window.location.replace(productUrl(urun));
    return;
  }

  searchQuery = search || '';
  syncFiltersFromUrl(kategori);
  initSidebarFilters();
  syncCategoryFilters(kategori || 'all');
  initCategoryChips();

  const staticBackup = grid.innerHTML;
  const hadStatic = !!grid.querySelector('.product-card--static');

  if (!hadStatic) {
    grid.innerHTML = '';
    for (let i = 0; i < 12; i += 1) {
      grid.appendChild(createSkeletonCard());
    }
  } else {
    if (fallbackMsg) fallbackMsg.hidden = true;
    initStaticCardImages(grid);
    if (kategori) filterStaticCards(grid, kategori);
    updateStaticCount(grid, countEl, kategori);
  }

  try {
    if (typeof ProductManager === 'undefined') {
      throw new Error('Ürün modülü yüklenemedi.');
    }
    const pm = new ProductManager();
    await pm.loadProducts();
    catalogProducts = pm.getAllProducts();

    if (!catalogProducts.length) {
      if (!hadStatic) {
        grid.innerHTML = '<p class="no-products-message">Ürün bulunamadı.</p>';
      }
      return;
    }

    const list = filterProducts(catalogProducts);
    if (countEl) countEl.textContent = `${list.length} Ürün Ailesi`;

    if (!list.length) {
      if (!hadStatic) {
        grid.innerHTML =
          '<p class="no-products-message">Seçilen filtrelere uygun ürün bulunamadı.</p>';
      }
      return;
    }

    if (renderProductCards(grid, list)) {
      if (fallbackMsg) fallbackMsg.hidden = true;
      return;
    }
    if (!hadStatic) {
      throw new Error('Ürünler gösterilemedi.');
    }
  } catch (e) {
    console.error('Ürün kataloğu:', e);
    if (hadStatic) {
      grid.innerHTML = staticBackup;
      grid.classList.remove('product-grid--loading');
      if (fallbackMsg) fallbackMsg.hidden = true;
      initStaticCardImages(grid);
      if (kategori) filterStaticCards(grid, kategori);
      updateStaticCount(grid, countEl, kategori);
      const existing = grid.parentElement.querySelector('.catalog-fallback-notice');
      if (!existing) {
        const notice = document.createElement('p');
        notice.className = 'catalog-fallback-notice';
        notice.textContent =
          e.message ||
          'İnteraktif katalog yüklenemedi. Aşağıdaki statik liste ve ürün sayfalarını kullanabilirsiniz.';
        grid.parentElement.insertBefore(notice, grid);
      }
      return;
    }
    grid.innerHTML = `<p class="no-products-message">${e.message || 'Ürünler yüklenemedi.'}</p>`;
    if (countEl) countEl.textContent = 'Ürünler yüklenemedi';
  }
});
