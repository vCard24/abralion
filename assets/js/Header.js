class Header {
  constructor() {
    this.mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    this.headerNav = document.querySelector('.header-nav');
    this.headerEl = document.querySelector('.header');
    this.searchInput = document.getElementById('header-search-input');
    this.searchBtn = document.getElementById('header-search-btn');
    this.navLinks = document.querySelectorAll('.header-nav-link');
    this.backdrop = null;
    this.navAnchor = null;
    this.navInsertBefore = null;
    this.mobileMq = window.matchMedia('(max-width: 768px)');
    this.init();
  }

  init() {
    this.ensureBackdrop();
    this.syncHeaderHeight();
    this.setupMobileNavPortal();
    this.setupMobileMenu();
    this.setupDropdown();
    this.setupSearch();
    this.highlightActivePage();
    window.addEventListener('resize', () => {
      this.syncHeaderHeight();
      this.setupMobileNavPortal();
    });
    this.mobileMq.addEventListener('change', () => this.setupMobileNavPortal());
  }

  setupMobileNavPortal() {
    if (!this.headerNav) return;
    const container = document.querySelector('.header-container');
    if (!container) return;

    if (this.mobileMq.matches) {
      if (this.headerNav.parentElement === document.body) return;
      this.navAnchor = container;
      this.navInsertBefore = this.mobileMenuToggle || null;
      document.body.appendChild(this.headerNav);
      return;
    }

    if (this.headerNav.parentElement !== document.body) return;
    if (this.navAnchor && this.navAnchor.isConnected) {
      this.navAnchor.insertBefore(this.headerNav, this.navInsertBefore);
    } else if (container) {
      container.appendChild(this.headerNav);
    }
  }

  ensureBackdrop() {
    if (this.backdrop) return;
    this.backdrop = document.createElement('div');
    this.backdrop.className = 'mobile-nav-backdrop';
    this.backdrop.hidden = true;
    this.backdrop.addEventListener('click', () => this.setMobileNavOpen(false));
    document.body.appendChild(this.backdrop);
  }

  syncHeaderHeight() {
    if (!this.headerEl) return;
    const h = Math.ceil(this.headerEl.getBoundingClientRect().height);
    document.documentElement.style.setProperty('--header-mobile-height', `${h}px`);
  }

  setMobileNavOpen(open) {
    if (!this.mobileMenuToggle || !this.headerNav) return;
    this.mobileMenuToggle.classList.toggle('active', open);
    this.headerNav.classList.toggle('active', open);
    this.mobileMenuToggle.setAttribute('aria-expanded', String(open));
    this.headerNav.setAttribute('aria-hidden', String(!open));
    document.body.classList.toggle('mobile-nav-open', open);
    if (this.backdrop) this.backdrop.hidden = !open;
    if (!open) {
      document.querySelectorAll('.header-nav-dropdown.active').forEach((dropdown) => {
        dropdown.classList.remove('active');
      });
    }
  }

  setupMobileMenu() {
    if (!this.mobileMenuToggle || !this.headerNav) return;

    this.headerNav.setAttribute('aria-hidden', 'true');

    this.mobileMenuToggle.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      const isExpanded = this.mobileMenuToggle.getAttribute('aria-expanded') === 'true';
      this.setMobileNavOpen(!isExpanded);
    });

    document.addEventListener(
      'click',
      (e) => {
        if (this.mobileMenuToggle.getAttribute('aria-expanded') !== 'true') return;
        if (
          e.target.closest('.header-nav') ||
          e.target.closest('.mobile-menu-toggle') ||
          e.target.closest('.mobile-nav-backdrop')
        ) {
          return;
        }
        this.setMobileNavOpen(false);
      },
      true
    );

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.mobileMenuToggle.getAttribute('aria-expanded') === 'true') {
        this.setMobileNavOpen(false);
        this.mobileMenuToggle.focus();
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
      const arrow = dropdown.querySelector('.dropdown-arrow');
      if (!link) return;

      if (arrow) {
        arrow.setAttribute('role', 'button');
        arrow.setAttribute('tabindex', '0');
        arrow.setAttribute('aria-label', 'Alt menüyü aç/kapat');
      }

      const toggleDropdown = (e) => {
        if (window.innerWidth > 768) return;
        e.preventDefault();
        e.stopPropagation();
        const willOpen = !dropdown.classList.contains('active');
        document.querySelectorAll('.header-nav-dropdown.active').forEach((other) => {
          if (other !== dropdown) other.classList.remove('active');
        });
        dropdown.classList.toggle('active', willOpen);
      };

      if (arrow) {
        arrow.addEventListener('click', toggleDropdown);
        arrow.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') toggleDropdown(e);
        });
      }

      link.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 && e.target.closest('.dropdown-arrow')) {
          return;
        }
        if (window.innerWidth <= 768 && dropdown.querySelector('.mega-menu, .dropdown-menu')?.children?.length) {
          const hasSubmenu = dropdown.querySelector('.mega-menu-tabs, .dropdown-menu li');
          if (hasSubmenu && !dropdown.classList.contains('active')) {
            e.preventDefault();
            toggleDropdown(e);
            return;
          }
        }
        this.setMobileNavOpen(false);
      });
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
      this.setMobileNavOpen(false);
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
