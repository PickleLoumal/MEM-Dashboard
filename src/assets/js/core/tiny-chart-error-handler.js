/**
 * 错误恢复和监控系统
 */
class TinyChartErrorHandler {
    constructor() {
        this.errorCount = new Map();
        this.maxRetries = 3;
        this.retryDelay = 1000;
        this.circuitBreaker = new Map();
        this.errorLog = [];
        this.maxLogSize = 100;
        
        console.log('🛡️ TinyChartErrorHandler initialized');
    }

    /**
     * 处理Chart创建错误
     */
    async handleChartError(chartId, error, retryFunction) {
        const errorKey = `${chartId}_${error.name}`;
        const currentCount = this.errorCount.get(errorKey) || 0;

        // 记录错误
        this.logError(chartId, error);

        console.error(`❌ Chart error for ${chartId}:`, error);

        // 更新错误计数
        this.errorCount.set(errorKey, currentCount + 1);

        // 检查熔断器状态
        if (this.isCircuitBreakerActive(chartId)) {
            console.warn(`💥 Circuit breaker active for ${chartId}, skipping retry`);
            this.createErrorPlaceholder(chartId, error);
            return;
        }

        // 检查是否达到最大重试次数
        if (currentCount < this.maxRetries) {
            console.log(`🔄 Retrying chart ${chartId} (attempt ${currentCount + 1}/${this.maxRetries})`);
            
            // 延迟重试
            await this.delay(this.retryDelay * (currentCount + 1));
            
            try {
                await retryFunction();
                // 成功后重置错误计数
                this.errorCount.delete(errorKey);
                console.log(`✅ Chart ${chartId} recovered successfully`);
            } catch (retryError) {
                return this.handleChartError(chartId, retryError, retryFunction);
            }
        } else {
            // 达到最大重试次数，启用熔断器
            console.error(`💥 Chart ${chartId} failed after ${this.maxRetries} attempts, activating circuit breaker`);
            this.activateCircuitBreaker(chartId);
            
            // 创建错误占位符
            this.createErrorPlaceholder(chartId, error);
        }
    }

    /**
     * 记录错误
     */
    logError(chartId, error) {
        const errorInfo = {
            timestamp: new Date().toISOString(),
            chartId: chartId,
            errorName: error.name,
            errorMessage: error.message,
            stack: error.stack
        };

        this.errorLog.push(errorInfo);

        // 保持日志大小限制
        if (this.errorLog.length > this.maxLogSize) {
            this.errorLog = this.errorLog.slice(-this.maxLogSize);
        }
    }

    /**
     * 激活熔断器
     */
    activateCircuitBreaker(chartId) {
        this.circuitBreaker.set(chartId, {
            isActive: true,
            activatedAt: Date.now(),
            resetTime: Date.now() + (5 * 60 * 1000) // 5分钟后重置
        });

        console.warn(`⚡ Circuit breaker activated for ${chartId}`);
    }

    /**
     * 检查熔断器状态
     */
    isCircuitBreakerActive(chartId) {
        const breaker = this.circuitBreaker.get(chartId);
        if (!breaker) return false;

        if (Date.now() > breaker.resetTime) {
            this.circuitBreaker.delete(chartId);
            console.log(`🔄 Circuit breaker reset for ${chartId}`);
            return false;
        }

        return breaker.isActive;
    }

    /**
     * 手动重置熔断器
     */
    resetCircuitBreaker(chartId) {
        if (this.circuitBreaker.has(chartId)) {
            this.circuitBreaker.delete(chartId);
            console.log(`🔄 Circuit breaker manually reset for ${chartId}`);
        }
    }

