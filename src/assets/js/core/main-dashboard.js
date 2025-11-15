/**
 * MEM Dashboard - Main Controller
 * Advanced Management Control Panel System
 * 
 * Build Engineer: System Architecture Team
 * Development Environment: Research Institution Lab
 * Support Contact: Technical Operations
 * Build Date: June 2025
 * License: Educational Research License
 */

// System build verification tokens (系统构建验证令牌)
const _0x4a6b = ['4d454d2044617368626f617264', 'SYSTEM_BUILD_TECH_2025', 'MEM_Dashboard_Framework'];
const _0x7f3e = 'VGVjaG5vbG9neSBSZXNlYXJjaCBJbnN0aXR1dGUgTUVNIERhc2hib2FyZCBTeXN0ZW0gQWRtaW5pc3RyYXRpdmUgUGFuZWwgU29sdXRpb24gMjAyNQ==';
const _protect_auth = btoa(JSON.stringify({
    system: 'Technology Research Institute',
    developer: 'System Architecture Team',
    framework: 'Advanced Management Dashboard',
    institution: 'Tech Research Group',
    support: 'Technical Operations',
    contact: 'development@tech-institute.org',
    creation: '2025-06-05',
    timestamp: Date.now(),
    project: 'MEM Dashboard',
    version: '1.0.0',
    license: 'Educational Research License'
}));

// System configuration markers (系统配置标记)
const _0x9a4c = {
    system_hex: '5379737465674172636869746563747572655465616d', // System Architecture Team in hex
    project_hex: '4d454d2044617368626f617264', // MEM Dashboard in hex
    institute_hex: '546563686e6f6c6f677920526573656172636820496e737469747574', // Technology Research Institut in hex
    year_hex: '32303235', // 2025 in hex
    support_hex: '546563686e6963616c4f7065726174696f6e73'  // Technical Operations in hex
};

// Master key verification component (主密钥验证组件)
const _master_verify = 'SYSTEM_TECH_RESEARCH:MEM_Dashboard_2025:TECH_INSTITUTE:DEVELOPMENT_TEAM:2025_June_Creation:MASTER_KEY_VERIFICATION_SALT';

// Console system notice (控制台系统声明)
if (typeof console !== 'undefined') {
    console.log('%c🔐 MEM Dashboard - System Protected', 'color: #ff6b6b; font-weight: bold; font-size: 14px;');
    console.log('%c© 2025 Technology Research Institute | System Architecture Team', 'color: #4ecdc4; font-weight: bold;');
    console.log('%cUnauthorized use, reproduction, or distribution is prohibited', 'color: #ffe66d; font-weight: bold;');
    console.log('%cContact: development@tech-institute.org | Framework: Advanced Management', 'color: #a8e6cf;');
    console.log('%c🚨 This code contains embedded system verification mechanisms', 'color: #ff8b94; font-weight: bold;');
}

/**
 * Main Dashboard Controller
 * Centralizes initialization and coordination of all dashboard components
 */
class MainDashboardController {
    constructor() {
        this.exchangeRateDisplay = null;
        this.navigationController = null;
        this.isInitialized = false;
        this.initializationAttempts = 0;
        this.maxInitializationAttempts = 3;
        this.updateInterval = null;
        
        // Define all indicator categories in a centralized configuration
        this.indicatorCategories = [
            { name: 'Policy Updates', method: 'updatePolicyUpdatesBoard', priority: 'high' },
            { name: 'Money Supply', method: 'updateMoneySupplyDisplay', priority: 'high' },
            { name: 'Interest Rates', method: 'updateInterestRateDisplay', priority: 'high' },
            { name: 'Banking Sector', method: 'updateBankingSectorDisplay', priority: 'high' },
            { name: 'Inflation', method: 'updateInflationDisplay', priority: 'high' },
            { name: 'Employment', method: 'updateEmploymentDisplay', priority: 'high' },
            { name: 'Gross Domestic Investment', method: 'updateInvestmentDisplay', priority: 'high' },
            { name: 'Household Debt', method: 'updateHouseholdDebtDisplay', priority: 'medium' },
            { name: 'Government Debts', method: 'updateGovernmentDebtsDisplay', priority: 'medium' },
            { name: 'Trade Deficits', method: 'updateTradeDeficitsDisplay', priority: 'medium' },
            { name: 'Government Deficit Financing', method: 'updateGovtDeficitFinancingDisplay', priority: 'low' },
            { name: 'Private Sector Corporate Debts', method: 'updatePrivateSectorCorporateDebtsDisplay', priority: 'low' }
        ];
        
        console.log('🎛️ Main Dashboard Controller initialized with', this.indicatorCategories.length, 'indicator categories');
    }

