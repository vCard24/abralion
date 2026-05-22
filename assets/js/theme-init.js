(function () {
  try {
    var theme = localStorage.getItem('theme') || 'dark';
    if (theme === 'dark') {
      document.documentElement.classList.add('dark-theme');
    }
  } catch (e) {
    document.documentElement.classList.add('dark-theme');
  }
})();
