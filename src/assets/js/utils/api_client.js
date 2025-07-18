/**
 * MEM Dashboard API Client
 * Simplified API client to fetch data from the Python backend service
 */

function MEMApiClient(baseUrl = null) {
    // Auto-detect environment and API configuration
    if (baseUrl) {
        this.baseUrl = baseUrl;
    } else if (window.API_CONFIG && window.API_CONFIG.baseUrl) {
        // Use configured API (Django or Flask)
        this.baseUrl = window.API_CONFIG.baseUrl;
        console.log(`🔗 Using ${window.API_CONFIG.name}: ${this.baseUrl}`);
    } else if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        // Development fallback to Flask API
        this.baseUrl = 'http://localhost:5001/api';
        console.log('🔗 Using default Flask API: ' + this.baseUrl);
    } else {
        // Production: use static JSON files (no serverless function auth issues)
        this.baseUrl = '/api';
    }
    this.cache = new Map();
    this.cacheTimeout = 60 * 60 * 1000; // 1 hour cache
    
    // Fallback data for when API calls fail
    this.fallbackData = {
        M2: {
            success: true,
            data: {
                value: 21862.5,
                yoy_change: 4.44,
                date: "2025-04-01",
                formatted_date: "Apr 2025",
                series_id: "M2SL",
                source: "FRED backup data"
            }
        },
        CPI: {
            success: true,
            data: {
                value: 307.8,
                yoy_change: 2.4,
                date: "2025-05-01",
                formatted_date: "May 2025",
                series_id: "CPIAUCSL",
                source: "FRED backup data"
            }
        },
        UNRATE: {
            success: true,
            data: {
                value: 3.7,
                yoy_change: -0.1,
                date: "2025-05-01",
                formatted_date: "May 2025",
                series_id: "UNRATE",
                source: "FRED backup data"
            }
        },
        M1: {
            success: true,
            data: {
                value: 18668.0,
                yoy_change: 3.86,
                date: "2025-04-01",
                formatted_date: "Apr 2025",
                series_id: "M1SL",
                source: "FRED backup data"
            }
        },
        M2V: {
            success: true,
            data: {
                value: 1.383,
                yoy_change: 0.73,
                date: "2025-01-01",
                formatted_date: "Q1 2025",
                series_id: "M2V",
                source: "FRED backup data"
            }
        },
        MonetaryBase: {
            success: true,
            data: {
                value: 5510.0,
                yoy_change: -3.2,
                date: "2025-05-01",
                formatted_date: "May 2025",
                series_id: "BOGMBASE",
                source: "FRED backup data"
            }
        },
        MotorVehicles: {
            success: true,
            data: {
                value: 750.144,
                yoy_change: -1.8,
                date: "2025-01-01",
                formatted_date: "Q1 2025",
                series_id: "MOTOR_VEHICLES",
                source: "BEA backup data"
            }
        }
    };
    
    console.log(`🔗 API Client initialized with base URL: ${this.baseUrl}`);
}

// Generic fetch with error handling and caching
MEMApiClient.prototype.fetchWithCache = async function(endpoint, cacheKey, fallbackKey = null) {
    // Check cache first
    const cached = this.cache.get(cacheKey);
    if (cached && (Date.now() - cached.timestamp) < this.cacheTimeout) {
        console.log(`📋 Using cached data for ${cacheKey}`);
        return cached.data;
    }

    try {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: 10000 // 10 second timeout
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        
        // Cache successful response
        this.cache.set(cacheKey, {
            data: data,
            timestamp: Date.now()
        });

        return data;
    } catch (error) {
        console.error(`❌ API call failed for ${endpoint}:`, error);
        
        // Use fallback data if available
        if (fallbackKey && this.fallbackData[fallbackKey]) {
            console.log(`🔄 Using fallback data for ${fallbackKey}`);
            return this.fallbackData[fallbackKey];
        }
        
        throw error;
    }
};

// Check if the API service is healthy
MEMApiClient.prototype.checkHealth = async function() {
    try {
        const response = await fetch(`${this.baseUrl}/health/`, {
            method: 'GET',
            timeout: 5000
        });
        return response.ok;
    } catch (error) {
        console.error('❌ Health check failed:', error);
        return false;
    }
};

// Fetch M2 Money Supply data - 统一FRED API
MEMApiClient.prototype.getM2Data = async function() {
    return await this.fetchWithCache('/fred/m2', 'M2_DATA', 'M2');
};