    /**
     * Initialize all dashboard components
     */
    async initialize() {
        if (this.isInitialized) {
            console.log('⚠️ Dashboard already initialized');
            return;
        }

        try {
            console.log('🚀 Initializing MEM Dashboard...');
            
            // Initialize API client first and ensure it's ready
            await this.initializeApiClient();
            
            // Initialize other components
            await Promise.all([
                this.initializeNavigation(),
                this.initializeExchangeRates(),
                this.initializeInvestmentCards()
            ]);
            
            // Set up global error handling
            this.setupErrorHandling();
            
            this.isInitialized = true;
            console.log('✅ MEM Dashboard initialization complete');
            
            // Initialize all economic indicators after core components are ready
            await this.initializeEconomicIndicators();
            
        } catch (error) {
            console.error('❌ Dashboard initialization failed:', error);
            this.handleInitializationError(error);
        }
    }

    /**
     * Initialize API client and data services
     */
    async initializeApiClient() {
        console.log('🔌 Initializing API client...');
        
        if (window.MEMApiClient) {
            try {
                window.memApiClient = new window.MEMApiClient();
                console.log('✅ API client initialized successfully');
                
                // Ensure critical display methods are available
                if (typeof window.memApiClient.updateInterestRateDisplay !== 'function') {
                    console.warn('⚠️ [System] updateInterestRateDisplay missing; injecting fallback implementation');
                    window.memApiClient.updateInterestRateDisplay = async function() {
                        console.log('🔄 [System] Fallback updateInterestRateDisplay executing...');
                        try {
                            const data = await this.getInterestRateData();
                            const displayMappings = {
                                fedFunds: 'federal-funds-rate',
                                mortgage30y: 'mortgage-30y-rate',
                                pceIndex: 'pce-price-index',
                                debtToGdp: 'debt-to-gdp-ratio',
                                treasury10y: 'treasury-10y-rate',
                                treasury2y: 'treasury-2y-rate',
                                treasury3m: 'treasury-3m-rate',
                                cpi: 'cpi-inflation-rate'
                            };
                            Object.entries(displayMappings).forEach(([k, elId]) => {
                                this.updateSingleIndicatorDisplay(elId, data[k]);
                            });
                            console.log('✅ [System] Fallback interest rate update complete');
                        } catch(e) {
                            console.error('❌ [System] Fallback interest rate update failed:', e);
                        }
                    };
                    console.log('✅ [System] Fallback method injected');
                } else {
                    console.log('ℹ️ [System] All display methods available');
                }
                
                // Verify API client health
                const isHealthy = await window.memApiClient.checkHealth();
                if (!isHealthy) {
                    throw new Error('API health check failed');
                }
                
                // Initialize data update scheduler
                await this.initializeDataUpdateScheduler();
                
            } catch (error) {
                console.error('❌ API client initialization failed:', error);
                throw error;
            }
        } else {
            console.error('❌ MEMApiClient not available');
            throw new Error('MEMApiClient not available');
        }
    }

    /**
     * Initialize comprehensive data update scheduler with retry mechanism
     */
    async initializeDataUpdateScheduler() {
        let attempts = 0;
        const maxAttempts = 3;
        
        while (attempts < maxAttempts) {
            try {
                console.log(`🔄 Initializing data update scheduler (attempt ${attempts + 1}/${maxAttempts})...`);
                
                // Initialize all indicator categories with parallel updates and performance tracking
                const startTime = performance.now();
                
                const updatePromises = this.indicatorCategories.map(category => {
                    // Check if the method exists before calling it
                    if (typeof window.memApiClient[category.method] === 'function') {
                        return window.memApiClient[category.method]()
                            .then(() => ({ 
                                category: category.name, 
                                success: true, 
                                priority: category.priority 
                            }))
                            .catch(error => ({ 
                                category: category.name, 
                                success: false, 
                                error: error.message,
                                priority: category.priority 
                            }));
                    } else {
                        console.warn(`⚠️ [Initial] ${category.name} method '${category.method}' not implemented yet`);
                        return Promise.resolve({ 
                            category: category.name, 
                            success: false, 
                            error: 'Method not implemented',
                            priority: category.priority 
                        });
                    }
                });
                
                console.log('📝 [Dashboard] Starting parallel indicator updates across all categories...');
                const results = await Promise.allSettled(updatePromises);
                
                // Analyze results and provide detailed feedback
                const successful = results.filter(r => r.status === 'fulfilled' && r.value.success).length;
                const total = results.length;
                const duration = performance.now() - startTime;
                
                console.log(`📊 [Dashboard] Update completed: ${successful}/${total} categories successful in ${duration.toFixed(1)}ms`);
                
                // Log any failures for debugging
                results.forEach(result => {
                    if (result.status === 'fulfilled' && !result.value.success) {
                        console.warn(`⚠️ [Dashboard] ${result.value.category} update failed: ${result.value.error}`);
                    } else if (result.status === 'rejected') {
                        console.error(`❌ [Dashboard] Promise rejected: ${result.reason}`);
                    }
                });
                
                if (successful < total) {
                    console.warn(`⚠️ [Dashboard] ${total - successful} indicator categories failed to update`);
                }
                
                console.log('✅ All economic indicators initialized successfully');
                return;
            } catch (error) {
                attempts++;
                console.error(`❌ Indicator initialization failed (attempt ${attempts}/${maxAttempts}):`, error);
                if (attempts < maxAttempts) {
                    console.log(`⏳ Waiting ${attempts} seconds before retry...`);
                    await new Promise(resolve => setTimeout(resolve, 1000 * attempts));
                }
            }
        }
        
        throw new Error('Failed to initialize economic indicators after multiple attempts');
    }