    /**
     * 创建错误占位符
     */
    createErrorPlaceholder(chartId, error) {
        // 尝试多种Canvas ID格式
        const possibleIds = [
            `tiny${chartId.charAt(0).toUpperCase() + chartId.slice(1)}Chart`,
            `tiny${chartId.replace(/-/g, '')}Chart`,
            chartId
        ];

        let canvas = null;
        for (const id of possibleIds) {
            canvas = document.getElementById(id);
            if (canvas) break;
        }

        if (canvas) {
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // 绘制错误指示器
            ctx.fillStyle = '#ef4444';
            ctx.fillRect(0, canvas.height - 2, canvas.width, 2);
            
            // 添加tooltip提示
            canvas.title = `Chart error: ${error.message}`;
            canvas.style.opacity = '0.3';
            
            console.log(`⚠️ Error placeholder created for ${chartId}`);
        } else {
            console.warn(`⚠️ Cannot create error placeholder: canvas not found for ${chartId}`);
        }
    }

    /**
     * 延迟函数
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * 获取错误统计
     */
    getErrorStatistics() {
        const recentErrors = this.errorLog.filter(error => 
            Date.now() - new Date(error.timestamp).getTime() < 60 * 60 * 1000 // 最近1小时
        );

        return {
            totalErrors: Array.from(this.errorCount.values()).reduce((a, b) => a + b, 0),
            uniqueErrors: this.errorCount.size,
            recentErrors: recentErrors.length,
            activeCircuitBreakers: this.circuitBreaker.size,
            errorBreakdown: Object.fromEntries(this.errorCount),
            circuitBreakers: Array.from(this.circuitBreaker.keys())
        };
    }

    /**
     * 获取最近的错误日志
     */
    getRecentErrors(limit = 10) {
        return this.errorLog.slice(-limit);
    }

    /**
     * 清理过期的错误计数
     */
    cleanupErrorCounts() {
        const now = Date.now();
        let cleanedCount = 0;

        // 清理熔断器
        for (const [chartId, breaker] of this.circuitBreaker.entries()) {
            if (now > breaker.resetTime) {
                this.circuitBreaker.delete(chartId);
                cleanedCount++;
            }
        }

        // 清理旧的错误日志
        const oneHourAgo = now - (60 * 60 * 1000);
        const initialLogLength = this.errorLog.length;
        this.errorLog = this.errorLog.filter(error => 
            new Date(error.timestamp).getTime() > oneHourAgo
        );

        const logCleaned = initialLogLength - this.errorLog.length;

        if (cleanedCount > 0 || logCleaned > 0) {
            console.log(`🧹 Error cleanup: ${cleanedCount} circuit breakers reset, ${logCleaned} old logs removed`);
        }
    }

    /**
     * 重置所有错误统计
     */
    reset() {
        this.errorCount.clear();
        this.circuitBreaker.clear();
        this.errorLog = [];
        console.log('🔄 All error statistics reset');
    }

    /**
     * 设置错误处理配置
     */
    setConfig(config) {
        if (config.maxRetries && config.maxRetries > 0) {
            this.maxRetries = config.maxRetries;
        }
        if (config.retryDelay && config.retryDelay > 0) {
            this.retryDelay = config.retryDelay;
        }
        if (config.maxLogSize && config.maxLogSize > 0) {
            this.maxLogSize = config.maxLogSize;
        }

        console.log(`⚙️ Error handler config updated:`, {
            maxRetries: this.maxRetries,
            retryDelay: this.retryDelay,
            maxLogSize: this.maxLogSize
        });
    }

    /**
     * 检查Chart是否处于错误状态
     */
    isChartInErrorState(chartId) {
        return this.isCircuitBreakerActive(chartId) || 
               Array.from(this.errorCount.keys()).some(key => key.startsWith(chartId));
    }

    /**
     * 生成错误报告
     */
    generateErrorReport() {
        const stats = this.getErrorStatistics();
        const recentErrors = this.getRecentErrors(5);

        return {
            timestamp: new Date().toISOString(),
            statistics: stats,
            recentErrors: recentErrors,
            config: {
                maxRetries: this.maxRetries,
                retryDelay: this.retryDelay,
                maxLogSize: this.maxLogSize
            }
        };
    }
}

// 导出到全局作用域
window.TinyChartErrorHandler = TinyChartErrorHandler;
