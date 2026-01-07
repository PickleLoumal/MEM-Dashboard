import React from 'react';
import ReactDOM from 'react-dom/client';
import { OpenAPI } from '@shared/api/generated';
import App from './App';

// Configure OpenAPI base URL BEFORE any API calls
// Production: empty string (generated paths already include /api prefix, CloudFront proxies /api/* to ALB)
// Development: localhost:8001
OpenAPI.BASE = (
  import.meta.env.VITE_API_BASE ??
  (import.meta.env.MODE === 'development' ? 'http://localhost:8001' : '')
).replace(/\/$/, '');

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Root element not found');
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

