document.addEventListener('DOMContentLoaded', async () => {
  const grid = document.getElementById('featured-products-grid');
  if (!grid) return;
  const pm = new ProductManager();
  try {
    await pm.loadProducts();
    const featured = pm.getFeaturedProducts().slice(0, 6);
    grid.innerHTML = '';
    featured.forEach((product) => {
      const card = new ProductCard(product);
      grid.appendChild(card.render());
    });
  } catch (e) {
    grid.innerHTML = `<p class="loading-message">${e.message || 'Ürünler yüklenemedi.'}</p>`;
  }
});
