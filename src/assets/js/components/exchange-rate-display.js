/**
 * Exchange Rate Display Manager
 * Handles the display and caching of exchange rate data
 */
class ExchangeRateDisplay {
    constructor() {
        this.supportedCurrencies = ['CNY', 'EUR', 'HKD', 'CAD', 'MXN'];
        this.cacheTimeout = 60 * 60 * 1000; // 1 hour in milliseconds
        console.log('💱 Exchange Rate Display Manager initialized');
    }

    /**
     * Update all exchange rates with fallback chain
     */
    async updateAllRates() {
        try {
            console.log('📊 Fetching exchange rates...');
            let data = await this.fetchFromPrimaryAPI();
            
            if (!data || !data.rates) {
                console.log('🔄 Primary API failed, trying alternative...');
                data = await this.fetchFromAlternativeAPI();
            }
            
            if (data && data.rates) {
                this.displayRates(data.rates);
                this.updateMoneySupply();
                localStorage.setItem('lastUSDCNYUpdate', Date.now().toString());
                console.log('✅ Exchange rates updated successfully');
            } else {
                throw new Error('No valid rate data received from any API');
            }
        } catch (error) {
            console.error('❌ All APIs failed:', error);
            this.displayFallbackRates();
        }
    }

    /**
     * Fetch from primary exchange rate API
     */
    async fetchFromPrimaryAPI() {
        try {
            const response = await fetch('https://open.er-api.com/v6/latest/USD');
            return await response.json();
        } catch (error) {
            console.log('Primary API error:', error);
            return null;
        }
    }

    /**
     * Fetch from alternative exchange rate API
     */
    async fetchFromAlternativeAPI() {
        try {
            const response = await fetch('https://api.exchangerate-api.com/v4/latest/USD');
            return await response.json();
        } catch (error) {
            console.log('Alternative API error:', error);
            return null;
        }
    }

    /**
     * Display exchange rates with change indicators
     */
    displayRates(rates) {
        const timestamp = new Date().toLocaleDateString();
        
        this.supportedCurrencies.forEach(currency => {
            const rate = rates[currency];
            if (!rate) return;
            
            const elementId = `usd-${currency.toLowerCase()}-rate`;
            const storageKey = `previousUSD${currency}`;
            const preStorageKey = `prePreviousUSD${currency}`;
            
            // Store current as pre-previous before updating
            const currentRate = localStorage.getItem(storageKey);
            if (currentRate) {
                localStorage.setItem(preStorageKey, currentRate);
            }
            
            // Calculate change display
            const changeDisplay = this.calculateChangeDisplay(rate, currentRate);
            
            // Update DOM
            const element = document.getElementById(elementId);
            if (element) {
                element.innerHTML = `${rate.toFixed(4)}${changeDisplay} <span class="text-gray-500 text-xs">(${timestamp})</span>`;
            }
            
            // Store new rate
            localStorage.setItem(storageKey, rate.toString());
        });
    }

    /**
     * Calculate change display HTML
     */
    calculateChangeDisplay(currentRate, previousRate) {
        if (!previousRate) return '';
        
        const change = ((currentRate - parseFloat(previousRate)) / parseFloat(previousRate) * 100);
        const changeClass = change >= 0 ? 'metric-change-positive' : 'metric-change-negative';
        const changeSign = change >= 0 ? '+' : '';
        
        return ` <span class="${changeClass}">[${changeSign}${change.toFixed(2)}%]</span>`;
    }

    /**
     * Update money supply data - DISABLED to prevent conflicts
     * This component should only handle exchange rates
     */
    async updateMoneySupply() {
        // DISABLED: Money supply is now exclusively managed by API Client
        console.log('💡 ExchangeRateDisplay: Money supply management delegated to API Client');
        // Do nothing - let the main API client handle money supply updates
    }

