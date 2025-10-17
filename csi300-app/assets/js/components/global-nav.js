/**
 * Global Navigation Component - Apple-inspired design
 * Handles navigation menu interactions and responsive behavior
 */
class GlobalNav {
    constructor() {
        this.activeSubmenu = null;
        this.activeMenuItem = null;
        this.mobileMenuOpen = false;
        this.hideTimeout = null;
        this.hoverBlockedUntil = 0;
        this.navElement = null;
        this.navContent = null;
        this.dropdownHost = null;
        this.dropdownHideHandler = null;
        this.navListElement = null;
        this.mobileMenuElement = null;
        this.companyNavItem = null;
        this.mobileCompanyGroup = null;
        this.companyMenuTitle = 'Company Insights';
        this.companyContext = null;
        this.activeSubmenuType = null;
        const rootInfo = this.getRootInfo();
        this.rootUrl = rootInfo.href;
        this.rootPath = rootInfo.path;
        this.primaryMenus = [
            { id: 'industry', label: 'Industry', href: 'index.html', analyticsTitle: 'industry hub' },
            { id: 'themes', label: 'Hot Themes', href: 'themes-information.html', analyticsTitle: 'hot themes' }
        ];
        this.submenuData = {
            industry: {
                groups: [
                    {
                        title: 'Industry Toolkit',
                        items: [
                            { text: 'Industry Primer', href: 'industry-primers.html' },
                            { text: 'Value Chain Explorer', href: 'value-chain.html' },
                            { text: 'Company Comparison', href: 'peer-comparison.html' },
                            { text: 'Competitor Analysis', href: 'competitor-analysis.html' },
                            { text: 'IM View', href: 'im-view.html' }
                        ]
                    },
                    {
                        title: 'Comparison Tools',
                        items: [
                            { text: 'Company Comparison', href: 'peer-comparison.html' },
                            { text: 'Moat Analysis', href: 'moat-analysis.html' }
                        ]
                    }
                ]
            },
            themes: {
                groups: [
                    {
                        title: 'Themes Coverage',
                        items: [
                            { text: 'Themes Information', href: 'themes-information.html' },
                            { text: 'Industry Benefit', href: 'industry-benefit.html' },
                            { text: 'Competitor Benefit', href: 'competitor-benefit.html' }
                        ]
                    }
                ]
            }
        };
        this.init();
    }

    getRootInfo() {
        const fallbackOrigin = (typeof window !== 'undefined' && window.location && window.location.origin && window.location.origin !== 'null')
            ? window.location.origin
            : '';

        const defaultHref = fallbackOrigin ? `${fallbackOrigin}/` : '/';
        const defaultPath = '/';

        if (typeof document === 'undefined') {
            return { href: defaultHref, path: defaultPath };
        }

        try {
            const scripts = document.getElementsByTagName('script');
            for (let i = scripts.length - 1; i >= 0; i--) {
                const src = scripts[i].getAttribute('src');
                if (!src) {
                    continue;
                }
                if (src.includes('assets/js/components/global-nav.js')) {
                    const url = new URL(src, window.location.href);
                    const hrefBase = url.href.replace(/assets\/js\/components\/global-nav\.js.*$/, '');
                    const pathBase = url.pathname.replace(/assets\/js\/components\/global-nav\.js.*$/, '');
                    const normalizedHref = hrefBase.endsWith('/') ? hrefBase : `${hrefBase}/`;
                    const normalizedPath = pathBase.endsWith('/') ? pathBase : `${pathBase}/`;
                    return { href: normalizedHref, path: normalizedPath };
                }
            }
        } catch (error) {
            console.warn('Unable to determine global nav root path:', error);
        }

        return { href: defaultHref, path: defaultPath };
    }

