import React from 'react';
import ReactDOM from 'react-dom/client';
import { OpenAPI } from '@shared/api/generated';

// 配置 API 基础地址 - 必须在导入 App 之前！
// 生产环境使用空字符串（API 路径已包含 /api 前缀，CloudFront 代理 /api/* -> ALB）
// 开发环境默认 localhost:8001
OpenAPI.BASE = (
  import.meta.env.VITE_API_BASE ??
  (import.meta.env.MODE === 'development' ? 'http://localhost:8001' : '')
).replace(/\/$/, '');

import App from './App';
import '@shared/styles/main.css';

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Root element not found');
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

