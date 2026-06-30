function variantBadgeText(variant, product) {
  if (variant.uzunluk_mm != null && variant.uc_genisligi_mm != null) {
    return `${variant.saft_mm ?? ''}x${variant.uzunluk_mm}x${variant.uc_genisligi_mm} mm`.replace(/^x/, '');
  }
  if (variant.uzunluk_mm != null) {
    return `${variant.saft_mm ?? ''}x${variant.uzunluk_mm} mm`.replace(/^x/, '');
  }
  if (variant.daire_capi_mm != null) {
    return `Ø${variant.daire_capi_mm}${variant.kalinlik_mm != null ? ' x ' + variant.kalinlik_mm : ''} mm`;
  }
  if (variant.cap_mm != null) {
    return `${variant.cap_mm} mm`;
  }
  if (variant.urun_kodu) {
    return variant.urun_kodu;
  }
  return variant.id || '';
}

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
      const sku = variant.urun_kodu || '';
      const inQuote = window.quoteManager?.isInList(product.id, variant.id || variant.urun_kodu);
      const quoteBtnClass = inQuote
        ? 'compare-btn-quote border border-abrasive-red text-abrasive-red bg-transparent'
        : 'compare-btn-quote bg-abrasive-red text-white';
      const quoteBtnLabel = inQuote ? 'Teklif Listesinde ✓' : 'Teklif Listesine Ekle';
      html += `<th class="compare-product-col p-6 border-b border-r border-steel-gray/20" scope="col">
        <div class="compare-product-header flex flex-col items-center gap-4 relative">
          <button type="button" class="compare-matrix-remove compare-remove-btn" data-key="${escapeHtml(key)}" aria-label="Kaldır">
            <span class="material-symbols-outlined text-lg" aria-hidden="true">close</span>
          </button>
          <img src="${escapeHtml(imgSrc)}" alt="" class="h-28 object-contain" loading="lazy">
          <p class="product-category font-label-caps text-[10px] uppercase text-abrasive-red m-0">${escapeHtml(product.categoryName)}</p>
          <h3 class="font-headline-md text-[18px] text-center text-white m-0">${escapeHtml(product.name)}</h3>
          <p class="compare-matrix-variant font-label-caps text-[11px] text-abrasive-red uppercase m-0">${escapeHtml(variantBadgeText(variant, product))}</p>
          <p class="compare-matrix-sku font-technical-data text-technical-data text-steel-gray m-0">${escapeHtml(String(sku))}</p>
          <div class="compare-matrix-actions w-full flex flex-col gap-3 mt-2">
            <button type="button" class="${quoteBtnClass} py-3 font-label-caps text-label-caps uppercase hover:brightness-110 transition-all w-full text-center compare-add-quote" data-key="${escapeHtml(key)}" data-product-id="${escapeHtml(product.id)}" data-variant-id="${escapeHtml(variant.id || variant.urun_kodu || '')}">${quoteBtnLabel}</button>
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
    <div class="compare-actions-footer flex flex-col sm:flex-row items-center justify-center gap-4 mt-10">
      <a href="${typeof buildQuotePageUrl === 'function' ? buildQuotePageUrl(entries.map((e) => e.key), base) : `${base}fiyat-teklifi.html?from=compare`}" class="inline-flex items-center justify-center gap-2 bg-abrasive-red text-white px-8 py-3 font-label-caps text-label-caps uppercase hover:brightness-110 transition-all" id="compare-request-quote">
        <span class="material-symbols-outlined text-lg" aria-hidden="true">request_quote</span>
        Seçili Modeller İçin Teklif İste
      </a>
      <button type="button" class="compare-btn-clear border border-steel-gray/30 text-on-surface px-8 py-3 font-label-caps text-label-caps uppercase hover:border-abrasive-red hover:text-abrasive-red transition-all" id="clear-compare">Tümünü temizle</button>
    </div>
  </div>`;

  container.innerHTML = html;

  container.querySelectorAll('.compare-matrix-remove').forEach((btn) => {
    btn.addEventListener('click', () => {
      window.compareManager.remove(btn.dataset.key);
      location.reload();
    });
  });

  container.querySelectorAll('.compare-add-quote').forEach((btn) => {
    btn.addEventListener('click', () => {
      if (!window.quoteManager) return;
      const { productId, variantId } = btn.dataset;
      const result = window.quoteManager.toggle(productId, variantId);
      showCompareToast(result.message);
      const inList = window.quoteManager.isInList(productId, variantId);
      btn.textContent = inList ? 'Teklif Listesinde ✓' : 'Teklif Listesine Ekle';
      btn.classList.toggle('bg-abrasive-red', !inList);
      btn.classList.toggle('text-white', !inList);
      btn.classList.toggle('border', inList);
      btn.classList.toggle('border-abrasive-red', inList);
      btn.classList.toggle('text-abrasive-red', inList);
      btn.classList.toggle('bg-transparent', inList);
    });
  });

  document.getElementById('compare-request-quote')?.addEventListener('click', (e) => {
    e.preventDefault();
    const keys = entries.map((entry) => entry.key);
    if (typeof navigateToQuotePage === 'function') {
      navigateToQuotePage(keys, base);
    } else {
      window.location.href = e.currentTarget.href;
    }
  });

  document.getElementById('clear-compare')?.addEventListener('click', () => {
    window.compareManager.clearAll();
    location.reload();
  });
});

function showCompareToast(message) {
  let toast = document.querySelector('.compare-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.className =
      'compare-toast fixed bottom-24 left-1/2 -translate-x-1/2 z-[1200] bg-surface-elevation border border-steel-gray/30 text-white px-6 py-3 rounded-lg shadow-lg font-body-md text-sm';
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.hidden = false;
  clearTimeout(showCompareToast._timer);
  showCompareToast._timer = setTimeout(() => {
    toast.hidden = true;
  }, 2600);
}

function escapeHtml(text) {
  const d = document.createElement('div');
  d.textContent = text == null ? '' : String(text);
  return d.innerHTML;
}