    resolveLink(path) {
        if (!path) {
            return '#';
        }

        if (path.startsWith('#') || path.startsWith('mailto:') || /^(?:[a-z]+:)?\/\//i.test(path)) {
            return path;
        }

        if (path.startsWith('/')) {
            try {
                return new URL(path, this.rootUrl).href;
            } catch (error) {
                console.warn('Failed to resolve absolute path in navigation links:', path, error);
                return path;
            }
        }

        try {
            return new URL(path, this.rootUrl).href;
        } catch (error) {
            console.warn('Failed to resolve navigation link:', path, error);
        }

        const normalizedRoot = this.rootPath.endsWith('/') ? this.rootPath : `${this.rootPath}/`;
        return `${normalizedRoot}${path}`.replace(/([^:]\/)\/+/g, '$1');
    }

    init() {
        this.createNavigation();
        this.restoreHoverBlock();
        this.bindEvents();
        window.CSI300GlobalNav = this;
        this.configureCompanyMenuVisibility();
        this.attachActionHandlers(this.mobileCompanyGroup);
        this.attachActionHandlers(this.mobileMenuElement);
    }

    createNavigation() {
        const navHTML = `
            <nav class="globalnav" data-analytics-element-engagement-start="globalnav:onFlyoutOpen" data-analytics-element-engagement-end="globalnav:onFlyoutClose">
                <div class="globalnav-content">
                    <a href="${this.resolveLink('index.html')}" class="globalnav-brand">
                        CSI300 Dashboard
                    </a>
                    <ul class="globalnav-list">
                        <li class="globalnav-item" data-menu="industry">
                            <a href="${this.resolveLink('index.html')}" class="globalnav-link" data-globalnav-item-name="industry" data-analytics-title="industry hub">
                                <span class="globalnav-link-text">Industry</span>
                            </a>
                        </li>
                        <li class="globalnav-item" data-menu="themes">
                            <a href="${this.resolveLink('themes-information.html')}" class="globalnav-link" data-globalnav-item-name="themes" data-analytics-title="hot themes">
                                <span class="globalnav-link-text">Hot Themes</span>
                            </a>
                        </li>
                        <li class="globalnav-item globalnav-item--company" data-menu="company" data-company-nav="desktop" style="display: none;">
                            <a href="${this.resolveLink('investment-summary-overview.html')}" class="globalnav-link" data-globalnav-item-name="company" data-analytics-title="company hub">
                                <span class="globalnav-link-text">Company</span>
                            </a>
                        </li>
                    </ul>

                    <div class="globalnav-menutrigger">
                        <button class="globalnav-menutrigger-button" aria-label="Menu" data-topnav-menu-label-open="Menu" data-topnav-menu-label-close="Close">
                            <svg width="18" height="18" viewBox="0 0 18 18">
                                <polyline class="globalnav-menutrigger-bread globalnav-menutrigger-bread-top"
                                    fill="none" stroke="currentColor" stroke-width="1.2"
                                    stroke-linecap="round" stroke-linejoin="round"
                                    points="2 5, 16 5">
                                </polyline>
                                <polyline class="globalnav-menutrigger-bread globalnav-menutrigger-bread-bottom"
                                    fill="none" stroke="currentColor" stroke-width="1.2"
                                    stroke-linecap="round" stroke-linejoin="round"
                                    points="2 12, 16 12">
                                </polyline>
                            </svg>
                        </button>
                    </div>
                </div>

                <!-- Mobile overlay -->
                <div class="globalnav-mobile-overlay"></div>

                <!-- Mobile menu -->
                <div class="globalnav-mobile-menu">
                    <div class="globalnav-submenu-group" data-company-nav="mobile" style="display: none;">
                        <h3 class="globalnav-submenu-header">Company Insights</h3>
                        <ul class="globalnav-submenu-list">
                            <li class="globalnav-submenu-list-item"><a href="#" class="globalnav-submenu-link" data-nav-action="investment-summary">Investment Summary</a></li>
                            <li class="globalnav-submenu-list-item"><a href="${this.resolveLink('events-alert.html')}" class="globalnav-submenu-link">Events Alert</a></li>
                            <li class="globalnav-submenu-list-item"><a href="#" class="globalnav-submenu-link" data-nav-action="value-chain">Value Chain Analysis</a></li>
                            <li class="globalnav-submenu-list-item"><a href="${this.resolveLink('fund-flow.html')}" class="globalnav-submenu-link">Fund Flow</a></li>
                            <li class="globalnav-submenu-list-item"><a href="#" class="globalnav-submenu-link" data-nav-action="back-to-list">Back to List</a></li>
                        </ul>
                    </div>
                    <div class="globalnav-submenu-group">
                        <h3 class="globalnav-submenu-header">Industry</h3>
                        <ul class="globalnav-submenu-list">
                            <li class="globalnav-submenu-list-item"><a href="${this.resolveLink('index.html')}" class="globalnav-submenu-link">Company Filter</a></li>
                            <li class="globalnav-submenu-list-item"><a href="${this.resolveLink('industry-primers.html')}" class="globalnav-submenu-link globalnav-submenu-link--coming-soon">Industry Primer</a></li>
                            <li class="globalnav-submenu-list-item"><a href="${this.resolveLink('value-chain.html')}" class="globalnav-submenu-link globalnav-submenu-link--coming-soon">Value Chain</a></li>
                            <li class="globalnav-submenu-list-item"><a href="${this.resolveLink('peer-comparison.html')}" class="globalnav-submenu-link">Company Comparison</a></li>
                            <li class="globalnav-submenu-list-item"><a href="${this.resolveLink('competitor-analysis.html')}" class="globalnav-submenu-link globalnav-submenu-link--coming-soon">Competitor Analysis</a></li>
                            <li class="globalnav-submenu-list-item"><a href="${this.resolveLink('im-view.html')}" class="globalnav-submenu-link globalnav-submenu-link--coming-soon">IM View</a></li>
                            <li class="globalnav-submenu-list-item"><a href="${this.resolveLink('browser.html')}" class="globalnav-submenu-link">View All</a></li>
                        </ul>
                    </div>
                    <div class="globalnav-submenu-group">
                        <h3 class="globalnav-submenu-header">Hot Themes</h3>
                        <ul class="globalnav-submenu-list">
                            <li class="globalnav-submenu-list-item"><a href="${this.resolveLink('themes-information.html')}" class="globalnav-submenu-link globalnav-submenu-link--coming-soon">Themes Information</a></li>
                            <li class="globalnav-submenu-list-item"><a href="${this.resolveLink('industry-benefit.html')}" class="globalnav-submenu-link globalnav-submenu-link--coming-soon">Industry Benefit</a></li>
                            <li class="globalnav-submenu-list-item"><a href="${this.resolveLink('competitor-benefit.html')}" class="globalnav-submenu-link globalnav-submenu-link--coming-soon">Competitor Benefit</a></li>
                        </ul>
                    </div>
                </div>
            </nav>
        `;

        // Insert navigation at the beginning of body
        document.body.insertAdjacentHTML('afterbegin', navHTML);

        // Cache references for later use
        this.navElement = document.querySelector('.globalnav');
        this.navContent = this.navElement ? this.navElement.querySelector('.globalnav-content') : null;
        this.navListElement = this.navElement ? this.navElement.querySelector('.globalnav-list') : null;
        this.mobileMenuElement = this.navElement ? this.navElement.querySelector('.globalnav-mobile-menu') : null;
        this.companyNavItem = this.navElement ? this.navElement.querySelector('[data-company-nav="desktop"]') : null;
        this.mobileCompanyGroup = this.navElement ? this.navElement.querySelector('[data-company-nav="mobile"]') : null;

        if (this.navElement && !this.dropdownHost) {
            this.dropdownHost = document.createElement('div');
            this.dropdownHost.className = 'globalnav-dropdown-host';
            this.navElement.appendChild(this.dropdownHost);
        }
    }

