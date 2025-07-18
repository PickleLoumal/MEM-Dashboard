// Main application initializer for MEM Dashboard
class MEMDashboard {
    constructor() {
        this.version = '1.0.0';
        this.initialized = false;
    }

    /**
     * Initialize the entire dashboard
     */
    async init() {
        if (this.initialized) {
            console.warn('⚠️ Dashboard already initialized');
            return;
        }

        console.log('🚀 MEM Dashboard starting initialization...');
        
        try {
            // Log system info
            console.log(`📊 MEM Dashboard v${this.version}`);
            console.log('🌐 User Agent:', navigator.userAgent);
            console.log('📱 Viewport:', `${window.innerWidth}x${window.innerHeight}`);

            // Initialize components sequentially
            await this.initializeComponents();
            
            // Setup global event listeners
            this.setupGlobalListeners();
            
            // Mark as initialized
            this.initialized = true;
            
            console.log('✅ MEM Dashboard initialization complete!');
            
            // Optional: Show success notification
            this.showInitializationSuccess();
            
        } catch (error) {
            console.error('❌ Dashboard initialization failed:', error);
            this.showInitializationError(error);
        }
    }

    /**
     * Initialize all dashboard components
     */
    async initializeComponents() {
        console.log('🔧 Initializing dashboard components...');

        // Clear cache for testing (remove in production)
        if (this.isTestMode()) {
            this.clearTestCache();
        }

        // Components will auto-initialize via their own DOMContentLoaded listeners
        // This method can be used for additional setup if needed
        
        // Wait a bit for all components to initialize
        await new Promise(resolve => setTimeout(resolve, 100));
    }

    /**
     * Check if we're in test mode
     */
    isTestMode() {
        return localStorage.getItem('mem_dashboard_test_mode') === 'true' || 
               window.location.search.includes('test=true');
    }

    /**
     * Clear test cache
     */
    clearTestCache() {
        console.log('🧹 Clearing cache for test mode...');
        const keysToRemove = [
            'lastUSDCNYUpdate',
            'previousM2',
            'lastM2Date',
            'previousM1',
            'lastM1Date'
        ];
        
        keysToRemove.forEach(key => localStorage.removeItem(key));
    }

    /**
     * Setup global event listeners
     */
    setupGlobalListeners() {
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                console.log('👁️ Page became visible, checking for updates...');
                this.handlePageVisible();
            }
        });

        // Handle window resize
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.handleWindowResize();
            }, 250);
        });

        // Handle errors globally
        window.addEventListener('error', (event) => {
            console.error('🚨 Global error caught:', event.error);
            this.handleGlobalError(event.error);
        });

        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            console.error('🚨 Unhandled promise rejection:', event.reason);
            this.handleGlobalError(event.reason);
        });
    }

    /**
     * Handle page becoming visible
     */
    handlePageVisible() {
        // Refresh data if page was hidden for more than 5 minutes
        const hiddenTime = Date.now() - (localStorage.getItem('page_hidden_time') || 0);
        if (hiddenTime > 5 * 60 * 1000) { // 5 minutes
            console.log('🔄 Page was hidden for 5+ minutes, refreshing data...');
            if (window.exchangeRateManager) {
                window.exchangeRateManager.refresh();
            }
        }
    }

    /**
     * Handle window resize
     */
    handleWindowResize() {
        console.log('📐 Window resized to:', `${window.innerWidth}x${window.innerHeight}`);
        // Add any responsive behavior here if needed
    }

    /**
     * Handle global errors
     */
    handleGlobalError(error) {
        // Log the error
        console.error('Error details:', {
            message: error.message,
            stack: error.stack,
            timestamp: new Date().toISOString()
        });

        // Could send to error tracking service here
        // this.sendErrorToService(error);
    }

    /**
     * Show initialization success notification
     */
    showInitializationSuccess() {
        // Could show a subtle notification or just log
        console.log('🎉 All systems operational!');
    }

    /**
     * Show initialization error
     */
    showInitializationError(error) {
        console.error('💥 Initialization failed:', error.message);
        
        // Could show user-friendly error message
        // For now, just ensure fallback data is shown
        document.body.classList.add('initialization-error');
    }

    /**
     * Get dashboard status
     */
    getStatus() {
        return {
            version: this.version,
            initialized: this.initialized,
            timestamp: new Date().toISOString(),
            components: {
                exchangeRateManager: !!window.exchangeRateManager,
                navigationController: !!window.navigationController,
                investmentCardController: !!window.investmentCardController,
                memApiClient: !!window.memApiClient
            }
        };
    }

    /**
     * Enable test mode
     */
    enableTestMode() {
        localStorage.setItem('mem_dashboard_test_mode', 'true');
        console.log('🧪 Test mode enabled');
    }

    /**
     * Disable test mode
     */
    disableTestMode() {
        localStorage.removeItem('mem_dashboard_test_mode');
        console.log('🏭 Test mode disabled');
    }
}

// Make class available globally
window.MEMDashboard = MEMDashboard;
window.DashboardInitializer = MEMDashboard; // Alias for compatibility

// Global dashboard instance
let memDashboard;

// NOTE: Auto-initialization DISABLED to prevent conflicts with main-dashboard.js
// Main dashboard controller now handles all initialization
// This file is kept for compatibility but initialization is now centralized

console.log('📋 dashboard-init.js loaded (initialization delegated to main-dashboard.js)');

// Store page hidden time for visibility tracking
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        localStorage.setItem('page_hidden_time', Date.now().toString());
    }
});

// Expose dashboard status globally for debugging
window.getDashboardStatus = () => {
    return window.mainDashboard ? window.mainDashboard.getStatus() : { error: 'Dashboard not initialized by main controller' };
};