    /**
     * Display fallback money supply values
     */
    displayFallbackMoneySupply() {
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
     * Display fallback exchange rates ONLY
     * Money supply fallbacks removed to prevent conflicts
     */
    displayFallbackRates() {
        const timestamp = new Date().toLocaleDateString();
        const fallbackRates = {
            CNY: 7.2450,
            EUR: 0.9200,
            HKD: 7.8100,
            CAD: 1.3520,
            MXN: 17.2500
        };
        
        this.supportedCurrencies.forEach(currency => {
            const elementId = `usd-${currency.toLowerCase()}-rate`;
            const element = document.getElementById(elementId);
            if (element) {
                element.innerHTML = `${fallbackRates[currency].toFixed(4)} <span class="text-gray-500 text-xs">(Fallback - ${timestamp})</span>`;
            }
        });
        
        // REMOVED: this.displayFallbackMoneySupply() to prevent conflicts
        console.log('💡 ExchangeRateDisplay: Money supply fallback skipped - handled by API Client');
    }

    /**
     * Load cached rates if available and recent
     */
    loadCachedRates() {
        console.log('📱 Loading cached exchange rates...');
        
        const timestamp = localStorage.getItem('lastUSDCNYUpdate');
        const cacheAge = timestamp ? Date.now() - parseInt(timestamp) : Infinity;
        
        if (cacheAge < this.cacheTimeout) {
            this.displayCachedData();
            return true;
        }
        
        return false;
    }

    /**
     * Display cached exchange rate data ONLY
     * Money supply caching removed to prevent conflicts
     */
    displayCachedData() {
        this.supportedCurrencies.forEach(currency => {
            const storageKey = `previousUSD${currency}`;
            const preStorageKey = `prePreviousUSD${currency}`;
            const elementId = `usd-${currency.toLowerCase()}-rate`;
            
            const cachedRate = localStorage.getItem(storageKey);
            const previousRate = localStorage.getItem(preStorageKey);
            
            if (cachedRate) {
                const changeDisplay = this.calculateChangeDisplay(parseFloat(cachedRate), previousRate);
                const element = document.getElementById(elementId);
                if (element) {
                    element.innerHTML = `${parseFloat(cachedRate).toFixed(4)}${changeDisplay} <span class="text-gray-500 text-xs">(Cached)</span>`;
                }
            }
        });
        
        // REMOVED: this.loadCachedMoneySupply() to prevent conflicts
        console.log('💡 ExchangeRateDisplay: Money supply caching skipped - handled by API Client');
    }

    /**
     * Load cached money supply data
     */
    loadCachedMoneySupply() {
        const cachedM2 = localStorage.getItem('previousM2');
        const cachedM1 = localStorage.getItem('previousM1');
        const previousM2 = localStorage.getItem('prePreviousM2');
        const previousM1 = localStorage.getItem('prePreviousM1');
        
        // Display M2
        if (cachedM2) {
            const m2ChangeDisplay = this.calculateChangeDisplay(parseFloat(cachedM2), previousM2);
            const m2Element = document.getElementById('us-m2-supply');
            if (m2Element) {
                m2Element.innerHTML = `$${parseFloat(cachedM2).toFixed(2)}T${m2ChangeDisplay} <span class="text-gray-500 text-xs">(Cached)</span>`;
            }
        }
        
        // Display M1
        if (cachedM1) {
            const m1ChangeDisplay = this.calculateChangeDisplay(parseFloat(cachedM1), previousM1);
            const m1Element = document.getElementById('us-m1-supply');
            if (m1Element) {
                m1Element.innerHTML = `$${parseFloat(cachedM1).toFixed(2)}T${m1ChangeDisplay} <span class="text-gray-500 text-xs">(Cached)</span>`;
            }
        }
        
        // Fallback if no cached data
        if (!cachedM2 || !cachedM1) {
            this.displayFallbackMoneySupply();
        }
    }

    /**
     * Check if rates need updating based on cache timeout
     */
    shouldUpdateRates() {
        const lastUpdate = localStorage.getItem('lastUSDCNYUpdate');
        if (!lastUpdate) return true;
        
        const now = Date.now();
        return (now - parseInt(lastUpdate)) > this.cacheTimeout;
    }

    /**
     * Manually refresh all rates
     */
    async refreshRates() {
        console.log('🔄 Manual refresh triggered');
        
        // Show loading state
        this.showLoadingState();
        
        // Force update
        await this.updateAllRates();
    }

    /**
     * Show loading state for exchange rates ONLY
     * Money supply loading states removed to prevent conflicts
     */
    showLoadingState() {
        this.supportedCurrencies.forEach(currency => {
            const elementId = `usd-${currency.toLowerCase()}-rate`;
            const element = document.getElementById(elementId);
            if (element) {
                element.innerHTML = 'Updating...';
            }
        });
        
        // REMOVED: Money supply loading states to prevent conflicts
        console.log('💡 ExchangeRateDisplay: Money supply loading states skipped - handled by API Client');
    }

    /**
     * Initialize automatic refresh timer
     */
    startAutoRefresh() {
        // Refresh every 24 hours
        setInterval(() => {
            if (this.shouldUpdateRates()) {
                console.log('🕒 Auto-refresh triggered');
                this.updateAllRates();
            }
        }, 86400000); // 24 hours in milliseconds
    }
}

// Make class available globally
window.ExchangeRateDisplay = ExchangeRateDisplay;
