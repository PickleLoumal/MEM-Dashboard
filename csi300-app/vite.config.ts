/// <reference types="vitest" />
import { resolve } from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const page = (name: string) => resolve(__dirname, `src/pages/${name}/index.html`);

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'dev-server-rewrite',
      configureServer(server) {
        server.middlewares.use((req, res, next) => {
          if (req.url) {
            // Rewrite production URLs to development paths
            const url = req.url.split('?')[0];
            if (url === '/browser.html') {
              req.url = '/src/pages/browser/index.html' + (req.url.includes('?') ? '?' + req.url.split('?')[1] : '');
            } else if (url === '/detail.html') {
              req.url = '/src/pages/detail/index.html' + (req.url.includes('?') ? '?' + req.url.split('?')[1] : '');
            } else if (url === '/fund-flow.html') {
              req.url = '/src/pages/fund-flow/index.html' + (req.url.includes('?') ? '?' + req.url.split('?')[1] : '');
            } else if (url === '/investment-summary-detail.html') {
              req.url = '/src/pages/investment-summary-detail/index.html' + (req.url.includes('?') ? '?' + req.url.split('?')[1] : '');
            } else if (url === '/index.html' || url === '/') {
              req.url = '/src/pages/index/index.html' + (req.url.includes('?') ? '?' + req.url.split('?')[1] : '');
            }
            // Map /assets requests to legacy assets folder
            else if (req.url.startsWith('/assets/')) {
              req.url = req.url.replace(/^\/assets\//, '/legacy/assets/');
            }
          }
          next();
        });
      }
    }
  ],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['../tests/frontend/setup.ts'],
    include: ['../tests/frontend/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    alias: {
      '@': resolve(__dirname, 'src'),
      '@shared': resolve(__dirname, 'src/shared'),
      // 显式指向 node_modules
      '@testing-library/jest-dom': resolve(__dirname, 'node_modules/@testing-library/jest-dom'),
      '@testing-library/react': resolve(__dirname, 'node_modules/@testing-library/react'),
      'vitest': resolve(__dirname, 'node_modules/vitest'),
      'react': resolve(__dirname, 'node_modules/react'),
      'react-dom': resolve(__dirname, 'node_modules/react-dom'),
      'react/jsx-dev-runtime': resolve(__dirname, 'node_modules/react/jsx-dev-runtime.js'),
      'react/jsx-runtime': resolve(__dirname, 'node_modules/react/jsx-runtime.js'),
    }
  },
  envPrefix: 'VITE_',
  resolve: {
    alias: {
      // Primary alias (backwards compatible)
      '@': resolve(__dirname, 'src'),
      // Feature-based aliases for scalable architecture
      '@shared': resolve(__dirname, 'src/shared'),
      '@components': resolve(__dirname, 'src/shared/components'),
      '@hooks': resolve(__dirname, 'src/shared/hooks'),
      '@lib': resolve(__dirname, 'src/shared/lib'),
      '@styles': resolve(__dirname, 'src/shared/styles'),
      '@features': resolve(__dirname, 'src/features'),
      '@app': resolve(__dirname, 'src/app'),
      '@pages': resolve(__dirname, 'src/pages'),
      // Legacy code alias
      '@legacy': resolve(__dirname, 'legacy')
    }
  },
  // Serve legacy files during development
  publicDir: 'public',
  server: {
    fs: {
      // Allow serving files from legacy directory
      allow: ['..']
    },
    // Proxy API requests to Django backend during development
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8001',
        ws: true,
      },
    },
  },
  preview: {
    // Proxy API requests to Django backend during preview (vite preview)
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8001',
        ws: true,
      },
    },
  },
  build: {
    // Keep React bundle output separate from legacy static files
    outDir: 'dist/react',
    rollupOptions: {
      input: {
        browser: page('browser'),
        index: page('index'),
        detail: page('detail'),
        'fund-flow': page('fund-flow'),
        'investment-summary-detail': page('investment-summary-detail')
      }
    }
  }
});
