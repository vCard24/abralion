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
  const visible = categoryId && categoryId !== 'all'
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
    return false;
  }
  grid.innerHTML = '';
  grid.appendChild(fragment);
  return true;
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

  syncCategoryFilters(kategori || 'all');
  initCategoryChips();

  try {
    if (typeof ProductManager === 'undefined') {
      throw new Error('Ürün modülü yüklenemedi.');
    }
    const pm = new ProductManager();
    await pm.loadProducts();
    let list = pm.getAllProducts();
    if (kategori) list = pm.filterByCategory(kategori);
    if (search) list = pm.search(search);

    if (countEl) countEl.textContent = `${list.length} ürün`;

    if (!list.length) {
      if (!hadStatic) {
        grid.innerHTML = '<p class="no-products-message">Ürün bulunamadı.</p>';
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
          e.message || 'İnteraktif katalog yüklenemedi. Aşağıdaki statik liste ve ürün sayfalarını kullanabilirsiniz.';
        grid.parentElement.insertBefore(notice, grid);
      }
      return;
    }
    grid.innerHTML = `<p class="no-products-message">${e.message || 'Ürünler yüklenemedi.'}</p>`;
    if (countEl) countEl.textContent = 'Ürünler yüklenemedi';
  }
});

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
