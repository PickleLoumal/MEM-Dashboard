/**
 * TinyChart应用程序初始化系统
 * 替换现有的硬编码初始化逻辑
 */
class TinyChartApplication {
    constructor() {
        this.tinyChartManager = null;
        this.performanceMonitor = null;
        this.isInitialized = false;
        this.updateInterval = null;
        this.cleanupInterval = null;
        
        console.log('🚀 TinyChartApplication instance created');
    }

    /**
     * 初始化应用程序
     */
    async initialize() {
        if (this.isInitialized) {
            console.log('⚠️ TinyChart application already initialized');
            return;
        }

        try {
            console.log('🚀 Initializing TinyChart application...');

            // 1. 等待DOM准备
            await this.waitForDOM();

            // 2. 验证依赖
            this.validateDependencies();

            // 3. 创建核心系统
            this.createCoreSystem();

            // 4. 初始化TinyChart系统
            await this.initializeTinyCharts();

            // 5. 设置监听器
            this.setupEventListeners();

            // 6. 启动定期更新
            this.startPeriodicUpdates();

            // 7. 启动性能监控
            this.startPerformanceMonitoring();

            this.isInitialized = true;
            console.log('✅ TinyChart application initialized successfully');

            // 输出初始化统计
            this.logInitializationStats();

        } catch (error) {
            console.error('❌ TinyChart application initialization failed:', error);
            throw error;
        }
    }

    /**
     * 等待DOM准备
     */
    async waitForDOM() {
        return new Promise(resolve => {
            if (document.readyState === 'complete') {
                resolve();
            } else {
                window.addEventListener('load', resolve, { once: true });
            }
        });
    }

    /**
     * 验证依赖
     */
    validateDependencies() {
        const requiredClasses = [
            'TinyChartManager',
            'TinyChartConfig', 
            'TinyChartDataManager',
            'TinyChartRenderQueue',
            'TinyChartErrorHandler'
        ];

        const requiredGlobals = [
            'TINYCHART_DEFINITIONS',
            'COLOR_STRATEGIES',
            'TINYCHART_CONFIG'
        ];

        // 检查类
        for (const className of requiredClasses) {
            if (!window[className]) {
                throw new Error(`Required class not found: ${className}`);
            }
        }

        // 检查全局变量
        for (const globalName of requiredGlobals) {
            if (!window[globalName]) {
                throw new Error(`Required global variable not found: ${globalName}`);
            }
        }

        // 检查Chart.js
        if (typeof Chart === 'undefined') {
            throw new Error('Chart.js library not found');
        }

        console.log('✅ All dependencies validated');
    }

    /**
     * 创建核心系统
     */
    createCoreSystem() {
        // 创建TinyChart管理器
        this.tinyChartManager = new TinyChartManager();
        
        // 设置全局引用
        window.tinyChartManager = this.tinyChartManager;
        
        // 应用配置
        this.applyConfiguration();
        
        console.log('🎯 Core TinyChart system created');
    }

    /**
     * 应用配置
     */
    applyConfiguration() {
        const config = window.TINYCHART_CONFIG;
        
        // 应用渲染配置
        if (config.rendering) {
            this.tinyChartManager.renderQueue.setBatchSize(config.rendering.batchSize);
            this.tinyChartManager.renderQueue.setBatchDelay(config.rendering.batchDelay);
        }
        
        // 应用错误处理配置
        if (config.errorHandling) {
            this.tinyChartManager.errorHandler.setConfig({
                maxRetries: config.errorHandling.maxRetries,
                retryDelay: config.errorHandling.retryDelay,
                maxLogSize: 100
            });
        }
        
        // 应用数据管理配置
        if (config.cache) {
            this.tinyChartManager.dataManager.cacheTimeout = config.cache.timeout;
        }
        
        if (config.api) {
            this.tinyChartManager.dataManager.maxConcurrentRequests = config.api.maxConcurrentRequests;
        }
        
        console.log('⚙️ Configuration applied');
    }

