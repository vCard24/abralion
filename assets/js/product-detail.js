/** Ürün detay sayfası — katalogdan tam içerik + teknik tablo */
function escapeHtml(text) {
  const d = document.createElement('div');
  d.textContent = text;
  return d.innerHTML;
}

function fillList(ul, items) {
  if (!ul) return;
  ul.innerHTML = (items || [])
    .map((item) => `<li>${escapeHtml(item.replace(/^✓\s*/, ''))}</li>`)
    .join('');
}

function renderGallery(product, container) {
  const base = getBasePath();
  const images = (product.images && product.images.length)
    ? product.images
    : [{ src: 'assets/images/placeholder/gorsel.jpg', alt: product.name }];

  const slides = images
    .map(
      (img, i) => {
        const src = img.src.startsWith('assets') ? `${base}${img.src}` : img.src;
        return `<img src="${src}" alt="${escapeHtml(img.alt || product.name)}" class="slider-image${i === 0 ? ' active' : ''}">`;
      }
    )
    .join('');

  const thumbs = images
    .map(
      (img, i) => {
        const src = img.src.startsWith('assets') ? `${base}${img.src}` : img.src;
        return `<button type="button" class="gallery-thumb-btn${i === 0 ? ' active' : ''}" aria-label="Görsel ${i + 1}" aria-selected="${i === 0 ? 'true' : 'false'}" data-index="${i}">
          <img src="${src}" alt="" class="gallery-thumb${i === 0 ? ' active' : ''}">
        </button>`;
      }
    )
    .join('');

  container.innerHTML = `
    <div class="product-gallery-main">
      <div class="product-image-slider gallery-main">
        <button type="button" class="slider-btn prev" aria-label="Önceki görsel">‹</button>
        <div class="slider-container">${slides}</div>
        <button type="button" class="slider-btn next" aria-label="Sonraki görsel">›</button>
      </div>
    </div>
    <div class="gallery-thumbs" role="tablist" aria-label="Ürün görselleri">${thumbs}</div>`;

  initProductGallery();
}

function renderBreadcrumb(product) {
  const base = getBasePath();
  const ol = document.getElementById('product-breadcrumb');
  if (!ol) return;
  ol.innerHTML = `
    <li><a href="${base}index.html">Ana Sayfa</a></li>
    <li><a href="${base}urunler.html">Ürünler</a></li>
    <li><a href="${base}urunler.html?kategori=${encodeURIComponent(product.categoryId)}">${escapeHtml(product.categoryName)}</a></li>
    <li aria-current="page">${escapeHtml(product.name)}</li>`;
}

function renderVariantTable(product, tableWrap) {
    const columns = getTableColumns(product);
    if (!columns.length) {
      tableWrap.innerHTML =
        '<p class="no-products-message">Bu ürün için tablo yapılandırması bulunamadı.</p>';
      return;
    }
    const headers = columns.map((c) => c.label);

  let thead =
    '<thead><tr><th class="compare-col" scope="col"><span class="sr-only">Karşılaştır</span></th>';
  thead += headers.map((h) => `<th scope="col">${h}</th>`).join('');
  thead += '</tr></thead>';

  let tbody = '<tbody>';
  (product.variants || []).forEach((variant, index) => {
    const vid = variant.urun_kodu || variant.id || `v${index + 1}`;
    const cells = variantRowCells(variant, columns);
    const label = variantLabel(variant, product.name).replace(/"/g, '&quot;');
    tbody += `<tr data-variant-id="${vid}">`;
    tbody += `<td class="compare-cell">
      <label class="compare-check" title="Karşılaştırmaya ekle">
        <input type="checkbox" class="compare-row-input"
          data-product-id="${product.id}"
          data-variant-id="${vid}"
          aria-label="${label} karşılaştır">
        <span class="compare-check-box" aria-hidden="true"></span>
      </label>
    </td>`;
    cells.forEach((cell) => {
      tbody += `<td>${cell}</td>`;
    });
    tbody += '</tr>';
  });
  tbody += '</tbody>';

  if (!(product.variants || []).length) {
    tableWrap.innerHTML =
      '<p class="no-products-message">Bu ürün için varyant verisi bulunamadı.</p>';
    return;
  }

  tableWrap.innerHTML = `<table class="specs-table">${thead}${tbody}</table>`;

  tableWrap.querySelectorAll('.compare-row-input').forEach((input) => {
    input.addEventListener('change', () => {
      const result = window.compareManager.toggle(
        input.dataset.productId,
        input.dataset.variantId
      );
      if (!result.success && input.checked) {
        input.checked = false;
        if (result.message) {
          const toast = document.createElement('div');
          toast.className = 'compare-toast';
          toast.textContent = result.message;
          document.body.appendChild(toast);
          requestAnimationFrame(() => toast.classList.add('show'));
          setTimeout(() => toast.remove(), 2500);
        }
      }
    });
  });

  window.compareManager?.syncCheckboxes();
}

function renderProductPage(product) {
  document.title = `${product.name} - Abralion`;

  const metaDesc = document.querySelector('meta[name="description"]');
  if (metaDesc && product.description) {
    metaDesc.setAttribute('content', product.description.slice(0, 160));
  }

  renderBreadcrumb(product);

  const catEl = document.getElementById('product-category');
  const titleEl = document.getElementById('product-title');
  const descEl = document.getElementById('product-description');
  if (catEl) catEl.textContent = product.categoryName || '';
  if (titleEl) titleEl.textContent = product.name || '';
  if (descEl) descEl.textContent = product.description || '';

  fillList(
    document.querySelector('#product-features-short ul'),
    product.features
  );
  fillList(
    document.querySelector('#product-features-detailed ul'),
    product.features
  );
  fillList(
    document.querySelector('#product-applications ul'),
    product.applications
  );

  const gallery = document.getElementById('product-gallery');
  if (gallery) renderGallery(product, gallery);

  const tableWrap = document.getElementById('variant-specs-table');
  if (tableWrap) renderVariantTable(product, tableWrap);
}

document.addEventListener('DOMContentLoaded', async () => {
  const productId = document.body.dataset.productId;
  if (!productId) return;

  const pm = new ProductManager();
  try {
    await pm.loadProducts();
    const product = pm.getProductById(productId);
    if (!product) {
      const main = document.querySelector('.product-detail .container');
      if (main) {
        main.innerHTML = `<p class="no-products-message">Ürün bulunamadı: ${escapeHtml(productId)}</p>`;
      }
      return;
    }
    renderProductPage(product);
  } catch (e) {
    console.error(e);
    const tableWrap = document.getElementById('variant-specs-table');
    if (tableWrap) {
      tableWrap.innerHTML = `<p class="no-products-message">${escapeHtml(e.message || 'Sayfa yüklenemedi.')}</p>`;
    }
  }
});
