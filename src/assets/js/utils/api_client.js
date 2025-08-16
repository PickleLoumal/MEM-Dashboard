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
    } else if (window.location.hostname === 'localhost' || 
               window.location.hostname === '127.0.0.1' || 
               window.location.protocol === 'file:') {
        // Development environment - use Django API
        this.baseUrl = 'http://localhost:8000/api';
        console.log('🔗 Using Django API for development: ' + this.baseUrl);
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
        },
        // 利率相关fallback数据
        FEDFUNDS: {
            success: true,
            data: {
                value: 4.33,
                formatted_date: "Jul 2025",
                yoy_change: -18.76,
                unit: "Percent",
                source: "Fallback Data"
            }
        },
        MORTGAGE30Y: {
            success: true,
            data: {
                value: 6.72,
                formatted_date: "Jul 2025",
                yoy_change: -0.88,
                unit: "Percent", 
                source: "Fallback Data"
            }
        },
        PCEINDEX: {
            success: true,
            data: {
                value: 126.56,
                formatted_date: "Jun 2025",
                yoy_change: 2.8,
                unit: "Index",
                source: "Fallback Data"
            }
        },
        DEBTTOGDP: {
            success: true,
            data: {
                value: 120.87,
                formatted_date: "Q1 2025", 
                yoy_change: 3.2,
                unit: "Percent",
                source: "Fallback Data"
            }
        },
        TREASURY10Y: {
            success: true,
            data: {
                value: 4.22,
                formatted_date: "Aug 2025",
                yoy_change: -8.12,
                unit: "Percent",
                source: "Fallback Data"
            }
        },
        TREASURY2Y: {
            success: true,
            data: {
                value: 3.69,
                formatted_date: "Aug 2025",
                yoy_change: -11.75,
                unit: "Percent",
                source: "Fallback Data"
            }
        },
        TREASURY3M: {
            success: true,
            data: {
                value: 4.25,
                formatted_date: "Jul 2025",
                yoy_change: -15.20,
                unit: "Percent",
                source: "Fallback Data"
            }
        },
        // Consumer and Household Debt indicators fallback data
        HOUSEHOLD_DEBT_GDP: {
            success: true,
            data: {
                value: 71.66,
                formatted_date: "Jul 2024",
                yoy_change: -1.2,
                unit: "Ratio",
                source: "Fallback Data"
            }
        },
        DEBT_SERVICE_RATIO: {
            success: true,
            data: {
                value: 11.25,
                formatted_date: "Q1 2025",
                yoy_change: 0.8,
                unit: "Percent",
                source: "Fallback Data"
            }
        },
        MORTGAGE_DEBT: {
            success: true,
            data: {
                value: 15841071.29,
                formatted_date: "Jul 2019",
                yoy_change: 0.0,
                unit: "Millions of Dollars",
                source: "Fallback Data"
            }
        },
        CREDIT_CARD_DEBT: {
            success: true,
            data: {
                value: 908.42,
                formatted_date: "Q1 2025",
                yoy_change: 5.2,
                unit: "Billions of U.S. Dollars",
                source: "Fallback Data"
            }
        },
        STUDENT_LOANS: {
            success: true,
            data: {
                value: 1813619.89,
                formatted_date: "Jun 2025",
                yoy_change: 2.8,
                unit: "Millions of U.S. Dollars",
                source: "Fallback Data"
            }
        },
        CONSUMER_CREDIT: {
            success: true,
            data: {
                value: 551973.3,
                formatted_date: "May 2025",
                yoy_change: 3.5,
                unit: "Millions of Dollars",
                source: "Fallback Data"
            }
        },
        TOTAL_DEBT: {
            success: true,
            data: {
                value: 45000000.0,
                formatted_date: "Current",
                yoy_change: 4.2,
                unit: "Millions of Dollars",
                source: "Fallback Data"
            }
        },
        
        // Government Debts indicators fallback data
        FEDERAL_DEBT_TOTAL: {
            success: true,
            data: {
                value: 36214310.0,
                formatted_date: "Jan 2025",
                yoy_change: 4.71,
                unit: "Millions of Dollars",
                source: "Fallback Data"
            }
        },
        FEDERAL_DEBT_GDP_RATIO: {
            success: true,
            data: {
                value: 120.87,
                formatted_date: "Jan 2025",
                yoy_change: 0.15,
                unit: "Percent of GDP",
                source: "Fallback Data"
            }
        },
        FEDERAL_SURPLUS_DEFICIT: {
            success: true,
            data: {
                value: -291142.66,
                formatted_date: "Jul 2025",
                yoy_change: 12.5,
                unit: "Millions of Dollars",
                source: "Fallback Data"
            }
        },
        POPULATION_55_OVER: {
            success: true,
            data: {
                value: 102914.0,
                formatted_date: "Jul 2025",
                yoy_change: 2.1,
                unit: "Thousands of Persons",
                source: "Fallback Data"
            }
        },
        GROSS_FEDERAL_DEBT: {
            success: true,
            data: {
                value: 32989.0,
                formatted_date: "Sep 2023",
                yoy_change: 8.2,
                unit: "Billions of Dollars",
                source: "Fallback Data"
            }
        },
        FEDERAL_INTEREST_GDP: {
            success: true,
            data: {
                value: 3.02,
                formatted_date: "Jan 2024",
                yoy_change: 26.9,
                unit: "Percent of GDP",
                source: "Fallback Data"
            }
        },
        FEDERAL_DEBT_PUBLIC_GDP: {
            success: true,
            data: {
                value: 96.57,
                formatted_date: "Jan 2025",
                yoy_change: -0.6,
                unit: "Percent of GDP",
                source: "Fallback Data"
            }
        },
        GOVERNMENT_CONSUMER_CREDIT: {
            success: true,
            data: {
                value: 1545470.48,
                formatted_date: "Jun 2025",
                yoy_change: 1.2,
                unit: "Millions of U.S. Dollars",
                source: "Fallback Data"
            }
        },
        CPI: {
            success: true,
            data: {
                value: 321.50,
                formatted_date: "Jun 2025",
                yoy_change: 3.1,
                unit: "Index",
                source: "Fallback Data"
            }
        },
        
        // Trade Deficits indicators fallback data
        TRADE_BALANCE_GOODS_SERVICES: {
            success: true,
            data: {
                value: -60177.0,
                formatted_date: "Jun 2025",
                yoy_change: -8.2,
                unit: "Millions of Dollars",
                source: "Fallback Data"
            }
        },
        CURRENT_ACCOUNT_BALANCE: {
            success: true,
            data: {
                value: -450170.0,
                formatted_date: "Jan 2025",
                yoy_change: -15.3,
                unit: "Millions of Dollars",
                source: "Fallback Data"
            }
        },
        FOREIGN_TREASURY_HOLDINGS: {
            success: true,
            data: {
                value: 3955210.0,
                formatted_date: "Jan 2025",
                yoy_change: -2.1,
                unit: "Millions of Dollars",
                source: "Fallback Data"
            }
        },
        CUSTOMS_DUTIES: {
            success: true,
            data: {
                value: 266.994,
                formatted_date: "Apr 2025",
                yoy_change: 12.8,
                unit: "Billions of Dollars",
                source: "Fallback Data"
            }
        },
        FEDERAL_SURPLUS_DEFICIT_MTS: {
            success: true,
            data: {
                value: -291142.66,
                formatted_date: "Jul 2025",
                yoy_change: 18.5,
                unit: "Millions of Dollars",
                source: "Fallback Data"
            }
        },
        NET_EXPORTS: {
            success: true,
            data: {
                value: -872.384,
                formatted_date: "Apr 2025",
                yoy_change: -12.4,
                unit: "Billions of Dollars",
                source: "Fallback Data"
            }
        },
        REAL_IMPORTS: {
            success: true,
            data: {
                value: 3654.411,
                formatted_date: "Apr 2025",
                yoy_change: 5.8,
                unit: "Billions of Chained 2017 Dollars",
                source: "Fallback Data"
            }
        },
        REAL_EXPORTS: {
            success: true,
            data: {
                value: 2628.14,
                formatted_date: "Apr 2025",
                yoy_change: 3.2,
                unit: "Billions of Chained 2017 Dollars",
                source: "Fallback Data"
            }
        },
        
        // Private Sector Corporate Debts indicators fallback data
        NBER_RECESSION_INDICATOR: {
            success: true,
            data: {
                value: 0.0,
                formatted_date: "Jul 2025",
                yoy_change: 0.0,
                unit: "+1 or 0",
                source: "Fallback Data"
            }
        },
        CONSUMER_PRICE_INFLATION: {
            success: true,
            data: {
                value: 2.95,
                formatted_date: "2024",
                yoy_change: -0.5,
                unit: "Percent",
                source: "Fallback Data"
            }
        },
        HIGH_YIELD_BOND_SPREAD: {
            success: true,
            data: {
                value: 2.93,
                formatted_date: "Aug 12, 2025",
                yoy_change: -0.8,
                unit: "Percent",
                source: "Fallback Data"
            }
        },
        PRIMARY_CREDIT_LOANS: {
            success: true,
            data: {
                value: 5540.0,
                formatted_date: "Aug 6, 2025",
                yoy_change: 12.3,
                unit: "Millions of U.S. Dollars",
                source: "Fallback Data"
            }
        },
        CORPORATE_DEBT_SECURITIES: {
            success: true,
            data: {
                value: 13950.22,
                formatted_date: "Q1 2025",
                yoy_change: 4.1,
                unit: "Billions of Dollars",
                source: "Fallback Data"
            }
        },
        AAA_CORPORATE_BOND_YIELD: {
            success: true,
            data: {
                value: 5.45,
                formatted_date: "Jul 2025",
                yoy_change: 8.2,
                unit: "Percent",
                source: "Fallback Data"
            }
        },
        BAA_CORPORATE_BOND_YIELD: {
            success: true,
            data: {
                value: 6.10,
                formatted_date: "Jul 2025",
                yoy_change: 7.8,
                unit: "Percent",
                source: "Fallback Data"
            }
        },
        CORPORATE_DEBT_EQUITY_RATIO: {
            success: true,
            data: {
                value: 19.28,
                formatted_date: "Q1 2025",
                yoy_change: 2.1,
                unit: "Percent",
                source: "Fallback Data"
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
    return await this.fetchWithCache('/fred-us/fed-funds/', 'FED_FUNDS_DATA', 'FEDFUNDS');
};

// Fetch 30-Year Mortgage Rate data - 统一FRED API
MEMApiClient.prototype.getMortgage30YData = async function() {
    return await this.fetchWithCache('/fred-us/mortgage-30y/', 'MORTGAGE_30Y_DATA', 'MORTGAGE30Y');
};

// Fetch PCE Price Index data - 统一FRED API
MEMApiClient.prototype.getPCEPriceIndexData = async function() {
    return await this.fetchWithCache('/fred-us/pce-price-index/', 'PCE_PRICE_INDEX_DATA', 'PCEINDEX');
};

// Fetch 10-Year Treasury Rate data - 统一FRED API
MEMApiClient.prototype.getTreasury10YData = async function() {
    return await this.fetchWithCache('/fred-us/treasury-10y/', 'TREASURY_10Y_DATA', 'TREASURY10Y');
};

// Fetch 2-Year Treasury Rate data - 统一FRED API
MEMApiClient.prototype.getTreasury2YData = async function() {
    return await this.fetchWithCache('/fred-us/treasury-2y/', 'TREASURY_2Y_DATA', 'TREASURY2Y');
};

// Fetch 3-Month Treasury Rate data - 统一FRED API
MEMApiClient.prototype.getTreasury3MData = async function() {
    return await this.fetchWithCache('/fred-us/treasury-3m/', 'TREASURY_3M_DATA', 'TREASURY3M');
};

// 利率相关指标获取方法
MEMApiClient.prototype.getInterestRateData = async function() {
    const endpoints = {
        fedFunds: '/fred-us/fed-funds/',
        mortgage30y: '/fred-us/mortgage-30y/', 
        pceIndex: '/fred-us/pce-price-index/',
        debtToGdp: '/fred-us/debt-to-gdp/',
        treasury10y: '/fred-us/treasury-10y/',
        treasury2y: '/fred-us/treasury-2y/',
        treasury3m: '/fred-us/treasury-3m/',
        cpi: '/fred-us/cpi/'
    };
    
    // 正确的fallback key映射
    const fallbackKeyMap = {
        fedFunds: 'FEDFUNDS',
        mortgage30y: 'MORTGAGE30Y',
        pceIndex: 'PCEINDEX',
        debtToGdp: 'DEBTTOGDP',
        treasury10y: 'TREASURY10Y',
        treasury2y: 'TREASURY2Y',
        treasury3m: 'TREASURY3M',
        cpi: 'CPI'
    };
    
    const results = {};
    
    for (const [key, endpoint] of Object.entries(endpoints)) {
        try {
            results[key] = await this.fetchWithCache(
                endpoint, 
                `INTEREST_RATE_${key.toUpperCase()}`, 
                fallbackKeyMap[key]
            );
        } catch (error) {
            console.error(`Failed to fetch ${key}:`, error);
            results[key] = this.fallbackData[fallbackKeyMap[key]] || null;
        }
    }
    
    return results;
};

// Government Debts indicators获取方法
MEMApiClient.prototype.getGovernmentDebtsData = async function() {
    console.log('🔄 [API Client] Fetching Government Debts indicators...');
    
    const endpoints = {
        federalDebtTotal: '/fred-us/federal-debt-total/',
        federalDebtGdpRatio: '/fred-us/federal-debt-gdp-ratio/',
        federalSurplusDeficit: '/fred-us/federal-surplus-deficit/',
        population55Over: '/fred-us/population-55-over/',
        grossFederalDebt: '/fred-us/gross-federal-debt/',
        federalInterestGdp: '/fred-us/federal-interest-gdp/',
        federalDebtPublicGdp: '/fred-us/federal-debt-public-gdp/',
        governmentConsumerCredit: '/fred-us/government-consumer-credit/'
    };
    
    // fallback key映射
    const fallbackKeyMap = {
        federalDebtTotal: 'FEDERAL_DEBT_TOTAL',
        federalDebtGdpRatio: 'FEDERAL_DEBT_GDP_RATIO',
        federalSurplusDeficit: 'FEDERAL_SURPLUS_DEFICIT',
        population55Over: 'POPULATION_55_OVER',
        grossFederalDebt: 'GROSS_FEDERAL_DEBT',
        federalInterestGdp: 'FEDERAL_INTEREST_GDP',
        federalDebtPublicGdp: 'FEDERAL_DEBT_PUBLIC_GDP',
        governmentConsumerCredit: 'GOVERNMENT_CONSUMER_CREDIT'
    };
    
    const results = {};
    
    for (const [key, endpoint] of Object.entries(endpoints)) {
        try {
            results[key] = await this.fetchWithCache(
                endpoint, 
                `GOVERNMENT_DEBT_${key.toUpperCase()}`, 
                fallbackKeyMap[key]
            );
        } catch (error) {
            console.error(`Failed to fetch ${key}:`, error);
            results[key] = this.fallbackData[fallbackKeyMap[key]] || null;
        }
    }
    
    console.log('✅ [API Client] Government Debts indicators fetched');
    return results;
};

// Government Deficit Financing indicators获取方法
MEMApiClient.prototype.getGovtDeficitFinancingData = async function() {
    console.log('🔄 [API Client] Fetching Government Deficit Financing indicators...');
    
    const endpoints = {
        federalDebtTotal: '/fred-us/federal-debt-total-gdf/',
        federalDebtGdpRatio: '/fred-us/federal-debt-gdp-ratio-gdf/',
        federalSurplusDeficit: '/fred-us/federal-surplus-deficit-gdf/',
        federalTaxReceipts: '/fred-us/federal-tax-receipts/',
        federalNetOutlays: '/fred-us/federal-net-outlays/',
        federalCurrentExpenditures: '/fred-us/federal-current-expenditures/',
        federalCurrentReceipts: '/fred-us/federal-current-receipts/',
        excessReserves: '/fred-us/excess-reserves/'
    };
    
    // fallback key映射
    const fallbackKeyMap = {
        federalDebtTotal: 'GFDEBTN',
        federalDebtGdpRatio: 'GFDEGDQ188S',
        federalSurplusDeficit: 'MTSDS133FMS',
        federalTaxReceipts: 'W006RC1Q027SBEA',
        federalNetOutlays: 'FYONET',
        federalCurrentExpenditures: 'FGEXPND',
        federalCurrentReceipts: 'FGRECPT',
        excessReserves: 'EXCSRESNW'
    };
    
    const results = {};
    
    for (const [key, endpoint] of Object.entries(endpoints)) {
        try {
            results[key] = await this.fetchWithCache(
                endpoint, 
                `GOVT_DEFICIT_FINANCING_${key.toUpperCase()}`, 
                fallbackKeyMap[key]
            );
        } catch (error) {
            console.error(`Failed to fetch ${key}:`, error);
            results[key] = this.fallbackData[fallbackKeyMap[key]] || null;
        }
    }
    
    console.log('✅ [API Client] Government Deficit Financing indicators fetched');
    return results;
};

// Consumer and Household Debt indicators获取方法
MEMApiClient.prototype.getHouseholdDebtData = async function() {
    const endpoints = {
        householdDebtGdp: '/fred-us/household-debt-gdp/',
        debtServiceRatio: '/fred-us/debt-service-ratio/',
        mortgageDebt: '/fred-us/mortgage-debt/',
        creditCardDebt: '/fred-us/credit-card-debt/',
        studentLoans: '/fred-us/student-loans/',
        consumerCredit: '/fred-us/consumer-credit/',
        totalDebt: '/fred-us/total-debt/',
        fedFunds: '/fred-us/fed-funds/' // 重用现有的联邦基金利率端点
    };
    
    // fallback key映射
    const fallbackKeyMap = {
        householdDebtGdp: 'HOUSEHOLD_DEBT_GDP',
        debtServiceRatio: 'DEBT_SERVICE_RATIO',
        mortgageDebt: 'MORTGAGE_DEBT',
        creditCardDebt: 'CREDIT_CARD_DEBT',
        studentLoans: 'STUDENT_LOANS',
        consumerCredit: 'CONSUMER_CREDIT',
        totalDebt: 'TOTAL_DEBT',
        fedFunds: 'FEDFUNDS'
    };
    
    const results = {};
    
    for (const [key, endpoint] of Object.entries(endpoints)) {
        try {
            results[key] = await this.fetchWithCache(
                endpoint, 
                `HOUSEHOLD_DEBT_${key.toUpperCase()}`, 
                fallbackKeyMap[key]
            );
        } catch (error) {
            console.error(`Failed to fetch ${key}:`, error);
            results[key] = this.fallbackData[fallbackKeyMap[key]] || null;
        }
    }

    return results;
};

// Trade Deficits and International Balance indicators获取方法
MEMApiClient.prototype.getTradeDeficitsData = async function() {
    const endpoints = {
        tradeBalance: '/fred-us/trade-balance-goods-services/',
        currentAccount: '/fred-us/current-account-balance/',
        foreignTreasuryHoldings: '/fred-us/foreign-treasury-holdings/',
        customsDuties: '/fred-us/customs-duties/',
        federalSurplusDeficitMts: '/fred-us/federal-surplus-deficit-mts/',
        netExports: '/fred-us/net-exports/',
        realImports: '/fred-us/real-imports/',
        realExports: '/fred-us/real-exports/'
    };
    
    // fallback key映射
    const fallbackKeyMap = {
        tradeBalance: 'TRADE_BALANCE_GOODS_SERVICES',
        currentAccount: 'CURRENT_ACCOUNT_BALANCE',
        foreignTreasuryHoldings: 'FOREIGN_TREASURY_HOLDINGS',
        customsDuties: 'CUSTOMS_DUTIES',
        federalSurplusDeficitMts: 'FEDERAL_SURPLUS_DEFICIT_MTS',
        netExports: 'NET_EXPORTS',
        realImports: 'REAL_IMPORTS',
        realExports: 'REAL_EXPORTS'
    };
    
    const results = {};
    
    for (const [key, endpoint] of Object.entries(endpoints)) {
        try {
            results[key] = await this.fetchWithCache(
                endpoint, 
                `TRADE_DEFICITS_${key.toUpperCase()}`, 
                fallbackKeyMap[key]
            );
        } catch (error) {
            console.error(`Failed to fetch ${key}:`, error);
            results[key] = this.fallbackData[fallbackKeyMap[key]] || null;
        }
    }

    return results;
};

// Private Sector Corporate Debts indicators获取方法
MEMApiClient.prototype.getPrivateSectorCorporateDebtsData = async function() {
    const endpoints = {
        nberRecessionIndicator: '/fred-us/nber-recession-indicator/',
        consumerPriceInflation: '/fred-us/consumer-price-inflation/',
        highYieldBondSpread: '/fred-us/high-yield-bond-spread/',
        primaryCreditLoans: '/fred-us/primary-credit-loans/',
        corporateDebtSecurities: '/fred-us/corporate-debt-securities/',
        aaaCorporateBondYield: '/fred-us/aaa-corporate-bond-yield/',
        baaCorporateBondYield: '/fred-us/baa-corporate-bond-yield/',
        corporateDebtEquityRatio: '/fred-us/corporate-debt-equity-ratio/'
    };
    
    // fallback key映射
    const fallbackKeyMap = {
        nberRecessionIndicator: 'NBER_RECESSION_INDICATOR',
        consumerPriceInflation: 'CONSUMER_PRICE_INFLATION',
        highYieldBondSpread: 'HIGH_YIELD_BOND_SPREAD',
        primaryCreditLoans: 'PRIMARY_CREDIT_LOANS',
        corporateDebtSecurities: 'CORPORATE_DEBT_SECURITIES',
        aaaCorporateBondYield: 'AAA_CORPORATE_BOND_YIELD',
        baaCorporateBondYield: 'BAA_CORPORATE_BOND_YIELD',
        corporateDebtEquityRatio: 'CORPORATE_DEBT_EQUITY_RATIO'
    };
    
    const results = {};
    
    for (const [key, endpoint] of Object.entries(endpoints)) {
        try {
            results[key] = await this.fetchWithCache(
                endpoint, 
                `PRIVATE_SECTOR_CORPORATE_DEBTS_${key.toUpperCase()}`, 
                fallbackKeyMap[key]
            );
        } catch (error) {
            console.error(`Failed to fetch ${key}:`, error);
            results[key] = this.fallbackData[fallbackKeyMap[key]] || null;
        }
    }

    return results;
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
        this.updateMoneySupplyData(),
        this.updateInterestRateDisplay(),
        this.updateHouseholdDebtDisplay(),
        this.updatePrivateSectorCorporateDebtsDisplay(),
        this.updateCPIDisplay(),
        this.updateUNRATEDisplay()
    ]);

    console.log('✅ [API Client] All indicators update complete');
};

