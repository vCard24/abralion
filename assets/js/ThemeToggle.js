function readStoredTheme() {
  try {
    return localStorage.getItem('theme') || 'dark';
  } catch {
    return 'dark';
  }
}

function writeStoredTheme(theme) {
  try {
    localStorage.setItem('theme', theme);
  } catch {
    /* ignore */
  }
}

class ThemeToggle {
  constructor() {
    this.currentTheme = readStoredTheme();
    this.init();
  }

  init() {
    this.createToggleButton();
    this.applyTheme(this.currentTheme);
    this.toggleButton.addEventListener('click', () => {
      this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
      this.applyTheme(this.currentTheme);
      writeStoredTheme(this.currentTheme);
    });
  }

  createToggleButton() {
    const btn = document.createElement('button');
    btn.id = 'theme-toggle';
    btn.className = 'theme-toggle-btn';
    btn.setAttribute('aria-label', 'Tema değiştir');
    document.body.appendChild(btn);
    this.toggleButton = btn;
  }

  applyTheme(theme) {
    const moon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    const sun = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/></svg>';
    if (theme === 'dark') {
      document.body.classList.add('dark-theme');
      if (this.toggleButton) {
        this.toggleButton.innerHTML = `<span class="theme-icon">${sun}</span>`;
      }
    } else {
      document.body.classList.remove('dark-theme');
      if (this.toggleButton) {
        this.toggleButton.innerHTML = `<span class="theme-icon">${moon}</span>`;
      }
    }
    this.updateLogos(theme);
    this.currentTheme = theme;
  }

  updateLogos(theme) {
    const base = getBasePath();
    const light = `${base}assets/images/logo.svg`;
    const dark = `${base}assets/images/logo-beyaz.svg`;
    const src = theme === 'dark' ? dark : light;
    document.querySelectorAll('[data-logo]').forEach((img) => {
      img.src = src;
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.themeToggle = new ThemeToggle();
});