    bindEvents() {
        // Desktop hover events with improved logic
        const navItems = document.querySelectorAll('.globalnav-item[data-menu]');
        navItems.forEach(item => {
            item.addEventListener('mouseenter', (e) => {
                if (window.innerWidth > 1068) {
                    if (Date.now() < this.hoverBlockedUntil) {
                        return;
                    }
                    // Clear any existing timeout
                    clearTimeout(this.hideTimeout);
                    this.showSubmenu(e.currentTarget);
                }
            });

            item.addEventListener('mouseleave', () => {
                if (window.innerWidth > 1068) {
                    // Delay hiding to allow mouse to move to submenu
                    clearTimeout(this.hideTimeout);
                    this.hideTimeout = setTimeout(() => {
                        this.hideSubmenu();
                    }, 150);
                }
            });

            // Keyboard navigation
            const link = item.querySelector('.globalnav-link');
            if (link) {
                link.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        if (window.innerWidth > 1068) {
                            this.showSubmenu(item);
                        } else {
                            // Navigate to link on mobile
                            window.location.href = link.href;
                        }
                    } else if (e.key === 'ArrowDown') {
                        e.preventDefault();
                        if (window.innerWidth > 1068) {
                            this.showSubmenu(item);
                            const firstSubmenuLink = item.querySelector('.globalnav-submenu-link');
                            if (firstSubmenuLink) {
                                firstSubmenuLink.focus();
                            }
                        }
                    }
                });
            }
        });

        const navLinks = document.querySelectorAll('.globalnav-list .globalnav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth > 1068) {
                    const blockUntil = Date.now() + 800;
                    sessionStorage.setItem('globalnavHoverBlockUntil', blockUntil.toString());
                    this.hoverBlockedUntil = blockUntil;
                    this.hideSubmenu(true);
                }
            });
        });

        // Handle submenu mouse events to prevent conflicts
        if (this.dropdownHost) {
            this.dropdownHost.addEventListener('mouseenter', () => {
                if (window.innerWidth > 1068) {
                    clearTimeout(this.hideTimeout);
                }
            });

            this.dropdownHost.addEventListener('mouseleave', () => {
                if (window.innerWidth > 1068) {
                    clearTimeout(this.hideTimeout);
                    this.hideTimeout = setTimeout(() => {
                        this.hideSubmenu();
                    }, 150);
                }
            });
        }

        // Mobile menu trigger
        const menuTrigger = document.querySelector('.globalnav-menutrigger-button');
        if (menuTrigger) {
            menuTrigger.addEventListener('click', () => {
                this.toggleMobileMenu();
            });
        }

        // Mobile overlay click
        const overlay = document.querySelector('.globalnav-mobile-overlay');
        if (overlay) {
            overlay.addEventListener('click', () => {
                this.closeMobileMenu();
            });
        }

        // Close mobile menu on navigation link click
        const mobileLinks = document.querySelectorAll('.globalnav-mobile-menu a');
        mobileLinks.forEach(link => {
            link.addEventListener('click', () => {
                this.closeMobileMenu();
            });
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });

        // Close menus when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.globalnav')) {
                this.hideSubmenu();
            }
        });
    }

    showSubmenu(item) {
        if (!this.dropdownHost || window.innerWidth <= 1068) {
            return;
        }

        if (Date.now() < this.hoverBlockedUntil) {
            return;
        }

        const menuType = item.dataset.menu;
        if (!menuType) {
            return;
        }

        if (this.activeMenuItem === item && this.dropdownHost.classList.contains('show')) {
            return;
        }

        clearTimeout(this.hideTimeout);

        const submenu = this.createSubmenu(menuType);
        if (!submenu) {
            return;
        }

        submenu.classList.add('globalnav-submenu--attached');

        // Reset previous state
        if (this.activeMenuItem) {
            this.activeMenuItem.classList.remove('is-active');
        }

        if (this.dropdownHideHandler) {
            this.dropdownHost.removeEventListener('transitionend', this.dropdownHideHandler);
            this.dropdownHideHandler = null;
        }

        this.dropdownHost.innerHTML = '';
        this.dropdownHost.appendChild(submenu);

        // Track active references
        this.activeMenuItem = item;
        this.activeSubmenu = submenu;
        this.activeSubmenuType = menuType;

        item.classList.add('is-active');

        // Attach hover handlers for the newly created submenu
        submenu.addEventListener('mouseenter', () => {
            if (window.innerWidth > 1068) {
                clearTimeout(this.hideTimeout);
            }
        });

        submenu.addEventListener('mouseleave', () => {
            if (window.innerWidth > 1068) {
                clearTimeout(this.hideTimeout);
                this.hideTimeout = setTimeout(() => {
                    this.hideSubmenu();
                }, 150);
            }
        });

        // Animate dropdown host height for a real dropdown feeling
        const targetHeight = submenu.scrollHeight;
        const isOpen = this.dropdownHost.classList.contains('show');
        const currentHeight = isOpen ? this.dropdownHost.getBoundingClientRect().height : 0;

        this.dropdownHost.style.height = `${currentHeight}px`;
        this.dropdownHost.classList.add('show');

        requestAnimationFrame(() => {
            this.dropdownHost.style.height = `${targetHeight}px`;
        });
    }

    hideSubmenu(immediate = false) {
        if (!this.dropdownHost) {
            return;
        }

        const activeSubmenu = this.activeSubmenu;

        if (this.activeMenuItem) {
            this.activeMenuItem.classList.remove('is-active');
            this.activeMenuItem = null;
        }

        if (!activeSubmenu && !this.dropdownHost.classList.contains('show')) {
            this.dropdownHost.innerHTML = '';
            this.dropdownHost.style.height = '';
            return;
        }

        if (immediate) {
            this.dropdownHost.classList.remove('show');
            this.dropdownHost.style.height = '';
            this.dropdownHost.innerHTML = '';
            this.activeSubmenu = null;
            this.activeSubmenuType = null;
            this.dropdownHideHandler = null;
            return;
        }

        this.dropdownHost.style.height = '0px';
        this.dropdownHost.classList.remove('show');

        const handleTransitionEnd = (event) => {
            if (event.propertyName !== 'height') {
                return;
            }

            this.dropdownHost.innerHTML = '';
            this.dropdownHost.style.height = '';
            this.dropdownHideHandler = null;
        };

        this.dropdownHost.addEventListener('transitionend', handleTransitionEnd, { once: true });
        this.dropdownHideHandler = handleTransitionEnd;
        this.activeSubmenu = null;
        this.activeSubmenuType = null;
    }

    restoreHoverBlock() {
        try {
            const stored = sessionStorage.getItem('globalnavHoverBlockUntil');
            if (stored) {
                this.hoverBlockedUntil = parseInt(stored, 10) || 0;
                sessionStorage.removeItem('globalnavHoverBlockUntil');
            }
        } catch (error) {
            console.warn('Unable to restore globalnav hover block state:', error);
            this.hoverBlockedUntil = 0;
        }
    }

    createSubmenu(menuType) {
        const submenuData = {
            company: {
                groups: [
                    {
                        title: this.companyMenuTitle,
                        items: [
                            { text: 'Investment Summary', action: 'investment-summary' },
                            { text: 'Events Alert', href: 'events-alert.html' ,comingSoon: true},
                            { text: 'Value Chain Analysis (demo version)', action: 'value-chain' },
                            { text: 'Fund Flow', href: 'fund-flow.html' ,comingSoon: true},
                        ]
                    },
                    {
                        title: '',
                        items: [
                            { text: '↩ Back to List', action: 'back-to-list' }
                        ]
                    }
                    
                ]
            },
            industry: {
                groups: [
                    {
                        title: 'Industry Overview',
                        items: [
                            { text: 'Company Filter', href: 'index.html' },
                            { text: 'Industry Primer', href: 'industry-primers.html', comingSoon: true },
                            { text: 'Value Chain Explorer', href: 'value-chain.html', comingSoon: true },
                            { text: 'Competitor Analysis', href: 'competitor-analysis.html', comingSoon: true },
                            { text: 'IM View', href: 'im-view.html', comingSoon: true },
                            { text: 'View All', href: 'browser.html' }
                        ]
                    },
                    {
                        title: 'Comparison Tools',
                        items: [
                            { text: 'Company Comparison', href: 'peer-comparison.html' },
                            { text: 'Moat Analysis', href: 'moat-analysis.html', comingSoon: true }
                        ]
                    }
                ]
            },
            themes: {
                groups: [
                    {
                        title: 'Hot Themes',
                        items: [
                            { text: 'Themes Information', href: 'themes-information.html', comingSoon: true },
                            { text: 'Industry Benefit', href: 'industry-benefit.html', comingSoon: true },
                            { text: 'Competitor Benefit', href: 'competitor-benefit.html', comingSoon: true }
                        ]
                    }
                ]
            }
        };

        const data = submenuData[menuType];
        if (!data) return null;

        const submenu = document.createElement('div');
        submenu.className = 'globalnav-submenu';

        submenu.innerHTML = `
            <div class="globalnav-submenu-content" style="--r-globalnav-flyout-elevated-group-count: 1; --r-globalnav-flyout-group-total: ${data.groups.length}; --r-globalnav-flyout-item-total: ${data.groups.reduce((acc, group) => acc + group.items.length, 0)};">
                ${data.groups.map((group, groupIndex) => `
                    <div class="globalnav-submenu-group ${groupIndex === 0 ? 'globalnav-submenu-group-elevated' : ''}" data-analytics-region="submenu-${menuType}-${groupIndex}">
                        <h2 class="globalnav-submenu-header">${group.title}</h2>
                        <ul class="globalnav-submenu-list" aria-labelledby="submenu-${menuType}-${groupIndex}">
                            ${group.items.map(item => `
                                <li class="globalnav-submenu-list-item">
                                    <a href="${item.href ? this.resolveLink(item.href) : '#'}"
                                       class="globalnav-submenu-link${item.action ? ' globalnav-submenu-link--action' : ''}${item.comingSoon ? ' globalnav-submenu-link--coming-soon' : ''}"
                                       data-analytics-title="${item.analyticsTitle || item.text}"${item.action ? ` data-nav-action="${item.action}"` : ''}>
                                        ${item.text}
                                    </a>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                `).join('')}
            </div>
        `;

        this.attachActionHandlers(submenu);

        return submenu;
    }

    attachActionHandlers(root) {
        if (!root) {
            return;
        }

        const actionLinks = root.querySelectorAll('[data-nav-action]');
        actionLinks.forEach(link => {
            if (link.dataset.navActionBound === 'true') {
                return;
            }

            link.addEventListener('click', (event) => {
                const action = link.dataset.navAction;
                if (action && this.handleNavAction(action, event)) {
                    link.blur();
                }
            });

            link.dataset.navActionBound = 'true';
        });
    }

    handleNavAction(action, event) {
        if (!action) {
            return false;
        }

        const hasContext = this.companyContext && this.companyContext.id;
        const appInstance = window.app;
        let handled = false;

        switch (action) {
            case 'investment-summary':
                if (!hasContext) {
                    return false;
                }
                event.preventDefault();
                if (appInstance && typeof appInstance.openInvestmentSummary === 'function') {
                    appInstance.openInvestmentSummary();
                } else {
                    const targetName = encodeURIComponent(this.companyContext.name || 'Unknown Company');
                    const targetId = this.companyContext.id;
                    const summaryPath = this.resolveLink('investment-summary/detail.html');
                    window.location.href = `${summaryPath}?company=${targetName}&id=${targetId}`;
                }
                handled = true;
                break;
            case 'value-chain':
                if (!hasContext) {
                    return false;
                }
                event.preventDefault();
                if (appInstance && typeof appInstance.openValueChainDetail === 'function') {
                    const sector = (typeof appInstance.getImSectorValue === 'function')
                        ? appInstance.getImSectorValue()
                        : (this.companyContext.imSector || '');
                    appInstance.openValueChainDetail(sector);
                } else {
                    const targetName = encodeURIComponent(this.companyContext.name || 'Unknown Company');
                    const targetId = this.companyContext.id;
                    const targetIndustry = this.resolveValueChainIndustry(this.companyContext.imSector);
                    const valueChainPath = this.resolveLink(`value-chain/${targetIndustry}/detail.html`);
                    window.location.href = `${valueChainPath}?company=${targetName}&id=${targetId}`;
                }
                handled = true;
                break;
            case 'back-to-list':
                event.preventDefault();
                handled = this.goBackToFilteredList();
                break;
            default:
                handled = false;
        }

        if (handled) {
            this.hideSubmenu(true);
            if (this.mobileMenuOpen) {
                this.closeMobileMenu();
            }
        }

        return handled;
    }

    goBackToFilteredList() {
        const referrer = document.referrer || '';
        let lastType = null;

        try {
            lastType = sessionStorage.getItem('csi300LastListType');
        } catch (error) {
            console.warn('Failed to read last list type:', error);
        }

        if (!lastType) {
            try {
                if (sessionStorage.getItem('csi300PeerState')) {
                    lastType = 'peer';
                } else if (sessionStorage.getItem('csi300LastBrowserUrl')) {
                    lastType = 'browser';
                }
            } catch (error) {
                console.warn('Failed to infer last list type from stored state:', error);
            }
        }

        const navigateToRelative = (url) => {
            if (!url) {
                return false;
            }
            window.location.href = this.resolveLink(url);
            return true;
        };

        const navigateToAbsolute = (url) => {
            if (!url) {
                return false;
            }
            window.location.href = url;
            return true;
        };

        if (lastType === 'peer') {
            if (referrer.includes('peer-comparison')) {
                if (window.history.length > 1) {
                    window.history.back();
                    return true;
                }
                return navigateToAbsolute(referrer);
            }

            try {
                const storedPeerUrl = sessionStorage.getItem('csi300LastPeerUrl');
                if (navigateToRelative(storedPeerUrl)) {
                    return true;
                }
            } catch (error) {
                console.warn('Failed to read last peer comparison URL from sessionStorage:', error);
            }

            if (window.history.length > 1) {
                window.history.back();
                return true;
            }
        }

        let storedBrowserUrl = null;
        try {
            storedBrowserUrl = sessionStorage.getItem('csi300LastBrowserUrl');
        } catch (error) {
            console.warn('Failed to read last browser URL from sessionStorage:', error);
        }

        if (referrer.includes('browser.html')) {
            if (window.history.length > 1) {
                window.history.back();
                return true;
            }
            return navigateToAbsolute(referrer);
        }

        if (storedBrowserUrl && navigateToRelative(storedBrowserUrl)) {
            return true;
        }

        if (referrer) {
            return navigateToAbsolute(referrer);
        }

        if (window.history.length > 1) {
            window.history.back();
            return true;
        }

        window.location.href = this.resolveLink('browser.html');
        return true;
    }

    showCompanyMenu(companyName) {
        if (this.companyNavItem) {
            this.companyNavItem.style.display = '';
            if (this.navListElement && this.companyNavItem.parentElement !== this.navListElement) {
                this.navListElement.appendChild(this.companyNavItem);
            } else if (this.navListElement) {
                this.navListElement.appendChild(this.companyNavItem);
            }
        }

        if (this.mobileCompanyGroup) {
            this.mobileCompanyGroup.style.display = '';
        }

        if (companyName) {
            this.updateCompanyMenuTitle(companyName);
        }

        this.updateCompanyMenuLink();
    }

    hideCompanyMenu() {
        if (this.companyNavItem) {
            this.companyNavItem.style.display = 'none';
        }

        if (this.mobileCompanyGroup) {
            this.mobileCompanyGroup.style.display = 'none';
        }

        this.companyContext = null;
        this.updateCompanyMenuTitle('Company Insights');
        this.updateCompanyMenuLink();
    }

    updateCompanyMenuTitle(name) {
        this.companyMenuTitle = (name && name.trim()) ? name.trim() : 'Company Insights';

        if (this.companyNavItem) {
            const linkTextElement = this.companyNavItem.querySelector('.globalnav-link-text');
            if (linkTextElement) {
                linkTextElement.textContent = this.companyMenuTitle;
            }
        }

        if (this.mobileCompanyGroup) {
            const header = this.mobileCompanyGroup.querySelector('.globalnav-submenu-header');
            if (header) {
                header.textContent = this.companyMenuTitle;
            }
        }

        if (this.activeSubmenuType === 'company' && this.dropdownHost) {
            const header = this.dropdownHost.querySelector('.globalnav-submenu-header');
            if (header) {
                header.textContent = this.companyMenuTitle;
            }
        }
    }

    updateCompanyMenuLink() {
        if (!this.companyNavItem) {
            return;
        }

        const linkElement = this.companyNavItem.querySelector('.globalnav-link');
        if (!linkElement) {
            return;
        }

        if (this.companyContext && this.companyContext.id) {
            const targetHref = this.resolveLink(`detail.html?id=${encodeURIComponent(this.companyContext.id)}`);
            linkElement.setAttribute('href', targetHref);
        } else {
            const defaultHref = this.resolveLink('investment-summary-overview.html');
            linkElement.setAttribute('href', defaultHref);
        }
    }

    setCompanyContext(context) {
        this.companyContext = context || null;
        if (this.companyContext) {
            this.showCompanyMenu(this.companyContext.name);
        } else {
            this.hideCompanyMenu();
        }

        this.updateCompanyMenuLink();
    }

    resolveValueChainIndustry(imSector) {
        if (!imSector) {
            return 'energy';
        }

        const sectorLower = imSector.toLowerCase();

        if (sectorLower.includes('supporting') && sectorLower.includes('technolog')) {
            return 'supporting-technology';
        }

        if (sectorLower.includes('technology') || sectorLower.includes('tech')) {
            return 'supporting-technology';
        }

        if (sectorLower.includes('energy')) {
            return 'energy';
        }

        return 'energy';
    }

    isCompanyDetailPage() {
        const path = (window.location && window.location.pathname) ? window.location.pathname.toLowerCase() : '';
        if (!path.endsWith('detail.html')) {
            return false;
        }
        return !(path.includes('/value-chain/') || path.includes('/investment-summary/'));
    }

    configureCompanyMenuVisibility() {
        if (this.isCompanyDetailPage()) {
            this.showCompanyMenu();
        } else {
            this.hideCompanyMenu();
        }
    }

    toggleMobileMenu() {
        this.mobileMenuOpen = !this.mobileMenuOpen;
        const overlay = document.querySelector('.globalnav-mobile-overlay');
        const mobileMenu = document.querySelector('.globalnav-mobile-menu');

        if (this.mobileMenuOpen) {
            overlay.classList.add('show');
            mobileMenu.classList.add('show');
            document.body.style.overflow = 'hidden';
        } else {
            this.closeMobileMenu();
        }
    }

    closeMobileMenu() {
        this.mobileMenuOpen = false;
        const overlay = document.querySelector('.globalnav-mobile-overlay');
        const mobileMenu = document.querySelector('.globalnav-mobile-menu');

        overlay.classList.remove('show');
        mobileMenu.classList.remove('show');
        document.body.style.overflow = '';
    }

    handleResize() {
        if (window.innerWidth > 1068) {
            this.closeMobileMenu();
        }
        this.hideSubmenu(true);
    }

}

// Initialize navigation when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new GlobalNav();
});
