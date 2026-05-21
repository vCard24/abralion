/**
 * Teknik tablo sütunları — PDF kataloğu ile birebir.
 * Boş değerler boş hücre olarak kalır (— kullanılmaz).
 */

const COLUMN_COMPUTERS = {
  max_hiz_flap_rpm(v) {
    if (v.max_hiz_rpm != null && v.max_hiz_ms != null) {
      return `${Number(v.max_hiz_rpm).toLocaleString('tr-TR')}-${v.max_hiz_ms} m/s`;
    }
    if (v.max_hiz_rpm != null) return `${Number(v.max_hiz_rpm).toLocaleString('tr-TR')} Rpm`;
    if (v.max_hiz_ms != null) return `${v.max_hiz_ms} m/s`;
    return '';
  },
  max_hiz_rpm_only(v) {
    if (v.max_hiz_rpm == null) return '';
    return `${Number(v.max_hiz_rpm).toLocaleString('tr-TR')} Rpm`;
  },
  max_hiz_ms_only(v) {
    if (v.max_hiz_rpm != null && v.max_hiz_ms != null) {
      return `${Number(v.max_hiz_rpm).toLocaleString('tr-TR')}-${v.max_hiz_ms} m/s`;
    }
    if (v.max_hiz_ms != null) return `${v.max_hiz_ms} m/s`;
    if (v.max_hiz_rpm != null) return `${Number(v.max_hiz_rpm).toLocaleString('tr-TR')} Rpm`;
    return '';
  },
  olcu_cap_uzunluk(v) {
    if (v.olcu_cap_mm == null && v.olcu_uzunluk_mm == null) return '';
    return `${v.olcu_cap_mm ?? ''}x${v.olcu_uzunluk_mm ?? ''} mm`.replace(/^x|x$/g, '').trim() || '';
  },
  olcu_saft_uzunluk_uc(v) {
    const parts = [v.saft_mm, v.uzunluk_mm, v.uc_genisligi_mm].filter((x) => x != null);
    if (!parts.length) return '';
    return parts.join(' x ') + (v.uc_genisligi_mm != null ? ' mm' : v.uzunluk_mm != null ? ' mm' : '');
  },
  olcu_saft_uzunluk(v) {
    const parts = [v.saft_mm, v.uzunluk_mm].filter((x) => x != null);
    if (!parts.length) return '';
    return parts.join(' x ') + ' mm';
  },
};