// 更新利率指标显示
MEMApiClient.prototype.updateInterestRateDisplay = async function() {
    console.log('🔄 [API Client] Updating Interest Rate indicators...');
    
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
    
    Object.entries(displayMappings).forEach(([dataKey, elementId]) => {
        this.updateSingleIndicatorDisplay(elementId, data[dataKey]);
    });
    
    console.log('✅ [API Client] Interest Rate indicators update complete');
};

// 更新债务指标显示
MEMApiClient.prototype.updateHouseholdDebtDisplay = async function() {
    console.log('🔄 [API Client] Updating Household Debt indicators...');
    
    const data = await this.getHouseholdDebtData();
    
    const displayMappings = {
        householdDebtGdp: 'household-debt-gdp',
        debtServiceRatio: 'debt-service-ratio',
        mortgageDebt: 'mortgage-debt-outstanding',
        creditCardDebt: 'credit-card-balances',
        studentLoans: 'student-loans',
        consumerCredit: 'consumer-credit',
        totalDebt: 'total-household-debt',
        fedFunds: 'fed-funds-rate'
    };
    
    Object.entries(displayMappings).forEach(([dataKey, elementId]) => {
        this.updateSingleIndicatorDisplay(elementId, data[dataKey]);
    });
    
    console.log('✅ [API Client] Household Debt indicators update complete');
};

