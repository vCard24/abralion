/* exported ProductManager */
class ProductManager {
  constructor(dataPath) {
    const base = typeof getBasePath === 'function' ? getBasePath() : '';
    const relative =
      typeof getCatalogDataPath === 'function'
        ? getCatalogDataPath()
        : document.documentElement.lang?.toLowerCase().startsWith('ru')
          ? 'data/products-ru.json'
          : 'data/products.json';
    this.dataPath = dataPath || this.resolvePath(`${base}${relative}`);
    this.products = [];
    this.categories = [];
    this.isLoaded = false;
  }

  resolvePath(relative) {
    try {
      return new URL(relative, window.location.href).href;
    } catch {
      return relative;
    }
  }

  async loadProducts() {
    if (window.ABRALION_CATALOG?.products) {
      this.applyData(window.ABRALION_CATALOG);
      return this.products;
    }

    try {
      const response = await fetch(this.dataPath);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      this.applyData(data);
      return this.products;
    } catch (fetchError) {
      if (window.ABRALION_CATALOG) {
        this.applyData(window.ABRALION_CATALOG);
        return this.products;
      }
      console.error('catalog load failed:', fetchError);
      throw new Error(
        typeof t === 'function' ? t('quote.catalog.loadError') : 'quote.catalog.loadError'
      );
    }
  }

  applyData(data) {
    this.products = data.products || [];
    this.categories = data.categories || [];
    this.isLoaded = true;
  }

  filterByCategory(categoryIdOrName) {
    if (!categoryIdOrName || categoryIdOrName === 'all') return this.products;
    return this.products.filter(
      (p) => p.categoryId === categoryIdOrName || p.categoryName === categoryIdOrName
    );
  }

  search(query) {
    if (!query || !query.trim()) return this.products;
    const term = query.toLowerCase().trim();
    return this.products.filter((p) => {
      const hay = [p.name, p.description, p.categoryName, ...(p.features || [])]
        .join(' ')
        .toLowerCase();
      return hay.includes(term);
    });
  }

  getProductById(id) {
    return this.products.find((p) => p.id === id || p.slug === id) || null;
  }

  getFeaturedProducts() {
    return this.products.filter((p) => p.featured);
  }

  getAllProducts() {
    return this.products;
  }
}
