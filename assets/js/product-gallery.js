let productGalleryController = null;
let productGalleryKeyHandler = null;

function initProductGallery() {
  const images = document.querySelectorAll('.gallery-main .slider-image');
  const thumbBtns = document.querySelectorAll('.gallery-thumb-btn');
  if (!images.length) {
    productGalleryController = null;
    return null;
  }

  let current = 0;
  let inlineKeyboardEnabled = true;

  function show(index) {
    current = (index + images.length) % images.length;
    images.forEach((img, i) => img.classList.toggle('active', i === current));
    thumbBtns.forEach((btn, i) => {
      btn.classList.toggle('active', i === current);
      btn.setAttribute('aria-selected', i === current ? 'true' : 'false');
      const thumbImg = btn.querySelector('.gallery-thumb');
      if (thumbImg) thumbImg.classList.toggle('active', i === current);
    });
  }

  document.querySelector('.slider-btn.prev')?.addEventListener('click', () => show(current - 1));
  document.querySelector('.slider-btn.next')?.addEventListener('click', () => show(current + 1));

  thumbBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      const idx = parseInt(btn.dataset.index, 10);
      if (!Number.isNaN(idx)) show(idx);
    });
  });

  if (productGalleryKeyHandler) {
    document.removeEventListener('keydown', productGalleryKeyHandler);
  }

  productGalleryKeyHandler = (e) => {
    if (!inlineKeyboardEnabled || window.GalleryLightbox?.isOpen()) return;
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      show(current - 1);
    }
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      show(current + 1);
    }
  };

  document.addEventListener('keydown', productGalleryKeyHandler);

  show(0);

  productGalleryController = {
    show,
    getIndex: () => current,
    setInlineKeyboardEnabled(enabled) {
      inlineKeyboardEnabled = !!enabled;
    },
  };

  return productGalleryController;
}