// 更新政府债务指标显示
MEMApiClient.prototype.updateGovernmentDebtsDisplay = async function() {
    console.log('🔄 [API Client] Updating Government Debts indicators...');
    
    const data = await this.getGovernmentDebtsData();
    
    const displayMappings = {
        federalDebtTotal: 'federal-debt-total',
        federalDebtGdpRatio: 'federal-debt-gdp-ratio',
        federalSurplusDeficit: 'federal-surplus-deficit',
        population55Over: 'population-55-over',
        grossFederalDebt: 'gross-federal-debt',
        federalInterestGdp: 'federal-interest-gdp',
        federalDebtPublicGdp: 'federal-debt-public-gdp',
        governmentConsumerCredit: 'government-consumer-credit'
    };
    
    Object.entries(displayMappings).forEach(([dataKey, elementId]) => {
        this.updateSingleIndicatorDisplay(elementId, data[dataKey]);
    });
    
    console.log('✅ [API Client] Government Debts indicators update complete');
};

// 更新贸易逆差指标显示
MEMApiClient.prototype.updateTradeDeficitsDisplay = async function() {
    console.log('🔄 [API Client] Updating Trade Deficits indicators...');
    
    const data = await this.getTradeDeficitsData();
    
    const displayMappings = {
        tradeBalance: 'trade-balance-goods-services',
        currentAccount: 'current-account-balance',
        foreignTreasuryHoldings: 'foreign-treasury-holdings',
        customsDuties: 'customs-duties',
        federalSurplusDeficitMts: 'federal-surplus-deficit-mts',
        netExports: 'net-exports',
        realImports: 'real-imports',
        realExports: 'real-exports'
    };
    
    Object.entries(displayMappings).forEach(([dataKey, elementId]) => {
        this.updateSingleIndicatorDisplay(elementId, data[dataKey]);
    });
    
    console.log('✅ [API Client] Trade Deficits indicators update complete');
};

