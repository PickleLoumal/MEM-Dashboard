// Exchange Rate Manager for MEM Dashboard
class ExchangeRateManager {
    constructor() {
        this.currencies = ['CNY', 'EUR', 'HKD', 'CAD', 'MXN'];
        this.apiEndpoints = {
            primary: 'https://api.exchangerate-api.com/v4/latest/USD',
            fallback: 'https://open.er-api.com/v6/latest/USD',
            alternative: 'https://api.fixer.io/latest?base=USD&symbols=CNY,HKD,CAD'
        };
        this.updateInterval = 60 * 60 * 1000; // 1 hour
        this.memApiClient = null;
    }

    /**
     * Initialize the exchange rate manager
     */
    async init() {
        console.log('🚀 Initializing Exchange Rate Manager...');
        
        // Use the global MEM API Client (initialized by main dashboard)
        // Wait a bit for it to be available
        let attempts = 0;
        while (!window.memApiClient && attempts < 10) {
            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
        }
        
        if (window.memApiClient) {
            this.memApiClient = window.memApiClient;
            console.log('✅ Using global MEM API Client');
        } else {
            console.warn('⚠️ Global MEMApiClient not available');
        }

        // Load initial data
        await this.loadExchangeRates();
        
        // Setup periodic updates
        this.setupPeriodicUpdates();
        
        console.log('✅ Exchange Rate Manager initialized');
    }

    /**
     * Check if we need to update rates (limit API calls)
     */
    shouldUpdate() {
        const lastUpdate = localStorage.getItem('lastUSDCNYUpdate');
        if (!lastUpdate) return true;
        
        const now = Date.now();
        return (now - parseInt(lastUpdate)) > this.updateInterval;
    }

    /**
     * Load exchange rates using preferred API
     */
    async loadExchangeRates() {
        if (this.shouldUpdate()) {
            console.log('🔄 Fetching fresh exchange rates...');
            try {
                await this.fetchFromSimpleAPI();
            } catch (error) {
                console.log('❌ Simple API failed, trying primary API...');
                try {
                    await this.fetchFromPrimaryAPI();
                } catch (error2) {
                    console.log('❌ Primary API also failed, using fallbacks');
                    this.useFallbackData();
                }
            }
        } else {
            console.log('📋 Using cached exchange rates...');
            this.loadFromCache();
        }
    }

    /**
     * Fetch from simple/reliable API
     */
    async fetchFromSimpleAPI() {
        const response = await fetch(this.apiEndpoints.fallback);
        const data = await response.json();
        
        if (data && data.rates) {
            this.updateRatesDisplay(data.rates);
            await this.updateMoneySupply();
            this.saveToStorage(data.rates);
            localStorage.setItem('lastUSDCNYUpdate', Date.now().toString());
            console.log('✅ Exchange rates updated via simple API');
        } else {
            throw new Error('Invalid data format from simple API');
        }
    }

    /**
     * Fetch from primary API
     */
    async fetchFromPrimaryAPI() {
        const response = await fetch(this.apiEndpoints.primary);
        const data = await response.json();
        
        if (data && data.rates) {
            this.updateRatesDisplay(data.rates);
            await this.updateMoneySupply();
            this.saveToStorage(data.rates);
            localStorage.setItem('lastUSDCNYUpdate', Date.now().toString());
            console.log('✅ Exchange rates updated via primary API');
        } else {
            throw new Error('Invalid data format from primary API');
        }
    }

    /**
     * Update money supply data using the API client
     */
    async updateMoneySupply() {
        try {
            if (this.memApiClient) {
                console.log('🔄 Exchange Rate Manager: Updating money supply via API client...');
                await this.memApiClient.updateMoneySupplyData();
                console.log('✅ Exchange Rate Manager: Money supply updated successfully');
            } else {
                console.warn('⚠️ MEMApiClient not available in Exchange Rate Manager, skipping money supply update');
                // Don't call useMoneySupplyFallback() - let the main API client handle it
            }
        } catch (error) {
            console.log('❌ Exchange Rate Manager: Money supply API failed:', error.message);
            // Don't use fallback here - let the main API client handle failures
        }
    }

    /**
     * Update exchange rates display in the UI
     */
    updateRatesDisplay(rates) {
        const timestamp = new Date().toLocaleDateString();
        
        this.currencies.forEach(currency => {
            const rate = rates[currency];
            if (rate) {
                const elementId = `usd-${currency.toLowerCase()}-rate`;
                const element = document.getElementById(elementId);
                
                if (element) {
                    const changeDisplay = this.calculateChangeDisplay(currency, rate);
                    element.innerHTML = 
                        `${rate.toFixed(4)}${changeDisplay} <span class="text-gray-500 text-xs">(${timestamp})</span>`;
                }
            }
        });
    }

    /**
     * Calculate and format the change display for a currency
     */
    calculateChangeDisplay(currency, currentRate) {
        const storageKey = `previousUSD${currency}`;
        const preStorageKey = `prePreviousUSD${currency}`;
        
        // Store current as pre-previous before updating
        const previousRate = localStorage.getItem(storageKey);
        if (previousRate) {
            localStorage.setItem(preStorageKey, previousRate);
        }
        
        if (previousRate) {
            const change = ((currentRate - parseFloat(previousRate)) / parseFloat(previousRate) * 100);
            const changeClass = change >= 0 ? 'metric-change-positive' : 'metric-change-negative';
            const changeSign = change >= 0 ? '+' : '';
            return ` <span class="${changeClass}">[${changeSign}${change.toFixed(2)}%]</span>`;
        }
        
        // Store current rate for next comparison
        localStorage.setItem(storageKey, currentRate.toString());
        return '';
    }

