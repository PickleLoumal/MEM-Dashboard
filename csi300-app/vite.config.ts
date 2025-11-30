import { resolve } from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const page = (name: string) => resolve(__dirname, `src/pages/${name}/index.html`);

export default defineConfig({
  plugins: [react()],
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
    }
  },
  build: {
    // Keep React bundle output separate from legacy static files
    outDir: 'dist/react',
    rollupOptions: {
      input: {
        browser: page('browser'),
        index: page('index')
      }
    }
  }
});
