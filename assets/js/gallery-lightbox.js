/**
 * Ürün galerisi lightbox — native dialog, swipe, klavye, inline slider senkronu
 */
(function () {
  const SWIPE_THRESHOLD = 50;
  const FOCUSABLE =
    'button:not([disabled]), [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

  let dialog = null;
  let stage = null;
  let imgEl = null;
  let counterEl = null;
  let btnPrev = null;
  let btnNext = null;
  let btnClose = null;

  let images = [];
  let current = 0;
  let openFlag = false;
  let inlineController = null;
  let lastFocus = null;

  let touchStartX = 0;
  let touchStartY = 0;
  let touchLock = null;

  function isOpen() {
    return openFlag && dialog?.open;
  }

  function collectImages() {
    return Array.from(document.querySelectorAll('.gallery-main .slider-image')).map((el) => ({
      src: el.currentSrc || el.src,
      alt: el.alt || '',
    }));
  }

  function ensureDialog() {
    if (dialog) return;

    dialog = document.createElement('dialog');
    dialog.className = 'gallery-lightbox';
    dialog.setAttribute('aria-label', 'Ürün görseli');
    dialog.innerHTML = `
      <div class="gallery-lightbox__inner">
        <button type="button" class="gallery-lightbox__close" aria-label="Kapat">×</button>
        <button type="button" class="gallery-lightbox__nav gallery-lightbox__nav--prev" aria-label="Önceki görsel">‹</button>
        <figure class="gallery-lightbox__stage">
          <img class="gallery-lightbox__img" src="" alt="" decoding="async">
          <figcaption class="gallery-lightbox__counter" aria-live="polite"></figcaption>
        </figure>
        <button type="button" class="gallery-lightbox__nav gallery-lightbox__nav--next" aria-label="Sonraki görsel">›</button>
      </div>`;

    document.body.appendChild(dialog);

    stage = dialog.querySelector('.gallery-lightbox__stage');
    imgEl = dialog.querySelector('.gallery-lightbox__img');
    counterEl = dialog.querySelector('.gallery-lightbox__counter');
    btnPrev = dialog.querySelector('.gallery-lightbox__nav--prev');
    btnNext = dialog.querySelector('.gallery-lightbox__nav--next');
    btnClose = dialog.querySelector('.gallery-lightbox__close');

    btnClose.addEventListener('click', () => close());
    btnPrev.addEventListener('click', () => go(-1));
    btnNext.addEventListener('click', () => go(1));

    dialog.addEventListener('click', (e) => {
      if (e.target === dialog) close();
    });

    dialog.addEventListener('close', () => {
      openFlag = false;
      document.documentElement.classList.remove('gallery-lightbox-open');
      inlineController?.setInlineKeyboardEnabled(true);
      if (lastFocus && typeof lastFocus.focus === 'function') {
        lastFocus.focus();
      }
      lastFocus = null;
    });

    dialog.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        go(-1);
        return;
      }
      if (e.key === 'ArrowRight') {
        e.preventDefault();
        go(1);
        return;
      }
      if (e.key === 'Tab') {
        trapFocus(e);
      }
    });

    bindTouch(stage);
  }

  function bindTouch(el) {
    el.addEventListener(
      'touchstart',
      (e) => {
        if (!isOpen() || e.touches.length !== 1) return;
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
        touchLock = null;
      },
      { passive: true }
    );

    el.addEventListener(
      'touchmove',
      (e) => {
        if (!isOpen() || e.touches.length !== 1) return;
        const dx = e.touches[0].clientX - touchStartX;
        const dy = e.touches[0].clientY - touchStartY;
        if (touchLock === null) {
          if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 8) touchLock = 'x';
          else if (Math.abs(dy) > Math.abs(dx) && Math.abs(dy) > 8) touchLock = 'y';
        }
        if (touchLock === 'x') e.preventDefault();
      },
      { passive: false }
    );

    el.addEventListener(
      'touchend',
      (e) => {
        if (!isOpen() || touchLock !== 'x') return;
        const dx = e.changedTouches[0].clientX - touchStartX;
        if (Math.abs(dx) >= SWIPE_THRESHOLD) go(dx > 0 ? -1 : 1);
        touchLock = null;
      },
      { passive: true }
    );
  }

  function trapFocus(e) {
    const nodes = dialog.querySelectorAll(FOCUSABLE);
    const list = Array.from(nodes).filter((n) => n.offsetParent !== null || n === btnClose);
    if (!list.length) return;
    const first = list[0];
    const last = list[list.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }

  function updateUi() {
    if (!images.length) return;
    const item = images[current];
    imgEl.src = item.src;
    imgEl.alt = item.alt;
    counterEl.textContent = `${current + 1} / ${images.length}`;

    const single = images.length <= 1;
    dialog.classList.toggle('gallery-lightbox--single', single);
    btnPrev.disabled = single;
    btnNext.disabled = single;
  }

  function syncInline(index) {
    inlineController?.show(index);
  }

  function go(delta) {
    if (images.length <= 1) return;
    current = (current + delta + images.length) % images.length;
    updateUi();
    syncInline(current);
  }

  function open(index) {
    images = collectImages();
    if (!images.length) return;

    ensureDialog();
    current = ((index % images.length) + images.length) % images.length;
    lastFocus = document.activeElement;

    updateUi();
    syncInline(current);

    inlineController?.setInlineKeyboardEnabled(false);
    document.documentElement.classList.add('gallery-lightbox-open');

    if (typeof dialog.showModal === 'function') {
      dialog.showModal();
    } else {
      dialog.setAttribute('open', '');
    }
    openFlag = true;
    btnClose.focus();
  }

  function close() {
    if (!dialog) return;
    if (typeof dialog.close === 'function') {
      dialog.close();
    } else {
      dialog.removeAttribute('open');
      openFlag = false;
      document.documentElement.classList.remove('gallery-lightbox-open');
      inlineController?.setInlineKeyboardEnabled(true);
    }
  }

  function bindGalleryTriggers() {
    const container = document.querySelector('.gallery-main .slider-container');
    if (container) {
      container.setAttribute('role', 'button');
      container.setAttribute('tabindex', '0');
      container.setAttribute('aria-label', 'Görseli büyüt');
      container.addEventListener('click', () => {
        const idx = inlineController?.getIndex?.() ?? current;
        open(idx);
      });
      container.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          const idx = inlineController?.getIndex?.() ?? current;
          open(idx);
        }
      });
    }

    document.querySelectorAll('.gallery-thumb-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const idx = parseInt(btn.dataset.index, 10);
        if (!Number.isNaN(idx)) open(idx);
      });
    });
  }

  function initGalleryLightbox(controller) {
    inlineController = controller || null;
    images = collectImages();
    ensureDialog();
    bindGalleryTriggers();
  }

  window.GalleryLightbox = { isOpen, open, close, init: initGalleryLightbox };
  window.initGalleryLightbox = initGalleryLightbox;
})();
