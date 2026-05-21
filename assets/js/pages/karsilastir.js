document.addEventListener('DOMContentLoaded', async () => {
  const container = document.getElementById('compare-content');
  if (!container) return;

  const base = getBasePath();
  const maxSlots = window.compareManager?.maxItems || 4;
  const keys = window.compareManager.getCompareList();

  if (keys.length < 1) {
    container.innerHTML = `
      <div class="compare-empty text-center">
        <p>Karşılaştırma listeniz boş.</p>
        <p class="compare-empty-hint">Ürün sayfasındaki teknik tabloda satır başındaki kutucuklarla model ekleyin.</p>
        <a href="${base}urunler.html" class="btn btn-primary mt-md">Ürünleri İncele</a>
      </div>`;
    return;
  }

  const pm = new ProductManager();
  await pm.loadProducts();
  const entries = window.compareManager.resolveEntries(pm.getAllProducts()).filter((e) => e.product);

  if (!entries.length) {
    container.innerHTML = '<p class="text-center">Liste yüklenemedi.</p>';
    return;
  }

  const allSpecKeys = new Map();
  const columnData = entries.map(({ key, product, variant }) => {
    const lines = variantSpecLines(variant, product);
    lines.forEach((line) => {
      if (!allSpecKeys.has(line.key)) allSpecKeys.set(line.key, line.label);
    });
    return {
      key,
      product,
      variant,
      lineMap: Object.fromEntries(lines.map((l) => [l.key, l.value])),
    };
  });

  const slots = Array.from({ length: maxSlots }, (_, i) => columnData[i] || null);

  const categories = new Set(entries.map((e) => e.product.categoryId));
  const mixedGroups = categories.size > 1;

  let html = `<div class="compare-container">
    <p class="compare-summary">${entries.length} / ${maxSlots} model karşılaştırılıyor</p>`;

  if (mixedGroups) {
    html += `<p class="compare-mixed-notice" role="status">
      Farklı ürün grupları birlikte listeleniyor. Ortak ve gruba özel satırlar aynı tabloda gösterilir; ilgili olmayan hücreler boş bırakılır.
    </p>`;
  }

  html += '<div class="compare-table-wrapper"><table class="compare-table compare-matrix"><thead><tr>';
  html += '<th class="compare-label-col" scope="col">Özellik</th>';

  slots.forEach((col) => {
    if (col) {
      const { key, product, variant } = col;
      const img = (product.images?.[0]?.src || 'assets/images/placeholder/gorsel.jpg').replace(/^\//, '');
      const imgSrc = img.startsWith('assets') ? `${base}${img}` : img;
      const sku = variant.urun_kodu || variant.id || '';
      html += `<th class="compare-product-col" scope="col">
        <div class="compare-product-header">
          <button type="button" class="btn-remove compare-matrix-remove" data-key="${escapeHtml(key)}" aria-label="Kaldır">×</button>
          <img src="${escapeHtml(imgSrc)}" alt="">
          <p class="product-category">${escapeHtml(product.categoryName)}</p>
          <h3>${escapeHtml(product.name)}</h3>
          <p class="compare-matrix-sku">${escapeHtml(String(sku))}</p>
          <div class="compare-matrix-actions">
            <a href="${productUrl(product.slug)}" class="btn btn-secondary btn-small">Ürün sayfası</a>
            <a href="${base}iletisim.html" class="btn btn-primary btn-small">Fiyat teklifi</a>
          </div>
        </div>
      </th>`;
    } else {
      html += `<th class="compare-product-col compare-slot-empty" scope="col">
        <div class="compare-slot-add">
          <span class="compare-slot-icon" aria-hidden="true">+</span>
          <p>Model ekle</p>
          <a href="${base}urunler.html" class="btn btn-secondary btn-small">Ürünleri incele</a>
        </div>
      </th>`;
    }
  });

  html += '</tr></thead><tbody>';

  allSpecKeys.forEach((label, specKey) => {
    html += `<tr><th class="compare-label-col" scope="row">${escapeHtml(label)}</th>`;
    slots.forEach((col) => {
      if (!col) {
        html += '<td class="compare-value-col compare-slot-empty-cell"> - </td>';
        return;
      }
      const val = col.lineMap[specKey];
      const text = val && val !== '—' ? val : ' - ';
      html += `<td class="compare-value-col">${escapeHtml(text)}</td>`;
    });
    html += '</tr>';
  });

  html += `</tbody></table></div>
    <p class="text-center compare-actions-footer">
      <button type="button" class="btn btn-secondary" id="clear-compare">Tümünü temizle</button>
    </p>
  </div>`;

  container.innerHTML = html;

  container.querySelectorAll('.compare-matrix-remove').forEach((btn) => {
    btn.addEventListener('click', () => {
      window.compareManager.remove(btn.dataset.key);
      location.reload();
    });
  });
  document.getElementById('clear-compare')?.addEventListener('click', () => {
    window.compareManager.clearAll();
    location.reload();
  });
});

function escapeHtml(text) {
  const d = document.createElement('div');
  d.textContent = text == null ? '' : String(text);
  return d.innerHTML;
}
