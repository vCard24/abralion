document.addEventListener('DOMContentLoaded', () => {
  if (typeof Header !== 'undefined') new Header();
  if (window.compareManager) {
    window.compareManager.ensureBar();
    window.compareManager.updateUI();
  }
});