// Fetch M1 Money Supply data - 统一FRED API
MEMApiClient.prototype.getM1Data = async function() {
    return await this.fetchWithCache('/fred/m1', 'M1_DATA', 'M1');
};

// Fetch M2 Money Velocity data - 统一FRED API
MEMApiClient.prototype.getM2VData = async function() {
    return await this.fetchWithCache('/fred/m2v', 'M2V_DATA', 'M2V');
};

// Get Monetary Base Total data - 统一FRED API
MEMApiClient.prototype.getMonetaryBaseData = async function() {
    return await this.fetchWithCache('/fred/monetary-base', 'MONETARY_BASE_DATA', 'MonetaryBase');
};

// Get Motor Vehicles and Parts data from BEA API - Django推荐端点，从SQL数据库获取
MEMApiClient.prototype.getMotorVehiclesData = async function() {
    console.log('🚗 [API Client] Fetching motor vehicles data...');
    console.log('🔗 [API Client] Base URL:', this.baseUrl);
    
    // 使用Django BEA API从SQL数据库获取数据
    if (this.baseUrl.includes('localhost') || this.baseUrl.includes('127.0.0.1')) {
        // 开发环境：使用Django BEA API (端口8000)
        const endpoint = '/bea/indicators/motor_vehicles/';
        console.log('🔗 [API Client] Using endpoint:', endpoint);
        console.log('🔗 [API Client] Full URL will be:', this.baseUrl + endpoint);
        return await this.fetchWithCache(endpoint, 'MOTOR_VEHICLES_DATA', 'MotorVehicles');
    } else {
        // 生产环境：回退到静态文件
        const endpoint = '/motor-vehicles.json';
        return await this.fetchWithCache(endpoint, 'MOTOR_VEHICLES_DATA', 'MotorVehicles');
    }
};

// Fetch CPI (Consumer Price Index) data - 统一FRED API
MEMApiClient.prototype.getCPIData = async function() {
    return await this.fetchWithCache('/fred/cpi', 'CPI_DATA', 'CPI');
};

// Fetch UNRATE (Unemployment Rate) data - 统一FRED API
MEMApiClient.prototype.getUNRATEData = async function() {
    return await this.fetchWithCache('/fred/unemployment', 'UNRATE_DATA', 'UNRATE');
};

// Fetch Debt-to-GDP data - 统一FRED API
MEMApiClient.prototype.getDebtToGDPData = async function() {
    return await this.fetchWithCache('/fred/debt-to-gdp/', 'DEBT_TO_GDP_DATA', null);
};

// Fetch Housing Starts data - 统一FRED API
MEMApiClient.prototype.getHousingData = async function() {
    return await this.fetchWithCache('/fred/housing', 'HOUSING_DATA', null);
};

// Fetch Federal Funds Rate data - 统一FRED API
MEMApiClient.prototype.getFedFundsData = async function() {
    return await this.fetchWithCache('/fred/fed-funds', 'FED_FUNDS_DATA', null);
};

// Get all FRED indicators at once - 统一FRED API
MEMApiClient.prototype.getAllFREDData = async function() {
    return await this.fetchWithCache('/fred/all', 'ALL_FRED_DATA', null);
};

// Get FRED system status - 统一FRED API
MEMApiClient.prototype.getFREDStatus = async function() {
    return await this.fetchWithCache('/fred/status', 'FRED_STATUS', null);
};

// Update M2 display in the HTML
MEMApiClient.prototype.updateM2Display = async function() {
    const element = document.getElementById('us-m2-supply');
    if (!element) {
        console.error('❌ [API Client] M2 display element not found: us-m2-supply');
        return;
    }

    try {
        console.log('🔄 [API Client] Updating M2 display...');
        element.innerHTML = 'Loading...';
        
        // Force fresh data fetch
        const result = await this.getM2Data();
        console.log('📊 [API Client] M2 API result:', result);
        
        if (result.success && result.data) {
            const data = result.data;
            let changeDisplay = '';
            
            // Convert value from string to number if needed
            const valueNum = parseFloat(data.value);
            
            if (data.yoy_change !== null && data.yoy_change !== undefined) {
                const changeClass = data.yoy_change >= 0 ? 'metric-change-positive' : 'metric-change-negative';
                const changeSign = data.yoy_change >= 0 ? '+' : '';
                changeDisplay = ` <span class="${changeClass}">[${changeSign}${data.yoy_change.toFixed(2)}% YoY]</span>`;
            }
            
            // Format value correctly - it comes in billions, convert to trillions
            const valueInTrillions = (valueNum / 1000).toFixed(2);
            element.innerHTML = 
                `$${valueInTrillions}T${changeDisplay} <span class="text-gray-500 text-xs">(FRED ${data.formatted_date})</span>`;
            
            console.log(`✅ [API Client] M2 updated: $${valueInTrillions}T (${data.formatted_date}) - PostgreSQL Live Data`);
            
            // Store successful update timestamp
            localStorage.setItem('lastM2Update', Date.now().toString());
            
            // Cache the value for fallback
            localStorage.setItem('previousM2', valueNum.toString());
            
        } else {
            throw new Error('PostgreSQL API returned invalid data format');
        }
    } catch (error) {
        console.error('❌ [API Client] Failed to update M2 display:', error);
        
        // Try fallback data if available
        if (this.fallbackData && this.fallbackData.M2) {
            const fallback = this.fallbackData.M2.data;
            const valueInTrillions = (fallback.value / 1000).toFixed(2);
            element.innerHTML = 
                `$${valueInTrillions}T <span class="text-gray-500 text-xs">(${fallback.source})</span>`;
            console.log('⚠️ [API Client] M2 using fallback data');
        } else {
            // Final fallback
            element.innerHTML = 
                'Error Loading <span class="text-gray-500 text-xs">(Connection Issue)</span>';
        }
    }
};

