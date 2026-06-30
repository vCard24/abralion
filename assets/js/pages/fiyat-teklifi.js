(function () {
  'use strict';

  const MAX_ROWS = 4;
  const SUBMIT_KEY = 'abralion_quote_last_submit';
  let products = [];
  let categories = [];
  let rowCount = 0;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  function boot() {
    bindStaticHandlers();
    loadCatalog().catch((err) => {
      console.error('Katalog yüklenemedi:', err);
      showToast(
        'Ürün kataloğu yüklenemedi. fiyat-teklifi.html ile aynı klasörde assets/js/products-data.js dosyasının olduğundan emin olun.',
        'error'
      );
      if (rowCount === 0) addProductRow();
    });

    if (new URLSearchParams(window.location.search).get('tesekkur') === '1') {
      showThankYou(readLastSubmit());
    }
  }

  function bindStaticHandlers() {
    const form = document.getElementById('quote-form');
    if (!form) return;

    form.addEventListener('submit', handleSubmit);
    document.getElementById('quote-pdf-btn')?.addEventListener('click', downloadPdf);
    document.getElementById('quote-add-row')?.addEventListener('click', () => {
      if (rowCount >= MAX_ROWS) return;
      addProductRow();
    });
    document.getElementById('quote-remove-row')?.addEventListener('click', () => {
      if (rowCount <= 1) return;
      const rowsHost = document.getElementById('quote-product-rows');
      const rows = rowsHost?.querySelectorAll('.quote-product-row');
      rows?.[rows.length - 1]?.remove();
      rowCount -= 1;
      updateRowControls();
      syncQuoteStorage();
    });
    document.getElementById('quote-new-request')?.addEventListener('click', () => {
      const url = new URL(window.location.href);
      url.searchParams.delete('tesekkur');
      window.location.href = url.pathname.split('/').pop() || 'fiyat-teklifi.html';
    });

    const rowsHost = document.getElementById('quote-product-rows');
    rowsHost?.addEventListener('change', (e) => {
      if (!e.target.matches('.quote-field-category, .quote-field-product, .quote-field-variant, .quote-field-qty')) {
        return;
      }
      const row = e.target.closest('.quote-product-row');
      if (e.target.matches('.quote-field-category')) onCategoryChange(row);
      else if (e.target.matches('.quote-field-product')) onProductChange(row);
      syncQuoteStorage();
      clearRowError();
    });
  }

  async function loadCatalog() {
    if (window.ABRALION_CATALOG?.products?.length) {
      products = window.ABRALION_CATALOG.products;
      categories = window.ABRALION_CATALOG.categories || [];
    } else if (window.ProductManager) {
      const pm = new ProductManager();
      await pm.loadProducts();
      products = pm.getAllProducts();
      categories = window.ABRALION_CATALOG?.categories || pm.categories || [];
    } else {
      throw new Error('Ürün kataloğu bulunamadı (products-data.js)');
    }

    if (!products.length) {
      throw new Error('Ürün listesi boş');
    }
    if (!categories.length) {
      throw new Error('Kategori listesi boş');
    }

    applyInitialRows();
  }

  function applyInitialRows() {
    const fromCompare =
      typeof isQuoteFromCompare === 'function' ? isQuoteFromCompare() : false;

    const keys =
      typeof getCompareKeysForPrefill === 'function' ? getCompareKeysForPrefill() : [];

    if (keys.length && window.quoteManager?.setList) {
      window.quoteManager.setList(keys);
    }

    const initialRows = resolveInitialRows(keys, fromCompare);

    if (fromCompare && keys.length && !initialRows.length) {
      showToast('Karşılaştırma modelleri forma aktarılamadı. Ürünleri listeden seçin.', 'error');
    }

    if (initialRows.length) {
      initialRows.forEach((row) => addProductRow(row));
      if (fromCompare) showPrefillBanner(initialRows.length);
    } else if (rowCount === 0) {
      addProductRow();
    }
  }

  function resolveInitialRows(keys, fromCompare) {
    const rows = [];

    if (keys.length) {
      const entries =
        typeof resolveCatalogKeys === 'function'
          ? resolveCatalogKeys(keys, products)
          : window.quoteManager?.resolveEntries(products) || [];

      entries.forEach(({ product, variant }) => {
        if (!product) return;
        rows.push({
          categoryId: product.categoryId,
          productId: product.id,
          variantId: variant?.id || variant?.urun_kodu,
          qty: '',
        });
      });
      if (rows.length) return rows.slice(0, MAX_ROWS);
    }

    const params = new URLSearchParams(window.location.search);
    const urun = params.get('urun');
    const kod = params.get('kod') || params.get('variant');
    if (urun) {
      const product = products.find((p) => p.slug === urun || p.id === urun);
      if (product) {
        rows.push({
          categoryId: product.categoryId,
          productId: product.id,
          variantId: kod || product.variants?.[0]?.id || product.variants?.[0]?.urun_kodu,
          qty: params.get('miktar') || '',
        });
      }
    }

    return rows;
  }

  function showPrefillBanner(count) {
    const banner = document.getElementById('quote-prefill-banner');
    const text = document.getElementById('quote-prefill-banner-text');
    if (!banner) return;
    if (text) {
      text.textContent =
        count === 1
          ? 'Karşılaştırma listenizden 1 model aktarıldı.'
          : `Karşılaştırma listenizden ${count} model aktarıldı.`;
    }
    banner.hidden = false;
    banner.classList.remove('hidden');
  }

  function addPrefillRow(data) {
    if (rowCount >= MAX_ROWS) return;
    const rowsHost = document.getElementById('quote-product-rows');
    if (!rowsHost) return;

    const index = rowCount + 1;
    rowCount += 1;

    const row = document.createElement('div');
    row.className = 'quote-product-row quote-prefill-card';
    row.dataset.rowIndex = String(index);
    row.innerHTML = `
      <div class="quote-prefill-card__body">
        <p class="quote-prefill-card__cat">${escapeHtml(data.categoryName || '')}</p>
        <p class="quote-prefill-card__name">${escapeHtml(data.productName || '')}</p>
        <p class="quote-prefill-card__variant">${escapeHtml(data.variantLabel || data.variantId || '')}</p>
      </div>
      <div class="quote-field">
        <label>Miktar <span class="quote-optional-tag">opsiyonel</span></label>
        <input type="text" class="quote-input quote-field-qty" placeholder="Adet / koli" aria-label="Miktar ${index}" value="${escapeAttr(data.qty || '')}">
      </div>
      <input type="hidden" class="quote-field-category" value="${escapeAttr(data.categoryId || '')}">
      <input type="hidden" class="quote-field-product" value="${escapeAttr(data.productId || '')}">
      <input type="hidden" class="quote-field-variant" value="${escapeAttr(data.variantId || '')}">`;

    rowsHost.appendChild(row);
    updateRowControls();
  }

  function addProductRow(prefill = {}) {
    if (rowCount >= MAX_ROWS) return;
    const rowsHost = document.getElementById('quote-product-rows');
    if (!rowsHost) return;

    const index = rowCount + 1;
    rowCount += 1;

    const row = document.createElement('div');
    row.className = 'quote-product-row';
    row.dataset.rowIndex = String(index);
    row.innerHTML = `
      <p class="quote-row-index">Ürün ${index}</p>
      <div class="quote-field-stack">
        <div class="quote-field">
          <label>Kategori *</label>
          <select class="quote-select quote-field-category" aria-label="Kategori ${index}">
            <option value="">Kategori seçin</option>
            ${categories
              .slice()
              .sort((a, b) => (a.order || 0) - (b.order || 0))
              .map((c) => `<option value="${escapeAttr(c.id)}">${escapeHtml(c.name)}</option>`)
              .join('')}
          </select>
        </div>
        <div class="quote-field">
          <label>Ürün *</label>
          <select class="quote-select quote-field-product" disabled aria-label="Ürün ${index}">
            <option value="">Önce kategori seçin</option>
          </select>
        </div>
        <div class="quote-field">
          <label>Model / Kod *</label>
          <select class="quote-select quote-field-variant" disabled aria-label="Model ${index}">
            <option value="">Önce ürün seçin</option>
          </select>
        </div>
        <div class="quote-field">
          <label>Miktar <span class="quote-optional-tag">opsiyonel</span></label>
          <input type="text" class="quote-input quote-field-qty" placeholder="Adet / koli" aria-label="Miktar ${index}">
        </div>
      </div>`;

    rowsHost.appendChild(row);

    if (prefill.categoryId) {
      row.querySelector('.quote-field-category').value = prefill.categoryId;
      onCategoryChange(row, prefill.productId, prefill.variantId);
    }

    if (prefill.qty) {
      row.querySelector('.quote-field-qty').value = prefill.qty;
    }

    updateRowControls();
  }

  function onCategoryChange(row, productId = '', variantId = '') {
    const catId = row.querySelector('.quote-field-category').value;
    const productSel = row.querySelector('.quote-field-product');
    const variantSel = row.querySelector('.quote-field-variant');

    productSel.innerHTML = '<option value="">Ürün seçin</option>';
    variantSel.innerHTML = '<option value="">Önce ürün seçin</option>';
    variantSel.disabled = true;
    productSel.classList.remove('error');
    variantSel.classList.remove('error');

    if (!catId) {
      productSel.disabled = true;
      return;
    }

    products.filter((p) => p.categoryId === catId).forEach((p) => {
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = p.name;
      productSel.appendChild(opt);
    });
    productSel.disabled = false;

    if (productId && [...productSel.options].some((o) => o.value === productId)) {
      productSel.value = productId;
      onProductChange(row, variantId);
    }
  }

  function onProductChange(row, variantId = '') {
    const productId = row.querySelector('.quote-field-product').value;
    const variantSel = row.querySelector('.quote-field-variant');
    variantSel.innerHTML = '<option value="">Model seçin</option>';
    variantSel.classList.remove('error');

    const product = products.find((p) => p.id === productId);
    if (!product?.variants?.length) {
      variantSel.disabled = true;
      return;
    }

    product.variants.forEach((v) => {
      const opt = document.createElement('option');
      opt.value = v.id || v.urun_kodu;
      opt.textContent = variantOptionLabel(v, product);
      variantSel.appendChild(opt);
    });
    variantSel.disabled = false;

    if (variantId) {
      const match = product.variants.find(
        (v) => v.id === variantId || v.urun_kodu === variantId || String(v.id) === String(variantId)
      );
      if (match) variantSel.value = match.id || match.urun_kodu;
    }
  }

  function variantOptionLabel(variant, product) {
    const code = variant.urun_kodu || variant.id;
    const badge = variantBadgeText(variant, product);
    if (badge && code) return `${code} — ${badge}`;
    if (code) return String(code);
    if (typeof variantLabel === 'function') return variantLabel(variant, product.name);
    return product.name;
  }

  function variantBadgeText(variant) {
    if (variant.uzunluk_mm != null && variant.uc_genisligi_mm != null) {
      return `${variant.saft_mm ?? ''}x${variant.uzunluk_mm}x${variant.uc_genisligi_mm} mm`.replace(/^x/, '');
    }
    if (variant.uzunluk_mm != null) {
      return `${variant.saft_mm ?? ''}x${variant.uzunluk_mm} mm`.replace(/^x/, '');
    }
    if (variant.daire_capi_mm != null) {
      return `Ø${variant.daire_capi_mm}${variant.kalinlik_mm != null ? ' x ' + variant.kalinlik_mm : ''} mm`;
    }
    if (variant.cap_mm != null) return `${variant.cap_mm} mm`;
    return '';
  }

  function updateRowControls() {
    const addBtn = document.getElementById('quote-add-row');
    const removeBtn = document.getElementById('quote-remove-row');
    if (addBtn) addBtn.disabled = rowCount >= MAX_ROWS;
    if (removeBtn) removeBtn.disabled = rowCount <= 1;
  }

  function collectProductRows() {
    const rows = [];
    document.querySelectorAll('.quote-product-row').forEach((row) => {
      const categoryId = row.querySelector('.quote-field-category')?.value;
      const productId = row.querySelector('.quote-field-product')?.value;
      const variantId = row.querySelector('.quote-field-variant')?.value;
      const qty = row.querySelector('.quote-field-qty')?.value?.trim() || '';
      if (!categoryId || !productId || !variantId) return;

      const product = products.find((p) => p.id === productId);
      const variant = product?.variants?.find((v) => v.id === variantId || v.urun_kodu === variantId);
      rows.push({
        categoryId,
        productId,
        variantId,
        qty,
        product,
        variant,
        label: product ? variantOptionLabel(variant || {}, product) : variantId,
      });
    });
    return rows;
  }

  function syncQuoteStorage() {
    if (!window.quoteManager) return;
    const keys = collectProductRows()
      .filter((r) => r.product && r.variant)
      .map((r) => window.quoteManager.makeKey(r.product.id, r.variant.id || r.variant.urun_kodu));
    window.quoteManager.setList(keys);
  }

  function collectFormData() {
    return {
      products: collectProductRows(),
      name: document.getElementById('quote-name')?.value?.trim() || '',
      phone: document.getElementById('quote-phone')?.value?.trim() || '',
      email: document.getElementById('quote-email')?.value?.trim() || '',
      company: document.getElementById('quote-company')?.value?.trim() || '',
      country: document.getElementById('quote-country')?.value?.trim() || '',
      city: document.getElementById('quote-city')?.value?.trim() || '',
      message: document.getElementById('quote-message')?.value?.trim() || '',
      application: document.getElementById('quote-application')?.value?.trim() || '',
      volume: document.getElementById('quote-volume')?.value?.trim() || '',
      delivery: document.getElementById('quote-delivery')?.value?.trim() || '',
      urgency: document.getElementById('quote-urgency')?.value || '',
      kvkk: document.getElementById('quote-kvkk')?.checked || false,
    };
  }

  function validateForm(data, { requireContact = true } = {}) {
    let ok = true;
    clearErrors();

    if (!data.products.length) {
      showRowError('En az bir ürün için kategori, ürün ve model seçmelisiniz.');
      markEmptyProductRows();
      ok = false;
    }

    if (!requireContact) return ok;

    const required = [
      ['quote-name', data.name, 'Ad soyad zorunludur.'],
      ['quote-phone', data.phone, 'Telefon zorunludur.'],
      ['quote-email', data.email, 'E-posta zorunludur.'],
      ['quote-country', data.country, 'Ülke zorunludur.'],
      ['quote-city', data.city, 'Şehir zorunludur.'],
    ];

    required.forEach(([id, val, msg]) => {
      if (!val) {
        showFieldError(id, msg);
        ok = false;
      }
    });

    if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      showFieldError('quote-email', 'Geçerli bir e-posta adresi girin.');
      ok = false;
    }

    if (!data.kvkk) {
      showFieldError('quote-kvkk', 'KVKK onayını işaretlemeniz gerekir.');
      ok = false;
    }

    if (!ok) scrollToFirstError();
    return ok;
  }

  function markEmptyProductRows() {
    document.querySelectorAll('.quote-product-row').forEach((row) => {
      if (row.querySelector('input[type="hidden"].quote-field-product')) return;
      ['.quote-field-category', '.quote-field-product', '.quote-field-variant'].forEach((sel) => {
        const el = row.querySelector(sel);
        if (el && !el.value) el.classList.add('error');
      });
    });
  }

  function showFieldError(fieldId, message) {
    const err = document.getElementById(`${fieldId}-error`);
    const field = document.getElementById(fieldId);
    if (err) {
      err.textContent = message;
      err.classList.add('show');
    }
    if (field) field.classList.add('error');
  }

  function showRowError(message) {
    const host = document.getElementById('quote-product-rows');
    if (!host) return;
    let note = host.querySelector('.quote-rows-error');
    if (!note) {
      note = document.createElement('p');
      note.className = 'quote-rows-error form-error show text-sm mb-3 m-0';
      host.prepend(note);
    }
    note.textContent = message;
  }

  function clearRowError() {
    document.querySelector('.quote-rows-error')?.remove();
  }

  function clearErrors() {
    document.querySelectorAll('#quote-form .form-error').forEach((el) => {
      el.textContent = '';
      el.classList.remove('show');
    });
    document.querySelectorAll('#quote-form .error').forEach((el) => el.classList.remove('error'));
    clearRowError();
  }

  function scrollToFirstError() {
    const target =
      document.querySelector('#quote-form .form-error.show') ||
      document.querySelector('.quote-rows-error') ||
      document.querySelector('#quote-form .error');
    target?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    if (target?.id?.endsWith('-error')) {
      const fieldId = target.id.replace(/-error$/, '');
      document.getElementById(fieldId)?.focus();
    }
  }

  function buildSummaryText(data) {
    const lines = [
      'ABRALION — FİYAT TEKLİFİ TALEBİ',
      `Tarih: ${new Date().toLocaleString('tr-TR')}`,
      `Referans: ${data.reference || '—'}`,
      '',
      '--- ÜRÜNLER ---',
    ];

    data.products.forEach((row, i) => {
      lines.push(
        `${i + 1}. ${row.product?.name || row.productId}`,
        `   Model: ${row.label}${row.qty ? ` | Miktar: ${row.qty}` : ''}`
      );
    });

    lines.push(
      '',
      '--- İLETİŞİM ---',
      `Ad Soyad: ${data.name}`,
      `Telefon: ${data.phone}`,
      `E-posta: ${data.email}`,
      data.company ? `Firma: ${data.company}` : '',
      `Ülke / Şehir: ${data.country} / ${data.city}`,
      '',
      '--- TALEP DETAYLARI ---',
      data.application ? `Uygulama: ${data.application}` : '',
      data.volume ? `Tahmini miktar: ${data.volume}` : '',
      data.delivery ? `Teslimat: ${data.delivery}` : '',
      data.urgency ? `Aciliyet: ${data.urgency}` : '',
      data.message ? `Mesaj: ${data.message}` : ''
    );

    return lines.filter(Boolean).join('\n');
  }

  function buildPrintHtml(data) {
    const productRows = data.products
      .map(
        (row, i) =>
          `<tr><td>${i + 1}</td><td>${escapeHtml(row.product?.name || '')}</td><td>${escapeHtml(row.label)}</td><td>${escapeHtml(row.qty || '—')}</td></tr>`
      )
      .join('');

    const details = [
      data.application && `Uygulama: ${escapeHtml(data.application)}`,
      data.volume && `Miktar: ${escapeHtml(data.volume)}`,
      data.delivery && `Teslimat: ${escapeHtml(data.delivery)}`,
      data.urgency && `Aciliyet: ${escapeHtml(data.urgency)}`,
      data.message && escapeHtml(data.message),
    ]
      .filter(Boolean)
      .join('<br>');

    return `<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><title>Abralion Teklif Talebi</title>
<style>
@page { margin: 18mm; }
body{font-family:Arial,"Helvetica Neue",Helvetica,sans-serif;padding:24px;color:#111;line-height:1.5}
h1{font-size:22px;margin:0 0 8px;color:#E2231A}
h2{font-size:14px;margin:24px 0 8px;text-transform:uppercase;letter-spacing:.08em}
table{width:100%;border-collapse:collapse;margin-top:8px}
th,td{border:1px solid #ccc;padding:8px;text-align:left;font-size:13px}
th{background:#f5f5f5}
.meta{font-size:13px;color:#444}
</style></head><body>
<h1>Abralion — Fiyat Teklifi Talebi</h1>
<p class="meta">${escapeHtml(new Date().toLocaleString('tr-TR'))}${data.reference ? ` · Ref: ${escapeHtml(data.reference)}` : ''}</p>
<h2>Ürünler</h2>
<table><thead><tr><th>#</th><th>Ürün</th><th>Model</th><th>Miktar</th></tr></thead><tbody>${productRows}</tbody></table>
<h2>İletişim</h2>
<p><strong>${escapeHtml(data.name || '—')}</strong><br>
${data.phone ? `Tel: ${escapeHtml(data.phone)}<br>` : ''}
${data.email ? `E-posta: ${escapeHtml(data.email)}<br>` : ''}
${data.company ? `Firma: ${escapeHtml(data.company)}<br>` : ''}
${escapeHtml(data.country || '—')} / ${escapeHtml(data.city || '—')}</p>
<h2>Talep detayları</h2>
<p>${details || '—'}</p>
<p style="margin-top:32px;font-size:12px;color:#666">EKS-PLAST LLC · info@abralion.com · www.abralion.com</p>
<script>window.onload=function(){window.focus();window.print();};<\/script>
</body></html>`;
  }

  function makeReference() {
    const d = new Date();
    const pad = (n) => String(n).padStart(2, '0');
    return `ABR-${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}`;
  }

  function saveSubmit(data) {
    try {
      sessionStorage.setItem(SUBMIT_KEY, JSON.stringify(data));
    } catch {
      /* ignore */
    }
  }

  function readLastSubmit() {
    try {
      const raw = sessionStorage.getItem(SUBMIT_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }

  function showThankYou(data) {
    const formWrap = document.getElementById('quote-form-wrap');
    const thankYou = document.getElementById('quote-thank-you');
    if (!thankYou) return;

    if (formWrap) {
      formWrap.hidden = true;
      formWrap.classList.add('hidden');
    }

    thankYou.hidden = false;
    thankYou.classList.remove('hidden');

    const refEl = document.getElementById('quote-thank-you-ref');
    const textEl = document.getElementById('quote-thank-you-text');
    if (data?.reference && refEl) {
      refEl.textContent = `Referans no: ${data.reference}`;
    }
    if (data?.name && textEl) {
      textEl.textContent = `Teşekkürler ${data.name}. Talebiniz kaydedildi; uzman ekibimiz genellikle 24 saat içinde size dönüş yapar.`;
    }

    thankYou.scrollIntoView({ behavior: 'smooth', block: 'start' });
    document.getElementById('quote-form-heading')?.scrollIntoView();
  }

  function tryOpenMailto(data) {
    try {
      const body = encodeURIComponent(buildSummaryText(data));
      const subject = encodeURIComponent(`Fiyat Teklifi — ${data.name} (${data.reference})`);
      const link = document.createElement('a');
      link.href = `mailto:info@abralion.com?subject=${subject}&body=${body}`;
      link.style.display = 'none';
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch {
      /* mailto isteğe bağlı */
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    const data = collectFormData();
    if (!validateForm(data, { requireContact: true })) {
      showToast('Lütfen işaretli zorunlu alanları doldurun.', 'error');
      return;
    }

    data.reference = makeReference();
    data.submittedAt = new Date().toISOString();
    syncQuoteStorage();
    saveSubmit(data);
    showThankYou(data);
    tryOpenMailto(data);

    const url = new URL(window.location.href);
    url.searchParams.set('tesekkur', '1');
    window.history.replaceState({}, '', url.pathname + url.search);
  }

  function urgencyLabel(value) {
    const map = {
      normal: 'Normal (1–2 hafta)',
      urgent: 'Acil (3–5 iş günü)',
      stock: 'Stoktan hemen',
    };
    return map[value] || value || '';
  }

  function pdfField(label, value, fullWidth) {
    const val = value == null || value === '' ? '—' : String(value);
    return `<div class="quote-pdf-field${fullWidth ? ' quote-pdf-field--full' : ''}">
      <span class="quote-pdf-field__label">${escapeHtml(label)}</span>
      <span class="quote-pdf-field__value">${escapeHtml(val)}</span>
    </div>`;
  }

  function pdfBlock(title, bodyHtml) {
    return `<section class="quote-pdf-block">
      <div class="quote-pdf-block__head">${escapeHtml(title)}</div>
      <div class="quote-pdf-block__body">${bodyHtml}</div>
    </section>`;
  }

  function buildPdfProductRows(data) {
    if (!data.products?.length) return '';
    return `<table class="quote-pdf-table">
      <thead><tr><th>#</th><th>Ürün</th><th>Model</th><th>Miktar</th></tr></thead>
      <tbody>${data.products
        .map(
          (row, i) =>
            `<tr><td>${i + 1}</td><td>${escapeHtml(row.product?.name || row.productId)}</td><td>${escapeHtml(row.label)}</td><td>${escapeHtml(row.qty || '—')}</td></tr>`
        )
        .join('')}</tbody></table>`;
  }

  function buildPdfSheet(data) {
    const sheet = document.getElementById('quote-pdf-sheet');
    if (!sheet) return null;

    const dateStr = new Date().toLocaleString('tr-TR');
    const productsHtml = buildPdfProductRows(data) || '<p class="quote-pdf-empty">Ürün seçilmedi</p>';

    const contactHtml =
      pdfField('Ad soyad', data.name) +
      pdfField('Telefon', data.phone) +
      pdfField('E-posta', data.email) +
      pdfField('Firma', data.company) +
      pdfField('Ülke', data.country) +
      pdfField('Şehir', data.city);

    const detailParts = [
      data.application ? pdfField('Uygulama alanı', data.application, true) : '',
      data.volume ? pdfField('Tahmini miktar', data.volume) : '',
      data.delivery ? pdfField('Teslimat bölgesi', data.delivery) : '',
      data.urgency ? pdfField('Teslimat aciliyeti', urgencyLabel(data.urgency)) : '',
      data.message ? pdfField('Mesaj', data.message, true) : '',
    ].filter(Boolean);

    const detailsBlock = detailParts.length
      ? pdfBlock('Talep detayları', `<div class="quote-pdf-fields">${detailParts.join('')}</div>`)
      : '';

    sheet.innerHTML = `<div class="quote-pdf-doc">
      <header class="quote-pdf-doc__header">
        <div class="quote-pdf-doc__logo"><span class="quote-pdf-doc__logo-text">ABRALION</span></div>
        <div class="quote-pdf-doc__header-main">
          <h1>Fiyat Teklifi Talep Formu</h1>
          <p class="quote-pdf-doc__date">Talep tarihi: ${escapeHtml(dateStr)}${data.reference ? ` · Ref: ${escapeHtml(data.reference)}` : ''}</p>
        </div>
      </header>
      ${pdfBlock('Seçilen ürünler', productsHtml)}
      ${pdfBlock('İletişim bilgileri', `<div class="quote-pdf-fields">${contactHtml}</div>`)}
      ${detailsBlock}
      <footer class="quote-pdf-doc__footer">
        <p>EKS-PLAST LLC · info@abralion.com · www.abralion.com · 8 (495) 142-42-67</p>
        <p class="quote-pdf-doc__footnote">Bu belge müşteri talep formunun özetidir; bağlayıcı fiyat teklifi niteliği taşımaz.</p>
      </footer>
    </div>`;

    return sheet;
  }

  function captureSheetToCanvas(sheet, h2c) {
    const target = sheet.querySelector('.quote-pdf-doc') || sheet;
    const baseOpts = {
      logging: false,
      backgroundColor: '#ffffff',
      scrollX: 0,
      scrollY: 0,
      useCORS: true,
    };
    return h2c(target, { ...baseOpts, scale: 1.25 }).catch(() => h2c(target, { ...baseOpts, scale: 1 }));
  }

  function canvasToPdf(pdf, canvas) {
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
    while (srcY < canvas.height && guard < 20) {
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

  function downloadPdf() {
    const data = collectFormData();
    if (!validateForm(data, { requireContact: false })) {
      showToast('PDF için en az bir ürün seçmelisiniz.', 'error');
      return;
    }

    data.reference = data.reference || makeReference();
    const btn = document.getElementById('quote-pdf-btn');
    const h2c = window.html2canvas;
    const JsPDF = window.jspdf && (window.jspdf.jsPDF || window.jspdf.default);

    if (!h2c || !JsPDF) {
      showToast('PDF modülü yüklenemedi. Sayfayı yenileyin.', 'error');
      return;
    }

    if (btn) btn.disabled = true;

    const sheet = buildPdfSheet(data);
    if (!sheet) {
      if (btn) btn.disabled = false;
      showToast('PDF sayfası oluşturulamadı.', 'error');
      return;
    }

    sheet.hidden = false;
    sheet.classList.add('is-capturing');
    sheet.setAttribute('aria-hidden', 'false');

    const fontReady = document.fonts?.ready ? document.fonts.ready : Promise.resolve();

    fontReady
      .then(
        () =>
          new Promise((resolve) => {
            requestAnimationFrame(() => requestAnimationFrame(resolve));
          })
      )
      .then(() => captureSheetToCanvas(sheet, h2c))
      .then((canvas) => {
        if (!canvas?.width || !canvas?.height) throw new Error('empty canvas');
        const pdf = new JsPDF('p', 'mm', 'a4');
        canvasToPdf(pdf, canvas);
        pdf.save(`Abralion-Teklif-${data.reference || 'ozet'}.pdf`);
        showToast('PDF indirildi.', 'success');
      })
      .catch((err) => {
        console.error('PDF error:', err);
        if (printViaIframe(buildPrintHtml(data))) {
          showToast('PDF oluşturulamadı; yazdır penceresinden “PDF olarak kaydet” kullanın.');
        } else {
          downloadHtmlFile(buildPrintHtml(data), data.reference);
          showToast('PDF oluşturulamadı; özet HTML dosyası indirildi.', 'error');
        }
      })
      .finally(() => {
        sheet.classList.remove('is-capturing');
        sheet.hidden = true;
        sheet.setAttribute('aria-hidden', 'true');
        if (btn) btn.disabled = false;
      });
  }

  function printViaIframe(html) {
    try {
      let frame = document.getElementById('quote-print-frame');
      if (!frame) {
        frame = document.createElement('iframe');
        frame.id = 'quote-print-frame';
        frame.title = 'Teklif yazdır';
        frame.style.cssText = 'position:fixed;right:0;bottom:0;width:0;height:0;border:0';
        frame.setAttribute('hidden', '');
        document.body.appendChild(frame);
      }

      const doc = frame.contentWindow || frame.contentDocument?.defaultView;
      if (!doc) return false;

      const docEl = frame.contentDocument || frame.contentWindow.document;
      docEl.open();
      docEl.write(html);
      docEl.close();

      setTimeout(() => {
        try {
          frame.contentWindow.focus();
          frame.contentWindow.print();
        } catch {
          downloadHtmlFile(html, makeReference());
        }
      }, 300);
      return true;
    } catch {
      return false;
    }
  }

  function downloadHtmlFile(html, reference) {
    const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Abralion-Teklif-${reference || 'ozet'}.html`;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function showToast(message, tone = 'info') {
    let toast = document.getElementById('quote-toast');
    if (!toast) return;
    toast.textContent = message;
    toast.classList.remove('hidden', 'quote-toast--error', 'quote-toast--success');
    if (tone === 'error') toast.classList.add('quote-toast--error');
    if (tone === 'success') toast.classList.add('quote-toast--success');
    toast.hidden = false;
    clearTimeout(showToast._timer);
    showToast._timer = setTimeout(() => {
      toast.hidden = true;
      toast.classList.add('hidden');
    }, 4200);
  }

  function escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text == null ? '' : String(text);
    return d.innerHTML;
  }

  function escapeAttr(text) {
    return escapeHtml(text).replace(/"/g, '&quot;');
  }
})();
