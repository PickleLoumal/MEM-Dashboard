/**
 * MEM Dashboard API Configuration
 * Uses CloudFront as unified entry point - handles both frontend and API proxy
 * CloudFront proxies /api/* requests to private ALB
 */

// Auto-detect environment
const isLocalDev = window.location.hostname === 'localhost' || 
                   window.location.hostname === '127.0.0.1' ||
                   window.location.protocol === 'file:';

// Production API configuration
const API_CONFIGS = {
    DJANGO: {
        name: 'Django REST API',
        // Use CloudFront as unified entry point (like CSI300 app)
        // CloudFront proxies /api/* to private ALB
        baseUrl: isLocalDev 
            ? 'http://localhost:8000/api'  // Local development
            : 'https://d1ht73txi7ykd0.cloudfront.net/api',  // Production via CloudFront
        description: 'Django REST Framework API with PostgreSQL data',
        version: '2.0',
        status: isLocalDev ? 'development' : 'production'
    }
};

// Get current API configuration
const getCurrentApiConfig = () => {
    return API_CONFIGS.DJANGO;
};

// Export configuration
window.API_CONFIG = getCurrentApiConfig();
window.API_CONFIGS = API_CONFIGS;

// Initialize production configuration
console.log('🚀 MEM Dashboard API Configuration - Production');
console.log(`📊 API Name: ${window.API_CONFIG.name}`);
console.log(`🔗 API URL: ${window.API_CONFIG.baseUrl}`);
console.log(`📝 Description: ${window.API_CONFIG.description}`);
console.log('✅ Production mode enabled');

// Production fetch interceptor
window.originalFetch = window.fetch;
window.fetch = (url, options) => {
    console.log('🔍 [PROD] Fetch called with URL:', url);
    
    // Handle relative API calls
    if (url.startsWith('/api/')) {
        url = window.API_CONFIG.baseUrl + url.replace('/api', '');
        console.log('🔄 [PROD] Redirected to:', url);
    }
    
    return window.originalFetch(url, options);
};

console.log('✅ Production API interceptor configured');
