function createSkeletonCard() {
  const card = document.createElement('div');
  card.className = 'product-card product-card--skeleton group bg-surface-elevation technical-border p-6 flex flex-col';
  card.setAttribute('aria-hidden', 'true');
  card.innerHTML = `
    <div class="relative mb-6 aspect-[1.73] animate-pulse bg-carbon-black"></div>
    <div class="mt-auto space-y-3">
      <div class="h-3 w-1/3 animate-pulse rounded bg-surface-container-high"></div>
      <div class="h-5 w-3/4 animate-pulse rounded bg-surface-container-high"></div>
      <div class="h-4 w-full animate-pulse rounded bg-surface-container-high"></div>
    </div>`;
  return card;
}

function initStaticCardImages(root) {
  root.querySelectorAll('.product-card-image[data-fallback]').forEach((img) => {
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

function renderProductCards(grid, products, cardOptions = {}) {
  if (typeof ProductCard === 'undefined') {
    return false;
  }
  const fragment = document.createDocumentFragment();
  let count = 0;
  products.forEach((product) => {
    try {
      fragment.appendChild(new ProductCard(product, cardOptions).render());
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

function getFeaturedVisibleCount() {
  if (window.innerWidth < 640) return 1;
  if (window.innerWidth < 1024) return 2;
  return 3;
}

function initFeaturedCarousel() {
  const carousel = document.querySelector('[data-featured-carousel]');
  const track = document.getElementById('featured-products-grid');
  if (!carousel || !track) return null;

  if (carousel._featuredCarousel) {
    carousel._featuredCarousel.reset();
    return carousel._featuredCarousel;
  }

  const prevBtn = carousel.querySelector('.featured-carousel__arrow--prev');
  const nextBtn = carousel.querySelector('.featured-carousel__arrow--next');
  if (!prevBtn || !nextBtn) return null;

  let index = 0;

  function maxIndex() {
    const cards = track.querySelectorAll('.product-card:not(.product-card--skeleton)');
    const visible = getFeaturedVisibleCount();
    return Math.max(0, cards.length - visible);
  }

  function stepSize() {
    const card = track.querySelector('.product-card:not(.product-card--skeleton)');
    if (!card) return 0;
    const styles = getComputedStyle(track);
    const gap = parseFloat(styles.columnGap || styles.gap || '24') || 24;
    return card.getBoundingClientRect().width + gap;
  }

  function update() {
    const cards = track.querySelectorAll('.product-card:not(.product-card--skeleton)');
    const visible = getFeaturedVisibleCount();
    const max = Math.max(0, cards.length - visible);
    index = Math.min(index, max);

    const offset = index * stepSize();
    track.style.transform = offset ? `translateX(-${offset}px)` : '';

    prevBtn.disabled = index <= 0;
    nextBtn.disabled = index >= max;
    carousel.classList.toggle('featured-carousel--scrollable', cards.length > visible);
  }

  prevBtn.addEventListener('click', () => {
    index = Math.max(0, index - 1);
    update();
  });

  nextBtn.addEventListener('click', () => {
    index = Math.min(maxIndex(), index + 1);
    update();
  });

  window.addEventListener('resize', () => {
    index = Math.min(index, maxIndex());
    update();
  });

  if (typeof ResizeObserver !== 'undefined') {
    const ro = new ResizeObserver(() => update());
    ro.observe(track);
  }

  const api = {
    reset() {
      index = 0;
      update();
    },
  };
  carousel._featuredCarousel = api;
  update();
  return api;
}

document.addEventListener('DOMContentLoaded', async () => {
  const grid = document.getElementById('featured-products-grid');
  if (!grid) return;

  const fallbackMsg = document.getElementById('featured-grid-fallback-msg');
  const staticBackup = grid.innerHTML;
  const hadStatic = !!grid.querySelector('.product-card--static');

  if (!hadStatic) {
    grid.innerHTML = '';
    for (let i = 0; i < 3; i += 1) {
      grid.appendChild(createSkeletonCard());
    }
  } else {
    if (fallbackMsg) fallbackMsg.hidden = true;
    initStaticCardImages(grid);
  }

  let carousel = initFeaturedCarousel();

  try {
    if (typeof ProductManager === 'undefined') {
      throw new Error('Ürün modülü yüklenemedi.');
    }
    const pm = new ProductManager();
    await pm.loadProducts();
    const featured = pm.getFeaturedProducts();
    if (!featured.length) {
      return;
    }
    if (renderProductCards(grid, featured, { compact: true })) {
      if (fallbackMsg) fallbackMsg.hidden = true;
      carousel = initFeaturedCarousel();
      return;
    }
    if (!hadStatic) {
      throw new Error('Öne çıkan ürünler gösterilemedi.');
    }
  } catch (e) {
    console.error('Öne çıkan ürünler:', e);
    if (hadStatic) {
      grid.innerHTML = staticBackup;
      if (fallbackMsg) fallbackMsg.hidden = true;
      initStaticCardImages(grid);
      carousel = initFeaturedCarousel();
      const existing = grid.closest('.featured-products')?.querySelector('.catalog-fallback-notice');
      if (!existing) {
        const notice = document.createElement('p');
        notice.className = 'catalog-fallback-notice';
        notice.textContent =
          e.message || 'Öne çıkan ürünler yüklenemedi. Statik liste gösteriliyor.';
        grid.closest('[data-featured-carousel]')?.insertAdjacentElement('afterend', notice);
      }
      return;
    }
    grid.innerHTML = `<p class="loading-message">${e.message || 'Ürünler yüklenemedi.'}</p>`;
    carousel = initFeaturedCarousel();
  }
});
