class Header {
  constructor() {
    this.mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    this.headerNav = document.querySelector('.header-nav');
    this.searchInput = document.getElementById('header-search-input');
    this.searchBtn = document.getElementById('header-search-btn');
    this.navLinks = document.querySelectorAll('.header-nav-link');
    this.init();
  }

  init() {
    this.setupMobileMenu();
    this.setupDropdown();
    this.setupSearch();
    this.highlightActivePage();
  }

  setMobileNavOpen(open) {
    if (!this.mobileMenuToggle || !this.headerNav) return;
    this.mobileMenuToggle.classList.toggle('active', open);
    this.headerNav.classList.toggle('active', open);
    this.mobileMenuToggle.setAttribute('aria-expanded', String(open));
    document.body.classList.toggle('mobile-nav-open', open);
    if (!open) {
      document.querySelectorAll('.header-nav-dropdown.active').forEach((dropdown) => {
        dropdown.classList.remove('active');
      });
    }
  }

  setupMobileMenu() {
    if (!this.mobileMenuToggle || !this.headerNav) return;
    this.mobileMenuToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      const isExpanded = this.mobileMenuToggle.getAttribute('aria-expanded') === 'true';
      this.setMobileNavOpen(!isExpanded);
    });
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.header-nav') && !e.target.closest('.mobile-menu-toggle')) {
        this.setMobileNavOpen(false);
      }
    });
    window.addEventListener('resize', () => {
      if (window.innerWidth > 768) {
        this.setMobileNavOpen(false);
      }
    });
  }

  setupDropdown() {
    document.querySelectorAll('.header-nav-dropdown').forEach((dropdown) => {
      const link = dropdown.querySelector('.header-nav-link');
      if (link) {
        link.addEventListener('click', (e) => {
          if (window.innerWidth <= 768) {
            e.preventDefault();
            const willOpen = !dropdown.classList.contains('active');
            document.querySelectorAll('.header-nav-dropdown.active').forEach((other) => {
              if (other !== dropdown) other.classList.remove('active');
            });
            dropdown.classList.toggle('active', willOpen);
          }
        });
      }
    });
  }

  setupSearch() {
    if (!this.searchInput || !this.searchBtn) return;
    this.searchBtn.addEventListener('click', () => this.performSearch());
    this.searchInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        this.performSearch();
      }
    });
  }

  performSearch() {
    const query = this.searchInput.value.trim();
    const base = getBasePath();
    if (query) {
      window.location.href = `${base}urunler.html?search=${encodeURIComponent(query)}`;
    }
  }

  highlightActivePage() {
    const path = window.location.pathname;
    const page = path.split('/').pop() || 'index.html';
    const inProductPage = path.includes('/urun/');

    this.navLinks.forEach((link) => {
      const href = link.getAttribute('href') || '';
      const linkPage = href.split('?')[0].replace(/^\.\//, '').replace(/^\.\.\//, '');
      let isActive = linkPage === page || (page === '' && linkPage === 'index.html');
      if (inProductPage && linkPage === 'urunler.html') isActive = true;
      link.classList.toggle('active', isActive);
    });
  }
}