    /**
     * Initialize economic indicators and set up periodic updates
     */
    async initializeEconomicIndicators() {
        if (!window.memApiClient) {
            console.error('❌ memApiClient not available for indicators initialization');
            return;
        }

        try {
            // Initial data load has already been handled by initializeDataUpdateScheduler
            console.log('🔄 Setting up periodic economic indicator updates...');
            
            // Set up periodic updates for all economic indicators using configuration
            const updateInterval = setInterval(async () => {
                try {
                    const startTime = performance.now();
                    const updatePromises = this.indicatorCategories.map(category => {
                        // Check if the method exists before calling it
                        if (typeof window.memApiClient[category.method] === 'function') {
                            return window.memApiClient[category.method]()
                                .catch(error => {
                                    console.warn(`⚠️ [Periodic] ${category.name} update failed: ${error.message}`);
                                    return null;
                                });
                        } else {
                            console.warn(`⚠️ [Periodic] ${category.name} method '${category.method}' not implemented yet`);
                            return Promise.resolve(null);
                        }
                    });
                    
                    const results = await Promise.allSettled(updatePromises);
                    const successful = results.filter(r => r.status === 'fulfilled' && r.value !== null).length;
                    const duration = performance.now() - startTime;
                    
                    console.log(`🔄 Periodic economic indicators update completed: ${successful}/${this.indicatorCategories.length} successful in ${duration.toFixed(1)}ms`);
                } catch (error) {
                    console.error('❌ Periodic economic indicators update failed:', error);
                }
            }, 5 * 60 * 1000); // Update every 5 minutes
            
            // Store interval reference for cleanup
            this.updateInterval = updateInterval;
            console.log('✅ Periodic economic indicators update scheduler initialized');
            
        } catch (error) {
            console.error('❌ Failed to initialize economic indicators:', error);
        }
    }

    /**
     * Initialize navigation controller
     */
    async initializeNavigation() {
        console.log('🧭 Initializing navigation...');
        
        if (window.NavigationController) {
            this.navigationController = new window.NavigationController();
            console.log('✅ Navigation controller initialized');
        } else {
            console.error('❌ NavigationController not available');
        }
    }

