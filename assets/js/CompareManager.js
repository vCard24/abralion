class CompareManager {
  constructor() {
    this.storageKey = 'abralion_compare_list';
    this.maxItems = 4;
    this.SEP = '::';
    this.compareList = [];
    this.loadFromStorage();
    this.ensureBar();
    this.updateUI();
    window.addEventListener('compareListUpdated', () => this.syncCheckboxes());
  }

  static makeKey(productId, variantId) {
    return `${productId}::${variantId}`;
  }

  parseKey(key) {
    if (!key || typeof key !== 'string') return null;
    if (key.includes(this.SEP)) {
      const [productId, variantId] = key.split(this.SEP);
      return { productId, variantId, key };
    }
    return { productId: key, variantId: key, key };
  }

  loadFromStorage() {
    try {
      const stored = localStorage.getItem(this.storageKey);
      let list = stored ? JSON.parse(stored) : [];
      if (!Array.isArray(list)) list = [];
      this.compareList = list.filter((k) => typeof k === 'string' && k.length > 0);
    } catch {
      this.compareList = [];
    }
  }

  saveToStorage() {
    localStorage.setItem(this.storageKey, JSON.stringify(this.compareList));
  }

  getCompareList() {
    return [...this.compareList];
  }

  getCount() {
    return this.compareList.length;
  }

  isFull() {
    return this.compareList.length >= this.maxItems;
  }

  makeKey(productId, variantId) {
    const vid = variantId || productId;
    return CompareManager.makeKey(productId, vid);
  }

  isInList(productId, variantId) {
    return this.compareList.includes(this.makeKey(productId, variantId));
  }

  add(productId, variantId) {
    const key = this.makeKey(productId, variantId);
    if (this.compareList.includes(key)) {
      return { success: false, message: 'Bu model zaten listede.' };
    }
    if (this.isFull()) {
      return { success: false, message: `En fazla ${this.maxItems} model karşılaştırabilirsiniz.` };
    }
    this.compareList.push(key);
    this.saveToStorage();
    this.updateUI();
    return { success: true, message: 'Karşılaştırma listesine eklendi.', key };
  }

  remove(keyOrProductId, variantId) {
    const key = variantId
      ? this.makeKey(keyOrProductId, variantId)
      : this.compareList.includes(keyOrProductId)
        ? keyOrProductId
        : this.makeKey(keyOrProductId, keyOrProductId);
    const index = this.compareList.indexOf(key);
    if (index === -1) return { success: false, message: 'Listede bulunamadı.' };
    this.compareList.splice(index, 1);
    this.saveToStorage();
    this.updateUI();
    return { success: true, message: 'Listeden çıkarıldı.', key };
  }

  toggle(productId, variantId) {
    if (this.isInList(productId, variantId)) {
      return this.remove(this.makeKey(productId, variantId));
    }
    return this.add(productId, variantId);
  }

  clearAll() {
    this.compareList = [];
    this.saveToStorage();
    this.updateUI();
  }

  /** Eski productId-only kayıtları çöz */
  resolveEntries(products) {
    return this.compareList.map((key) => {
      const parsed = this.parseKey(key);
      const product = products.find((p) => p.id === parsed.productId || p.slug === parsed.productId);
      if (!product) return { key, product: null, variant: null };
      let variant = product.variants?.find(
        (v) =>
          v.id === parsed.variantId ||
          v.urun_kodu === parsed.variantId ||
          String(v.id) === String(parsed.variantId)
      );
      if (!variant && product.variants?.length) {
        variant = product.variants[0];
      }
      return {
        key,
        product,
        variant: variant || { id: parsed.variantId, urun_kodu: parsed.variantId },
      };
    });
  }

  ensureBar() {
    if (document.getElementById('compare-bar')) return;
    const base = typeof getBasePath === 'function' ? getBasePath() : '';
    const bar = document.createElement('div');
    bar.id = 'compare-bar';
    bar.className = 'compare-bar';
    bar.setAttribute('aria-live', 'polite');
    bar.hidden = true;
    bar.innerHTML = `
      <div class="compare-bar-inner container">
        <span class="compare-bar-text"><strong class="compare-bar-count">0</strong> model seçildi</span>
        <div class="compare-bar-actions">
          <a href="${base}karsilastir.html" class="btn btn-primary btn-small">Karşılaştır</a>
          <button type="button" class="btn btn-secondary btn-small" id="compare-bar-clear">Temizle</button>
        </div>
      </div>`;
    document.body.appendChild(bar);
    document.getElementById('compare-bar-clear')?.addEventListener('click', () => this.clearAll());
  }

  updateUI() {
    const count = this.getCount();
    document.querySelectorAll('.compare-badge').forEach((badge) => {
      badge.textContent = count;
      badge.style.display = count > 0 ? 'inline-block' : 'none';
    });
    const bar = document.getElementById('compare-bar');
    if (bar) {
      bar.hidden = count === 0;
      const countEl = bar.querySelector('.compare-bar-count');
      if (countEl) countEl.textContent = count;
    }
    document.body.classList.toggle('has-compare-bar', count > 0);
    this.syncCheckboxes();
    window.dispatchEvent(
      new CustomEvent('compareListUpdated', { detail: { count, items: this.getCompareList() } })
    );
  }

  syncCheckboxes() {
    const full = this.isFull();
    document.querySelectorAll('.compare-row-input').forEach((input) => {
      const pid = input.dataset.productId;
      const vid = input.dataset.variantId;
      const inList = this.isInList(pid, vid);
      input.checked = inList;
      input.disabled = !inList && full;
      const row = input.closest('tr');
      if (row) row.classList.toggle('compare-row-active', inList);
    });
    document.querySelectorAll('.btn-icon-compare').forEach((btn) => {
      const pid = btn.dataset.productId;
      const vid = btn.dataset.variantId;
      const inList = pid && vid && this.isInList(pid, vid);
      btn.classList.toggle('in-compare', inList);
      btn.disabled = !inList && full;
      btn.setAttribute('aria-pressed', inList ? 'true' : 'false');
    });
  }
}

window.compareManager = new CompareManager();

// Geriye uyumluluk
CompareManager.prototype.addProduct = function (productId, variantId) {
  if (arguments.length === 1) {
    return this.add(productId, productId);
  }
  return this.add(productId, variantId);
};
CompareManager.prototype.removeProduct = function (a, b) {
  return this.remove(a, b);
};
CompareManager.prototype.isInCompareList = function (productId, variantId) {
  if (arguments.length === 1 && productId.includes('::')) {
    return this.compareList.includes(productId);
  }
  return this.isInList(productId, variantId);
};