    /**
     * 初始化TinyCharts
     */
    async initializeTinyCharts() {
        // 设置颜色计算函数
        this.tinyChartManager.calculateTrendColor = (data, strategy) => {
            const colorFunction = window.COLOR_STRATEGIES[strategy] || window.COLOR_STRATEGIES['neutral'];
            return colorFunction(data);
        };

        // 验证所有定义
        this.validateDefinitions();

        // 批量初始化所有Charts
        await this.tinyChartManager.initializeCharts(window.TINYCHART_DEFINITIONS);

        console.log('📊 TinyCharts initialized');
    }

    /**
     * 验证Chart定义
     */
    validateDefinitions() {
        const definitions = window.TINYCHART_DEFINITIONS;
        let validCount = 0;
        let invalidCount = 0;

        definitions.forEach(def => {
            const validation = window.validateTinyChartDefinition(def);
            if (validation.isValid) {
                validCount++;
            } else {
                invalidCount++;
                console.warn(`⚠️ Invalid chart definition: ${def.id}`, validation.errors);
            }
            
            if (validation.warnings.length > 0) {
                console.warn(`⚠️ Chart definition warnings for ${def.id}:`, validation.warnings);
            }
        });

        console.log(`📋 Definition validation: ${validCount} valid, ${invalidCount} invalid`);
    }

    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 窗口resize时重新计算Chart尺寸
        window.addEventListener('resize', this.debounce(() => {
            this.handleWindowResize();
        }, 250));

