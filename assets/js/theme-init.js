/* İlk boyamadan önce tema — localStorage yoksa dark */
(function () {
  var theme = localStorage.getItem('theme') || 'dark';
  if (theme === 'dark' && document.body) {
    document.body.classList.add('dark-theme');
  }
})();