// Update M1 display in the HTML
MEMApiClient.prototype.updateM1Display = async function() {
    const element = document.getElementById('us-m1-supply');
    if (!element) {
        console.error('❌ [API Client] M1 display element not found: us-m1-supply');
        return;
    }

    try {
        console.log('🔄 [API Client] Updating M1 display...');
        element.innerHTML = 'Loading...';
        
        const result = await this.getM1Data();
        console.log('📊 [API Client] M1 API result:', result);
        
        // Handle the new unified FRED API response format - FIX APPLIED
        const data = (result.success && result.data) ? result.data : (result.data ? result.data : null);
        
        if (data && data.value !== undefined) {
            let changeDisplay = '';
            
            // Convert value from string to number if needed
            const valueNum = parseFloat(data.value);
            
            if (data.yoy_change !== null && data.yoy_change !== undefined) {
                const changeClass = data.yoy_change >= 0 ? 'metric-change-positive' : 'metric-change-negative';
                const changeSign = data.yoy_change >= 0 ? '+' : '';
                changeDisplay = ` <span class="${changeClass}">[${changeSign}${data.yoy_change.toFixed(2)}% YoY]</span>`;
            }
            
            // Format value correctly - it comes in billions, convert to trillions
            const valueInTrillions = (valueNum / 1000).toFixed(2);
            element.innerHTML = 
                `$${valueInTrillions}T${changeDisplay} <span class="text-gray-500 text-xs">(FRED ${data.formatted_date})</span>`;
            
            console.log(`✅ [API Client] M1 updated: $${valueInTrillions}T (${data.formatted_date}) - PostgreSQL Live Data`);
        } else {
            throw new Error('PostgreSQL API returned invalid data format');
        }
    } catch (error) {
        console.error('❌ [API Client] Failed to update M1 display:', error);
        
        // Try fallback data if available
        if (this.fallbackData && this.fallbackData.M1) {
            const fallback = this.fallbackData.M1.data;
            const valueInTrillions = (fallback.value / 1000).toFixed(2);
            element.innerHTML = 
                `$${valueInTrillions}T <span class="text-gray-500 text-xs">(${fallback.source})</span>`;
            console.log('⚠️ [API Client] M1 using fallback data');
        } else {
            element.innerHTML = 
                'Error Loading <span class="text-gray-500 text-xs">(PostgreSQL Connection Issue)</span>';
        }
    }
};

