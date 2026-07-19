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

  const prevBtn = carousel.querySelector('.featured-carousel__arrow--prev');
  const nextBtn = carousel.querySelector('.featured-carousel__arrow--next');
  const viewport = carousel.querySelector('.featured-carousel__viewport');
  if (!prevBtn || !nextBtn) return null;

  let index = 0;
  let resizeRaf = 0;

  function cards() {
    return [...track.querySelectorAll('.product-card:not(.product-card--skeleton)')];
  }

  function maxIndex() {
    const visible = getFeaturedVisibleCount();
    return Math.max(0, cards().length - visible);
  }

  function updateControls() {
    const max = maxIndex();
    prevBtn.disabled = index <= 0;
    nextBtn.disabled = index >= max;
    carousel.classList.toggle('featured-carousel--scrollable', max > 0);
  }

  function scrollToIndex(behavior = 'smooth') {
    const items = cards();
    const target = items[index];
    if (!target || !viewport) return;
    viewport.scrollTo({
      left: target.offsetLeft - track.offsetLeft,
      behavior,
    });
    updateControls();
  }

  prevBtn.addEventListener('click', () => {
    index = Math.max(0, index - 1);
    scrollToIndex();
  });

  nextBtn.addEventListener('click', () => {
    index = Math.min(maxIndex(), index + 1);
    scrollToIndex();
  });

  window.addEventListener('resize', () => {
    if (resizeRaf) cancelAnimationFrame(resizeRaf);
    resizeRaf = requestAnimationFrame(() => {
      resizeRaf = 0;
      index = Math.min(index, maxIndex());
      scrollToIndex('auto');
    });
  });

  updateControls();
  return carousel;
}

document.addEventListener('DOMContentLoaded', () => {
  const grid = document.getElementById('featured-products-grid');
  if (!grid) return;
  const fallbackMsg = document.getElementById('featured-grid-fallback-msg');
  if (fallbackMsg) fallbackMsg.hidden = true;
  initStaticCardImages(grid);
  initFeaturedCarousel();
});
