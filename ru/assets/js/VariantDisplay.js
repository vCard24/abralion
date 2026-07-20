/**
 * Teknik tablo sütunları — PDF kataloğu ile birebir.
 * Boş değerler boş hücre olarak kalır (— kullanılmaz).
 */

/* exported getTableColumns, getSpecColumnClass, variantRowCells, variantSpecLines, variantLabel */

function fmtNum(value) {
  if (typeof formatNumber === 'function') return formatNumber(value);
  const locale =
    typeof getIntlLocale === 'function'
      ? getIntlLocale()
      : document.documentElement.lang?.toLowerCase().startsWith('ru')
        ? 'ru-RU'
        : 'tr-TR';
  return Number(value).toLocaleString(locale);
}

const COLUMN_COMPUTERS = {
  max_hiz_flap_rpm(v) {
    if (v.max_hiz_rpm != null && v.max_hiz_ms != null) {
      return `${fmtNum(v.max_hiz_rpm)}-${v.max_hiz_ms} м/с`;
    }
    if (v.max_hiz_rpm != null) return `${fmtNum(v.max_hiz_rpm)} об/мин`;
    if (v.max_hiz_ms != null) return `${v.max_hiz_ms} м/с`;
    return '';
  },
  max_hiz_rpm_only(v) {
    if (v.max_hiz_rpm == null) return '';
    return `${fmtNum(v.max_hiz_rpm)} об/мин`;
  },
  max_hiz_ms_only(v) {
    if (v.max_hiz_rpm != null && v.max_hiz_ms != null) {
      return `${fmtNum(v.max_hiz_rpm)}-${v.max_hiz_ms} м/с`;
    }
    if (v.max_hiz_ms != null) return `${v.max_hiz_ms} м/с`;
    if (v.max_hiz_rpm != null) return `${fmtNum(v.max_hiz_rpm)} об/мин`;
    return '';
  },
  olcu_cap_uzunluk(v) {
    if (v.olcu_cap_mm == null && v.olcu_uzunluk_mm == null) return '';
    return (
      `${v.olcu_cap_mm ?? ''}x${v.olcu_uzunluk_mm ?? ''} mm`.replace(/^x|x$/g, '').trim() || ''
    );
  },
  olcu_saft_uzunluk_uc(v) {
    const parts = [v.saft_mm, v.uzunluk_mm, v.uc_genisligi_mm].filter((x) => x != null);
    if (!parts.length) return '';
    return (
      parts.join(' x ') + (v.uc_genisligi_mm != null ? ' mm' : v.uzunluk_mm != null ? ' mm' : '')
    );
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
    { key: 'urun_kodu', label: 'spec.urun_kodu' },
    { key: 'daire_capi_mm', label: 'spec.daire_capi' },
    { key: 'gobek_capi_mm', label: 'spec.gobek_capi' },
    { key: 'kalinlik_mm', label: 'spec.kalinlik' },
    { key: 'max_hiz_rpm', label: 'spec.max_hiz_rpm' },
    { key: 'asindirici_kodu', label: 'spec.asindirici_kodu' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  '355mm-metal-sabit-tezgah-kesme-diski': [
    { key: 'urun_kodu', label: 'spec.urun_kodu' },
    { key: 'daire_capi_mm', label: 'spec.daire_capi' },
    { key: 'gobek_capi_mm', label: 'spec.gobek_capi' },
    { key: 'kalinlik_mm', label: 'spec.kalinlik' },
    { key: 'max_hiz_rpm', label: 'spec.max_hiz_rpm' },
    { key: 'asindirici_kodu', label: 'spec.asindirici_kodu' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'metal-inox-taslama-diski': [
    { key: 'urun_kodu', label: 'spec.urun_kodu' },
    { key: 'daire_capi_mm', label: 'spec.daire_capi' },
    { key: 'gobek_capi_mm', label: 'spec.gobek_capi' },
    { key: 'kalinlik_mm', label: 'spec.kalinlik' },
    { key: 'max_hiz_rpm', label: 'spec.max_hiz_rpm' },
    { key: 'asindirici_kodu', label: 'spec.asindirici_kodu' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'zr-zirkon-flap-disk': [
    { key: 'urun_kodu', label: 'spec.urun_kodu' },
    { key: 'daire_capi_mm', label: 'spec.daire_capi' },
    { key: 'gobek_capi_mm', label: 'spec.gobek_capi' },
    { key: 'asindirici_tipi', label: 'spec.asindirici_tipi' },
    { compute: 'max_hiz_flap_rpm', label: 'spec.max_hiz_rpm' },
    { key: 'grit', label: 'spec.grit' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'ao-aluminyum-oksit-flap-disk': [
    { key: 'urun_kodu', label: 'spec.urun_kodu' },
    { key: 'daire_capi_mm', label: 'spec.daire_capi' },
    { key: 'gobek_capi_mm', label: 'spec.gobek_capi' },
    { key: 'asindirici_tipi', label: 'spec.asindirici_tipi' },
    { compute: 'max_hiz_flap_rpm', label: 'spec.max_hiz_rpm' },
    { key: 'grit', label: 'spec.grit' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'segmentli-standart-elmas-kesici': [
    { key: 'urun_kodu', label: 'spec.urun_kodu' },
    { key: 'daire_capi_mm', label: 'spec.daire_capi' },
    { key: 'gobek_capi_mm', label: 'spec.gobek_capi' },
    { compute: 'max_hiz_rpm_only', label: 'spec.max_hiz_rpm' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'ultra-ince-elmas-disk': [
    { key: 'urun_kodu', label: 'spec.urun_kodu' },
    { key: 'daire_capi_mm', label: 'spec.daire_capi' },
    { key: 'gobek_capi_mm', label: 'spec.gobek_capi' },
    { compute: 'max_hiz_rpm_only', label: 'spec.max_hiz_rpm' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'granit-ve-mermer-segmentli-taslama-diski': [
    { key: 'urun_kodu', label: 'spec.urun_kodu' },
    { key: 'daire_capi_mm', label: 'spec.daire_capi' },
    { key: 'gobek_capi_mm', label: 'spec.gobek_capi' },
    { compute: 'max_hiz_ms_only', label: 'spec.max_hiz_ms' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'asfalt-icin-elmas-kesme-diski': [
    { key: 'urun_kodu', label: 'spec.urun_kodu' },
    { key: 'daire_capi_mm', label: 'spec.daire_capi' },
    { key: 'gobek_capi_mm', label: 'spec.gobek_capi' },
    { compute: 'max_hiz_rpm_only', label: 'spec.max_hiz_rpm' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'guclendirilmis-beton-icin-elmas-kesme-diski': [
    { key: 'urun_kodu', label: 'spec.urun_kodu' },
    { key: 'daire_capi_mm', label: 'spec.daire_capi' },
    { key: 'gobek_capi_mm', label: 'spec.gobek_capi' },
    { compute: 'max_hiz_ms_only', label: 'spec.max_hiz_ms' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'sds-max-burc-aleti-tarakli-murc': [
    { key: 'urun_kodu', label: 'spec.urun_kodu' },
    { key: 'baglanti_tipi', label: 'spec.baglanti_tipi' },
    { key: 'kafa_olcusu_mm', label: 'spec.kafa_olcusu' },
    { key: 'uzunluk_mm', label: 'spec.uzunluk' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'hss-matkap-ucu': [
    { key: 'urun_tipi', label: 'spec.urun_tipi' },
    { key: 'cap_mm', label: 'spec.cap_mm' },
    { key: 'kullanim_yeri', label: 'spec.kullanim_yeri' },
    { key: 'kutu_ici_adet', label: 'spec.kutu_ici_adet' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'sds-plus-4-kesicili-beton-matkap-ucu-quadro': [
    { key: 'urun_tipi', label: 'spec.urun_tipi' },
    { key: 'cap_mm', label: 'spec.cap_mm' },
    { key: 'toplam_uzunluk_mm', label: 'spec.toplam_uzunluk' },
    { key: 'baglanti_tipi', label: 'spec.baglanti_tipi' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'miknatisli-anahtar-ucu-manyetik-somun-adaptoru': [
    { key: 'urun_tipi', label: 'spec.urun_tipi' },
    { compute: 'olcu_cap_uzunluk', label: 'spec.olcu_cap_uzunluk' },
    { key: 'malzeme', label: 'spec.malzeme' },
    { key: 'kutu_ici_adet', label: 'spec.kutu_ici_adet' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'ph2-manyetik-bits-uc': [
    { key: 'urun_tipi', label: 'spec.urun_tipi' },
    { key: 'uc_tipi', label: 'spec.uc_tipi' },
    { key: 'uzunluk_mm', label: 'spec.uzunluk' },
    { key: 'malzeme', label: 'spec.malzeme' },
    { key: 'kutu_ici_adet', label: 'spec.kutu_ici_adet' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'duz-keski-sds-plus': [
    { key: 'urun_tipi', label: 'spec.urun_tipi' },
    { compute: 'olcu_saft_uzunluk_uc', label: 'spec.olcu_saft_uzunluk_uc' },
    { key: 'baglanti_tipi', label: 'spec.baglanti_tipi' },
    { key: 'malzeme', label: 'spec.malzeme' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'duz-keski-sds-max': [
    { key: 'urun_tipi', label: 'spec.urun_tipi' },
    { compute: 'olcu_saft_uzunluk_uc', label: 'spec.olcu_saft_uzunluk_uc' },
    { key: 'baglanti_tipi', label: 'spec.baglanti_tipi' },
    { key: 'malzeme', label: 'spec.malzeme' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'sivri-uclu-keski-murc-sds-plus': [
    { key: 'urun_tipi', label: 'spec.urun_tipi' },
    { compute: 'olcu_saft_uzunluk', label: 'spec.olcu_saft_uzunluk' },
    { key: 'baglanti_tipi', label: 'spec.baglanti_tipi' },
    { key: 'malzeme', label: 'spec.malzeme' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'sivri-uclu-keski-murc-sds-max': [
    { key: 'urun_tipi', label: 'spec.urun_tipi' },
    { compute: 'olcu_saft_uzunluk', label: 'spec.olcu_saft_uzunluk' },
    { key: 'baglanti_tipi', label: 'spec.baglanti_tipi' },
    { key: 'malzeme', label: 'spec.malzeme' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'cok-fonksiyonlu-cam-ve-seramik-matkap-ucu-4-kesicili': [
    { key: 'urun_tipi', label: 'spec.urun_tipi' },
    { key: 'cap_mm', label: 'spec.cap_mm' },
    { key: 'saft_tipi', label: 'spec.saft_tipi' },
    { key: 'kutu_ici_adet', label: 'spec.kutu_ici_adet' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'cam-seramik-matkap-ucu': [
    { key: 'urun_tipi', label: 'spec.urun_tipi' },
    { key: 'cap_mm', label: 'spec.cap_mm' },
    { key: 'saft_tipi', label: 'spec.saft_tipi' },
    { key: 'kutu_ici_adet', label: 'spec.kutu_ici_adet' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'profesyonel-plastik-maket-bicagi': [
    { key: 'urun_tipi', label: 'spec.urun_tipi' },
    { key: 'bicak_genisligi_mm', label: 'spec.bicak_genisligi' },
    { key: 'govde_kizak_tipi', label: 'spec.govde_kizak_tipi' },
    { key: 'bicak_malzemesi', label: 'spec.bicak_malzemesi' },
    { key: 'kutu_ici_adet', label: 'spec.kutu_ici' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'profesyonel-metal-maket-bicagi': [
    { key: 'urun_tipi', label: 'spec.urun_tipi' },
    { key: 'bicak_genisligi_mm', label: 'spec.bicak_genisligi' },
    { key: 'govde_kizak_tipi', label: 'spec.govde_kizak_tipi' },
    { key: 'bicak_malzemesi', label: 'spec.bicak_malzemesi' },
    { key: 'kutu_ici_adet', label: 'spec.kutu_ici' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'maket-bicagi-yedek-ucu': [
    { key: 'urun_tipi', label: 'spec.urun_tipi' },
    { key: 'bicak_genisligi_mm', label: 'spec.bicak_genisligi' },
    { key: 'paket_icerigi', label: 'spec.paket_icerigi' },
    { key: 'bicak_malzemesi', label: 'spec.bicak_malzemesi' },
    { key: 'kutu_ici_adet', label: 'spec.kutu_ici' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'abs-govdeli-profesyonel-serit-metre': [
    { key: 'urun_tipi', label: 'spec.urun_tipi' },
    { key: 'uzunluk_m', label: 'spec.uzunluk' },
    { key: 'serit_genisligi_mm', label: 'spec.serit_genisligi' },
    { key: 'kasa_malzemesi', label: 'spec.kasa_malzemesi' },
    { key: 'kutu_ici_adet', label: 'spec.kutu_ici_adet' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],

  // --- YENİ ÜRÜNLER (Haziran 2026 Kataloğu) ---
  'granit-mermer-segmentli-taslama-diski': [
    { key: 'urun_kodu', label: 'spec.urun_kodu' },
    { key: 'daire_capi_mm', label: 'spec.daire_capi' },
    { key: 'gobek_capi_mm', label: 'spec.gobek_capi' },
    { compute: 'max_hiz_rpm_only', label: 'spec.max_hiz_rpm' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'asfalt-elmas-kesme-diski': [
    { key: 'urun_kodu', label: 'spec.urun_kodu' },
    { key: 'daire_capi_mm', label: 'spec.daire_capi' },
    { key: 'gobek_capi_mm', label: 'spec.gobek_capi' },
    { compute: 'max_hiz_ms_only', label: 'spec.max_hiz_ms' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'beton-elmas-kesme-diski': [
    { key: 'urun_kodu', label: 'spec.urun_kodu' },
    { key: 'daire_capi_mm', label: 'spec.daire_capi' },
    { key: 'gobek_capi_mm', label: 'spec.gobek_capi' },
    { compute: 'max_hiz_ms_only', label: 'spec.max_hiz_ms' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'genel-amacli-elmas-kesme-diski': [
    { key: 'daire_capi_mm', label: 'spec.daire_capi' },
    { key: 'gobek_capi_mm', label: 'spec.gobek_capi' },
    { compute: 'max_hiz_ms_only', label: 'spec.max_hiz_ms' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'sds-plus-2-kesicili-beton-matkap-ucu': [
    { key: 'urun_tipi', label: 'spec.urun_tipi' },
    { key: 'cap_mm', label: 'spec.cap_mm' },
    { key: 'toplam_uzunluk_mm', label: 'spec.toplam_uzunluk' },
    { key: 'baglanti_tipi', label: 'spec.baglanti_tipi' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'sds-plus-4-kesicili-beton-matkap-ucu': [
    { key: 'cap_mm', label: 'spec.cap_mm' },
    { key: 'saft_tipi', label: 'spec.saft_tipi' },
    { key: 'kutu_ici_adet', label: 'spec.kutu_ici_adet' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'sds-max-burc-aleti': [
    { key: 'baglanti_tipi', label: 'spec.baglanti_tipi' },
    { key: 'kafa_olcusu_mm', label: 'spec.kafa_olcusu' },
    { key: 'uzunluk_mm', label: 'spec.uzunluk' },
    { key: 'kutu_adet', label: 'spec.kutu' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'miknatisli-anahtar-ucu': [
    { key: 'urun_tipi', label: 'spec.urun_tipi' },
    { compute: 'olcu_cap_uzunluk', label: 'spec.olcu_cap_uzunluk' },
    { key: 'malzeme', label: 'spec.malzeme' },
    { key: 'kutu_ici_adet', label: 'spec.kutu_ici_adet' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
  'profesyonel-maket-bicagi': [
    { key: 'urun_tipi', label: 'spec.urun_tipi' },
    { key: 'bicak_genisligi_mm', label: 'spec.bicak_genisligi' },
    { key: 'govde_kizak_tipi', label: 'spec.govde_kizak_tipi' },
    { key: 'bicak_malzemesi', label: 'spec.bicak_malzemesi' },
    { key: 'kutu_ici_adet', label: 'spec.kutu_ici' },
    { key: 'koli_adet', label: 'spec.koli' },
  ],
};


/** Tablo sütun genişliği — dar sayısal / geniş metin alanları */
const SPEC_COL_NARROW = new Set([
  'cap_mm',
  'daire_capi_mm',
  'gobek_capi_mm',
  'kalinlik_mm',
  'kutu_adet',
  'koli_adet',
  'kutu_ici_adet',
  'grit',
  'uzunluk_mm',
  'toplam_uzunluk_mm',
  'bicak_genisligi_mm',
  'kafa_olcusu_mm',
  'serit_genisligi_mm',
  'uzunluk_m',
]);

const SPEC_COL_WIDE = new Set([
  'saft_tipi',
  'kullanim_yeri',
  'malzeme',
  'asindirici_tipi',
  'baglanti_tipi',
  'govde_kizak_tipi',
  'bicak_malzemesi',
  'urun_tipi',
  'asindirici_kodu',
  'uc_tipi',
  'paket_icerigi',
  'kasa_malzemesi',
]);

const SPEC_COL_COMPUTE_WIDE = new Set([
  'olcu_saft_uzunluk_uc',
  'olcu_saft_uzunluk',
  'olcu_cap_uzunluk',
  'max_hiz_flap_rpm',
  'max_hiz_ms_only',
  'max_hiz_rpm_only',
]);

function getSpecColumnClass(col) {
  const id = col.key || col.compute;
  if (!id) return 'spec-col--medium';
  if (id === 'urun_kodu') return 'spec-col--code';
  if (SPEC_COL_NARROW.has(id)) return 'spec-col--narrow';
  if (SPEC_COL_WIDE.has(id) || SPEC_COL_COMPUTE_WIDE.has(id)) return 'spec-col--wide';
  if (id === 'max_hiz_rpm' || id === 'max_hiz_ms') return 'spec-col--medium';
  return 'spec-col--medium';
}

function formatVariantValue(key, value) {
  if (value === null || value === undefined || value === '') return '';
  if (key === 'daire_capi_mm') return `Ø ${value} mm`;
  if (key === 'gobek_capi_mm') return `${value} mm`;
  if (key === 'kalinlik_mm') return `${value} mm`;
  if (key === 'max_hiz_rpm') return `${fmtNum(value)} об/мин`;
  if (key === 'max_hiz_ms') return `${value} м/с`;
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
  const raw = col.key === 'urun_kodu' ? (variant.urun_kodu ?? variant.id) : variant[col.key];
  return formatVariantValue(col.key, raw);
}

function getTableColumns(product) {
  let columns = [];
  if (product.tableColumns?.length) {
    columns = product.tableColumns;
  } else if (product.slug && PRODUCT_TABLE_COLUMNS[product.slug]) {
    columns = PRODUCT_TABLE_COLUMNS[product.slug];
  }
  return columns.map((col) => ({
    ...col,
    label: typeof t === 'function' ? t(col.label) : col.label,
  }));
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