// Update M2V display in the HTML
MEMApiClient.prototype.updateM2VDisplay = async function() {
    const element = document.getElementById('us-m2v-velocity');
    if (!element) {
        console.error('❌ [API Client] M2V display element not found: us-m2v-velocity');
        return;
    }

    try {
        console.log('🔄 [API Client] Updating M2V display...');
        element.innerHTML = 'Loading...';
        
        const result = await this.getM2VData();
        console.log('📊 [API Client] M2V API result:', result);
        
        // Handle the new unified FRED API response format - FIX APPLIED
        const data = (result.success && result.data) ? result.data : (result.data ? result.data : null);
        
        if (data && data.value !== undefined) {
            let changeDisplay = '';
            
            // Convert value from string to number if needed
            const valueNum = parseFloat(data.value);
            
            if (data.yoy_change !== null && data.yoy_change !== undefined) {
                const changeClass = data.yoy_change >= 0 ? 'metric-change-positive' : 'metric-change-negative';
                const changeSign = data.yoy_change >= 0 ? '+' : '';
                changeDisplay = ` <span class="${changeClass}">[${changeSign}${data.yoy_change.toFixed(2)}% YoY]</span>`;
            }
            
            element.innerHTML = 
                `${valueNum.toFixed(3)}${changeDisplay} <span class="text-gray-500 text-xs">(FRED ${data.formatted_date})</span>`;
            
            console.log(`✅ [API Client] M2V updated: ${valueNum.toFixed(3)} (${data.formatted_date}) - PostgreSQL Live Data`);
        } else {
            throw new Error('PostgreSQL API returned invalid data format');
        }
    } catch (error) {
        console.error('❌ [API Client] Failed to update M2V display:', error);
        
        // Try fallback data if available
        if (this.fallbackData && this.fallbackData.M2V) {
            const fallback = this.fallbackData.M2V.data;
            element.innerHTML = 
                `${fallback.value.toFixed(3)} <span class="text-gray-500 text-xs">(${fallback.source})</span>`;
            console.log('⚠️ [API Client] M2V using fallback data');
        } else {
            element.innerHTML = 
                'Error Loading <span class="text-gray-500 text-xs">(PostgreSQL Connection Issue)</span>';
        }
    }
};

// Update Monetary Base Total display in the HTML
MEMApiClient.prototype.updateMonetaryBaseDisplay = async function() {
    const element = document.getElementById('monetary-base-total');
    if (!element) {
        console.error('❌ [API Client] Monetary Base display element not found: monetary-base-total');
        return;
    }

    try {
        console.log('🔄 [API Client] Updating Monetary Base display...');
        element.innerHTML = 'Loading...';
        
        const result = await this.getMonetaryBaseData();
        console.log('📊 [API Client] Monetary Base API result:', result);
        
        // Handle the new unified FRED API response format - FIX APPLIED 
        const data = (result.success && result.data) ? result.data : (result.data ? result.data : null);
        
        if (data && data.value !== undefined) {
            let changeDisplay = '';
            
            // Convert value from string to number if needed
            const valueNum = parseFloat(data.value);
            
            if (data.yoy_change !== null && data.yoy_change !== undefined) {
                const changeClass = data.yoy_change >= 0 ? 'metric-change-positive' : 'metric-change-negative';
                const changeSign = data.yoy_change >= 0 ? '+' : '';
                changeDisplay = ` <span class="${changeClass}">[${changeSign}${data.yoy_change.toFixed(2)}% YoY]</span>`;
            }
            
            // Format value correctly - it comes in billions, convert to trillions
            const valueInTrillions = (valueNum / 1000).toFixed(2);
            element.innerHTML = 
                `$${valueInTrillions}T${changeDisplay} <span class="text-gray-500 text-xs">(FRED ${data.formatted_date})</span>`;
            
            console.log(`✅ [API Client] Monetary Base updated: $${valueInTrillions}T (${data.formatted_date}) - PostgreSQL Live Data`);
        } else {
            throw new Error('PostgreSQL API returned invalid data format');
        }
    } catch (error) {
        console.error('❌ [API Client] Failed to update Monetary Base display:', error);
        
        // Try fallback data if available
        if (this.fallbackData && this.fallbackData.MonetaryBase) {
            const fallback = this.fallbackData.MonetaryBase.data;
            const valueInTrillions = (fallback.value / 1000).toFixed(2);
            element.innerHTML = 
                `$${valueInTrillions}T <span class="text-gray-500 text-xs">(${fallback.source})</span>`;
            console.log('⚠️ [API Client] Monetary Base using fallback data');
        } else {
            element.innerHTML = 
                'Error Loading <span class="text-gray-500 text-xs">(PostgreSQL Connection Issue)</span>';
        }
    }
};

