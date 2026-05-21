document.addEventListener('DOMContentLoaded', async () => {
  const grid = document.getElementById('products-grid');
  const countEl = document.getElementById('products-count');
  const pm = new ProductManager();
  const params = new URLSearchParams(window.location.search);
  const kategori = params.get('kategori');
  const search = params.get('search');
  const urun = params.get('urun');
  if (urun) {
    window.location.replace(productUrl(urun));
    return;
  }

  try {
    await pm.loadProducts();
    let list = pm.getAllProducts();
    if (kategori) list = pm.filterByCategory(kategori);
    if (search) list = pm.search(search);

    if (countEl) countEl.textContent = `${list.length} ürün`;
    grid.innerHTML = '';
    if (!list.length) {
      grid.innerHTML = '<p class="no-products-message">Ürün bulunamadı.</p>';
      return;
    }
    list.forEach((product) => {
      grid.appendChild(new ProductCard(product).render());
    });

    document.querySelectorAll('.category-btn').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.category === (kategori || 'all'));
    });
  } catch (e) {
    grid.innerHTML = `<p class="no-products-message">${e.message || 'Ürünler yüklenemedi.'}</p>`;
  }
});

function filterCategory(cat) {
  const base = getBasePath();
  if (!cat || cat === 'all') {
    window.location.href = `${base}urunler.html`;
  } else {
    window.location.href = `${base}urunler.html?kategori=${encodeURIComponent(cat)}`;
  }
}
