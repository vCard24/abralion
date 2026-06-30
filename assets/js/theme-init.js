/** Abralion — yalnızca koyu tema (light mode yok) */
(function () {
  document.documentElement.classList.add('dark-theme', 'dark');
  try {
    localStorage.setItem('theme', 'dark');
  } catch {
    /* ignore */
  }

  function applyDarkBody() {
    document.body.classList.add('dark-theme');
  }

  function applyLogos() {
    const base = document.body ? document.body.getAttribute('data-base') || '' : '';
    const src = `${base}assets/images/logo-beyaz.svg`;
    document.querySelectorAll('[data-logo]').forEach((img) => {
      img.src = src;
    });
  }

  function onReady() {
    applyDarkBody();
    applyLogos();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', onReady);
  } else {
    onReady();
  }
})();