// Update CPI display in the HTML
MEMApiClient.prototype.updateCPIDisplay = async function() {
    const element = document.getElementById('cpi-value');
    if (!element) {
        console.error('❌ CPI display element not found: cpi-value');
        return;
    }

    try {
        console.log('🔄 Updating CPI display...');
        element.innerHTML = 'Loading...';
        
        const result = await this.getCPIData();
        console.log('📊 CPI API result:', result);
        
        if (result.success && result.data) {
            const data = result.data;
            let changeDisplay = '';
            
            if (data.yoy_change !== null) {
                const changeClass = data.yoy_change >= 0 ? 'metric-change-positive' : 'metric-change-negative';
                const changeSign = data.yoy_change >= 0 ? '+' : '';
                changeDisplay = ` <span class="${changeClass}">[${changeSign}${data.yoy_change.toFixed(2)}% YoY]</span>`;
            }
            
            element.innerHTML = 
                `${data.value}${changeDisplay} <span class="text-gray-500 text-xs">(FRED ${data.formatted_date})</span>`;
            
            console.log(`✅ CPI updated: ${data.value} (${data.formatted_date})`);
        } else {
            // Use fallback data
            const fallback = this.fallbackData.CPI;
            element.innerHTML = 
                `${fallback.data.value} <span class="text-gray-500 text-xs">(${fallback.data.source})</span>`;
            console.log('⚠️ CPI using fallback data');
        }
    } catch (error) {
        console.error('❌ Failed to update CPI display:', error);
        // Final fallback
        element.innerHTML = 
            '307.8 <span class="text-gray-500 text-xs">(Static Fallback)</span>';
    }
};

// Update UNRATE display in the HTML
MEMApiClient.prototype.updateUNRATEDisplay = async function() {
    const element = document.getElementById('unrate-value');
    if (!element) {
        console.error('❌ UNRATE display element not found: unrate-value');
        return;
    }

    try {
        console.log('🔄 Updating UNRATE display...');
        element.innerHTML = 'Loading...';
        
        const result = await this.getUNRATEData();
        console.log('📊 UNRATE API result:', result);
        
        if (result.success && result.data) {
            const data = result.data;
            let changeDisplay = '';
            
            if (data.yoy_change !== null) {
                const changeClass = data.yoy_change >= 0 ? 'metric-change-positive' : 'metric-change-negative';
                const changeSign = data.yoy_change >= 0 ? '+' : '';
                changeDisplay = ` <span class="${changeClass}">[${changeSign}${data.yoy_change.toFixed(2)}% YoY]</span>`;
            }
            
            element.innerHTML = 
                `${data.value}%${changeDisplay} <span class="text-gray-500 text-xs">(FRED ${data.formatted_date})</span>`;
            
            console.log(`✅ UNRATE updated: ${data.value}% (${data.formatted_date})`);
        } else {
            // Use fallback data
            const fallback = this.fallbackData.UNRATE;
            element.innerHTML = 
                `${fallback.data.value}% <span class="text-gray-500 text-xs">(${fallback.data.source})</span>`;
            console.log('⚠️ UNRATE using fallback data');
        }
    } catch (error) {
        console.error('❌ Failed to update UNRATE display:', error);
        // Final fallback
        element.innerHTML = 
            '3.7% <span class="text-gray-500 text-xs">(Static Fallback)</span>';
    }
};

// Update M1, M2, M2V, and Monetary Base displays
MEMApiClient.prototype.updateMoneySupplyData = async function() {
    console.log('🔄 [API Client] Updating money supply data...');
    
    // Check if API service is healthy
    const isHealthy = await this.checkHealth();
    if (!isHealthy) {
        console.warn('⚠️ [API Client] API service is not healthy, using fallbacks');
    }

    // Clear existing cache before update
    this.cache.delete('M2_DATA');
    this.cache.delete('M1_DATA');
    this.cache.delete('M2V_DATA');
    this.cache.delete('MONETARY_BASE_DATA');

    // Update M1, M2, M2V, and Monetary Base in parallel
    const updatePromises = [
        this.updateM2Display(),
        this.updateM1Display(),
        this.updateM2VDisplay(),
        this.updateMonetaryBaseDisplay()
    ];
    
    const results = await Promise.allSettled(updatePromises);
    
    // Log results
    const indicators = ['M2', 'M1', 'M2V', 'Monetary Base'];
    results.forEach((result, index) => {
        if (result.status === 'fulfilled') {
            console.log(`✅ [API Client] ${indicators[index]} updated successfully`);
        } else {
            console.error(`❌ [API Client] ${indicators[index]} update failed:`, result.reason);
        }
    });

    console.log('✅ [API Client] Money supply data update complete');
};

// Update all monetary indicators including CPI and Unemployment Rate
MEMApiClient.prototype.updateAllIndicators = async function() {
    // Update all indicators in parallel
    await Promise.allSettled([
        this.updateM2Display(),
        this.updateM1Display(),
        this.updateM2VDisplay(),
        this.updateMonetaryBaseDisplay(),
        this.updateCPIDisplay(),
        this.updateUNRATEDisplay()
    ]);

    console.log('✅ All indicators update complete');
};

// Export for use in the main HTML file
window.MEMApiClient = MEMApiClient;
