/* exported Header */
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
    this.desktopMq = window.matchMedia('(min-width: 769px)');
    this.init();
  }

  ensureCompareNavLink() {
    const navList = document.querySelector('.header-nav-list');
    if (!navList || navList.querySelector('.header-nav-compare')) return;

    const headerCompare = document.querySelector('.header-compare-link');
    const base = typeof getBasePath === 'function' ? getBasePath() : '';
    const href = headerCompare?.getAttribute('href') || `${base}karsilastir.html`;
    const badge = headerCompare?.querySelector('.compare-badge');
    const count = badge?.textContent?.trim() || '0';

    const li = document.createElement('li');
    li.className = 'header-nav-compare md:hidden';
    li.innerHTML = `
      <a href="${href}" class="header-nav-link font-body-md text-body-md text-on-surface-variant transition-colors">
        Karşılaştır
        <span class="compare-badge bg-surface-container-highest px-1.5 rounded text-xs font-bold"${badge?.style.display === 'none' ? ' style="display: none;"' : ''}>${count}</span>
      </a>`;
    navList.appendChild(li);

    window.addEventListener('compareListUpdated', (e) => {
      const navBadge = li.querySelector('.compare-badge');
      if (!navBadge) return;
      const n = e.detail?.count ?? 0;
      navBadge.textContent = String(n);
      navBadge.style.display = n > 0 ? 'inline-block' : 'none';
    });
  }

  init() {
    this.ensureCompareNavLink();
    this.ensureBackdrop();
    this.setupMobileNavPortal();
    this.setupMobileMenu();
    this.setupDropdown();
    this.setupSearch();
    this.highlightActivePage();
    window.addEventListener('resize', () => {
      this.setupMobileNavPortal();
      this.syncNavAccessibility();
    });
    this.mobileMq.addEventListener('change', () => {
      this.setupMobileNavPortal();
      this.syncNavAccessibility();
    });
  }

  setupMobileNavPortal() {
    if (!this.headerNav) return;
    const container = document.querySelector('.header-container');
    const brandNav = document.querySelector('.header-brand-nav');
    if (!container) return;

    if (this.mobileMq.matches) {
      if (this.headerNav.parentElement === document.body) return;
      this.navAnchor = brandNav || container;
      this.navInsertBefore = null;
      this.headerNav.classList.add('header-nav--mobile-drawer');
      document.body.appendChild(this.headerNav);
      return;
    }

    this.headerNav.classList.remove('header-nav--mobile-drawer');

    if (this.headerNav.parentElement !== document.body) return;
    if (this.navAnchor && this.navAnchor.isConnected) {
      if (this.navInsertBefore) {
        this.navAnchor.insertBefore(this.headerNav, this.navInsertBefore);
      } else {
        this.navAnchor.appendChild(this.headerNav);
      }
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

  isMobileMenuOpen() {
    return this.mobileMenuToggle?.getAttribute('aria-expanded') === 'true';
  }

  getNavFocusableElements() {
    if (!this.headerNav) return [];
    return [
      ...this.headerNav.querySelectorAll(
        'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
      ),
    ];
  }

  setNavFocusable(enabled) {
    this.getNavFocusableElements().forEach((el) => {
      if (enabled) {
        if ('prevTabindex' in el.dataset) {
          if (el.dataset.prevTabindex === '') el.removeAttribute('tabindex');
          else el.setAttribute('tabindex', el.dataset.prevTabindex);
          delete el.dataset.prevTabindex;
        }
        return;
      }
      if (!('prevTabindex' in el.dataset)) {
        el.dataset.prevTabindex = el.getAttribute('tabindex') ?? '';
      }
      el.setAttribute('tabindex', '-1');
    });
  }

  setDropdownArrowsInteractive(enabled) {
    if (!this.headerNav) return;
    this.headerNav.querySelectorAll('.dropdown-arrow').forEach((arrow) => {
      if (enabled && this.mobileMq.matches) {
        arrow.removeAttribute('aria-hidden');
        arrow.setAttribute('role', 'button');
        arrow.setAttribute('tabindex', '0');
        arrow.setAttribute('aria-label', 'Alt menüyü aç/kapat');
        return;
      }
      arrow.setAttribute('aria-hidden', 'true');
      arrow.removeAttribute('role');
      arrow.removeAttribute('tabindex');
      arrow.removeAttribute('aria-label');
    });
  }

  syncNavAccessibility() {
    if (!this.headerNav) return;

    const isMobile = this.mobileMq.matches;
    const menuOpen = this.isMobileMenuOpen();

    if (!isMobile) {
      this.headerNav.removeAttribute('aria-hidden');
      this.headerNav.removeAttribute('inert');
      this.setNavFocusable(true);
      this.setDropdownArrowsInteractive(false);
      return;
    }

    const hidden = !menuOpen;
    this.headerNav.setAttribute('aria-hidden', String(hidden));
    if (hidden) this.headerNav.setAttribute('inert', '');
    else this.headerNav.removeAttribute('inert');
    this.setNavFocusable(!hidden);
    this.setDropdownArrowsInteractive(!hidden);
  }

  setMobileNavOpen(open) {
    if (!this.mobileMenuToggle || !this.headerNav) return;
    this.mobileMenuToggle.classList.toggle('active', open);
    this.headerNav.classList.toggle('active', open);
    this.mobileMenuToggle.setAttribute('aria-expanded', String(open));
    document.body.classList.toggle('mobile-nav-open', open);
    if (this.backdrop) this.backdrop.hidden = !open;
    if (!open) {
      document.querySelectorAll('.header-nav-dropdown.active').forEach((dropdown) => {
        dropdown.classList.remove('active');
      });
    }
    this.syncNavAccessibility();
  }

  setupMobileMenu() {
    if (!this.mobileMenuToggle || !this.headerNav) return;

    this.mobileMenuToggle.setAttribute('aria-expanded', 'false');
    this.syncNavAccessibility();

    this.mobileMenuToggle.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      this.setMobileNavOpen(!this.isMobileMenuOpen());
    });

    document.addEventListener(
      'click',
      (e) => {
        if (!this.isMobileMenuOpen()) return;
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
      if (e.key === 'Escape' && this.isMobileMenuOpen()) {
        this.setMobileNavOpen(false);
        this.mobileMenuToggle.focus();
      }
    });

    window.addEventListener('resize', () => {
      if (this.desktopMq.matches) {
        this.setMobileNavOpen(false);
      }
    });
  }

  setupDropdown() {
    document.querySelectorAll('.header-nav-dropdown').forEach((dropdown) => {
      const link = dropdown.querySelector('.header-nav-link');
      const arrow = dropdown.querySelector('.dropdown-arrow');
      if (!link) return;

      const toggleDropdown = (e) => {
        if (this.desktopMq.matches) return;
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
        if (!this.desktopMq.matches && e.target.closest('.dropdown-arrow')) {
          return;
        }
        if (
          !this.desktopMq.matches &&
          dropdown.querySelector('.mega-menu, .dropdown-menu')?.children?.length
        ) {
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
      const linkPage = href
        .split('?')[0]
        .replace(/^\.\//, '')
        .replace(/^\.\.\//, '');
      let isActive = linkPage === page || (page === '' && linkPage === 'index.html');
      if (inProductPage && linkPage === 'urunler.html') isActive = true;
      link.classList.toggle('active', isActive);
    });
  }
}