        // 页面visibility变化时暂停/恢复更新
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseUpdates();
            } else {
                this.resumeUpdates();
            }
        });

        // 内存清理
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });

        // 错误处理
        window.addEventListener('error', (event) => {
            console.error('🚨 Global error caught:', event.error);
        });

        console.log('👂 Event listeners setup complete');
    }

    /**
     * 处理窗口大小变化
     */
    handleWindowResize() {
        // TinyCharts是固定尺寸，通常不需要resize处理
        // 但可以在这里添加任何必要的逻辑
        console.log('📐 Window resized - TinyCharts are fixed size');
    }

    /**
     * 启动定期更新
     */
    startPeriodicUpdates() {
        const config = window.TINYCHART_CONFIG;
        
        // 每5分钟更新一次数据
        this.updateInterval = setInterval(async () => {
            try {
                await this.updateAllCharts();
            } catch (error) {
                console.error('❌ Periodic update failed:', error);
            }
        }, 5 * 60 * 1000);

        // 每小时清理一次缓存和错误
        this.cleanupInterval = setInterval(() => {
            this.performMaintenance();
        }, 60 * 60 * 1000);

        console.log('⏰ Periodic updates started');
    }

    /**
     * 启动性能监控
     */
    startPerformanceMonitoring() {
        const config = window.TINYCHART_CONFIG;
        
        if (config.monitoring && config.monitoring.enabled) {
            this.performanceMonitor = setInterval(() => {
                this.collectPerformanceMetrics();
            }, config.monitoring.collectInterval);
            
            console.log('📈 Performance monitoring started');
        }
    }

    /**
     * 收集性能指标
     */
    collectPerformanceMetrics() {
        const stats = this.tinyChartManager.getStatistics();
        const config = window.TINYCHART_CONFIG;
        
        if (config.monitoring && config.monitoring.enableConsoleOutput) {
            console.log('📊 TinyChart Performance Metrics:', stats);
        }
        
        // 检查内存使用
        if (stats.memoryUsage && config.monitoring.memoryThreshold) {
            const memoryUsageRatio = stats.memoryUsage.used / stats.memoryUsage.limit;
            if (memoryUsageRatio > config.monitoring.memoryThreshold) {
                console.warn(`⚠️ High memory usage: ${(memoryUsageRatio * 100).toFixed(1)}%`);
                this.triggerMemoryOptimization();
            }
        }
    }

    /**
     * 触发内存优化
     */
    triggerMemoryOptimization() {
        console.log('🧹 Triggering memory optimization...');
        
        // 清理缓存
        this.tinyChartManager.dataManager.cleanupCache();
        
        // 清理错误处理器
        this.tinyChartManager.errorHandler.cleanupErrorCounts();
        
        // 手动垃圾回收（如果支持）
        if (window.gc) {
            window.gc();
        }
    }

    /**
     * 更新所有Charts
     */
    async updateAllCharts() {
        console.log('🔄 Starting periodic chart update...');
        
        const updateList = window.TINYCHART_DEFINITIONS.map(def => ({
            id: def.id,
            newData: def.dataSource
        }));

        await this.tinyChartManager.updateCharts(updateList);
        
        console.log('✅ Periodic chart update completed');
    }

    /**
     * 暂停更新
     */
    pauseUpdates() {
        console.log('⏸️ Updates paused (page hidden)');
        // 可以在这里暂停特定的更新操作
    }

    /**
     * 恢复更新
     */
    resumeUpdates() {
        console.log('▶️ Updates resumed (page visible)');
        // 可以在这里恢复更新操作
    }

    /**
     * 执行维护任务
     */
    performMaintenance() {
        console.log('🔧 Performing maintenance tasks...');
        
        // 清理数据缓存
        this.tinyChartManager.dataManager.cleanupCache();
        
        // 清理错误统计
        this.tinyChartManager.errorHandler.cleanupErrorCounts();
        
        // 输出统计信息
        const stats = this.tinyChartManager.getStatistics();
        console.log('📊 Maintenance stats:', stats);
    }

    /**
     * 防抖函数
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * 清理资源
     */
    cleanup() {
        console.log('🧹 Cleaning up TinyChart application...');
        
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        
        if (this.cleanupInterval) {
            clearInterval(this.cleanupInterval);
            this.cleanupInterval = null;
        }
        
        if (this.performanceMonitor) {
            clearInterval(this.performanceMonitor);
            this.performanceMonitor = null;
        }
        
        // 销毁所有Charts
        if (this.tinyChartManager) {
            this.tinyChartManager.destroyAll();
        }
        
        this.isInitialized = false;
        console.log('✅ Cleanup completed');
    }

    /**
     * 获取应用状态
     */
    getApplicationStatus() {
        return {
            isInitialized: this.isInitialized,
            chartStats: this.tinyChartManager ? this.tinyChartManager.getStatistics() : null,
            hasUpdateInterval: !!this.updateInterval,
            hasCleanupInterval: !!this.cleanupInterval,
            hasPerformanceMonitor: !!this.performanceMonitor
        };
    }

    /**
     * 记录初始化统计
     */
    logInitializationStats() {
        const stats = this.tinyChartManager.getStatistics();
        const configStats = window.getTinyChartConfigStats();
        
        console.log('📊 Initialization completed successfully:');
        console.log('   - Total charts:', stats.totalCharts);
        console.log('   - Active charts:', stats.activeCharts);
        console.log('   - Fallback charts:', stats.fallbackCharts);
        console.log('   - Configuration definitions:', configStats.totalDefinitions);
        console.log('   - Available themes:', configStats.availableThemes);
        console.log('   - Memory usage:', stats.memoryUsage ? `${stats.memoryUsage.used}MB` : 'N/A');
    }

    /**
     * 重新初始化
     */
    async reinitialize() {
        console.log('🔄 Reinitializing TinyChart application...');
        
        this.cleanup();
        await new Promise(resolve => setTimeout(resolve, 100)); // 短暂延迟
        await this.initialize();
        
        console.log('✅ Reinitialization completed');
    }
}

// 导出到全局作用域
window.TinyChartApplication = TinyChartApplication;

// 自动初始化（如果DOM已准备好）
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.tinyChartApp = new TinyChartApplication();
    });
} else {
    window.tinyChartApp = new TinyChartApplication();
}

console.log('🚀 TinyChart application system loaded');
