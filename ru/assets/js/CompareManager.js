/* exported CompareManager */
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
    const sep = key.indexOf(this.SEP);
    if (sep !== -1) {
      return {
        productId: key.slice(0, sep),
        variantId: key.slice(sep + this.SEP.length),
        key,
      };
    }
    return { productId: key, variantId: key, key };
  }

  loadFromStorage() {
    try {
      const stored = localStorage.getItem(this.storageKey);
      let list = stored ? JSON.parse(stored) : [];
      if (!Array.isArray(list)) list = [];
      const seen = new Set();
      this.compareList = list
        .filter((k) => typeof k === 'string' && k.length > 0)
        .filter((k) => {
          if (seen.has(k)) return false;
          seen.add(k);
          return true;
        })
        .slice(0, this.maxItems);
    } catch {
      this.compareList = [];
    }
  }

  saveToStorage() {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.compareList));
      return true;
    } catch {
      const msg =
        typeof t === 'function' ? t('storage.saveError') : 'storage.saveError';
      if (typeof window.showToast === 'function') window.showToast(msg, 'error');
      else console.warn(msg);
      return false;
    }
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
      return { success: false, message: t('compare.alreadyAdded') };
    }
    if (this.isFull()) {
      return {
        success: false,
        message: t('compare.limit', { max: this.maxItems }),
      };
    }
    this.compareList.push(key);
    if (!this.saveToStorage()) {
      this.compareList.pop();
      return { success: false, message: t('storage.saveError') };
    }
    this.updateUI();
    return { success: true, message: t('compare.added'), key };
  }

  remove(keyOrProductId, variantId) {
    const key = variantId
      ? this.makeKey(keyOrProductId, variantId)
      : this.compareList.includes(keyOrProductId)
        ? keyOrProductId
        : this.makeKey(keyOrProductId, keyOrProductId);
    const index = this.compareList.indexOf(key);
    if (index === -1) return { success: false, message: t('compare.notFound') };
    this.compareList.splice(index, 1);
    this.saveToStorage();
    this.updateUI();
    return { success: true, message: t('compare.removed'), key };
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

  /** Resolve keys against catalog; drop unknown variants (no silent first-variant fallback). */
  resolveEntries(products) {
    const resolved = [];
    const keepKeys = [];
    this.compareList.forEach((key) => {
      const parsed = this.parseKey(key);
      const product = products.find(
        (p) => p.id === parsed.productId || p.slug === parsed.productId
      );
      if (!product) return;
      const variant = product.variants?.find(
        (v) =>
          v.id === parsed.variantId ||
          v.urun_kodu === parsed.variantId ||
          String(v.id) === String(parsed.variantId)
      );
      if (!variant) return;
      const canonicalKey = this.makeKey(product.id, variant.id);
      keepKeys.push(canonicalKey);
      resolved.push({ key: canonicalKey, product, variant });
    });
    const next = [...new Set(keepKeys)].slice(0, this.maxItems);
    if (
      next.length !== this.compareList.length ||
      next.some((k, i) => k !== this.compareList[i])
    ) {
      this.compareList = next;
      this.saveToStorage();
      this.updateUI();
    }
    return resolved;
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
        <span class="compare-bar-text">${t('compare.selectedCount', { count: '<strong class="compare-bar-count">0</strong>' })}</span>
        <div class="compare-bar-actions">
          <a href="${base}sravnenie.html" class="btn btn-primary btn-small">${t('compare.open')}</a>
          <a href="${base}zapros-tseny.html?from=compare" class="btn btn-primary btn-small compare-bar-quote" id="compare-bar-quote">${t('quote.open')}</a>
          <button type="button" class="btn btn-secondary btn-small" id="compare-bar-clear">${t('common.clear')}</button>
        </div>
      </div>`;
    document.body.appendChild(bar);
    document.getElementById('compare-bar-clear')?.addEventListener('click', () => this.clearAll());
    document.getElementById('compare-bar-quote')?.addEventListener('click', (e) => {
      e.preventDefault();
      const keys = this.getCompareList();
      const b = typeof getBasePath === 'function' ? getBasePath() : '';
      if (typeof navigateToQuotePage === 'function') {
        navigateToQuotePage(keys, b);
      } else {
        window.location.href = `${b}zapros-tseny.html?from=compare`;
      }
    });
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
      const vid = btn.dataset.variantId || pid;
      const inList = Boolean(pid) && this.isInList(pid, vid);
      btn.classList.toggle('in-compare', inList);
      btn.disabled = !inList && full;
      btn.setAttribute('aria-pressed', inList ? 'true' : 'false');
    });
  }
}

window.compareManager = new CompareManager();

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
