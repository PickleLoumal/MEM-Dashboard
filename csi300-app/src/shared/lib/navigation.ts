// Map of pages that have been migrated to React (for DEV mode only)
export const REACT_PAGES: Record<string, string> = {
  'index.html': '/src/pages/index/index.html',
  'browser.html': '/src/pages/browser/index.html',
  'detail.html': '/src/pages/detail/index.html',
  'investment-summary-detail.html': '/src/pages/investment-summary-detail/index.html'
};

export function resolveLink(path: string): string {
  if (!path) return '#';
  if (path.startsWith('#') || path.startsWith('mailto:') || /^(?:[a-z]+:)?\/\//i.test(path)) {
    return path;
  }

  // Use MODE to determine environment (more reliable than DEV)
  // @ts-ignore  
  const mode = import.meta.env.MODE;
  const isDevMode = mode === 'development';
  
  // Remove query params for matching
  const [basePath, query] = path.split('?');
  
  // DEV mode: use Vite dev server paths for migrated React pages
  if (isDevMode && REACT_PAGES[basePath]) {
    return `${REACT_PAGES[basePath]}${query ? '?' + query : ''}`;
  }
  
  // PRODUCTION mode: use flattened paths at root
  return `/${path}`;
}

