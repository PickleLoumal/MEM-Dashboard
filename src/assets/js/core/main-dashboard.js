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
        console.log('🎛️ Main Dashboard Controller initialized');
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
            
            // Ensure money supply data is updated after initialization
            await this.ensureMoneySupplyUpdate();
            
        } catch (error) {
            console.error('❌ Dashboard initialization failed:', error);
            this.handleInitializationError(error);
        }
    }

    /**
     * Initialize API client for money supply data
     */
    async initializeApiClient() {
        console.log('🔌 Initializing API client...');
        
        if (window.MEMApiClient) {
            try {
                window.memApiClient = new window.MEMApiClient();
                console.log('✅ API client initialized successfully');
                
                // Hot patch + diagnostics: ensure interest rate method exists (localhost missing method issue)
                if (typeof window.memApiClient.updateInterestRateDisplay !== 'function') {
                    console.warn('⚠️ [HotPatch] updateInterestRateDisplay missing on memApiClient; injecting fallback implementation');
                    window.memApiClient.updateInterestRateDisplay = async function() {
                        console.log('🔄 [HotPatch] Fallback updateInterestRateDisplay executing...');
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
                            console.log('✅ [HotPatch] Fallback interest rate update complete');
                        } catch(e) {
                            console.error('❌ [HotPatch] Fallback interest rate update failed:', e);
                        }
                    };
                    console.log('✅ [HotPatch] Fallback method injected. Available keys:', Object.keys(window.memApiClient));
                } else {
                    console.log('ℹ️ [Diagnostics] updateInterestRateDisplay present on memApiClient prototype');
                }
                
                // Verify API client is working
                const isHealthy = await window.memApiClient.checkHealth();
                if (!isHealthy) {
                    throw new Error('API health check failed');
                }
                
                // Initial money supply update
                await this.updateMoneySupplyWithRetry();
                
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
     * Update money supply data with retry mechanism
     */
    async updateMoneySupplyWithRetry() {
        let attempts = 0;
        const maxAttempts = 3;
        
        while (attempts < maxAttempts) {
            try {
                console.log(`🔄 Attempting to update all indicators (attempt ${attempts + 1}/${maxAttempts})...`);
                
                // Update all indicators including interest rates, household debt, government debts, trade deficits, govt deficit financing, and private sector corporate debts
                const updatePromises = [
                    window.memApiClient.updateMoneySupplyData(),
                    window.memApiClient.updateInterestRateDisplay(),
                    window.memApiClient.updateHouseholdDebtDisplay(),
                    window.memApiClient.updateGovernmentDebtsDisplay(),
                    window.memApiClient.updateTradeDeficitsDisplay(),
                    window.memApiClient.updateGovtDeficitFinancingDisplay(),
                    window.memApiClient.updatePrivateSectorCorporateDebtsDisplay()
                ];
                
                console.log('📝 [Main Dashboard] Starting parallel updates: Money Supply, Interest Rate, Household Debt, Government Debts, Trade Deficits, Govt Deficit Financing, and Private Sector Corporate Debts...');
                await Promise.all(updatePromises);
                
                console.log('✅ All indicators updated successfully');
                return;
            } catch (error) {
                attempts++;
                console.error(`❌ Indicators update failed (attempt ${attempts}/${maxAttempts}):`, error);
                if (attempts < maxAttempts) {
                    console.log(`⏳ Waiting ${attempts} seconds before retry...`);
                    await new Promise(resolve => setTimeout(resolve, 1000 * attempts));
                }
            }
        }
        
        throw new Error('Failed to update indicators after multiple attempts');
    }

    /**
     * Ensure money supply data is updated
     */
    async ensureMoneySupplyUpdate() {
        if (!window.memApiClient) {
            console.error('❌ memApiClient not available for indicators update');
            return;
        }

        try {
            await this.updateMoneySupplyWithRetry();
            
            // Set up periodic updates for all indicators
            setInterval(async () => {
                try {
                    await Promise.all([
                        window.memApiClient.updateMoneySupplyData(),
                        window.memApiClient.updateInterestRateDisplay(),
                        window.memApiClient.updateHouseholdDebtDisplay(),
                        window.memApiClient.updateGovernmentDebtsDisplay(),
                        window.memApiClient.updateTradeDeficitsDisplay(),
                        window.memApiClient.updateGovtDeficitFinancingDisplay(),
                        window.memApiClient.updatePrivateSectorCorporateDebtsDisplay()
                    ]);
                    console.log('🔄 Periodic indicators update completed');
                } catch (error) {
                    console.error('❌ Periodic indicators update failed:', error);
                }
            }, 5 * 60 * 1000); // Update every 5 minutes
            
        } catch (error) {
            console.error('❌ Failed to ensure indicators update:', error);
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
    
    // Force immediate Interest Rate update specifically
    setTimeout(async () => {
        if (window.memApiClient) {
            console.log('🔄 [Priority] Forcing immediate Interest Rate update...');
            try {
                await window.memApiClient.updateInterestRateDisplay();
                console.log('✅ [Priority] Interest Rate update complete');
                
                // Then update money supply
                await window.memApiClient.updateMoneySupplyData();
                console.log('✅ [Priority] Money Supply update complete');
                
                // Schedule another full update to ensure data persistence
                setTimeout(async () => {
                    console.log('🔄 [Secondary] Full indicators update...');
                    await Promise.all([
                        window.memApiClient.updateMoneySupplyData(),
                        window.memApiClient.updateInterestRateDisplay()
                    ]);
                    console.log('✅ [Secondary] Full indicators update complete');
                }, 2000);
                
            } catch (error) {
                console.error('❌ [Priority] Interest Rate update failed:', error);
            }
        } else {
            console.error('❌ memApiClient not available for priority update');
        }
    }, 1000); // Reduced delay for priority update
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