// 更新Private Sector Corporate Debts指标显示
MEMApiClient.prototype.updatePrivateSectorCorporateDebtsDisplay = async function() {
    console.log('🔄 [API Client] Updating Private Sector Corporate Debts indicators...');
    
    const data = await this.getPrivateSectorCorporateDebtsData();
    
    const displayMappings = {
        nberRecessionIndicator: 'nber-recession-indicator',
        consumerPriceInflation: 'consumer-price-inflation',
        highYieldBondSpread: 'high-yield-bond-spread',
        primaryCreditLoans: 'primary-credit-loans',
        corporateDebtSecurities: 'corporate-debt-securities',
        aaaCorporateBondYield: 'aaa-corporate-bond-yield',
        baaCorporateBondYield: 'baa-corporate-bond-yield',
        corporateDebtEquityRatio: 'corporate-debt-equity-ratio'
    };
    
    Object.entries(displayMappings).forEach(([dataKey, elementId]) => {
        this.updateSingleIndicatorDisplay(elementId, data[dataKey]);
    });
    
    console.log('✅ [API Client] Private Sector Corporate Debts indicators update complete');
};

// 通用指标显示更新方法
MEMApiClient.prototype.updateSingleIndicatorDisplay = function(elementId, apiData) {
    const element = document.getElementById(elementId);
    if (!element) {
        console.warn(`❌ [API Client] Element not found: ${elementId}`);
        console.warn(`Available elements with similar IDs:`, Array.from(document.querySelectorAll('[id*="rate"], [id*="index"], [id*="gdp"]')).map(el => el.id));
        return;
    }
    
    console.log(`🔄 [API Client] Updating element: ${elementId}`);
    
    try {
        if (apiData && apiData.success && apiData.data) {
            const data = apiData.data;
            console.log(`📊 [API Client] ${elementId} data:`, data);
            
            // 格式化数值显示
            let displayValue = data.value;
            if (data.unit && data.unit.toLowerCase().includes('percent')) {
                displayValue = `${data.value}%`;
            } else if (data.series_id === 'GFDEGDQ188S') {
                displayValue = `${data.value.toFixed(2)}%`;
            } else if (data.series_id && data.series_id.includes('DGS') || data.series_id === 'FEDFUNDS' || data.series_id === 'MORTGAGE30US' || data.series_id === 'TB3MS') {
                displayValue = `${data.value}%`;
            } else if (data.series_id === 'PCEPI' || data.series_id === 'CPIAUCSL') {
                displayValue = `${data.value}`;
            } 
            // 债务指标特殊格式化
            else if (data.series_id === 'HDTGPDUSQ163N') {
                displayValue = `${data.value.toFixed(2)}%`;
            } else if (data.series_id === 'TDSP') {
                displayValue = `${data.value.toFixed(2)}%`;
            } else if (data.series_id === 'MDOAH') {
                displayValue = `$${(data.value / 1000000).toFixed(2)}T`;
            } else if (data.series_id === 'RCCCBBALTOT') {
                displayValue = `$${data.value.toFixed(0)}B`;
            } else if (data.series_id === 'SLOASM') {
                displayValue = `$${(data.value / 1000000).toFixed(2)}T`;
            } else if (data.series_id === 'TOTALSL') {
                displayValue = `$${data.value.toFixed(0)}B`;
            } else if (data.series_id === 'DTCOLNVHFNM') {
                displayValue = `$${(data.value / 1000000).toFixed(2)}T`;
            }
            // 贸易逆差指标特殊格式化
            else if (data.series_id === 'BOPGSTB') {
                // 贸易平衡（百万美元）
                displayValue = data.value < 0 ? `-$${Math.abs(data.value / 1000).toFixed(1)}B` : `$${(data.value / 1000).toFixed(1)}B`;
            } else if (data.series_id === 'IEABC') {
                // 经常账户余额（百万美元）
                displayValue = data.value < 0 ? `-$${Math.abs(data.value / 1000).toFixed(1)}B` : `$${(data.value / 1000).toFixed(1)}B`;
            } else if (data.series_id === 'BOGZ1FL263061130Q') {
                // 外国持有美债（百万美元）
                displayValue = `$${(data.value / 1000000).toFixed(2)}T`;
            } else if (data.series_id === 'B235RC1Q027SBEA') {
                // 关税收入（十亿美元）
                displayValue = `$${data.value.toFixed(1)}B`;
            } else if (data.series_id === 'MTSDS133FMS') {
                // 联邦盈余/赤字（百万美元）
                displayValue = data.value < 0 ? `-$${Math.abs(data.value / 1000).toFixed(1)}B` : `$${(data.value / 1000).toFixed(1)}B`;
            } else if (data.series_id === 'NETEXP') {
                // 净出口（十亿美元）
                displayValue = data.value < 0 ? `-$${Math.abs(data.value).toFixed(1)}B` : `$${data.value.toFixed(1)}B`;
            } else if (data.series_id === 'IMPGSC1') {
                // 实际进口（十亿美元）
                displayValue = `$${data.value.toFixed(1)}B`;
            } else if (data.series_id === 'EXPGSC1') {
                // 实际出口（十亿美元）
                displayValue = `$${data.value.toFixed(1)}B`;
            }
            // Private Sector Corporate Debts指标特殊格式化
            else if (data.series_id === 'USREC') {
                // NBER衰退指标（0或1）
                displayValue = data.value === 0 ? 'No Recession' : 'In Recession';
            } else if (data.series_id === 'FPCPITOTLZGUSA') {
                // 消费者价格通胀（百分比）
                displayValue = `${data.value.toFixed(2)}%`;
            } else if (data.series_id === 'BAMLH0A0HYM2') {
                // 高收益债券利差（百分比）
                displayValue = `${data.value.toFixed(2)}%`;
            } else if (data.series_id === 'WPC') {
                // 主要信贷贷款（百万美元）
                displayValue = `$${(data.value / 1000).toFixed(1)}B`;
            } else if (data.series_id === 'BCNSDODNS') {
                // 企业债务证券（十亿美元）
                displayValue = `$${(data.value / 1000).toFixed(1)}T`;
            } else if (data.series_id === 'AAA') {
                // AAA企业债券收益率（百分比）
                displayValue = `${data.value.toFixed(2)}%`;
            } else if (data.series_id === 'BAA') {
                // BAA企业债券收益率（百分比）
                displayValue = `${data.value.toFixed(2)}%`;
            } else if (data.series_id === 'NCBCMDPMVCE') {
                // 企业债务股权比率（百分比）
                displayValue = `${data.value.toFixed(2)}%`;
            }
            
            // 同比变化显示
            let changeDisplay = '';
            if (data.yoy_change !== null && data.yoy_change !== undefined) {
                const changeClass = data.yoy_change >= 0 ? 'metric-change-positive' : 'metric-change-negative';
                const changeSign = data.yoy_change >= 0 ? '+' : '';
                changeDisplay = ` <span class="${changeClass}">[${changeSign}${data.yoy_change.toFixed(2)}% YoY]</span>`;
            }
            
            const finalHTML = `${displayValue}${changeDisplay} <span class="text-gray-500 text-xs">(FRED ${data.formatted_date})</span>`;
            element.innerHTML = finalHTML;
            console.log(`✅ [API Client] ${elementId} updated: ${displayValue} (${data.formatted_date})`);
            
        } else {
            console.warn(`⚠️ [API Client] ${elementId} - No valid API data, using fallback`);
            // 使用fallback数据
            element.innerHTML = 'Data unavailable <span class="text-gray-500 text-xs">(Fallback)</span>';
            console.warn(`⚠️ [API Client] ${elementId} using fallback - no valid API data`);
        }
        
    } catch (error) {
        console.error(`❌ [API Client] Error updating ${elementId}:`, error);
        element.innerHTML = 'Loading error <span class="text-gray-500 text-xs">(Error)</span>';
    }
};

