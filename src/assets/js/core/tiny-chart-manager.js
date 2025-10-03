/**
 * TinyChart Global Management System
 * 统一管理所有微型图表的核心系统
 * 
 * 解决问题：
 * - 消除硬编码依赖
 * - 统一内存管理
 * - 批量渲染优化
 * - 配置统一管理
 */

/**
 * TinyChart统一管理器
 * 解决硬编码、内存泄漏、性能问题
 */
class TinyChartManager {
    constructor() {
        this.charts = new Map(); // 使用Map提供更好的性能
        this.config = new TinyChartConfig();
        this.dataManager = new TinyChartDataManager();
        this.renderQueue = new TinyChartRenderQueue();
        this.errorHandler = new TinyChartErrorHandler();
        this.isInitialized = false;
        
        console.log('🎯 TinyChartManager initialized');
    }

    /**
     * 批量初始化所有TinyChart
     * @param {Array} chartDefinitions - Chart定义数组
     */
    async initializeCharts(chartDefinitions) {
        if (this.isInitialized) {
            console.log('⚠️ TinyCharts already initialized');
            return;
        }
        
        try {
            console.log(`🚀 Initializing ${chartDefinitions.length} TinyCharts...`);
            
            // 1. 预加载所有必需的数据
            await this.dataManager.preloadData(chartDefinitions);
            
            // 2. 批量创建DOM元素（如果需要）
            this.prepareDOMElements(chartDefinitions);
            
            // 3. 分批渲染避免阻塞主线程
            await this.renderQueue.processBatches(chartDefinitions, this);
            
            this.isInitialized = true;
            console.log(`✅ Successfully initialized ${chartDefinitions.length} TinyCharts`);
            
        } catch (error) {
            console.error('❌ TinyChart batch initialization failed:', error);
            throw error;
        }
    }

    /**
     * 创建单个TinyChart
     * @param {Object} definition - Chart定义
     */
    async createChart(definition) {
        const {
            id,
            canvasId,
            dataSource,
            colorStrategy,
            customConfig = {}
        } = definition;

        try {
            // 1. 获取Canvas元素
            const canvas = this.getOrCreateCanvas(canvasId);
            if (!canvas) {
                throw new Error(`Canvas element not found: ${canvasId}`);
            }

            // 2. 销毁现有Chart（如果存在）
            await this.destroyChart(id);

            // 3. 获取数据
            const data = await this.dataManager.getData(dataSource);
            if (!data || !data.values || data.values.length === 0) {
                throw new Error(`No valid data for chart: ${id}`);
            }

            // 4. 计算趋势颜色
            const color = this.calculateTrendColor(data, colorStrategy);

            // 5. 构建Chart配置
            const chartConfig = this.config.buildConfig(data.values, color, customConfig);

            // 6. 创建Chart实例
            const ctx = canvas.getContext('2d');
            const chartInstance = new Chart(ctx, chartConfig);

            // 7. 注册Chart实例
            this.charts.set(id, {
                instance: chartInstance,
                canvas: canvas,
                definition: definition,
                lastUpdate: Date.now()
            });

            console.log(`✅ TinyChart created: ${id}`);
            return chartInstance;

        } catch (error) {
            console.error(`❌ Failed to create TinyChart: ${id}`, error);
            
            // 使用错误处理器进行降级处理
            await this.errorHandler.handleChartError(id, error, () => 
                this.createFallbackChart(definition)
            );
        }
    }

