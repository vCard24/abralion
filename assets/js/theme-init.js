(function () {
  var theme = 'dark';
  try {
    theme = localStorage.getItem('theme') || 'dark';
    if (theme === 'dark') {
      document.documentElement.classList.add('dark-theme', 'dark');
    }
  } catch (e) {
    document.documentElement.classList.add('dark-theme', 'dark');
  }

  function applyLogos() {
    var base = document.body ? document.body.getAttribute('data-base') || '' : '';
    var src = base + 'assets/images/' + (theme === 'dark' ? 'logo-beyaz.svg' : 'logo.svg');
    document.querySelectorAll('[data-logo]').forEach(function (img) {
      img.src = src;
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyLogos);
  } else {
    applyLogos();
  }
})();