    /**
     * Save rates to localStorage for caching
     */
    saveToStorage(rates) {
        this.currencies.forEach(currency => {
            const rate = rates[currency];
            if (rate) {
                localStorage.setItem(`previousUSD${currency}`, rate.toString());
            }
        });
    }

    /**
     * Load cached rates from localStorage
     */
    loadFromCache() {
        this.currencies.forEach(currency => {
            const cachedRate = localStorage.getItem(`previousUSD${currency}`);
            const previousRate = localStorage.getItem(`prePreviousUSD${currency}`);
            
            if (cachedRate) {
                const elementId = `usd-${currency.toLowerCase()}-rate`;
                const element = document.getElementById(elementId);
                
                if (element) {
                    let changeDisplay = '';
                    if (previousRate) {
                        const change = ((parseFloat(cachedRate) - parseFloat(previousRate)) / parseFloat(previousRate) * 100);
                        const changeClass = change >= 0 ? 'metric-change-positive' : 'metric-change-negative';
                        const changeSign = change >= 0 ? '+' : '';
                        changeDisplay = ` <span class="${changeClass}">[${changeSign}${change.toFixed(2)}%]</span>`;
                    }
                    
                    element.innerHTML = 
                        `${parseFloat(cachedRate).toFixed(4)}${changeDisplay} <span class="text-gray-500 text-xs">(Cached)</span>`;
                }
            }
        });

        // Load cached money supply data
        this.loadCachedMoneySupply();
    }

    /**
     * Load cached money supply data
     */
    loadCachedMoneySupply() {
        // Exchange Rate Manager should not manage money supply display
        // This is now handled by the main API client
        console.log('💡 Exchange Rate Manager: Skipping cached money supply load - handled by main API client');
    }

    /**
     * Update money supply element with cached data
     */
    updateMoneySupplyElement(elementId, currentValue, previousValue, type) {
        const element = document.getElementById(elementId);
        if (!element) return;

        let changeDisplay = '';
        if (previousValue) {
            const change = ((parseFloat(currentValue) - parseFloat(previousValue)) / parseFloat(previousValue) * 100);
            const changeClass = change >= 0 ? 'metric-change-positive' : 'metric-change-negative';
            const changeSign = change >= 0 ? '+' : '';
            changeDisplay = ` <span class="${changeClass}">[${changeSign}${change.toFixed(2)}%]</span>`;
        }

        element.innerHTML = 
            `$${parseFloat(currentValue).toFixed(2)}T${changeDisplay} <span class="text-gray-500 text-xs">(Cached)</span>`;
    }

    /**
     * Use fallback data when APIs fail
     */
    useFallbackData() {
        const timestamp = new Date().toLocaleDateString();
        const fallbackRates = {
            CNY: 7.2450,
            EUR: 0.9200,
            HKD: 7.8100,
            CAD: 1.3520,
            MXN: 17.2500
        };

        this.currencies.forEach(currency => {
            const elementId = `usd-${currency.toLowerCase()}-rate`;
            const element = document.getElementById(elementId);
            if (element) {
                element.innerHTML = 
                    `${fallbackRates[currency].toFixed(4)} <span class="text-gray-500 text-xs">(Fallback - ${timestamp})</span>`;
            }
        });

        // Don't use money supply fallback - let main API client handle money supply
        console.log('💡 Exchange Rate Manager: Using exchange rate fallbacks only');
    }

    /**
     * Use fallback money supply data
     */
    useMoneySupplyFallback() {
        const m2Element = document.getElementById('us-m2-supply');
        const m1Element = document.getElementById('us-m1-supply');

        if (m2Element) {
            m2Element.innerHTML = '$21.08T <span class="text-gray-500 text-xs">(FRED Apr 2025)</span>';
        }

        if (m1Element) {
            m1Element.innerHTML = '$18.53T <span class="text-gray-500 text-xs">(FRED May 2024)</span>';
        }
    }

    /**
     * Setup periodic updates
     */
    setupPeriodicUpdates() {
        setInterval(() => {
            if (this.shouldUpdate()) {
                this.loadExchangeRates();
            }
        }, 86400000); // Check every 24 hours
    }

    /**
     * Manual refresh function
     */
    async refresh() {
        console.log('🔄 Manual refresh triggered...');
        
        // Show loading state
        this.currencies.forEach(currency => {
            const elementId = `usd-${currency.toLowerCase()}-rate`;
            const element = document.getElementById(elementId);
            if (element) {
                element.innerHTML = 'Updating...';
            }
        });

        const m2Element = document.getElementById('us-m2-supply');
        const m1Element = document.getElementById('us-m1-supply');
        if (m2Element) m2Element.innerHTML = 'Updating...';
        if (m1Element) m1Element.innerHTML = 'Updating...';

        // Force update
        try {
            await this.fetchFromSimpleAPI();
        } catch (error) {
            try {
                await this.fetchFromPrimaryAPI();
            } catch (error2) {
                this.useFallbackData();
            }
        }
    }
}

// Make class available globally
window.ExchangeRateManager = ExchangeRateManager;

// Global instance
let exchangeRateManager;

// NOTE: Initialization now controlled by main-dashboard.js to prevent conflicts
// No auto-initialization here to avoid multiple DOMContentLoaded listeners

// Global refresh function
function refreshExchangeRate() {
    if (exchangeRateManager) {
        exchangeRateManager.refresh();
    }
}
