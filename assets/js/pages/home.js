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
  const grid = document.getElementById('featured-products-grid');
  if (!grid) return;

  const fallbackMsg = document.getElementById('featured-grid-fallback-msg');
  const staticBackup = grid.innerHTML;
  const hadStatic = !!grid.querySelector('.product-card--static');

  if (!hadStatic) {
    grid.innerHTML = '';
    for (let i = 0; i < 6; i += 1) {
      grid.appendChild(createSkeletonCard());
    }
  } else {
    if (fallbackMsg) fallbackMsg.hidden = true;
    initStaticCardImages(grid);
  }

  try {
    if (typeof ProductManager === 'undefined') {
      throw new Error('Ürün modülü yüklenemedi.');
    }
    const pm = new ProductManager();
    await pm.loadProducts();
    const featured = pm.getFeaturedProducts().slice(0, 6);
    if (!featured.length) {
      return;
    }
    if (renderProductCards(grid, featured)) {
      if (fallbackMsg) fallbackMsg.hidden = true;
      return;
    }
    if (!hadStatic) {
      throw new Error('Öne çıkan ürünler gösterilemedi.');
    }
  } catch (e) {
    console.error('Öne çıkan ürünler:', e);
    if (hadStatic) {
      grid.innerHTML = staticBackup;
      grid.classList.remove('product-grid--loading');
      if (fallbackMsg) fallbackMsg.hidden = true;
      initStaticCardImages(grid);
      const existing = grid.parentElement.querySelector('.catalog-fallback-notice');
      if (!existing) {
        const notice = document.createElement('p');
        notice.className = 'catalog-fallback-notice';
        notice.textContent =
          e.message || 'Öne çıkan ürünler yüklenemedi. Statik liste gösteriliyor.';
        grid.parentElement.insertBefore(notice, grid);
      }
      return;
    }
    grid.innerHTML = `<p class="loading-message">${e.message || 'Ürünler yüklenemedi.'}</p>`;
  }
});
