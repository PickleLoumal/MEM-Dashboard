/**
 * TinyChart数据管理器
 * 统一处理数据获取、缓存、错误处理
 */
class TinyChartDataManager {
    constructor() {
        this.cache = new Map();
        this.apiClient = null;
        this.cacheTimeout = 5 * 60 * 1000; // 5分钟缓存
        this.maxConcurrentRequests = 10; // 限制并发请求数量
        this.requestQueue = [];
        this.activeRequests = 0;
        
        console.log('📊 TinyChartDataManager initialized');
    }

    /**
     * 预加载所有必需的数据
     * @param {Array} chartDefinitions - Chart定义数组
     */
    async preloadData(chartDefinitions) {
        const uniqueDataSources = this.getUniqueDataSources(chartDefinitions);
        
        console.log(`📊 Preloading data for ${uniqueDataSources.length} unique sources...`);
        
        // 批量请求数据
        const dataPromises = uniqueDataSources.map(source => 
            this.getData(source, { useCache: false })
        );

        const results = await Promise.allSettled(dataPromises);
        
        // 统计结果
        const successful = results.filter(r => r.status === 'fulfilled').length;
        const failed = results.filter(r => r.status === 'rejected').length;
        
        console.log(`✅ Data preload complete: ${successful} successful, ${failed} failed`);
        
        return results;
    }

    /**
     * 获取唯一数据源
     */
    getUniqueDataSources(chartDefinitions) {
        const sources = chartDefinitions.map(def => def.dataSource);
        const uniqueSources = [];
        
        sources.forEach(source => {
            const key = this.generateCacheKey(source);
            if (!uniqueSources.find(s => this.generateCacheKey(s) === key)) {
                uniqueSources.push(source);
            }
        });
        
        return uniqueSources;
    }

    /**
     * 获取数据（带缓存）
     * @param {Object} dataSource - 数据源配置
     * @param {Object} options - 选项
     */
    async getData(dataSource, options = {}) {
        const { useCache = true } = options;
        const cacheKey = this.generateCacheKey(dataSource);

        // 检查缓存
        if (useCache && this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.cacheTimeout) {
                console.log(`📋 Cache hit for: ${cacheKey}`);
                return cached.data;
            }
        }

        try {
            // 限制并发请求
            await this.waitForSlot();
            
            const data = await this.fetchData(dataSource);
            
            // 缓存数据
            this.cache.set(cacheKey, {
                data: data,
                timestamp: Date.now()
            });

            console.log(`✅ Data fetched and cached: ${cacheKey}`);
            return data;

        } catch (error) {
            console.error(`❌ Failed to fetch data for ${dataSource.type}:`, error);
            
            // 返回降级数据
            return this.getFallbackData(dataSource);
            
        } finally {
            this.activeRequests--;
            this.processQueue();
        }
    }

    /**
     * 实际数据获取逻辑
     * @param {Object} dataSource - 数据源配置
     */
    async fetchData(dataSource) {
        const { type, endpoint, processor } = dataSource;

        switch (type) {
            case 'fred':
                return await this.fetchFredData(endpoint);
            case 'bea':
                return await this.fetchBeaData(endpoint);
            case 'custom':
                return await this.fetchCustomData(endpoint);
            default:
                throw new Error(`Unknown data source type: ${type}`);
        }
    }

    /**
     * 获取FRED数据
     */
    async fetchFredData(endpoint) {
        const response = await fetch(`/api/fred/${endpoint}`);
        if (!response.ok) {
            throw new Error(`FRED API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.observations && data.observations.length > 0) {
            return {
                values: data.observations
                    .filter(obs => obs.value && obs.value !== '.')
                    .sort((a, b) => new Date(a.date) - new Date(b.date))
                    .map(obs => parseFloat(obs.value)),
                source: 'fred',
                lastUpdate: Date.now()
            };
        }
        
        throw new Error('No valid FRED observations');
    }

    /**
     * 获取BEA数据
     */
    async fetchBeaData(endpoint) {
        if (!this.apiClient) {
            this.apiClient = window.memApiClient || new MEMApiClient();
        }

        const response = await this.apiClient.getBEAData(endpoint);
        
        if (response && response.success && response.data) {
            let values;
            
            if (response.data.quarterly_data && response.data.quarterly_data.length > 0) {
                values = response.data.quarterly_data
                    .sort((a, b) => a.TimePeriod.localeCompare(b.TimePeriod))
                    .map(item => parseFloat(item.DataValue));
            } else if (response.data.value) {
                values = [response.data.value];
            } else {
                throw new Error('No valid BEA data');
            }

            return {
                values: values,
                yoyChange: response.data.yoy_change,
                source: 'bea',
                lastUpdate: Date.now()
            };
        }
        
        throw new Error('BEA API response invalid');
    }

    /**
     * 获取自定义数据
     */
    async fetchCustomData(endpoint) {
        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error(`Custom API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // 假设自定义API返回标准格式
        if (data.values && Array.isArray(data.values)) {
            return {
                values: data.values.map(v => parseFloat(v)),
                source: 'custom',
                lastUpdate: Date.now()
            };
        }
        
        throw new Error('Invalid custom data format');
    }

    /**
     * 并发控制
     */
    async waitForSlot() {
        if (this.activeRequests < this.maxConcurrentRequests) {
            this.activeRequests++;
            return;
        }

        // 等待队列
        return new Promise(resolve => {
            this.requestQueue.push(resolve);
        });
    }

    /**
     * 处理等待队列
     */
    processQueue() {
        if (this.requestQueue.length > 0 && this.activeRequests < this.maxConcurrentRequests) {
            const resolve = this.requestQueue.shift();
            this.activeRequests++;
            resolve();
        }
    }

    /**
     * 生成缓存键
     */
    generateCacheKey(dataSource) {
        return `${dataSource.type}_${dataSource.endpoint}`;
    }

    /**
     * 获取降级数据
     */
    getFallbackData(dataSource) {
        // 根据数据源类型返回合理的降级数据
        const fallbackData = {
            fred: [100, 102, 98, 105, 103, 107, 104, 108],
            bea: [750, 755, 748, 762, 758, 765, 759, 768],
            custom: [50, 52, 48, 55, 53, 57, 54, 58]
        };

        console.log(`🔄 Using fallback data for: ${dataSource.type}`);

        return {
            values: fallbackData[dataSource.type] || fallbackData.custom,
            source: 'fallback',
            lastUpdate: Date.now()
        };
    }

    /**
     * 清理过期缓存
     */
    cleanupCache() {
        const now = Date.now();
        let cleanedCount = 0;
        
        for (const [key, value] of this.cache.entries()) {
            if (now - value.timestamp > this.cacheTimeout) {
                this.cache.delete(key);
                cleanedCount++;
            }
        }
        
        if (cleanedCount > 0) {
            console.log(`🧹 Cleaned ${cleanedCount} expired cache entries`);
        }
    }

    /**
     * 获取缓存统计信息
     */
    getCacheStatistics() {
        const cacheEntries = Array.from(this.cache.values());
        const now = Date.now();
        
        return {
            totalEntries: this.cache.size,
            validEntries: cacheEntries.filter(entry => 
                now - entry.timestamp < this.cacheTimeout
            ).length,
            activeRequests: this.activeRequests,
            queuedRequests: this.requestQueue.length
        };
    }

    /**
     * 强制刷新所有缓存
     */
    invalidateCache() {
        this.cache.clear();
        console.log('🔄 All cache entries invalidated');
    }
}

// 导出到全局作用域
window.TinyChartDataManager = TinyChartDataManager;
