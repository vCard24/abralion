/* exported QuoteManager */
class QuoteManager {
  constructor() {
    this.storageKey = 'abralion_quote_list';
    this.maxItems = 4;
    this.SEP = '::';
    this.quoteList = [];
    this.loadFromStorage();
  }

  static makeKey(productId, variantId) {
    const vid = variantId || productId;
    return `${productId}::${vid}`;
  }

  loadFromStorage() {
    try {
      const stored = localStorage.getItem(this.storageKey);
      let list = stored ? JSON.parse(stored) : [];
      if (!Array.isArray(list)) list = [];
      const seen = new Set();
      this.quoteList = list
        .filter((k) => typeof k === 'string' && k.length > 0)
        .filter((k) => {
          if (seen.has(k)) return false;
          seen.add(k);
          return true;
        })
        .slice(0, this.maxItems);
    } catch {
      this.quoteList = [];
    }
  }

  saveToStorage() {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.quoteList));
      return true;
    } catch {
      const msg =
        typeof t === 'function' ? t('storage.saveError') : 'storage.saveError';
      if (typeof window.showToast === 'function') window.showToast(msg, 'error');
      else console.warn(msg);
      return false;
    }
  }

  makeKey(productId, variantId) {
    return QuoteManager.makeKey(productId, variantId || productId);
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

  getQuoteList() {
    return [...this.quoteList];
  }

  getCount() {
    return this.quoteList.length;
  }

  isFull() {
    return this.quoteList.length >= this.maxItems;
  }

  isInList(productId, variantId) {
    return this.quoteList.includes(this.makeKey(productId, variantId));
  }

  add(productId, variantId) {
    const key = this.makeKey(productId, variantId);
    if (this.quoteList.includes(key)) {
      return { success: false, message: t('quote.alreadyAdded') };
    }
    if (this.isFull()) {
      return {
        success: false,
        message: t('quote.limit', { max: this.maxItems }),
      };
    }
    this.quoteList.push(key);
    if (!this.saveToStorage()) {
      this.quoteList.pop();
      return { success: false, message: t('storage.saveError') };
    }
    this.updateUI();
    return { success: true, message: t('quote.added'), key };
  }

  remove(keyOrProductId, variantId) {
    const key = variantId
      ? this.makeKey(keyOrProductId, variantId)
      : this.quoteList.includes(keyOrProductId)
        ? keyOrProductId
        : this.makeKey(keyOrProductId, keyOrProductId);
    const index = this.quoteList.indexOf(key);
    if (index === -1) return { success: false, message: t('quote.notFound') };
    this.quoteList.splice(index, 1);
    this.saveToStorage();
    this.updateUI();
    return { success: true, message: t('quote.removed'), key };
  }

  toggle(productId, variantId) {
    if (this.isInList(productId, variantId)) {
      return this.remove(this.makeKey(productId, variantId));
    }
    return this.add(productId, variantId);
  }

  setList(keys) {
    if (!Array.isArray(keys)) return;
    const seen = new Set();
    this.quoteList = keys
      .filter((k) => typeof k === 'string' && k.length > 0)
      .filter((k) => {
        if (seen.has(k)) return false;
        seen.add(k);
        return true;
      })
      .slice(0, this.maxItems);
    this.saveToStorage();
    this.updateUI();
  }

  importFromCompare(compareManager) {
    if (!compareManager?.getCompareList) return;
    this.setList(compareManager.getCompareList());
  }

  clearAll() {
    this.quoteList = [];
    this.saveToStorage();
    this.updateUI();
  }

  resolveEntries(products) {
    const resolved = [];
    const keepKeys = [];
    this.quoteList.forEach((key) => {
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
      next.length !== this.quoteList.length ||
      next.some((k, i) => k !== this.quoteList[i])
    ) {
      this.quoteList = next;
      this.saveToStorage();
      this.updateUI();
    }
    return resolved;
  }

  updateUI() {
    window.dispatchEvent(
      new CustomEvent('quoteListUpdated', {
        detail: { count: this.getCount(), items: this.getQuoteList() },
      })
    );
  }
}

window.quoteManager = new QuoteManager();
