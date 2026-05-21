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

document.addEventListener('DOMContentLoaded', async () => {
  const grid = document.getElementById('products-grid');
  const countEl = document.getElementById('products-count');
  const fallbackMsg = document.getElementById('products-grid-fallback-msg');
  const pm = new ProductManager();
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
    grid.classList.add('product-grid--loading');
    if (fallbackMsg) fallbackMsg.hidden = true;
    initStaticCardImages(grid);
    if (kategori) filterStaticCards(grid, kategori);
  }

  document.querySelectorAll('.category-btn').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.category === (kategori || 'all'));
  });

  try {
    await pm.loadProducts();
    let list = pm.getAllProducts();
    if (kategori) list = pm.filterByCategory(kategori);
    if (search) list = pm.search(search);

    if (countEl) countEl.textContent = `${list.length} ürün`;
    grid.classList.remove('product-grid--loading');
    grid.innerHTML = '';
    if (!list.length) {
      grid.innerHTML = '<p class="no-products-message">Ürün bulunamadı.</p>';
      return;
    }
    list.forEach((product) => {
      grid.appendChild(new ProductCard(product).render());
    });
  } catch (e) {
    grid.classList.remove('product-grid--loading');
    if (hadStatic) {
      grid.innerHTML = staticBackup;
      if (fallbackMsg) fallbackMsg.hidden = true;
      initStaticCardImages(grid);
      if (kategori) filterStaticCards(grid, kategori);
      const visible = grid.querySelectorAll('.product-card--static:not([hidden])').length;
      const total = grid.querySelectorAll('.product-card--static').length;
      if (countEl) countEl.textContent = `${visible || total} ürün`;
      const notice = document.createElement('p');
      notice.className = 'catalog-fallback-notice';
      notice.textContent =
        e.message || 'İnteraktif katalog yüklenemedi. Aşağıdaki statik liste ve ürün sayfalarını kullanabilirsiniz.';
      grid.parentElement.insertBefore(notice, grid);
    } else {
      grid.innerHTML = `<p class="no-products-message">${e.message || 'Ürünler yüklenemedi.'}</p>`;
      if (countEl) countEl.textContent = 'Ürünler yüklenemedi';
    }
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
