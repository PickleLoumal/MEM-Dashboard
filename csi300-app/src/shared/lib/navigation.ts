// Map of pages that have been migrated to React
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

  // In dev mode, check if this page has been migrated to React
  // @ts-ignore
  const isDev = import.meta.env.DEV;
  
  // Remove query params for matching
  const [basePath, query] = path.split('?');
  
  if (isDev && REACT_PAGES[basePath]) {
    return `${REACT_PAGES[basePath]}${query ? '?' + query : ''}`;
  }

  // For production or non-migrated pages, use the original path
  // In production build, we flatten the structure so browser.html is at root
  return `/${path}`;
}

