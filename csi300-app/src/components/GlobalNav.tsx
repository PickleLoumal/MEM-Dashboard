import React, { useCallback, useEffect, useRef, useState } from 'react';

type MenuItem = {
  text: string;
  href?: string;
  action?: string;
  comingSoon?: boolean;
};

type MenuGroup = {
  title: string;
  items: MenuItem[];
};

type SubmenuData = {
  groups: MenuGroup[];
};

const SUBMENU_DATA: Record<string, SubmenuData> = {
  industry: {
    groups: [
      {
        title: 'Industry Overview',
        items: [
          { text: 'Company Filter', href: 'index.html' },
          { text: 'Industry Primer', href: 'industry-primers.html', comingSoon: true },
          { text: 'Value Chain Explorer', href: 'value-chain.html', comingSoon: true },
          { text: 'Fund Flow', href: 'fund-flow.html' },
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

// Map of pages that have been migrated to React
const REACT_PAGES: Record<string, string> = {
  'index.html': '/src/pages/index/index.html',
  'browser.html': '/src/pages/browser/index.html'
};

function resolveLink(path: string): string {
  if (!path) return '#';
  if (path.startsWith('#') || path.startsWith('mailto:') || /^(?:[a-z]+:)?\/\//i.test(path)) {
    return path;
  }

  // In dev mode, check if this page has been migrated to React
  const isDev = import.meta.env.DEV;
  if (isDev && REACT_PAGES[path]) {
    return REACT_PAGES[path];
  }

  // For production or non-migrated pages, use the original path
  return `/${path}`;
}

function SubmenuContent({ menuType, onClose }: { menuType: string; onClose: () => void }) {
  const data = SUBMENU_DATA[menuType];
  if (!data) return null;

  return (
    <div
      className="globalnav-submenu-content"
      style={{
        '--r-globalnav-flyout-elevated-group-count': 1,
        '--r-globalnav-flyout-group-total': data.groups.length,
        '--r-globalnav-flyout-item-total': data.groups.reduce((acc, g) => acc + g.items.length, 0)
      } as React.CSSProperties}
    >
      {data.groups.map((group, groupIndex) => (
        <div
          key={groupIndex}
          className={`globalnav-submenu-group ${groupIndex === 0 ? 'globalnav-submenu-group-elevated' : ''}`}
        >
          <h2 className="globalnav-submenu-header">{group.title}</h2>
          <ul className="globalnav-submenu-list">
            {group.items.map((item, itemIndex) => (
              <li key={itemIndex} className="globalnav-submenu-list-item">
                <a
                  href={item.href ? resolveLink(item.href) : '#'}
                  className={`globalnav-submenu-link${item.comingSoon ? ' globalnav-submenu-link--coming-soon' : ''}`}
                  onClick={onClose}
                >
                  {item.text}
                </a>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

function MobileMenu({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  return (
    <>
      <div
        className={`globalnav-mobile-overlay ${isOpen ? 'show' : ''}`}
        onClick={onClose}
      />
      <div className={`globalnav-mobile-menu ${isOpen ? 'show' : ''}`}>
        <div className="globalnav-submenu-group">
          <h3 className="globalnav-submenu-header">Industry</h3>
          <ul className="globalnav-submenu-list">
            <li className="globalnav-submenu-list-item">
              <a href={resolveLink('index.html')} className="globalnav-submenu-link" onClick={onClose}>Company Filter</a>
            </li>
            <li className="globalnav-submenu-list-item">
              <a href={resolveLink('industry-primers.html')} className="globalnav-submenu-link globalnav-submenu-link--coming-soon" onClick={onClose}>Industry Primer</a>
            </li>
            <li className="globalnav-submenu-list-item">
              <a href={resolveLink('value-chain.html')} className="globalnav-submenu-link globalnav-submenu-link--coming-soon" onClick={onClose}>Value Chain</a>
            </li>
            <li className="globalnav-submenu-list-item">
              <a href={resolveLink('peer-comparison.html')} className="globalnav-submenu-link" onClick={onClose}>Company Comparison</a>
            </li>
            <li className="globalnav-submenu-list-item">
              <a href={resolveLink('fund-flow.html')} className="globalnav-submenu-link" onClick={onClose}>Fund Flow</a>
            </li>
            <li className="globalnav-submenu-list-item">
              <a href={resolveLink('competitor-analysis.html')} className="globalnav-submenu-link globalnav-submenu-link--coming-soon" onClick={onClose}>Competitor Analysis</a>
            </li>
            <li className="globalnav-submenu-list-item">
              <a href={resolveLink('im-view.html')} className="globalnav-submenu-link globalnav-submenu-link--coming-soon" onClick={onClose}>IM View</a>
            </li>
            <li className="globalnav-submenu-list-item">
              <a href={resolveLink('browser.html')} className="globalnav-submenu-link" onClick={onClose}>View All</a>
            </li>
          </ul>
        </div>
        <div className="globalnav-submenu-group">
          <h3 className="globalnav-submenu-header">Hot Themes</h3>
          <ul className="globalnav-submenu-list">
            <li className="globalnav-submenu-list-item">
              <a href={resolveLink('themes-information.html')} className="globalnav-submenu-link globalnav-submenu-link--coming-soon" onClick={onClose}>Themes Information</a>
            </li>
            <li className="globalnav-submenu-list-item">
              <a href={resolveLink('industry-benefit.html')} className="globalnav-submenu-link globalnav-submenu-link--coming-soon" onClick={onClose}>Industry Benefit</a>
            </li>
            <li className="globalnav-submenu-list-item">
              <a href={resolveLink('competitor-benefit.html')} className="globalnav-submenu-link globalnav-submenu-link--coming-soon" onClick={onClose}>Competitor Benefit</a>
            </li>
          </ul>
        </div>
      </div>
    </>
  );
}

export function GlobalNav() {
  const [activeMenu, setActiveMenu] = useState<string | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [dropdownHeight, setDropdownHeight] = useState(0);
  const hideTimeoutRef = useRef<number | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const clearHideTimeout = useCallback(() => {
    if (hideTimeoutRef.current !== null) {
      window.clearTimeout(hideTimeoutRef.current);
      hideTimeoutRef.current = null;
    }
  }, []);

  const showSubmenu = useCallback((menuType: string) => {
    clearHideTimeout();
    setActiveMenu(menuType);
  }, [clearHideTimeout]);

  const hideSubmenu = useCallback(() => {
    clearHideTimeout();
    hideTimeoutRef.current = window.setTimeout(() => {
      setActiveMenu(null);
      setDropdownHeight(0);
    }, 150);
  }, [clearHideTimeout]);

  const handleMouseEnter = useCallback((menuType: string) => {
    if (window.innerWidth > 1068) {
      showSubmenu(menuType);
    }
  }, [showSubmenu]);

  const handleMouseLeave = useCallback(() => {
    if (window.innerWidth > 1068) {
      hideSubmenu();
    }
  }, [hideSubmenu]);

  const handleDropdownMouseEnter = useCallback(() => {
    if (window.innerWidth > 1068) {
      clearHideTimeout();
    }
  }, [clearHideTimeout]);

  const handleDropdownMouseLeave = useCallback(() => {
    if (window.innerWidth > 1068) {
      hideSubmenu();
    }
  }, [hideSubmenu]);

  const toggleMobileMenu = useCallback(() => {
    setMobileMenuOpen((prev) => !prev);
  }, []);

  const closeMobileMenu = useCallback(() => {
    setMobileMenuOpen(false);
  }, []);

  // Update dropdown height when activeMenu changes
  useEffect(() => {
    if (activeMenu && dropdownRef.current) {
      const content = dropdownRef.current.querySelector('.globalnav-submenu-content');
      if (content) {
        setDropdownHeight(content.scrollHeight);
      }
    } else {
      setDropdownHeight(0);
    }
  }, [activeMenu]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 1068) {
        setMobileMenuOpen(false);
      }
      setActiveMenu(null);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Handle click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('.globalnav')) {
        setActiveMenu(null);
        setDropdownHeight(0);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  // Lock body scroll when mobile menu is open
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [mobileMenuOpen]);

  return (
    <nav className="globalnav">
      <div className="globalnav-content">
        <a href={resolveLink('index.html')} className="globalnav-brand">
          Chinese Stock Dashboard
        </a>

        <ul className="globalnav-list">
          <li
            className={`globalnav-item ${activeMenu === 'industry' ? 'is-active' : ''}`}
            onMouseEnter={() => handleMouseEnter('industry')}
            onMouseLeave={handleMouseLeave}
          >
            <a href={resolveLink('index.html')} className="globalnav-link">
              <span className="globalnav-link-text">Industry</span>
            </a>
          </li>
          <li
            className={`globalnav-item ${activeMenu === 'themes' ? 'is-active' : ''}`}
            onMouseEnter={() => handleMouseEnter('themes')}
            onMouseLeave={handleMouseLeave}
          >
            <a href={resolveLink('themes-information.html')} className="globalnav-link">
              <span className="globalnav-link-text">Hot Themes</span>
            </a>
          </li>
        </ul>

        <div className="globalnav-menutrigger">
          <button
            className="globalnav-menutrigger-button"
            aria-label="Menu"
            onClick={toggleMobileMenu}
          >
            <svg width="18" height="18" viewBox="0 0 18 18">
              <polyline
                className="globalnav-menutrigger-bread globalnav-menutrigger-bread-top"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.2"
                strokeLinecap="round"
                strokeLinejoin="round"
                points="2 5, 16 5"
              />
              <polyline
                className="globalnav-menutrigger-bread globalnav-menutrigger-bread-bottom"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.2"
                strokeLinecap="round"
                strokeLinejoin="round"
                points="2 12, 16 12"
              />
            </svg>
          </button>
        </div>

        {/* Desktop dropdown host */}
        <div
          ref={dropdownRef}
          className={`globalnav-dropdown-host ${activeMenu ? 'show' : ''}`}
          style={{ height: dropdownHeight > 0 ? dropdownHeight : undefined }}
          onMouseEnter={handleDropdownMouseEnter}
          onMouseLeave={handleDropdownMouseLeave}
        >
          {activeMenu && (
            <div className="globalnav-submenu globalnav-submenu--attached">
              <SubmenuContent
                menuType={activeMenu}
                onClose={() => {
                  setActiveMenu(null);
                  setDropdownHeight(0);
                }}
              />
            </div>
          )}
        </div>
      </div>

      {/* Mobile menu */}
      <MobileMenu isOpen={mobileMenuOpen} onClose={closeMobileMenu} />
    </nav>
  );
}

