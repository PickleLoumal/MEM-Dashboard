import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { OpenAPI } from '@shared/api/generated';
import '@shared/styles/main.css';
import './styles.css';

// Configure OpenAPI base URL (must be done before any API calls)
// Production: empty string (generated paths already include /api prefix)
OpenAPI.BASE = (import.meta.env.VITE_API_BASE ?? (import.meta.env.MODE === 'development' ? 'http://localhost:8001' : '')).replace(/\/$/, '');

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Root element not found');
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

