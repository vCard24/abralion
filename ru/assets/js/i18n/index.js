(function () {
  'use strict';

  window.I18N_MESSAGES = window.I18N_MESSAGES || {};

  function detectLocale() {
    const lang = (document.documentElement.lang || '').toLowerCase();
    if (lang.startsWith('ru')) return 'ru';
    return 'tr';
  }

  const LOCALE = detectLocale();
  window.ABRALION_LOCALE = LOCALE;
  window.ABRALION_SITE_ORIGIN = 'https://abralion.com/ru';
  window.ABRALION_TR_SITE_ORIGIN = 'https://abralion.com';
  window.ABRALION_OG_LOCALE = LOCALE === 'ru' ? 'ru_RU' : 'tr_TR';

  window.getLocale = function getLocale() {
    return window.ABRALION_LOCALE || LOCALE;
  };

  window.getOgLocale = function getOgLocale() {
    return window.ABRALION_OG_LOCALE || (window.getLocale() === 'ru' ? 'ru_RU' : 'tr_TR');
  };

  /** BCP 47 tag for Intl / toLocaleString (ru-RU | tr-TR). */
  window.getIntlLocale = function getIntlLocale() {
    return window.getLocale() === 'ru' ? 'ru-RU' : 'tr-TR';
  };

  window.t = function t(key, params) {
    const locale = window.getLocale();
    const bucket = window.I18N_MESSAGES[locale];
    let text = bucket && bucket[key];
    if (text == null) {
      console.warn('[i18n] missing key:', key);
      return key;
    }
    if (params && typeof params === 'object') {
      Object.keys(params).forEach((name) => {
        text = String(text).replace(new RegExp(`\\{${name}\\}`, 'g'), String(params[name]));
      });
    }
    return text;
  };

  window.formatNumber = function formatNumber(value) {
    const n = Number(value);
    if (!Number.isFinite(n)) return String(value ?? '');
    return new Intl.NumberFormat(window.getIntlLocale()).format(n);
  };

  window.formatDateTime = function formatDateTime(date) {
    const d = date instanceof Date ? date : new Date(date);
    return d.toLocaleString(window.getIntlLocale());
  };

  /** Relative catalog JSON path for the active locale (RU must not fall back to TR). */
  window.getCatalogDataPath = function getCatalogDataPath() {
    return window.getLocale() === 'ru' ? 'data/products-ru.json' : 'data/products.json';
  };
})();
