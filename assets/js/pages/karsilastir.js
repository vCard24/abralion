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

const MAIL_SITE_ORIGIN = 'https://abralion.com';
let compareExportState = null;
let compareLogoDataUrl = '';

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
      <button type="button" class="compare-btn-export compare-btn-print border border-steel-gray/30 text-on-surface px-8 py-3 font-label-caps text-label-caps uppercase hover:border-abrasive-red hover:text-abrasive-red transition-all" id="compare-print-btn">
        <span class="material-symbols-outlined text-lg" aria-hidden="true">print</span>
        Yazdır
      </button>
      <button type="button" class="compare-btn-export compare-btn-pdf border border-steel-gray/30 text-on-surface px-8 py-3 font-label-caps text-label-caps uppercase hover:border-abrasive-red hover:text-abrasive-red transition-all" id="compare-pdf-btn">
        <span class="material-symbols-outlined text-lg" aria-hidden="true">download</span>
        PDF indir
      </button>
      <button type="button" class="compare-btn-clear border border-steel-gray/30 text-on-surface px-8 py-3 font-label-caps text-label-caps uppercase hover:border-abrasive-red hover:text-abrasive-red transition-all" id="clear-compare">Tümünü temizle</button>
    </div>
  </div>`;

  compareExportState = {
    entries,
    columnData,
    slots,
    allSpecKeys,
    maxSlots,
    base,
    mixedGroups,
  };

  container.innerHTML = html;
  bindCompareExportHandlers();

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

function bindCompareExportHandlers() {
  document.getElementById('compare-print-btn')?.addEventListener('click', printCompareTable);
  document.getElementById('compare-pdf-btn')?.addEventListener('click', downloadComparePdf);
}

function printCompareTable() {
  if (!compareExportState?.entries?.length) {
    showCompareToast('Yazdırmak için en az bir model seçin.');
    return;
  }
  window.print();
}

function compareAbsoluteUrl(relativePath) {
  const base = typeof getBasePath === 'function' ? getBasePath() : '';
  const combined = `${base}${relativePath}`.replace(/\/+/g, '/').replace(/^\//, '');
  if (
    window.location.protocol === 'file:' ||
    !window.location.origin ||
    window.location.origin === 'null'
  ) {
    return `${MAIL_SITE_ORIGIN}/${combined}`.replace(/([^:]\/)\/+/g, '$1');
  }
  try {
    return new URL(`${base}${relativePath}`, window.location.href).href;
  } catch {
    return `${MAIL_SITE_ORIGIN}/${combined}`;
  }
}

function compareProductImageUrl(product) {
  if (!product) return '';
  const slug = product.slug || product.id;
  let rel = `assets/images/products/${slug}/${slug}-kart.jpg`;
  if (slug === 'metal-inox-kesme-tasi') {
    rel = `assets/images/products/${slug}/${slug}-kart.png`;
  }
  if (product.images?.[0]?.src) {
    rel = String(product.images[0].src).replace(/^\//, '');
  }
  return compareAbsoluteUrl(rel);
}

function imageElementToDataUrl(imgEl) {
  if (!imgEl || !imgEl.complete || !imgEl.naturalWidth) return '';
  try {
    let w = imgEl.naturalWidth;
    let h = imgEl.naturalHeight;
    const max = 900;
    if (w > max || h > max) {
      if (w >= h) {
        h = Math.max(1, Math.round((h * max) / w));
        w = max;
      } else {
        w = Math.max(1, Math.round((w * max) / h));
        h = max;
      }
    }
    const canvas = document.createElement('canvas');
    canvas.width = w;
    canvas.height = h;
    canvas.getContext('2d').drawImage(imgEl, 0, 0, w, h);
    return canvas.toDataURL('image/jpeg', 0.88);
  } catch {
    return '';
  }
}

function blobToDataUrl(blob) {
  return new Promise((resolve) => {
    if (!blob) {
      resolve('');
      return;
    }
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result || '');
    reader.onerror = () => resolve('');
    reader.readAsDataURL(blob);
  });
}

function xhrBlobToDataUrl(url) {
  return new Promise((resolve) => {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'blob';
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300 && xhr.response) {
        blobToDataUrl(xhr.response).then(resolve);
      } else {
        resolve('');
      }
    };
    xhr.onerror = () => resolve('');
    xhr.send();
  });
}

function urlToDataUrl(url) {
  return new Promise((resolve) => {
    if (!url || url.startsWith('data:')) {
      resolve(url || '');
      return;
    }
    const loader = new Image();
    loader.crossOrigin = 'anonymous';
    loader.onload = () => resolve(imageElementToDataUrl(loader) || '');
    loader.onerror = () => resolve('');
    loader.src = url;
  });
}

function resolveImageDataUrl(url) {
  if (!url) return Promise.resolve('');
  if (url.startsWith('data:')) return Promise.resolve(url);
  if (window.location.protocol === 'file:') return Promise.resolve('');
  return xhrBlobToDataUrl(url).then((dataUrl) => (dataUrl ? dataUrl : urlToDataUrl(url)));
}

  function ensureCompareLogoDataUrl() {
    if (compareLogoDataUrl) return Promise.resolve(compareLogoDataUrl);
    if (typeof window.ensureAbralionPdfLogoDataUrl === 'function') {
      return window.ensureAbralionPdfLogoDataUrl().then((data) => {
        compareLogoDataUrl = data || '';
        return compareLogoDataUrl;
      });
    }
    return Promise.resolve('');
  }

function resolveCompareExportImages(state) {
  return Promise.all(
    state.columnData.map((col) => {
      if (!col?.product) return Promise.resolve();
      return resolveImageDataUrl(compareProductImageUrl(col.product)).then((dataUrl) => {
        col.exportImageDataUrl = dataUrl || '';
      });
    })
  );
}

function buildCompareExportSheet(state) {
  const sheet = document.getElementById('compare-pdf-sheet');
  if (!sheet || !state) return null;

  const dateStr = new Date().toLocaleString('tr-TR');
  const logoHtml = compareLogoDataUrl
    ? `<img class="compare-export-doc__logo-image" src="${escapeAttr(compareLogoDataUrl)}" alt="" />`
    : '<span class="compare-export-doc__logo-text">ABRALION</span>';

  let headHtml = `<th class="compare-export-label-col" scope="col">Teknik Özellikler</th>`;
  state.slots.forEach((col) => {
    if (!col) return;
    const { product, variant } = col;
    const imgSrc = col.exportImageDataUrl || compareProductImageUrl(product);
    const imgHtml = imgSrc
      ? `<img src="${escapeAttr(imgSrc)}" alt="" />`
      : '';
    headHtml += `<th scope="col"><div class="compare-export-product-head">
      ${imgHtml}
      <p class="compare-export-product-head__cat">${escapeHtml(product.categoryName || '')}</p>
      <p class="compare-export-product-head__name">${escapeHtml(product.name || '')}</p>
      <p class="compare-export-product-head__variant">${escapeHtml(variantBadgeText(variant, product))}</p>
    </div></th>`;
  });

  let bodyHtml = '';
  state.allSpecKeys.forEach((label, specKey) => {
    bodyHtml += `<tr><th class="compare-export-label-col" scope="row">${escapeHtml(label)}</th>`;
    state.slots.forEach((col) => {
      if (!col) return;
      const val = col.lineMap[specKey];
      const text = val && val !== '—' ? val : '—';
      bodyHtml += `<td>${escapeHtml(text)}</td>`;
    });
    bodyHtml += '</tr>';
  });

  const mixedNote = state.mixedGroups
    ? '<p class="compare-export-doc__summary" style="margin-bottom:10px;color:#92400e;background:#fffbeb;border:1px solid #fcd34d;border-radius:6px;padding:8px 10px;text-transform:none;letter-spacing:0;font-weight:500;">Farklı ürün grupları birlikte listeleniyor; ilgili olmayan hücreler boş bırakılır.</p>'
    : '';

  sheet.innerHTML = `<div class="compare-export-doc">
    <header class="compare-export-doc__header">
      <table class="compare-export-doc__header-table" role="presentation" cellspacing="0" cellpadding="0">
        <tr>
          <td class="compare-export-doc__logo-cell">${logoHtml}</td>
          <td class="compare-export-doc__header-text">
            <h1>Ürün Karşılaştırma</h1>
            <p class="compare-export-doc__date">${escapeHtml(dateStr)}</p>
          </td>
        </tr>
      </table>
    </header>
    <p class="compare-export-doc__summary">${state.entries.length} / ${state.maxSlots} model karşılaştırılıyor</p>
    ${mixedNote}
    <table class="compare-export-table">
      <thead><tr>${headHtml}</tr></thead>
      <tbody>${bodyHtml}</tbody>
    </table>
    <footer class="compare-export-doc__footer">
      <strong style="color:#111827;">Abralion — EKS-PLAST LLC</strong><br />
      www.abralion.com · info@abralion.com · +7 985 789-60-62<br />
      Bu belge bilgilendirme amaçlıdır; bağlayıcı teklif niteliği taşımaz.
    </footer>
  </div>`;

  return sheet;
}

function waitForOneImage(img) {
  if (!img) return Promise.resolve();
  if (img.complete) return Promise.resolve();
  return new Promise((resolve) => {
    img.addEventListener('load', resolve, { once: true });
    img.addEventListener('error', resolve, { once: true });
    setTimeout(resolve, 6000);
  });
}

function prepareCompareExportImages(container) {
  const imgs = container.querySelectorAll('img');
  return Promise.all(
    Array.from(imgs).map((img) => {
      const src = img.getAttribute('src') || img.src || '';
      if (!src || /^data:image\/(jpeg|png|webp)/i.test(src)) return Promise.resolve();
      return urlToDataUrl(src)
        .then((dataUrl) => {
          if (dataUrl) {
            img.setAttribute('src', dataUrl);
            img.src = dataUrl;
          }
        })
        .then(() => waitForOneImage(img));
    })
  );
}

function captureCompareSheetToCanvas(sheet, h2c) {
  const target = sheet.querySelector('.compare-export-doc') || sheet;
  const baseOpts = {
    logging: false,
    backgroundColor: '#ffffff',
    scrollX: 0,
    scrollY: 0,
    useCORS: true,
  };
  return h2c(target, { ...baseOpts, scale: 1.25 }).catch(() => h2c(target, { ...baseOpts, scale: 1 }));
}

function compareCanvasToPdf(pdf, canvas) {
  const margin = 8;
  const pageW = pdf.internal.pageSize.getWidth();
  const pageH = pdf.internal.pageSize.getHeight();
  const usableW = pageW - margin * 2;
  const usableH = pageH - margin * 2;
  const imgW = usableW;
  const imgH = (canvas.height * imgW) / canvas.width;

  let jpeg;
  try {
    jpeg = canvas.toDataURL('image/jpeg', 0.92);
  } catch {
    jpeg = canvas.toDataURL('image/png');
  }
  const imgFormat = jpeg.startsWith('data:image/png') ? 'PNG' : 'JPEG';

  if (imgH <= usableH) {
    pdf.addImage(jpeg, imgFormat, margin, margin, imgW, imgH);
    return;
  }

  const sliceHeightPx = Math.max(1, Math.floor((usableH * canvas.width) / imgW));
  let srcY = 0;
  let pageIndex = 0;
  let guard = 0;
  while (srcY < canvas.height && guard < 24) {
    guard += 1;
    if (pageIndex > 0) pdf.addPage();
    const sliceH = Math.min(sliceHeightPx, canvas.height - srcY);
    const pageCanvas = document.createElement('canvas');
    pageCanvas.width = canvas.width;
    pageCanvas.height = sliceH;
    const ctx = pageCanvas.getContext('2d');
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, pageCanvas.width, sliceH);
    ctx.drawImage(canvas, 0, srcY, canvas.width, sliceH, 0, 0, canvas.width, sliceH);
    const sliceImgH = (sliceH * imgW) / canvas.width;
    let sliceData;
    try {
      sliceData = pageCanvas.toDataURL('image/jpeg', 0.92);
      pdf.addImage(sliceData, 'JPEG', margin, margin, imgW, sliceImgH);
    } catch {
      sliceData = pageCanvas.toDataURL('image/png');
      pdf.addImage(sliceData, 'PNG', margin, margin, imgW, sliceImgH);
    }
    srcY += sliceH;
    pageIndex += 1;
  }
}

function downloadComparePdf() {
  if (!compareExportState?.entries?.length) {
    showCompareToast('PDF için en az bir model seçin.');
    return;
  }

  const btn = document.getElementById('compare-pdf-btn');
  const h2c = window.html2canvas;
  const JsPDF = window.jspdf && (window.jspdf.jsPDF || window.jspdf.default);

  if (!h2c || !JsPDF) {
    showCompareToast('PDF modülü yüklenemedi. Sayfayı yenileyin.');
    return;
  }

  if (btn) btn.disabled = true;

  const state = {
    ...compareExportState,
    columnData: compareExportState.columnData.map((col) => ({ ...col })),
  };

  let sheet = null;

  resolveCompareExportImages(state)
    .then(() => ensureCompareLogoDataUrl())
    .then(() => {
      sheet = buildCompareExportSheet(state);
      if (!sheet) throw new Error('missing sheet');
      sheet.hidden = false;
      sheet.classList.add('is-capturing');
      sheet.setAttribute('aria-hidden', 'false');
      const fontReady = document.fonts?.ready ? document.fonts.ready : Promise.resolve();
      return fontReady;
    })
    .then(() => prepareCompareExportImages(sheet))
    .then(
      () =>
        new Promise((resolve) => {
          requestAnimationFrame(() => requestAnimationFrame(resolve));
        })
    )
    .then(() => captureCompareSheetToCanvas(sheet, h2c))
    .then((canvas) => {
      if (!canvas?.width || !canvas?.height) throw new Error('empty canvas');
      const pdf = new JsPDF('l', 'mm', 'a4');
      compareCanvasToPdf(pdf, canvas);
      const stamp = new Date().toISOString().slice(0, 10);
      pdf.save(`Abralion-Karsilastirma-${stamp}.pdf`);
      showCompareToast('PDF indirildi.');
    })
    .catch((err) => {
      console.error('Compare PDF error:', err);
      showCompareToast('PDF oluşturulamadı. Yazdır ile “PDF olarak kaydet” deneyin.');
      window.print();
    })
    .finally(() => {
      if (sheet) {
        sheet.classList.remove('is-capturing');
        sheet.hidden = true;
        sheet.setAttribute('aria-hidden', 'true');
      }
      if (btn) btn.disabled = false;
    });
}

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

function escapeAttr(text) {
  return escapeHtml(text).replace(/"/g, '&quot;');
}