/** Ürün slug → PDF tablo sütunları */
const PRODUCT_TABLE_COLUMNS = {
  'metal-inox-kesme-tasi': [
    { key: 'urun_kodu', label: 'Ürün Kodu' },
    { key: 'daire_capi_mm', label: 'Daire Çapı Ø' },
    { key: 'gobek_capi_mm', label: 'Göbek Çapı Ø' },
    { key: 'kalinlik_mm', label: 'Kalınlık' },
    { key: 'max_hiz_rpm', label: 'Maksimum Hız (Rpm)' },
    { key: 'asindirici_kodu', label: 'Aşındırıcı Kodu' },
    { key: 'kutu_adet', label: 'Kutu' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  '355mm-metal-sabit-tezgah-kesme-diski': [
    { key: 'urun_kodu', label: 'Ürün Kodu' },
    { key: 'daire_capi_mm', label: 'Daire Çapı Ø' },
    { key: 'gobek_capi_mm', label: 'Göbek Çapı Ø' },
    { key: 'kalinlik_mm', label: 'Kalınlık' },
    { key: 'max_hiz_rpm', label: 'Maksimum Hız (Rpm)' },
    { key: 'asindirici_kodu', label: 'Aşındırıcı Kodu' },
    { key: 'kutu_adet', label: 'Kutu' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'metal-inox-taslama-diski': [
    { key: 'urun_kodu', label: 'Ürün Kodu' },
    { key: 'daire_capi_mm', label: 'Daire Çapı Ø' },
    { key: 'gobek_capi_mm', label: 'Göbek Çapı Ø' },
    { key: 'kalinlik_mm', label: 'Kalınlık' },
    { key: 'max_hiz_rpm', label: 'Maksimum Hız (Rpm)' },
    { key: 'asindirici_kodu', label: 'Aşındırıcı Kodu' },
    { key: 'kutu_adet', label: 'Kutu' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'zr-zirkon-flap-disk': [
    { key: 'urun_kodu', label: 'Ürün Kodu' },
    { key: 'daire_capi_mm', label: 'Daire Çapı Ø' },
    { key: 'gobek_capi_mm', label: 'Göbek Çapı Ø' },
    { key: 'asindirici_tipi', label: 'Aşındırıcı Tipi' },
    { compute: 'max_hiz_flap_rpm', label: 'Maksimum Hız (Rpm)' },
    { key: 'grit', label: 'Grit' },
    { key: 'kutu_adet', label: 'Kutu' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'ao-aluminyum-oksit-flap-disk': [
    { key: 'urun_kodu', label: 'Ürün Kodu' },
    { key: 'daire_capi_mm', label: 'Daire Çapı Ø' },
    { key: 'gobek_capi_mm', label: 'Göbek Çapı Ø' },
    { key: 'asindirici_tipi', label: 'Aşındırıcı Tipi' },
    { compute: 'max_hiz_flap_rpm', label: 'Maksimum Hız (Rpm)' },
    { key: 'grit', label: 'Grit' },
    { key: 'kutu_adet', label: 'Kutu' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'segmentli-standart-elmas-kesici': [
    { key: 'urun_kodu', label: 'Ürün Kodu' },
    { key: 'daire_capi_mm', label: 'Daire Çapı Ø' },
    { key: 'gobek_capi_mm', label: 'Göbek Çapı Ø' },
    { compute: 'max_hiz_ms_only', label: 'Maksimum Hız (m/s)' },
    { key: 'kutu_adet', label: 'Kutu' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'ultra-ince-elmas-disk': [
    { key: 'urun_kodu', label: 'Ürün Kodu' },
    { key: 'daire_capi_mm', label: 'Daire Çapı Ø' },
    { key: 'gobek_capi_mm', label: 'Göbek Çapı Ø' },
    { compute: 'max_hiz_rpm_only', label: 'Maksimum Hız (Rpm)' },
    { key: 'kutu_adet', label: 'Kutu' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'granit-ve-mermer-segmentli-taslama-diski': [
    { key: 'urun_kodu', label: 'Ürün Kodu' },
    { key: 'daire_capi_mm', label: 'Daire Çapı Ø' },
    { key: 'gobek_capi_mm', label: 'Göbek Çapı Ø' },
    { compute: 'max_hiz_ms_only', label: 'Maksimum Hız (m/s)' },
    { key: 'kutu_adet', label: 'Kutu' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'asfalt-icin-elmas-kesme-diski': [
    { key: 'urun_kodu', label: 'Ürün Kodu' },
    { key: 'daire_capi_mm', label: 'Daire Çapı Ø' },
    { key: 'gobek_capi_mm', label: 'Göbek Çapı Ø' },
    { compute: 'max_hiz_rpm_only', label: 'Maksimum Hız (Rpm)' },
    { key: 'kutu_adet', label: 'Kutu' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'guclendirilmis-beton-icin-elmas-kesme-diski': [
    { key: 'urun_kodu', label: 'Ürün Kodu' },
    { key: 'daire_capi_mm', label: 'Daire Çapı Ø' },
    { key: 'gobek_capi_mm', label: 'Göbek Çapı Ø' },
    { compute: 'max_hiz_ms_only', label: 'Maksimum Hız (m/s)' },
    { key: 'kutu_adet', label: 'Kutu' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'sds-max-burc-aleti-tarakli-murc': [
    { key: 'urun_kodu', label: 'Ürün Kodu' },
    { key: 'baglanti_tipi', label: 'Bağlantı Tipi' },
    { key: 'kafa_olcusu_mm', label: 'Kafa Ölçüsü' },
    { key: 'uzunluk_mm', label: 'Uzunluk' },
    { key: 'kutu_adet', label: 'Kutu' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'hss-matkap-ucu': [
    { key: 'urun_tipi', label: 'Ürün Tipi' },
    { key: 'cap_mm', label: 'Çap (mm)' },
    { key: 'kullanim_yeri', label: 'Kullanım Yeri' },
    { key: 'kutu_ici_adet', label: 'Kutu İçi Adet' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'sds-plus-4-kesicili-beton-matkap-ucu-quadro': [
    { key: 'urun_tipi', label: 'Ürün Tipi' },
    { key: 'cap_mm', label: 'Çap (mm)' },
    { key: 'toplam_uzunluk_mm', label: 'Toplam Uzunluk (mm)' },
    { key: 'baglanti_tipi', label: 'Bağlantı Tipi' },
    { key: 'kutu_adet', label: 'Kutu' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'miknatisli-anahtar-ucu-manyetik-somun-adaptoru': [
    { key: 'urun_tipi', label: 'Ürün Tipi' },
    { compute: 'olcu_cap_uzunluk', label: 'Ölçü (Çap x Uzunluk)' },
    { key: 'malzeme', label: 'Malzeme' },
    { key: 'kutu_ici_adet', label: 'Kutu İçi Adet' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'ph2-manyetik-bits-uc': [
    { key: 'urun_tipi', label: 'Ürün Tipi' },
    { key: 'uc_tipi', label: 'Uç Tipi' },
    { key: 'uzunluk_mm', label: 'Uzunluk' },
    { key: 'malzeme', label: 'Malzeme' },
    { key: 'kutu_ici_adet', label: 'Kutu İçi Adet' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'duz-keski-sds-plus': [
    { key: 'urun_tipi', label: 'Ürün Tipi' },
    { compute: 'olcu_saft_uzunluk_uc', label: 'Ölçü (Şaft x Uzunluk x Uç Genişliği)' },
    { key: 'baglanti_tipi', label: 'Bağlantı Tipi' },
    { key: 'malzeme', label: 'Malzeme' },
    { key: 'kutu_adet', label: 'Kutu' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'duz-keski-sds-max': [
    { key: 'urun_tipi', label: 'Ürün Tipi' },
    { compute: 'olcu_saft_uzunluk_uc', label: 'Ölçü (Şaft x Uzunluk x Uç Genişliği)' },
    { key: 'baglanti_tipi', label: 'Bağlantı Tipi' },
    { key: 'malzeme', label: 'Malzeme' },
    { key: 'kutu_adet', label: 'Kutu' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'sivri-uclu-keski-murc-sds-plus': [
    { key: 'urun_tipi', label: 'Ürün Tipi' },
    { compute: 'olcu_saft_uzunluk', label: 'Ölçü (Şaft x Uzunluk)' },
    { key: 'baglanti_tipi', label: 'Bağlantı Tipi' },
    { key: 'malzeme', label: 'Malzeme' },
    { key: 'kutu_adet', label: 'Kutu' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'sivri-uclu-keski-murc-sds-max': [
    { key: 'urun_tipi', label: 'Ürün Tipi' },
    { compute: 'olcu_saft_uzunluk', label: 'Ölçü (Şaft x Uzunluk)' },
    { key: 'baglanti_tipi', label: 'Bağlantı Tipi' },
    { key: 'malzeme', label: 'Malzeme' },
    { key: 'kutu_adet', label: 'Kutu' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'cok-fonksiyonlu-cam-ve-seramik-matkap-ucu-4-kesicili': [
    { key: 'urun_tipi', label: 'Ürün Tipi' },
    { key: 'cap_mm', label: 'Çap (mm)' },
    { key: 'saft_tipi', label: 'Şaft Tipi' },
    { key: 'kutu_ici_adet', label: 'Kutu İçi Adet' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'profesyonel-plastik-maket-bicagi': [
    { key: 'urun_tipi', label: 'Ürün Tipi' },
    { key: 'bicak_genisligi_mm', label: 'Bıçak Genişliği' },
    { key: 'govde_kizak_tipi', label: 'Gövde / Kızak Tipi' },
    { key: 'bicak_malzemesi', label: 'Bıçak Malzemesi' },
    { key: 'kutu_ici_adet', label: 'Kutu İçi' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'profesyonel-metal-maket-bicagi': [
    { key: 'urun_tipi', label: 'Ürün Tipi' },
    { key: 'bicak_genisligi_mm', label: 'Bıçak Genişliği' },
    { key: 'govde_kizak_tipi', label: 'Gövde / Kızak Tipi' },
    { key: 'bicak_malzemesi', label: 'Bıçak Malzemesi' },
    { key: 'kutu_ici_adet', label: 'Kutu İçi' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'maket-bicagi-yedek-ucu': [
    { key: 'urun_tipi', label: 'Ürün Tipi' },
    { key: 'bicak_genisligi_mm', label: 'Bıçak Genişliği' },
    { key: 'paket_icerigi', label: 'Paket İçeriği' },
    { key: 'bicak_malzemesi', label: 'Bıçak Malzemesi' },
    { key: 'kutu_ici_adet', label: 'Kutu İçi' },
    { key: 'koli_adet', label: 'Koli' },
  ],
  'abs-govdeli-profesyonel-serit-metre': [
    { key: 'urun_tipi', label: 'Ürün Tipi' },
    { key: 'uzunluk_m', label: 'Uzunluk' },
    { key: 'serit_genisligi_mm', label: 'Şerit Genişliği' },
    { key: 'kasa_malzemesi', label: 'Kasa Malzemesi' },
    { key: 'kutu_ici_adet', label: 'Kutu İçi Adet' },
    { key: 'koli_adet', label: 'Koli' },
  ],
};

function formatVariantValue(key, value) {
  if (value === null || value === undefined || value === '') return '';
  if (key === 'daire_capi_mm') return `Ø ${value} mm`;
  if (key === 'gobek_capi_mm') return `${value} mm`;
  if (key === 'kalinlik_mm') return `${value} mm`;
  if (key === 'max_hiz_rpm') return `${Number(value).toLocaleString('tr-TR')} Rpm`;
  if (key === 'max_hiz_ms') return `${value} m/s`;
  if (key === 'cap_mm') return `${value} mm`;
  if (key === 'uzunluk_mm' || key === 'toplam_uzunluk_mm') return `${value} mm`;
  if (key === 'uzunluk_m') return `${value} m`;
  if (key === 'serit_genisligi_mm') return `${value} mm`;
  if (key === 'bicak_genisligi_mm') return `${value} mm`;
  if (key === 'kafa_olcusu_mm') return `${value}`;
  if (key === 'koli_adet' && (value === '-' || value === '–')) return '-';
  return String(value);
}

function getCellValue(variant, col) {
  if (col.compute && COLUMN_COMPUTERS[col.compute]) {
    return COLUMN_COMPUTERS[col.compute](variant);
  }
  const raw = col.key === 'urun_kodu' ? variant.urun_kodu ?? variant.id : variant[col.key];
  return formatVariantValue(col.key, raw);
}

function getTableColumns(product) {
  if (product.tableColumns?.length) return product.tableColumns;
  if (product.slug && PRODUCT_TABLE_COLUMNS[product.slug]) {
    return PRODUCT_TABLE_COLUMNS[product.slug];
  }
  return [];
}

function variantRowCells(variant, columns) {
  return columns.map((col) => getCellValue(variant, col));
}

function variantSpecLines(variant, product) {
  const columns = getTableColumns(product);
  return columns
    .map((col) => {
      const value = getCellValue(variant, col);
      if (!value) return null;
      return { key: col.key || col.compute, label: col.label, value };
    })
    .filter(Boolean);
}

function variantLabel(variant, productName) {
  const code = variant.urun_kodu || variant.id;
  if (code && !String(code).includes('-v')) {
    return `${productName} · ${code}`;
  }
  const cap = variant.daire_capi_mm || variant.cap_mm;
  if (cap) return `${productName} · Ø${cap} mm`;
  if (variant.uzunluk_mm) return `${productName} · ${variant.uzunluk_mm} mm`;
  if (variant.uzunluk_m) return `${productName} · ${variant.uzunluk_m} m`;
  if (variant.urun_tipi) return `${productName} · ${variant.urun_tipi}`;
  return productName;
}
