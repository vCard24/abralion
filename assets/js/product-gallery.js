function initProductGallery() {
  const images = document.querySelectorAll('.gallery-main .slider-image');
  const thumbBtns = document.querySelectorAll('.gallery-thumb-btn');
  if (!images.length) return;

  let current = 0;

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

  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') show(current - 1);
    if (e.key === 'ArrowRight') show(current + 1);
  });

  show(0);
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.querySelector('.gallery-main .slider-image')) {
    initProductGallery();
  }
});
