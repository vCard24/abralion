document.addEventListener('DOMContentLoaded', async () => {
  const container = document.getElementById('compare-content');
  if (!container) return;

  const base = getBasePath();
  const maxSlots = window.compareManager?.maxItems || 4;
  const keys = window.compareManager.getCompareList();

  if (keys.length < 1) {
    container.innerHTML = `
      <div class="compare-empty text-center py-16 px-6 border border-steel-gray/20 rounded-lg bg-surface-elevation">
        <span class="material-symbols-outlined text-abrasive-red text-5xl mb-6 block" aria-hidden="true">compare_arrows</span>
        <p class="font-headline-md text-headline-md text-white mb-2">Karşılaştırma listeniz boş</p>
        <p class="compare-empty-hint font-body-md text-on-surface-variant max-w-md mx-auto mb-8">
          Ürün sayfasındaki teknik tabloda satır başındaki kutucuklarla model ekleyin veya ürünler sayfasından seçim yapın.
        </p>
        <a href="${base}urunler.html" class="inline-flex items-center justify-center gap-2 bg-abrasive-red text-white px-8 py-4 font-label-caps text-label-caps uppercase hover:brightness-110 transition-all">
          Ürünleri İncele
        </a>
      </div>`;
    return;
  }

  const pm = new ProductManager();
  await pm.loadProducts();
  const entries = window.compareManager.resolveEntries(pm.getAllProducts()).filter((e) => e.product);

  if (!entries.length) {
    container.innerHTML = '<p class="text-center font-body-md text-on-surface-variant py-12">Liste yüklenemedi.</p>';
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
    <p class="compare-summary font-label-caps text-label-caps text-steel-gray uppercase tracking-widest text-center mb-4">
      ${entries.length} / ${maxSlots} model karşılaştırılıyor
    </p>`;

  if (mixedGroups) {
    html += `<p class="compare-mixed-notice font-body-md text-body-md" role="status">
      Farklı ürün grupları birlikte listeleniyor. Ortak ve gruba özel satırlar aynı tabloda gösterilir; ilgili olmayan hücreler boş bırakılır.
    </p>`;
  }

  html += `<div class="compare-table-wrapper overflow-x-auto border border-steel-gray/20 rounded-lg">
    <table class="compare-table compare-matrix w-full text-left border-collapse min-w-[1000px]">
      <thead>
        <tr class="bg-surface-container-low">
          <th class="compare-label-col p-6 border-b border-r border-steel-gray/20 w-1/5" scope="col">
            <h3 class="font-headline-md text-headline-md text-white m-0">Teknik Özellikler</h3>
          </th>`;

  slots.forEach((col) => {
    if (col) {
      const { key, product, variant } = col;
      const img = (product.images?.[0]?.src || 'assets/images/placeholder/gorsel.jpg').replace(/^\//, '');
      const imgSrc = img.startsWith('assets') ? `${base}${img}` : img;
      const sku = variant.urun_kodu || variant.id || '';
      const quoteHref = `${base}iletisim.html?konu=${encodeURIComponent(product.name)}`;
      html += `<th class="compare-product-col p-6 border-b border-r border-steel-gray/20" scope="col">
        <div class="compare-product-header flex flex-col items-center gap-4 relative">
          <button type="button" class="compare-matrix-remove compare-remove-btn" data-key="${escapeHtml(key)}" aria-label="Kaldır">
            <span class="material-symbols-outlined text-lg" aria-hidden="true">close</span>
          </button>
          <img src="${escapeHtml(imgSrc)}" alt="" class="h-28 object-contain" loading="lazy">
          <p class="product-category font-label-caps text-[10px] uppercase text-abrasive-red m-0">${escapeHtml(product.categoryName)}</p>
          <h3 class="font-headline-md text-[18px] text-center text-white m-0">${escapeHtml(product.name)}</h3>
          <p class="compare-matrix-sku font-technical-data text-technical-data text-steel-gray m-0">${escapeHtml(String(sku))}</p>
          <div class="compare-matrix-actions w-full flex flex-col gap-3 mt-2">
            <a href="${quoteHref}" class="compare-btn-quote bg-abrasive-red text-white py-3 font-label-caps text-label-caps uppercase hover:brightness-110 transition-all w-full text-center">Teklif Listesine Ekle</a>
            <a href="${productUrl(product.slug)}" class="compare-btn-detail text-center font-label-caps text-label-caps uppercase text-on-surface-variant hover:text-white transition-colors">Detayları İncele →</a>
          </div>
        </div>
      </th>`;
    } else {
      html += `<th class="compare-product-col compare-slot-empty p-6 border-b border-r border-steel-gray/20" scope="col">
        <div class="compare-slot-add flex flex-col items-center justify-center gap-4 min-h-[280px]">
          <span class="compare-slot-icon material-symbols-outlined text-4xl text-steel-gray/50" aria-hidden="true">add</span>
          <p class="font-label-caps text-label-caps uppercase text-steel-gray m-0">Model ekle</p>
          <a href="${base}urunler.html" class="font-label-caps text-label-caps uppercase text-on-surface-variant hover:text-abrasive-red transition-colors">Ürünleri incele →</a>
        </div>
      </th>`;
    }
  });

  html += '</tr></thead><tbody class="font-technical-data text-technical-data">';

  let rowIndex = 0;
  allSpecKeys.forEach((label, specKey) => {
    const rowClass = rowIndex % 2 === 0 ? 'compare-row-dim' : 'compare-row-low';
    html += `<tr class="${rowClass} hover:bg-surface-container-high transition-colors">
      <th class="compare-label-col p-6 border-b border-r border-steel-gray/10 text-on-surface-variant font-label-caps uppercase" scope="row">${escapeHtml(label)}</th>`;
    slots.forEach((col) => {
      if (!col) {
        html += '<td class="compare-value-col compare-slot-empty-cell p-6 border-b border-r border-steel-gray/10 text-center text-steel-gray">—</td>';
        return;
      }
      const val = col.lineMap[specKey];
      const text = val && val !== '—' ? val : '—';
      html += `<td class="compare-value-col p-6 border-b border-r border-steel-gray/10 text-center text-on-surface">${escapeHtml(text)}</td>`;
    });
    html += '</tr>';
    rowIndex += 1;
  });

  html += `</tbody></table></div>
    <p class="text-center compare-actions-footer mt-10">
      <button type="button" class="compare-btn-clear border border-steel-gray/30 text-on-surface px-8 py-3 font-label-caps text-label-caps uppercase hover:border-abrasive-red hover:text-abrasive-red transition-all" id="clear-compare">Tümünü temizle</button>
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
