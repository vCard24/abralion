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
      this.quoteList = list
        .filter((k) => typeof k === 'string' && k.length > 0)
        .slice(0, this.maxItems);
    } catch {
      this.quoteList = [];
    }
  }

  saveToStorage() {
    localStorage.setItem(this.storageKey, JSON.stringify(this.quoteList));
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
      return { success: false, message: 'Bu model zaten teklif listesinde.' };
    }
    if (this.isFull()) {
      return {
        success: false,
        message: `En fazla ${this.maxItems} ürün için teklif isteyebilirsiniz.`,
      };
    }
    this.quoteList.push(key);
    this.saveToStorage();
    this.updateUI();
    return { success: true, message: 'Teklif listesine eklendi.', key };
  }

  remove(keyOrProductId, variantId) {
    const key = variantId
      ? this.makeKey(keyOrProductId, variantId)
      : this.quoteList.includes(keyOrProductId)
        ? keyOrProductId
        : this.makeKey(keyOrProductId, keyOrProductId);
    const index = this.quoteList.indexOf(key);
    if (index === -1) return { success: false, message: 'Listede bulunamadı.' };
    this.quoteList.splice(index, 1);
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

  setList(keys) {
    if (!Array.isArray(keys)) return;
    this.quoteList = keys
      .filter((k) => typeof k === 'string' && k.length > 0)
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
    return this.quoteList.map((key) => {
      const parsed = this.parseKey(key);
      const product = products.find(
        (p) => p.id === parsed.productId || p.slug === parsed.productId
      );
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

  updateUI() {
    window.dispatchEvent(
      new CustomEvent('quoteListUpdated', {
        detail: { count: this.getCount(), items: this.getQuoteList() },
      })
    );
  }
}

window.quoteManager = new QuoteManager();
