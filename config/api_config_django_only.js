/**
 * MEM Dashboard API Configuration
 * Django-Only 配置 (Flask已移除)
 */

// API配置 - 仅Django
const API_CONFIGS = {
    DJANGO: {
        name: 'Django REST API',
        baseUrl: 'http://localhost:8001/api',
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

/*
🎯 MEM Dashboard Django-Only API配置
=======================================
📊 当前API: Django REST Framework
🔗 地址: http://localhost:8001/api
📈 功能: 完整的FRED和BEA数据系统
✅ 状态: Flask已完全移除
*/
