/**
 * TinyChart渲染队列管理器
 * 优化大批量Chart的渲染性能
 */
class TinyChartRenderQueue {
    constructor() {
        this.batchSize = 10; // 每批处理10个Chart
        this.batchDelay = 16; // 16ms延迟（60fps）
        this.queue = [];
        this.isProcessing = false;
        this.processedCount = 0;
        this.failedCount = 0;
        
        console.log('⚡ TinyChartRenderQueue initialized');
    }

    /**
     * 分批处理Chart渲染
     * @param {Array} chartDefinitions - Chart定义数组
     * @param {TinyChartManager} chartManager - Chart管理器实例
     */
    async processBatches(chartDefinitions, chartManager) {
        if (this.isProcessing) {
            console.warn('⚠️ Render queue already processing');
            return;
        }

        this.queue = [...chartDefinitions];
        this.isProcessing = true;
        this.processedCount = 0;
        this.failedCount = 0;

        const totalBatches = Math.ceil(this.queue.length / this.batchSize);
        let currentBatch = 0;

        console.log(`🔄 Processing ${this.queue.length} charts in ${totalBatches} batches...`);

        while (this.queue.length > 0 && this.isProcessing) {
            currentBatch++;
            
            // 取出一批Chart定义
            const batch = this.queue.splice(0, this.batchSize);
            
            // 显示进度
            console.log(`📊 Processing batch ${currentBatch}/${totalBatches} (${batch.length} charts)`);

            // 并行处理当前批次
            const batchPromises = batch.map(definition => 
                this.renderChart(definition, chartManager)
            );

            const results = await Promise.allSettled(batchPromises);
            
            // 统计结果
            results.forEach(result => {
                if (result.status === 'fulfilled') {
                    this.processedCount++;
                } else {
                    this.failedCount++;
                }
            });

            // 让出主线程给其他任务
            if (this.queue.length > 0) {
                await this.yield();
            }
        }

        this.isProcessing = false;
        console.log(`✅ Batch processing completed: ${this.processedCount} successful, ${this.failedCount} failed`);
    }

    /**
     * 渲染单个Chart
     * @param {Object} definition - Chart定义
     * @param {TinyChartManager} chartManager - Chart管理器实例
     */
    async renderChart(definition, chartManager) {
        try {
            await chartManager.createChart(definition);
            return { success: true, chartId: definition.id };
        } catch (error) {
            console.error(`❌ Failed to render chart ${definition.id}:`, error);
            return { success: false, chartId: definition.id, error: error.message };
        }
    }

    /**
     * 让出主线程
     */
    async yield() {
        return new Promise(resolve => {
            if (this.batchDelay > 0) {
                setTimeout(resolve, this.batchDelay);
            } else {
                // 使用MessageChannel实现零延迟让出
                const channel = new MessageChannel();
                channel.port1.onmessage = () => resolve();
                channel.port2.postMessage(null);
            }
        });
    }

    /**
     * 停止处理
     */
    stop() {
        this.isProcessing = false;
        this.queue = [];
        console.log(`⏹️ Chart rendering queue stopped`);
    }

    /**
     * 暂停处理
     */
    pause() {
        this.isProcessing = false;
        console.log(`⏸️ Chart rendering queue paused`);
    }

    /**
     * 恢复处理
     */
    resume(chartManager) {
        if (this.queue.length > 0 && !this.isProcessing) {
            console.log(`▶️ Chart rendering queue resumed`);
            this.processBatches([...this.queue], chartManager);
        }
    }

    /**
     * 添加Chart到队列
     * @param {Object} definition - Chart定义
     */
    addChart(definition) {
        if (!this.isProcessing) {
            this.queue.push(definition);
            console.log(`➕ Chart added to queue: ${definition.id}`);
        } else {
            console.warn(`⚠️ Cannot add chart while processing: ${definition.id}`);
        }
    }

    /**
     * 从队列移除Chart
     * @param {string} chartId - Chart ID
     */
    removeChart(chartId) {
        const initialLength = this.queue.length;
        this.queue = this.queue.filter(def => def.id !== chartId);
        
        if (this.queue.length < initialLength) {
            console.log(`➖ Chart removed from queue: ${chartId}`);
        }
    }

    /**
     * 设置批处理大小
     * @param {number} size - 批处理大小
     */
    setBatchSize(size) {
        if (size > 0 && size <= 50) {
            this.batchSize = size;
            console.log(`⚙️ Batch size set to: ${size}`);
        } else {
            console.warn(`⚠️ Invalid batch size: ${size}, must be between 1 and 50`);
        }
    }

    /**
     * 设置批处理延迟
     * @param {number} delay - 延迟时间（毫秒）
     */
    setBatchDelay(delay) {
        if (delay >= 0) {
            this.batchDelay = delay;
            console.log(`⚙️ Batch delay set to: ${delay}ms`);
        } else {
            console.warn(`⚠️ Invalid batch delay: ${delay}, must be >= 0`);
        }
    }

    /**
     * 获取队列状态
     */
    getStatus() {
        return {
            isProcessing: this.isProcessing,
            queueLength: this.queue.length,
            processedCount: this.processedCount,
            failedCount: this.failedCount,
            batchSize: this.batchSize,
            batchDelay: this.batchDelay,
            successRate: this.processedCount + this.failedCount > 0 ? 
                         (this.processedCount / (this.processedCount + this.failedCount) * 100).toFixed(1) : 0
        };
    }

    /**
     * 重置统计信息
     */
    resetStats() {
        this.processedCount = 0;
        this.failedCount = 0;
        console.log('📊 Render queue statistics reset');
    }

    /**
     * 清空队列
     */
    clear() {
        this.queue = [];
        this.resetStats();
        console.log('🗑️ Render queue cleared');
    }
}

// 导出到全局作用域
window.TinyChartRenderQueue = TinyChartRenderQueue;
