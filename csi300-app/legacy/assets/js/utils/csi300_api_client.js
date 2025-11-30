/**
 * CSI300 API Client
 * Handles all API communications for CSI300 application
 */

class CSI300ApiClient {
    constructor() {
        this.baseUrl = CSI300Config.BASE_URL;
        this.cache = new Map();
        this.cacheEnabled = CSI300Config.CACHE_CONFIG.ENABLED;
    }

    /**
     * Make HTTP request with error handling
     */
    async makeRequest(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    /**
     * Get cached data or fetch from API
     */
    async getCachedOrFetch(cacheKey, fetchFunction, ttl) {
        if (this.cacheEnabled && this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < ttl) {
                return cached.data;
            }
        }

        const data = await fetchFunction();
        
        if (this.cacheEnabled) {
            this.cache.set(cacheKey, {
                data: data,
                timestamp: Date.now()
            });
        }

        return data;
    }

    /**
     * Health check endpoint
     */
    async healthCheck() {
        const url = `${this.baseUrl}${CSI300Config.ENDPOINTS.HEALTH_CHECK}`;
        return await this.makeRequest(url);
    }

    /**
     * Get all companies with optional filters
     */
    async getCompanies(filters = {}) {
        // Create cache key that includes pagination parameters
        const cacheKey = `companies_${JSON.stringify(filters)}`;
        
        return await this.getCachedOrFetch(
            cacheKey,
            async () => {
                const queryPairs = [];

                // Add filters to query params
                if (filters.im_sector || filters.im_code) {
                    queryPairs.push(['im_sector', filters.im_sector || filters.im_code]);
                }
                if (filters.industry) {
                    queryPairs.push(['industry', filters.industry]);
                }
                if (filters.gics_industry) {
                    queryPairs.push(['gics_industry', filters.gics_industry]);
                }
                if (filters.market_cap_min) {
                    queryPairs.push(['market_cap_min', filters.market_cap_min]);
                }
                if (filters.market_cap_max) {
                    queryPairs.push(['market_cap_max', filters.market_cap_max]);
                }
                if (filters.company_search) {
                    queryPairs.push(['search', filters.company_search]);
                }
                if (filters.industry_search) {
                    queryPairs.push(['industry_search', filters.industry_search]);
                }
                if (typeof filters.region === 'string') {
                    const regionValue = filters.region.trim();
                    if (regionValue) {
                        const normalizedRegion = regionValue.replace(/\s*\(.*\)$/, '');
                        queryPairs.push(['region', normalizedRegion]);
                    }
                }
                
                // Use Django REST framework pagination parameters
                if (filters.page_size) queryPairs.push(['page_size', filters.page_size]);
                if (filters.page) queryPairs.push(['page', filters.page]);
                
                // Legacy support for limit/offset (convert to page-based)
                if (filters.limit && !filters.page_size) queryPairs.push(['page_size', filters.limit]);
                if (filters.offset !== undefined && filters.offset > 0 && !filters.page) {
                    const pageSize = filters.limit || filters.page_size || 20;
                    const page = Math.floor(filters.offset / pageSize) + 1;
                    queryPairs.push(['page', page]);
                }

                const queryParams = new URLSearchParams(queryPairs);

                const url = `${this.baseUrl}${CSI300Config.ENDPOINTS.COMPANIES_LIST}?${queryParams.toString()}`;
                console.log('API Request URL:', url);
                console.log('Request filters:', filters);
                return await this.makeRequest(url);
            },
            // Reduce cache TTL for paginated results to ensure fresh data
            filters.page || filters.page_size || filters.limit || filters.offset !== undefined ? 60000 : CSI300Config.CACHE_CONFIG.COMPANIES_TTL
        );
    }

    /**
     * Get single company details
     */
    async getCompanyDetail(companyId) {
        const cacheKey = `company_${companyId}`;
        
        return await this.getCachedOrFetch(
            cacheKey,
            async () => {
                const url = `${this.baseUrl}${CSI300Config.ENDPOINTS.COMPANY_DETAIL.replace('{id}', companyId)}`;
                return await this.makeRequest(url);
            },
            CSI300Config.CACHE_CONFIG.COMPANIES_TTL
        );
    }

    /**
     * Get filter options (IM sectors, etc.) with optional filtering parameters
     */
    async getFilterOptions(params = {}) {
        // Create cache key that includes parameters to avoid stale cache
        const cacheKey = `filter_options_${JSON.stringify(params)}`;
        
        console.log('getFilterOptions called with params:', params);
        console.log('Cache key:', cacheKey);
        
        return await this.getCachedOrFetch(
            cacheKey,
            async () => {
                const queryString = new URLSearchParams(params).toString();
                const url = `${this.baseUrl}${CSI300Config.ENDPOINTS.FILTER_OPTIONS}${queryString ? '?' + queryString : ''}`;
                console.log('Filter options API URL:', url);
                return await this.makeRequest(url);
            },
            CSI300Config.CACHE_CONFIG.FILTER_OPTIONS_TTL
        );
    }

    /**
     * Search companies by name or ticker
     */
    async searchCompanies(query) {
        const url = `${this.baseUrl}${CSI300Config.ENDPOINTS.COMPANIES_LIST}?search=${encodeURIComponent(query)}`;
        return await this.makeRequest(url);
    }

    /**
     * Get investment summary for a specific company
     */
    async getInvestmentSummary(companyId) {
        const cacheKey = `investment_summary_${companyId}`;
        
        return await this.getCachedOrFetch(
            cacheKey,
            async () => {
                const url = `${this.baseUrl}/api/csi300/api/companies/${companyId}/investment_summary/`;
                return await this.makeRequest(url);
            },
            CSI300Config.CACHE_CONFIG.COMPANY_DETAIL_TTL
        );
    }

    /**
     * Get industry peers comparison for a company
     */
    async getIndustryPeersComparison(companyId) {
        const cacheKey = `industry_peers_${companyId}`;
        
        return await this.getCachedOrFetch(
            cacheKey,
            async () => {
                // Note: This endpoint is not in the ENDPOINTS config, using direct path
                const url = `${this.baseUrl}/api/csi300/api/companies/${companyId}/industry_peers_comparison/`;
                return await this.makeRequest(url);
            },
            CSI300Config.CACHE_CONFIG.COMPANY_DETAIL_TTL // Reuse company detail TTL
        );
    }

    /**
     * Clear cache (useful for development or forced refresh)
     */
    clearCache() {
        this.cache.clear();
        console.log('CSI300 API cache cleared');
    }

    /**
     * Get cache status
     */
    getCacheStatus() {
        return {
            enabled: this.cacheEnabled,
            size: this.cache.size,
            keys: Array.from(this.cache.keys())
        };
    }
}

// Create global instance
window.csi300ApiClient = new CSI300ApiClient();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CSI300ApiClient;
}
