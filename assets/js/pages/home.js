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

const featuredMqSm = window.matchMedia('(max-width: 639px)');
const featuredMqLg = window.matchMedia('(max-width: 1023px)');

function getFeaturedVisibleCount() {
  if (featuredMqSm.matches) return 1;
  if (featuredMqLg.matches) return 2;
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
  let pendingUpdate = false;

  function maxIndex() {
    const cards = track.querySelectorAll('.product-card:not(.product-card--skeleton)');
    const visible = getFeaturedVisibleCount();
    return Math.max(0, cards.length - visible);
  }

  let cachedStep = 0;

  function measureStep() {
    const card = track.querySelector('.product-card:not(.product-card--skeleton)');
    if (!card) return 0;
    const styles = getComputedStyle(track);
    const gap = parseFloat(styles.columnGap || styles.gap || '24') || 24;
    return card.getBoundingClientRect().width + gap;
  }

  function update() {
    pendingUpdate = false;
    const cards = track.querySelectorAll('.product-card:not(.product-card--skeleton)');
    const visible = getFeaturedVisibleCount();
    const max = Math.max(0, cards.length - visible);
    index = Math.min(index, max);

    // Read geometry in this frame, write transform in the next — avoids forced reflow
    const step = cachedStep > 0 ? cachedStep : measureStep();
    cachedStep = step;
    const offset = index * step;
    const atStart = index <= 0;
    const atEnd = index >= max;
    const scrollable = cards.length > visible;

    requestAnimationFrame(() => {
      track.style.transform = offset ? `translateX(-${offset}px)` : '';
      prevBtn.disabled = atStart;
      nextBtn.disabled = atEnd;
      carousel.classList.toggle('featured-carousel--scrollable', scrollable);
    });
  }

  function scheduleUpdate() {
    if (pendingUpdate) return;
    pendingUpdate = true;
    cachedStep = 0;
    requestAnimationFrame(update);
  }

  prevBtn.addEventListener('click', () => {
    index = Math.max(0, index - 1);
    scheduleUpdate();
  });

  nextBtn.addEventListener('click', () => {
    index = Math.min(maxIndex(), index + 1);
    scheduleUpdate();
  });

  window.addEventListener('resize', () => {
    index = Math.min(index, maxIndex());
    scheduleUpdate();
  });

  if (typeof ResizeObserver !== 'undefined') {
    const ro = new ResizeObserver(() => scheduleUpdate());
    ro.observe(track);
  }

  const api = {
    reset() {
      index = 0;
      scheduleUpdate();
    },
  };
  carousel._featuredCarousel = api;
  // LCP sonrası ölç — ilk boyamada zorunlu reflow'u erteler
  if (document.readyState === 'complete') {
    scheduleUpdate();
  } else {
    window.addEventListener('load', () => scheduleUpdate(), { once: true });
  }
  return api;
}

document.addEventListener('DOMContentLoaded', async () => {
  const grid = document.getElementById('featured-products-grid');
  if (!grid) return;

  const fallbackMsg = document.getElementById('featured-grid-fallback-msg');
  const staticBackup = grid.innerHTML;
  const hadStatic = !!grid.querySelector('.product-card--static');

  if (hadStatic) {
    if (fallbackMsg) fallbackMsg.hidden = true;
    initStaticCardImages(grid);
    initFeaturedCarousel();
    return;
  }

  const viewport = grid.closest('.featured-carousel__viewport');
  if (viewport) viewport.style.minHeight = '300px';

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
      initFeaturedCarousel();
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
      initFeaturedCarousel();
      const existing = grid
        .closest('.featured-products')
        ?.querySelector('.catalog-fallback-notice');
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
    initFeaturedCarousel();
  }
});
