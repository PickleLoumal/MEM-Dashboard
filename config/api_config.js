/**
 * MEM Dashboard API Configuration
 * Django-Only 配置 (Flask已移除)
 */

// API配置 - 仅Django
const API_CONFIGS = {
    DJANGO: {
        name: 'Django REST API',
        baseUrl: 'http://localhost:8000/api',
        description: 'Django REST Framework API with PostgreSQL data',
        version: '2.0',
        status: 'production'
    }
};

// 获取当前API配置 - 总是返回Django
const getCurrentApiConfig = () => {
    return API_CONFIGS.DJANGO;
};

// 导出配置
window.API_CONFIG = getCurrentApiConfig();
window.API_CONFIGS = API_CONFIGS;

// 初始化时显示当前配置
console.log('🚀 MEM Dashboard API 配置:');
console.log(`📊 API名称: ${window.API_CONFIG.name}`);
console.log(`🔗 API地址: ${window.API_CONFIG.baseUrl}`);
console.log(`📝 描述: ${window.API_CONFIG.description}`);
console.log('✅ Django-Only模式已启用');

// 测试API拦截器是否会被调用
console.log('🧪 [测试] 设置API拦截器...');

// 全局API拦截器 - 智能端口重定向
window.originalFetch = window.fetch;
window.fetch = (url, options) => {
    console.log('🔍 [DEBUG] Fetch called with URL:', url);
    
    if (url.includes('/api/')) {
        const originalUrl = url;
        
        // 智能端口重定向
        url = url.replace(/localhost:8001\/api\//, 'localhost:8000/api/');
        url = url.replace(/localhost:3000\/api\//, 'localhost:8000/api/');
        url = url.replace(/localhost:5001\/api\//, 'localhost:8000/api/');
        
        // 处理相对路径API调用 - 转换为绝对路径
        if (url.startsWith('/api/')) {
            url = `http://localhost:8000${url}`;
        }
        
        console.log('🔧 [Global API Interceptor] Original URL:', originalUrl);
        console.log('🔧 [Global API Interceptor] Redirected to Django API:', url);
        
        // 检查URL是否正确转换
        if (url.includes('localhost:3000')) {
            console.error('❌ [API Interceptor ERROR] URL still contains port 3000:', url);
        }
    } else {
        console.log('ℹ️ [DEBUG] Non-API fetch call:', url);
    }
    
    return window.originalFetch(url, options);
};

console.log('✅ [测试] API拦截器已设置完成');

// 立即测试API拦截器是否工作
setTimeout(() => {
    console.log('🧪 [测试] 验证API拦截器是否工作...');
    console.log('🧪 [测试] window.fetch !== window.originalFetch:', window.fetch !== window.originalFetch);
}, 100);

/*
🎯 MEM Dashboard Django-Only API配置
=======================================
📊 当前API: Django REST Framework
🔗 地址: http://localhost:8000/api
📈 功能: 完整的FRED和BEA数据系统
✅ 状态: Flask已完全移除
*/
