/**
 * CSI300 Application API Configuration
 * Standalone configuration for CSI300 frontend application
 */

const CSI300Config = {
    // Use CloudFront as unified entry point - handles both frontend and API proxy
    BASE_URL: 'http://localhost:8001',
    API_BASE: '/api/csi300',

    // CSI300 app endpoints (CloudFront API paths)
    ENDPOINTS: {
        COMPANIES_LIST: '/api/csi300/api/companies/',
        COMPANY_DETAIL: '/api/csi300/api/companies/{id}/',
        FILTER_OPTIONS: '/api/csi300/api/companies/filter_options/',
        SEARCH: '/api/csi300/api/companies/',  // Use the main companies endpoint with search parameter
        HEALTH_CHECK: '/api/csi300/health/'
    },
    
    // Application settings
    APP_CONFIG: {
        APP_NAME: 'Chinese Stock Dashboard',
        VERSION: '1.0.0',
        PAGE_SIZE: 20,
        DEFAULT_CURRENCY: 'CNY'
    },
    
    // UI Configuration
    UI_CONFIG: {
        MOBILE_BREAKPOINT: 768,
        TABLET_BREAKPOINT: 1024,
        ENABLE_ANIMATIONS: true,
        DEFAULT_THEME: 'light'
    },
    
    // Cache settings
    CACHE_CONFIG: {
        COMPANIES_TTL: 300000, // 5 minutes
        COMPANY_DETAIL_TTL: 300000, // 5 minutes
        FILTER_OPTIONS_TTL: 600000, // 10 minutes
        ENABLED: true
    }
};

// Make configuration available globally
window.CSI300Config = CSI300Config;

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CSI300Config;
}