    /**
     * 获取或创建Canvas元素
     */
    getOrCreateCanvas(canvasId) {
        let canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.warn(`⚠️ Canvas not found: ${canvasId}, checking if it exists in DOM`);
            // 可以在这里添加动态创建Canvas的逻辑
        }
        return canvas;
    }

    /**
     * 计算趋势颜色
     */
    calculateTrendColor(data, colorStrategy) {
        if (window.COLOR_STRATEGIES && window.COLOR_STRATEGIES[colorStrategy]) {
            return window.COLOR_STRATEGIES[colorStrategy](data);
        }
        
        // 默认策略
        const isIncreasing = data.values[data.values.length - 1] > data.values[data.values.length - 2];
        return isIncreasing ? '#22c55e' : '#ef4444';
    }

    /**
     * 安全销毁Chart实例
     * @param {string} chartId - Chart ID
     */
    async destroyChart(chartId) {
        const chartInfo = this.charts.get(chartId);
        if (!chartInfo) return;

        try {
            // 1. 销毁Chart.js实例
            if (chartInfo.instance && typeof chartInfo.instance.destroy === 'function') {
                chartInfo.instance.destroy();
            }

            // 2. 清理全局注册
            const globalChart = Chart.getChart(chartInfo.canvas);
            if (globalChart) {
                globalChart.destroy();
            }

            // 3. 清理Canvas
            if (chartInfo.canvas) {
                const ctx = chartInfo.canvas.getContext('2d');
                ctx.clearRect(0, 0, chartInfo.canvas.width, chartInfo.canvas.height);
            }

            // 4. 移除注册
            this.charts.delete(chartId);

            console.log(`🗑️ TinyChart destroyed: ${chartId}`);

        } catch (error) {
            console.warn(`⚠️ Error destroying chart ${chartId}:`, error);
            // 强制清理
            this.charts.delete(chartId);
        }
    }

    /**
     * 准备DOM元素
     */
    prepareDOMElements(chartDefinitions) {
        // 检查所有需要的Canvas元素是否存在
        chartDefinitions.forEach(def => {
            const canvas = document.getElementById(def.canvasId);
            if (!canvas) {
                console.warn(`⚠️ Canvas missing: ${def.canvasId} for chart: ${def.id}`);
            }
        });
    }

    /**
     * 创建降级Chart
     */
    async createFallbackChart(definition) {
        try {
            console.log(`🔄 Creating fallback chart for: ${definition.id}`);
            
            const canvas = this.getOrCreateCanvas(definition.canvasId);
            if (!canvas) return;

            // 使用降级数据
            const fallbackData = this.dataManager.getFallbackData(definition.dataSource);
            const color = this.calculateTrendColor(fallbackData, definition.colorStrategy);
            const chartConfig = this.config.buildConfig(fallbackData.values, color, definition.customConfig);

            const ctx = canvas.getContext('2d');
            const chartInstance = new Chart(ctx, chartConfig);

            this.charts.set(definition.id, {
                instance: chartInstance,
                canvas: canvas,
                definition: definition,
                lastUpdate: Date.now(),
                isFallback: true
            });

            console.log(`✅ Fallback chart created: ${definition.id}`);

        } catch (error) {
            console.error(`❌ Fallback chart creation failed: ${definition.id}`, error);
        }
    }

    /**
     * 批量更新Charts
     * @param {Array} updateList - 需要更新的Chart列表
     */
    async updateCharts(updateList) {
        const updatePromises = updateList.map(async (update) => {
            try {
                const chartInfo = this.charts.get(update.id);
                if (chartInfo) {
                    // 重新创建chart而不是更新
                    await this.createChart(chartInfo.definition);
                }
            } catch (error) {
                console.error(`❌ Failed to update chart ${update.id}:`, error);
            }
        });

        await Promise.allSettled(updatePromises);
        console.log(`🔄 Batch update completed for ${updateList.length} charts`);
    }

    /**
     * 销毁所有Charts
     */
    async destroyAll() {
        console.log(`🗑️ Destroying all ${this.charts.size} TinyCharts...`);
        
        const destroyPromises = Array.from(this.charts.keys()).map(chartId => 
            this.destroyChart(chartId)
        );
        
        await Promise.allSettled(destroyPromises);
        this.charts.clear();
        this.isInitialized = false;
        
        console.log('✅ All TinyCharts destroyed');
    }

    /**
     * 获取Chart统计信息
     */
    getStatistics() {
        const chartStats = Array.from(this.charts.values());
        
        return {
            totalCharts: this.charts.size,
            activeCharts: chartStats.filter(c => c.instance).length,
            fallbackCharts: chartStats.filter(c => c.isFallback).length,
            lastUpdate: Math.max(...chartStats.map(c => c.lastUpdate || 0)),
            memoryUsage: this.calculateMemoryUsage(),
            isInitialized: this.isInitialized
        };
    }

    /**
     * 计算内存使用情况
     */
    calculateMemoryUsage() {
        if (performance.memory) {
            return {
                used: Math.round(performance.memory.usedJSHeapSize / 1048576), // MB
                total: Math.round(performance.memory.totalJSHeapSize / 1048576), // MB
                limit: Math.round(performance.memory.jsHeapSizeLimit / 1048576) // MB
            };
        }
        return null;
    }
}

// 导出到全局作用域
window.TinyChartManager = TinyChartManager;
