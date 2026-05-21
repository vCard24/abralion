class ProductCard {
  constructor(product) {
    this.product = product;
    this.element = null;
  }

  render() {
    this.element = this.createCardElement();
    this.attachEventListeners();
    return this.element;
  }

  createCardElement() {
    const base = getBasePath();
    const p = this.product;
    const firstVar = p.variants?.[0];
    const variantId = firstVar ? (firstVar.urun_kodu || firstVar.id) : p.id;
    const kartSrc = ProductCard.kartImageSrc(base, p.slug);

    const card = document.createElement('div');
    card.className = 'product-card';
    card.setAttribute('data-product-id', p.id);

    const imageBlock = `<div class="product-card-image-container product-card-image-container--static-hero">
        <img class="product-card-image product-card-image--hero" src="${kartSrc}" alt="${p.name}" loading="lazy"
          data-fallback="${base}assets/images/products/${p.slug}/${p.slug}-kart.png">
      </div>`;

    card.innerHTML = `
      ${imageBlock}
      <div class="product-card-content">
        <div class="product-card-category">${p.categoryName || ''}</div>
        <h3 class="product-card-title">${p.name}</h3>
        <p class="product-card-description">${(p.description || '').length > 120 ? (p.description || '').slice(0, 120) + '…' : (p.description || '')}</p>
        <div class="product-card-actions">
          <a href="${productUrl(p.slug)}" class="btn btn-primary btn-small">Detaylar</a>
          <button type="button" class="btn-icon-compare" title="İlk modeli karşılaştırmaya ekle"
            data-product-id="${p.id}" data-variant-id="${variantId}" aria-label="Karşılaştır">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M16 3h5v5M4 20 21 3M21 16v5h-5M15 15l6 6M4 4l5 5"/>
            </svg>
          </button>
        </div>
      </div>
    `;
    return card;
  }

  static kartImageSrc(base, slug) {
    const jpg = `${base}assets/images/products/${slug}/${slug}-kart.jpg`;
    const png = `${base}assets/images/products/${slug}/${slug}-kart.png`;
    return slug === 'metal-inox-kesme-tasi' ? png : jpg;
  }

  attachEventListeners() {
    const heroImg = this.element.querySelector('.product-card-image--hero');
    if (heroImg) {
      heroImg.addEventListener('error', () => {
        if (heroImg.dataset.fallbackDone) return;
        const fallback = heroImg.dataset.fallback;
        if (fallback && heroImg.src !== fallback) {
          heroImg.dataset.fallbackDone = '1';
          heroImg.src = fallback;
        }
      });
    }

    const compareBtn = this.element.querySelector('.btn-icon-compare');
    if (compareBtn) {
      compareBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (!window.compareManager) return;
        const pid = compareBtn.dataset.productId;
        const vid = compareBtn.dataset.variantId;
        const result = window.compareManager.toggle(pid, vid);
        if (!result.success && result.message) {
          const toast = document.createElement('div');
          toast.className = 'compare-toast';
          toast.textContent = result.message;
          document.body.appendChild(toast);
          requestAnimationFrame(() => toast.classList.add('show'));
          setTimeout(() => toast.remove(), 2500);
        }
      });
    }
    this.element.addEventListener('click', (e) => {
      if (e.target.closest('button') || e.target.closest('a')) return;
      window.location.href = productUrl(this.product.slug);
    });
    this.element.style.cursor = 'pointer';
  }
}
