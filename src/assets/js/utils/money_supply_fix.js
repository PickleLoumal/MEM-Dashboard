class MoneySupplyFix {
    constructor() {
        // 使用动态API配置，而不是硬编码
        this.apiBaseUrl = window.API_CONFIG ? window.API_CONFIG.baseUrl.replace('/api', '') : 'http://localhost:8000';
        this.updateInProgress = false;
        this.retryCount = 0;
        this.maxRetries = 3;
        
        console.log(`💰 Money Supply Fix initialized with API: ${this.apiBaseUrl}`);
    }

    /**
     * Force update all money supply indicators directly from PostgreSQL API
     */
    async forceUpdate() {
        if (this.updateInProgress) {
            console.log('⏳ Money supply update already in progress...');
            return;
        }

        this.updateInProgress = true;
        console.log('💪 Forcing money supply data update...');

        try {
            // Clear any existing cache that might interfere
            this.clearCache();

            // Update all indicators in parallel
            await Promise.allSettled([
                this.updateM2(),
                this.updateM1(),
                this.updateM2V(),
                this.updateMonetaryBase()
            ]);

            console.log('✅ Money supply force update completed');
            this.retryCount = 0;
            
        } catch (error) {
            console.error('❌ Money supply force update failed:', error);
            
            if (this.retryCount < this.maxRetries) {
                this.retryCount++;
                console.log(`🔄 Retrying money supply update (${this.retryCount}/${this.maxRetries})...`);
                setTimeout(() => this.forceUpdate(), 2000 * this.retryCount);
            }
        } finally {
            this.updateInProgress = false;
        }
    }

    /**
     * Update M2 Money Supply
     */
    async updateM2() {
        const element = document.getElementById('us-m2-supply');
        if (!element) {
            console.error('❌ M2 element not found');
            return;
        }

        try {
            console.log('📊 Updating M2 Money Supply...');
            element.innerHTML = 'Loading...';

            const response = await fetch(`${this.apiBaseUrl}/api/fred/m2`);
            const data = await response.json();

            if (data.success && data.data) {
                const value = parseFloat(data.data.value);
                const valueInTrillions = (value / 1000).toFixed(2);
                
                let changeDisplay = '';
                if (data.data.yoy_change !== null && data.data.yoy_change !== undefined) {
                    const changeClass = data.data.yoy_change >= 0 ? 'metric-change-positive' : 'metric-change-negative';
                    const changeSign = data.data.yoy_change >= 0 ? '+' : '';
                    changeDisplay = ` <span class="${changeClass}">[${changeSign}${data.data.yoy_change.toFixed(2)}% YoY]</span>`;
                }

                element.innerHTML = `$${valueInTrillions}T${changeDisplay} <span class="text-gray-500 text-xs">(FRED ${data.data.formatted_date})</span>`;
                console.log(`✅ M2 updated successfully: $${valueInTrillions}T`);
                
            } else {
                throw new Error('Invalid M2 data format');
            }
        } catch (error) {
            console.error('❌ M2 update failed:', error);
            element.innerHTML = '$21.86T <span class="text-gray-500 text-xs">(Fallback)</span>';
        }
    }

    /**
     * Update M1 Money Supply
     */
    async updateM1() {
        const element = document.getElementById('us-m1-supply');
        if (!element) {
            console.error('❌ M1 element not found');
            return;
        }

        try {
            console.log('📊 Updating M1 Money Supply...');
            element.innerHTML = 'Loading...';

            const response = await fetch(`${this.apiBaseUrl}/api/fred/m1`);
            const data = await response.json();

            if (data.success && data.data) {
                const value = parseFloat(data.data.value);
                const valueInTrillions = (value / 1000).toFixed(2);
                
                let changeDisplay = '';
                if (data.data.yoy_change !== null && data.data.yoy_change !== undefined) {
                    const changeClass = data.data.yoy_change >= 0 ? 'metric-change-positive' : 'metric-change-negative';
                    const changeSign = data.data.yoy_change >= 0 ? '+' : '';
                    changeDisplay = ` <span class="${changeClass}">[${changeSign}${data.data.yoy_change.toFixed(2)}% YoY]</span>`;
                }

                element.innerHTML = `$${valueInTrillions}T${changeDisplay} <span class="text-gray-500 text-xs">(FRED ${data.data.formatted_date})</span>`;
                console.log(`✅ M1 updated successfully: $${valueInTrillions}T`);
                
            } else {
                throw new Error('Invalid M1 data format');
            }
        } catch (error) {
            console.error('❌ M1 update failed:', error);
            element.innerHTML = '$18.67T <span class="text-gray-500 text-xs">(Fallback)</span>';
        }
    }

    /**
     * Update M2 Money Velocity
     */
    async updateM2V() {
        const element = document.getElementById('us-m2v-velocity');
        if (!element) {
            console.error('❌ M2V element not found');
            return;
        }

        try {
            console.log('📊 Updating M2 Money Velocity...');
            element.innerHTML = 'Loading...';

            const response = await fetch(`${this.apiBaseUrl}/api/fred/m2v`);
            const data = await response.json();

            if (data.success && data.data) {
                const value = parseFloat(data.data.value);
                
                let changeDisplay = '';
                if (data.data.yoy_change !== null && data.data.yoy_change !== undefined) {
                    const changeClass = data.data.yoy_change >= 0 ? 'metric-change-positive' : 'metric-change-negative';
                    const changeSign = data.data.yoy_change >= 0 ? '+' : '';
                    changeDisplay = ` <span class="${changeClass}">[${changeSign}${data.data.yoy_change.toFixed(2)}% YoY]</span>`;
                }

                element.innerHTML = `${value.toFixed(3)}${changeDisplay} <span class="text-gray-500 text-xs">(FRED ${data.data.formatted_date})</span>`;
                console.log(`✅ M2V updated successfully: ${value.toFixed(3)}`);
                
            } else {
                throw new Error('Invalid M2V data format');
            }
        } catch (error) {
            console.error('❌ M2V update failed:', error);
            element.innerHTML = '1.387 <span class="text-gray-500 text-xs">(Fallback)</span>';
        }
    }

    /**
     * Update Monetary Base
     */
    async updateMonetaryBase() {
        const element = document.getElementById('monetary-base-total');
        if (!element) {
            console.error('❌ Monetary Base element not found');
            return;
        }

        try {
            console.log('📊 Updating Monetary Base...');
            element.innerHTML = 'Loading...';

            const response = await fetch(`${this.apiBaseUrl}/api/fred/monetary-base`);
            const data = await response.json();

            if (data.success && data.data) {
                const value = parseFloat(data.data.value);
                const valueInTrillions = (value / 1000).toFixed(2);
                
                let changeDisplay = '';
                if (data.data.yoy_change !== null && data.data.yoy_change !== undefined) {
                    const changeClass = data.data.yoy_change >= 0 ? 'metric-change-positive' : 'metric-change-negative';
                    const changeSign = data.data.yoy_change >= 0 ? '+' : '';
                    changeDisplay = ` <span class="${changeClass}">[${changeSign}${data.data.yoy_change.toFixed(2)}% YoY]</span>`;
                }

                element.innerHTML = `$${valueInTrillions}T${changeDisplay} <span class="text-gray-500 text-xs">(FRED ${data.data.formatted_date})</span>`;
                console.log(`✅ Monetary Base updated successfully: $${valueInTrillions}T`);
                
            } else {
                throw new Error('Invalid Monetary Base data format');
            }
        } catch (error) {
            console.error('❌ Monetary Base update failed:', error);
            element.innerHTML = '$5.73T <span class="text-gray-500 text-xs">(Fallback)</span>';
        }
    }

    /**
     * Clear any interfering cache
     */
    clearCache() {
        const cacheKeys = [
            'M2_DATA', 'M1_DATA', 'M2V_DATA', 'MONETARY_BASE_DATA',
            'lastM2Update', 'lastM1Update', 'lastM2VUpdate', 'lastMonetaryBaseUpdate'
        ];
        
        cacheKeys.forEach(key => localStorage.removeItem(key));
        console.log('🧹 Cache cleared for money supply data');
    }

    /**
     * Schedule periodic updates
     */
    startPeriodicUpdates() {
        // Update every 5 minutes
        setInterval(() => {
            console.log('⏰ Periodic money supply update triggered');
            this.forceUpdate();
        }, 5 * 60 * 1000);
        
        console.log('⏰ Periodic updates scheduled every 5 minutes');
    }

    /**
     * Check if all money supply elements are displaying correctly
     */
    isDataDisplayedCorrectly() {
        const elements = [
            { id: 'us-m2-supply', name: 'M2' },
            { id: 'us-m1-supply', name: 'M1' },
            { id: 'us-m2v-velocity', name: 'M2V' },
            { id: 'monetary-base-total', name: 'Monetary Base' }
        ];

        let allCorrect = true;
        elements.forEach(item => {
            const element = document.getElementById(item.id);
            if (element && element.textContent.includes('Loading')) {
                console.warn(`⚠️ ${item.name} still showing "Loading..."`);
                allCorrect = false;
            }
        });

        return allCorrect;
    }
}

// Initialize the money supply fix
let moneySupplyFix;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for other scripts to load
    setTimeout(() => {
        moneySupplyFix = new MoneySupplyFix();
        
        // Force immediate update
        moneySupplyFix.forceUpdate();
        
        // Start periodic updates
        moneySupplyFix.startPeriodicUpdates();
        
        // Check after 3 seconds if data loaded correctly
        setTimeout(() => {
            if (!moneySupplyFix.isDataDisplayedCorrectly()) {
                console.log('🔧 Data not displaying correctly, forcing another update...');
                moneySupplyFix.forceUpdate();
            }
        }, 3000);
        
    }, 1000);
});

// Global access for manual debugging
window.moneySupplyFix = moneySupplyFix;
window.fixMoneySupply = () => {
    if (window.moneySupplyFix) {
        window.moneySupplyFix.forceUpdate();
    } else {
        console.error('❌ Money Supply Fix not initialized');
    }
};

console.log('💰 Money Supply Fix script loaded');
