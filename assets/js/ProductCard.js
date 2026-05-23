class ProductCard {
  constructor(product, options = {}) {
    this.product = product;
    this.noir = Boolean(options.noir);
    this.compact = Boolean(options.compact);
    this.element = null;
  }

  render() {
    this.element = this.noir ? this.createNoirCardElement() : this.createCardElement();
    this.attachEventListeners();
    return this.element;
  }

  static kartImageSrc(base, slug) {
    const jpg = `${base}assets/images/products/${slug}/${slug}-kart.jpg`;
    const png = `${base}assets/images/products/${slug}/${slug}-kart.png`;
    return slug === 'metal-inox-kesme-tasi' ? png : jpg;
  }

  static formatTechnicalSpec(product) {
    const v = product.variants?.[0];
    if (!v) return product.categoryName || '';

    if (v.daire_capi_mm != null && v.kalinlik_mm != null) {
      const dim = `Ø${v.daire_capi_mm} × ${v.kalinlik_mm} mm`;
      const rpm = v.max_hiz_rpm ? ` · ${v.max_hiz_rpm} RPM` : '';
      return dim + rpm;
    }

    if (v.daire_capi_mm != null && v.grit) {
      const grit = v.grit;
      const rpm = v.max_hiz_rpm ? ` · ${v.max_hiz_rpm} RPM` : '';
      return `Ø${v.daire_capi_mm} mm · ${grit}${rpm}`;
    }

    if (v.daire_capi_mm != null && v.max_hiz_rpm) {
      return `Ø${v.daire_capi_mm} mm · ${v.max_hiz_rpm} RPM`;
    }

    return v.urun_kodu || product.categoryName || '';
  }

  /** Stitch katalog kartı — örn. 115mm x 1.0mm */
  static formatTechnicalSpecLabel(product) {
    const variants = product.variants || [];
    const v = variants[0];
    if (!v) return product.categoryName || '';

    if (v.daire_capi_mm != null && v.kalinlik_mm != null) {
      return `${v.daire_capi_mm}mm x ${v.kalinlik_mm}mm`;
    }

    if (v.daire_capi_mm != null && v.grit) {
      const caps = variants.map((x) => x.daire_capi_mm).filter((n) => n != null);
      const grits = [...new Set(variants.map((x) => x.grit).filter(Boolean))];
      if (caps.length > 1) {
        const min = Math.min(...caps);
        const max = Math.max(...caps);
        return grits.length ? `${min}mm - ${max}mm · ${grits[0]}` : `${min}mm - ${max}mm`;
      }
      return grits.length ? `${v.daire_capi_mm}mm · ${grits[0]}` : `${v.daire_capi_mm}mm`;
    }

    if (v.daire_capi_mm != null) {
      const caps = variants.map((x) => x.daire_capi_mm).filter((n) => n != null);
      if (caps.length > 1) {
        const min = Math.min(...caps);
        const max = Math.max(...caps);
        return min === max ? `${min}mm` : `${min}mm - ${max}mm`;
      }
      return `${v.daire_capi_mm}mm`;
    }

    if (v.cap_mm != null) {
      return `${v.cap_mm}mm`;
    }

    return v.urun_kodu || product.categoryName || '';
  }

  static truncateDescription(text, max = 120) {
    const t = text || '';
    return t.length > max ? `${t.slice(0, max)}…` : t;
  }

  static categoryTags(product) {
    const tags = [];
    const name = (product.name || '').toLowerCase();

    if (name.includes('inox')) tags.push('INOX');
    if (name.includes('metal') || product.categoryId === 'kesici-taslama-flap-disk') {
      if (!tags.includes('METAL')) tags.push('METAL');
    }
    if (product.categoryId === 'elmas-kesici') tags.push('ELMAS');
    if (product.categoryId === 'uclar') tags.push('ENDÜSTRİYEL');

    if (!tags.length && product.categoryName) {
      const short = product.categoryName.split(/[-–&]/)[0].trim().toUpperCase();
      if (short) tags.push(short.slice(0, 14));
    }

    return tags.slice(0, 2);
  }

  static renderCategoryTags(product) {
    return ProductCard.categoryTags(product)
      .map(
        (tag) =>
          `<span class="text-[10px] text-steel-gray font-technical-data tracking-widest uppercase">${tag}</span>`
      )
      .join('');
  }

  static detailIconSvg() {
    return `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="M12 5l7 7-7 7"/></svg>`;
  }

  createNoirCardElement() {
    const base = getBasePath();
    const p = this.product;
    const url = productUrl(p.slug);
    const kartSrc = ProductCard.kartImageSrc(base, p.slug);
    const fallback = `${base}assets/images/products/${p.slug}/${p.slug}-kart.png`;
    const spec = ProductCard.formatTechnicalSpec(p);
    const name = p.name.replace(/"/g, '&quot;');

    const card = document.createElement('article');
    card.className =
      'product-card product-card--noir group flex flex-col overflow-hidden rounded-lg border border-steel-gray/20 bg-surface-elevation transition-colors duration-300 hover:border-abrasive-red/50';
    card.setAttribute('data-product-id', p.id);
    if (p.categoryId) card.setAttribute('data-category-id', p.categoryId);

    card.innerHTML = `
      <a href="${url}" class="product-card-media block aspect-[4/3] overflow-hidden bg-carbon-black p-4">
        <img class="product-card-image mx-auto max-h-full w-full object-contain transition-transform duration-500 group-hover:scale-105"
          src="${kartSrc}" alt="${name}" loading="lazy" width="400" height="300"
          data-fallback="${fallback}">
      </a>
      <div class="product-card-content flex flex-1 flex-col gap-3 p-5">
        <h3 class="product-card-title font-headline-md text-headline-md leading-snug">
          <a href="${url}" class="text-white transition-colors hover:text-abrasive-red">${p.name}</a>
        </h3>
        <div class="product-card-footer mt-auto flex items-end justify-between gap-3 border-t border-steel-gray/20 pt-4">
          <p class="product-card-spec font-technical-data text-technical-data uppercase text-steel-gray">${spec}</p>
          <a href="${url}" class="product-card-detail flex h-10 w-10 shrink-0 items-center justify-center rounded text-abrasive-red transition-colors hover:bg-abrasive-red/10" aria-label="${name} detayları">${ProductCard.detailIconSvg()}</a>
        </div>
      </div>
    `;
    return card;
  }

  createCardElement() {
    const base = getBasePath();
    const p = this.product;
    const firstVar = p.variants?.[0];
    const variantId = firstVar ? (firstVar.urun_kodu || firstVar.id) : p.id;
    const kartSrc = ProductCard.kartImageSrc(base, p.slug);
    const fallback = `${base}assets/images/products/${p.slug}/${p.slug}-kart.png`;
    const url = productUrl(p.slug);
    const spec = ProductCard.formatTechnicalSpecLabel(p);
    const name = p.name.replace(/"/g, '&quot;');
    const description = ProductCard.truncateDescription(p.description);
    const categoryLabel = (p.categoryName || '').replace(/"/g, '&quot;');
    const tagsHtml = ProductCard.renderCategoryTags(p);
    const featuredBadge = p.featured
      ? `<div class="absolute top-0 right-0 p-3">
          <span class="bg-abrasive-red/10 text-abrasive-red text-[10px] font-bold px-2 py-0.5 border border-abrasive-red/20">NEW</span>
        </div>`
      : '';

    const descriptionHtml = this.compact
      ? ''
      : `<p class="product-card-description text-technical-data text-on-surface-variant line-clamp-2 mb-6 opacity-70">${description}</p>`;

    const actionsHtml = this.compact
      ? ''
      : `<div class="product-card-actions flex items-center justify-between pt-6 border-t border-steel-gray/10">
          <span class="product-card-spec font-technical-data text-abrasive-red">${spec}</span>
          <div class="flex items-center gap-3 shrink-0">
            <button type="button" class="btn-icon-compare flex h-10 w-10 items-center justify-center rounded text-steel-gray transition-colors hover:bg-surface-container-high hover:text-abrasive-red"
              title="İlk modeli karşılaştırmaya ekle"
              data-product-id="${p.id}" data-variant-id="${variantId}" aria-label="Karşılaştır">
              <span class="material-symbols-outlined text-[20px]" data-icon="compare_arrows">compare_arrows</span>
            </button>
            <a href="${url}" class="product-card-detail flex items-center gap-2 font-label-caps group/btn transition-all text-on-surface hover:text-abrasive-red"
              data-product-id="${p.id}" aria-label="${name} detayları">
              DETAYLAR
              <span class="material-symbols-outlined text-[18px] group-hover/btn:translate-x-1 transition-transform" data-icon="arrow_forward">arrow_forward</span>
            </a>
          </div>
        </div>`;

    const card = document.createElement('div');
    card.className =
      'product-card group bg-surface-elevation technical-border p-6 flex flex-col transition-all duration-500 hover:border-abrasive-red/50' +
      (this.compact ? ' product-card--compact' : '');
    card.setAttribute('data-product-id', p.id);
    if (p.categoryId) card.setAttribute('data-category-id', p.categoryId);

    card.innerHTML = `
      <div class="relative overflow-hidden mb-6 aspect-[1.73] bg-carbon-black">
        <img class="product-card-image absolute inset-0 h-full w-full object-cover transform group-hover:scale-110 transition-transform duration-700"
          src="${kartSrc}" alt="${name}" loading="lazy" width="400" height="300"
          data-fallback="${fallback}">
        ${featuredBadge}
      </div>
      <div class="mt-auto">
        <div class="flex gap-2 mb-3 product-card-tags">
          ${tagsHtml || `<span class="text-[10px] text-steel-gray font-technical-data tracking-widest uppercase product-card-category">${categoryLabel}</span>`}
        </div>
        <h3 class="product-card-title font-headline-md text-[20px] ${this.compact ? '' : 'mb-3 '}group-hover:text-abrasive-red transition-colors">${p.name}</h3>
        ${descriptionHtml}
        ${actionsHtml}
      </div>
    `;
    return card;
  }

  attachEventListeners() {
    const img = this.element.querySelector('.product-card-image');
    if (img) {
      img.addEventListener('error', () => {
        if (img.dataset.fallbackDone) return;
        const fallback = img.dataset.fallback;
        if (fallback && img.src !== fallback) {
          img.dataset.fallbackDone = '1';
          img.src = fallback;
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

    if (!this.noir) {
      this.element.addEventListener('click', (e) => {
        if (e.target.closest('button') || e.target.closest('a')) return;
        window.location.href = productUrl(this.product.slug);
      });
      this.element.style.cursor = 'pointer';
    }
  }
}