// Update Government Deficit Financing display method
MEMApiClient.prototype.updateGovtDeficitFinancingDisplay = async function() {
    console.log('🔄 [API Client] Updating Government Deficit Financing display...');
    
    try {
        const data = await this.getGovtDeficitFinancingData();
        console.log('📊 [API Client] Government Deficit Financing data received:', data);
        
        // 元素ID和数据键的映射
        const elementMappings = {
            'gdf-federal-debt-total': data.federalDebtTotal,
            'gdf-federal-debt-gdp-ratio': data.federalDebtGdpRatio,
            'gdf-federal-surplus-deficit': data.federalSurplusDeficit,
            'gdf-federal-tax-receipts': data.federalTaxReceipts,
            'gdf-federal-net-outlays': data.federalNetOutlays,
            'gdf-federal-current-expenditures': data.federalCurrentExpenditures,
            'gdf-federal-current-receipts': data.federalCurrentReceipts,
            'gdf-excess-reserves': data.excessReserves
        };
        
        // 更新每个指标显示
        for (const [elementId, apiData] of Object.entries(elementMappings)) {
            await this.updateSingleIndicatorDisplay(elementId, apiData);
        }
        
        console.log('✅ [API Client] Government Deficit Financing display update completed');
        
    } catch (error) {
        console.error('❌ [API Client] Failed to update Government Deficit Financing display:', error);
    }
};

// Export for use in the main HTML file
window.MEMApiClient = MEMApiClient;