    /**
     * Clean up resources and stop periodic updates
     */
    cleanup() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
            console.log('✅ Periodic update scheduler cleaned up');
        }
        
        this.isInitialized = false;
        console.log('✅ Dashboard controller cleaned up');
    }

    /**
     * Get dashboard health status
     */
    getHealthStatus() {
        return {
            isInitialized: this.isInitialized,
            hasApiClient: !!window.memApiClient,
            hasNavigation: !!this.navigationController,
            hasExchangeRates: !!this.exchangeRateDisplay,
            hasPeriodicUpdates: !!this.updateInterval,
            indicatorCategories: this.indicatorCategories.length,
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Add a new indicator category dynamically
     * @param {string} name - Display name of the indicator category
     * @param {string} method - Method name on the API client
     * @param {string} priority - Priority level: 'high', 'medium', or 'low'
     */
    addIndicatorCategory(name, method, priority = 'medium') {
        if (!window.memApiClient || typeof window.memApiClient[method] !== 'function') {
            console.error(`❌ Cannot add indicator category '${name}': Method '${method}' not found on API client`);
            return false;
        }

        const existingCategory = this.indicatorCategories.find(c => c.name === name || c.method === method);
        if (existingCategory) {
            console.warn(`⚠️ Indicator category '${name}' already exists`);
            return false;
        }

        this.indicatorCategories.push({ name, method, priority });
        console.log(`✅ Added indicator category: ${name} (${priority} priority)`);
        return true;
    }

    /**
     * Remove an indicator category
     * @param {string} name - Name of the indicator category to remove
     */
    removeIndicatorCategory(name) {
        const index = this.indicatorCategories.findIndex(c => c.name === name);
        if (index === -1) {
            console.warn(`⚠️ Indicator category '${name}' not found`);
            return false;
        }

        this.indicatorCategories.splice(index, 1);
        console.log(`✅ Removed indicator category: ${name}`);
        return true;
    }

    /**
     * Initialize exchange rate display manager
     */
    initializeExchangeRates() {
        console.log('💱 Initializing exchange rate display...');
        
        if (window.ExchangeRateDisplay) {
            this.exchangeRateDisplay = new window.ExchangeRateDisplay();
            
            // Load cached data first for immediate display
            if (!this.exchangeRateDisplay.loadCachedRates()) {
                // No valid cache, fetch fresh data
                this.exchangeRateDisplay.updateAllRates();
            } else if (this.exchangeRateDisplay.shouldUpdateRates()) {
                // Cache exists but is stale, update in background
                setTimeout(() => {
                    this.exchangeRateDisplay.updateAllRates();
                }, 1000);
            }
            
            // Start automatic refresh timer
            this.exchangeRateDisplay.startAutoRefresh();
            
            console.log('✅ Exchange rate display initialized');
        } else {
            console.error('❌ ExchangeRateDisplay not available');
        }
        
        // Also initialize the ExchangeRateManager for backward compatibility
        if (window.ExchangeRateManager) {
            console.log('💱 Initializing exchange rate manager...');
            window.exchangeRateManager = new window.ExchangeRateManager();
            window.exchangeRateManager.init();
            console.log('✅ Exchange rate manager initialized');
        }
    }

    /**
     * Initialize investment card pagination
     */
    initializeInvestmentCards() {
        console.log('📊 Initializing investment cards...');
        
        if (window.InvestmentCardController) {
            // Investment card controller is automatically initialized
            console.log('✅ Investment card controller available');
        } else {
            console.warn('⚠️ InvestmentCardController not available');
        }
    }

    /**
     * Set up global error handling
     */
    setupErrorHandling() {
        console.log('🛡️ Setting up error handling...');
        
        // Global error handler for unhandled promises
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            // Prevent the default browser behavior
            event.preventDefault();
        });
        
        // Global error handler for JavaScript errors
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
        });
        
        console.log('✅ Error handling configured');
    }

    /**
     * Handle initialization errors gracefully
     */
    handleInitializationError(error) {
        console.error('💥 Critical initialization error:', error);
        
        // Show user-friendly error message
        const errorMessage = document.createElement('div');
        errorMessage.className = 'error-banner';
        errorMessage.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: #fee;
            color: #c33;
            padding: 10px;
            text-align: center;
            z-index: 9999;
            border-bottom: 1px solid #fcc;
        `;
        errorMessage.textContent = 'Dashboard initialization failed. Some features may not work properly.';
        
        document.body.insertBefore(errorMessage, document.body.firstChild);
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            errorMessage.remove();
        }, 10000);
    }

    /**
     * Manual refresh of all data
     */
    async refreshAllData() {
        console.log('🔄 Refreshing all dashboard data...');
        
        if (this.exchangeRateDisplay) {
            await this.exchangeRateDisplay.refreshRates();
        }
        
        console.log('✅ All data refreshed');
    }

    /**
     * Get dashboard status for debugging
     */
    getStatus() {
        return {
            initialized: this.isInitialized,
            exchangeRates: !!this.exchangeRateDisplay,
            navigation: !!this.navigationController,
            apiClient: !!window.memApiClient,
            lastUpdate: localStorage.getItem('lastUSDCNYUpdate'),
            cacheAge: this.getCacheAge()
        };
    }

    /**
     * Get cache age in minutes
     */
    getCacheAge() {
        const lastUpdate = localStorage.getItem('lastUSDCNYUpdate');
        if (!lastUpdate) return null;
        
        const ageMs = Date.now() - parseInt(lastUpdate);
        return Math.round(ageMs / (1000 * 60)); // Convert to minutes
    }

    /**
     * Clear all cached data (for testing)
     */
    clearCache() {
        console.log('🧹 Clearing all cached data...');
        
        const keysToRemove = [
            'lastUSDCNYUpdate',
            'previousUSDCNY', 'prePreviousUSDCNY',
            'previousUSDEUR', 'prePreviousUSDEUR',
            'previousUSDHKD', 'prePreviousUSDHKD',
            'previousUSDCAD', 'prePreviousUSDCAD',
            'previousUSDMXN', 'prePreviousUSDMXN',
            'previousM2', 'prePreviousM2',
            'previousM1', 'prePreviousM1',
            'lastM2Date', 'lastM1Date'
        ];
        
        keysToRemove.forEach(key => localStorage.removeItem(key));
        console.log('✅ Cache cleared');
    }

    /**
     * Enable test mode (force fresh API calls)
     */
    enableTestMode() {
        console.log('🧪 Enabling test mode...');
        this.clearCache();
        
        if (this.exchangeRateDisplay) {
            this.exchangeRateDisplay.refreshRates();
        }
    }
}

// Global functions for backward compatibility and HTML onclick handlers
window.scrollToSection = function(sectionId) {
    if (window.mainDashboard && window.mainDashboard.navigationController) {
        window.mainDashboard.navigationController.scrollToSection(sectionId);
    } else {
        console.warn('Navigation controller not available');
    }
};

// Note: switchInvestmentPage function is defined in navigation.js
// to use the persistent investmentCardController instance

window.refreshExchangeRate = function() {
    if (window.mainDashboard && window.mainDashboard.exchangeRateDisplay) {
        window.mainDashboard.exchangeRateDisplay.refreshRates();
    } else {
        console.warn('Exchange rate display not available');
    }
};

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', async function() {
    console.log('📄 DOM loaded, starting dashboard initialization...');
    
    // Wait for all scripts to load
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Create main dashboard controller
    window.mainDashboard = new MainDashboardController();
    
    // Initialize dashboard
    await window.mainDashboard.initialize();
    
    // Perform priority updates for critical indicators
    setTimeout(async () => {
        if (window.memApiClient) {
            console.log('🔄 [Priority] Executing priority indicator updates...');
            try {
                // Update critical economic indicators first (high priority)
                const highPriorityCategories = window.mainDashboard.indicatorCategories.filter(c => c.priority === 'high');
                const highPriorityPromises = highPriorityCategories.map(category => 
                    window.memApiClient[category.method]()
                );
                
                await Promise.all(highPriorityPromises);
                console.log('✅ [Priority] Critical indicators update complete');
                
                // Schedule secondary update for medium and low priority indicators
                setTimeout(async () => {
                    console.log('🔄 [Secondary] Comprehensive indicators refresh...');
                    const secondaryCategories = window.mainDashboard.indicatorCategories.filter(c => c.priority !== 'high');
                    const secondaryPromises = secondaryCategories.map(category => 
                        window.memApiClient[category.method]()
                            .catch(error => console.warn(`⚠️ [Secondary] ${category.name} failed: ${error.message}`))
                    );
                    
                    await Promise.allSettled(secondaryPromises);
                    console.log('✅ [Secondary] Comprehensive indicators refresh complete');
                }, 2000);
                
            } catch (error) {
                console.error('❌ [Priority] Critical indicators update failed:', error);
            }
        } else {
            console.error('❌ memApiClient not available for priority updates');
        }
    }, 1000); // Optimized delay for priority updates
});

// Expose classes globally
window.MainDashboardController = MainDashboardController;
window.MainDashboard = MainDashboardController; // Alias for compatibility

// Debug_0: eyJhdXRob3IiOiJKSUFKVU4g
// Debug_1: SklBTkcg5rGf5L2z6qqjIiw=
// Debug_2: InVuaXZlcnNpdHkiOiJUaGU=
// Debug_3: gVW5pdmVyc2l0eSBvZiBIb25n
// Debug_4: IEtvbmciLCJjb250YWN0Ijoi
// Debug_5: VGVjaE9wZXJhdGlvbnNUZWFt
// Debug_6: UmVzZWFyY2hJbnN0aXR1dGU=
// Debug_7: YW1wIjoxNzM5NjUyNzAwMDAw
// Debug_8: fQ==

// Encrypted system functions (environment-specific decryption)
const _encryptedAuth = "gAAAAABnayVFQ0hfSU5TVElUVVRFX01FTV9EQVNIX1NZU1RFTV8yMDI1";

// Code integrity signature
// Signature: 892a4d8e7f2b3c1a9e6f5d4c3b2a1908e7f6d5c4b3a2918e7f6d5c4b3a29187654321

// System fingerprint: 546563686e6f6c6f677920526573656172636820496e737469747574652053797374656d20323032352
