/**
 * Resolve internal navigation links.
 *
 * All React pages use production-style URLs (e.g., /browser.html, /detail.html).
 * In development mode, Vite's dev-server-rewrite middleware handles the
 * URL rewriting to actual source paths automatically.
 *
 * @param path - The target path (e.g., 'browser.html', 'detail.html?id=123')
 * @returns The resolved URL with leading slash
 */
export function resolveLink(path: string): string {
  // Handle empty paths
  if (!path) return '#';

  // Pass through special URLs unchanged
  if (
    path.startsWith('#') ||
    path.startsWith('mailto:') ||
    path.startsWith('tel:') ||
    /^(?:[a-z]+:)?\/\//i.test(path) // absolute URLs (http://, https://, //)
  ) {
    return path;
  }

  // Already has leading slash - return as-is
  if (path.startsWith('/')) {
    return path;
  }

  // Add leading slash for relative paths
  return `/${path}`;
}

