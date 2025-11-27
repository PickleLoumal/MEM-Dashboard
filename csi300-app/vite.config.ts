import { resolve } from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const page = (name: string) => resolve(__dirname, `src/pages/${name}/index.html`);

export default defineConfig({
  plugins: [react()],
  envPrefix: 'VITE_',
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
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
