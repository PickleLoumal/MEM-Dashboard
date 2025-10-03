/**
 * TinyChart HTML集成脚本
 * 为主要HTML页面提供统一的TinyChart加载和初始化
 */

// TinyChart系统启动器
(function() {
    'use strict';

    // Temporary global disable flag to bypass TinyChart system (requested)
    window.TINYCHART_DISABLED = true;

    /**
     * TinyChart HTML集成器
     */
    class TinyChartHTMLIntegrator {
        constructor() {
            this.loadedModules = new Set();
            this.initializationPromise = null;
            this.isReady = false;
            
            console.log('🌐 TinyChart HTML integrator loaded');
        }

        /**
         * 异步加载所有必需的模块
         */
        async loadModules() {
            const modules = [
                '/src/assets/js/core/tiny-chart-definitions.js', // 基础定义
                '/src/assets/js/tiny-chart-production-config.js', // 生产环境配置
                '/src/assets/js/core/tiny-chart-error-handler.js',
                '/src/assets/js/core/tiny-chart-render-queue.js',
                '/src/assets/js/core/tiny-chart-data-manager.js',
                '/src/assets/js/core/tiny-chart-config.js',
                '/src/assets/js/core/tiny-chart-manager.js',
                '/src/assets/js/core/tiny-chart-legacy-adapter.js',
                '/src/assets/js/core/tiny-chart-app.js',
                '/src/assets/js/tiny-chart-tester.js' // 测试系统
            ];

            const loadPromises = modules.map(module => this.loadScript(module));
            
            try {
                await Promise.all(loadPromises);
                console.log('✅ All TinyChart modules loaded successfully');
                return true;
            } catch (error) {
                console.error('❌ Failed to load TinyChart modules:', error);
                throw error;
            }
        }

        /**
         * 加载单个脚本
         */
        loadScript(src) {
            return new Promise((resolve, reject) => {
                if (this.loadedModules.has(src)) {
                    resolve();
                    return;
                }

                const script = document.createElement('script');
                script.src = src;
                script.async = true;
                
                script.onload = () => {
                    this.loadedModules.add(src);
                    console.log(`✅ Loaded: ${src}`);
                    resolve();
                };
                
                script.onerror = () => {
                    console.error(`❌ Failed to load: ${src}`);
                    reject(new Error(`Failed to load script: ${src}`));
                };
                
                document.head.appendChild(script);
            });
        }

        /**
         * 初始化TinyChart系统
         */
        async initialize() {
            if (window.TINYCHART_DISABLED) {
                console.warn('🚫 TinyChart system disabled (TINYCHART_DISABLED=true). Initialization skipped.');
                return false;
            }
            if (this.initializationPromise) {
                return this.initializationPromise;
            }

            this.initializationPromise = this._doInitialize();
            return this.initializationPromise;
        }

        async _doInitialize() {
            try {
                console.log('🚀 Starting TinyChart system initialization...');

                // 1. 等待DOM准备
                await this.waitForDOM();

                // 2. 验证Chart.js依赖
                await this.ensureChartJS();

                // 3. 加载所有模块
                await this.loadModules();

                // 4. 等待所有全局变量可用
                await this.waitForGlobals();

                // 5. 创建并初始化应用
                await this.initializeApplication();

                // 6. 处理遗留Chart迁移
                await this.handleLegacyMigration();

                this.isReady = true;
                console.log('🎉 TinyChart system fully initialized and ready!');

                // 触发自定义事件
                this.dispatchReadyEvent();

                return true;

            } catch (error) {
                console.error('❌ TinyChart initialization failed:', error);
                throw error;
            }
        }

        /**
         * 等待DOM准备
         */
        waitForDOM() {
            return new Promise(resolve => {
                if (document.readyState === 'complete' || document.readyState === 'interactive') {
                    resolve();
                } else {
                    document.addEventListener('DOMContentLoaded', resolve, { once: true });
                }
            });
        }

        /**
         * 确保Chart.js已加载
         */
        async ensureChartJS() {
            // 检查Chart.js是否已经加载
            if (typeof Chart !== 'undefined') {
                console.log('✅ Chart.js already loaded');
                return;
            }

            console.log('📦 Loading Chart.js from CDN...');
            
            // 从CDN加载Chart.js
            await this.loadScript('https://cdn.jsdelivr.net/npm/chart.js');
            
            // 验证加载
            if (typeof Chart === 'undefined') {
                throw new Error('Chart.js failed to load');
            }
            
            console.log('✅ Chart.js loaded successfully');
        }

        /**
         * 等待所有全局变量可用
         */
        async waitForGlobals() {
            const requiredGlobals = [
                'TINYCHART_DEFINITIONS',
                'COLOR_STRATEGIES', 
                'TINYCHART_CONFIG',
                'TinyChartManager',
                'TinyChartApplication'
            ];

            const maxWait = 10000; // 10秒超时
            const checkInterval = 100; // 100ms检查间隔
            let elapsed = 0;

            while (elapsed < maxWait) {
                const missing = requiredGlobals.filter(name => !window[name]);
                
                if (missing.length === 0) {
                    console.log('✅ All required globals are available');
                    return;
                }

                await new Promise(resolve => setTimeout(resolve, checkInterval));
                elapsed += checkInterval;
            }

            const stillMissing = requiredGlobals.filter(name => !window[name]);
            throw new Error(`Timeout waiting for globals: ${stillMissing.join(', ')}`);
        }

        /**
         * 初始化应用程序
         */
        async initializeApplication() {
            if (!window.tinyChartApp) {
                window.tinyChartApp = new TinyChartApplication();
            }
            
            await window.tinyChartApp.initialize();
        }

        /**
         * 处理遗留Chart迁移
         */
        async handleLegacyMigration() {
            // 创建遗留适配器
            const legacyAdapter = new TinyChartLegacyAdapter();
            
            // 扫描遗留Chart
            const legacyCharts = legacyAdapter.scanLegacyCharts();
            
            if (legacyCharts.length > 0) {
                console.log(`🔄 Found ${legacyCharts.length} legacy charts, starting migration...`);
                
                try {
                    await legacyAdapter.migrateAllLegacy();
                    const report = legacyAdapter.generateMigrationReport();
                    console.log('📊 Migration completed:', report.summary);
                } catch (error) {
                    console.error('❌ Legacy migration failed:', error);
                    // 不阻止初始化，遗留Chart保持原样
                }
            } else {
                console.log('ℹ️ No legacy charts found');
            }

            // 保存适配器引用
            window.tinyChartLegacyAdapter = legacyAdapter;
        }

        /**
         * 触发准备完成事件
         */
        dispatchReadyEvent() {
            const event = new CustomEvent('tinyChartReady', {
                detail: {
                    timestamp: new Date(),
                    version: '2.0.0',
                    chartCount: window.tinyChartManager?.getStatistics()?.totalCharts || 0
                }
            });
            
            document.dispatchEvent(event);
            console.log('📢 tinyChartReady event dispatched');
        }

        /**
         * 获取系统状态
         */
        getStatus() {
            return {
                isReady: this.isReady,
                loadedModules: Array.from(this.loadedModules),
                applicationStatus: window.tinyChartApp?.getApplicationStatus?.() || null,
                chartStats: window.tinyChartManager?.getStatistics?.() || null
            };
        }
    }

    // 创建全局集成器实例
    window.tinyChartIntegrator = new TinyChartHTMLIntegrator();

    // 自动初始化（受禁用标志保护）
    if (!window.TINYCHART_DISABLED) {
        window.tinyChartIntegrator.initialize().catch(error => {
            console.error('❌ Auto-initialization failed:', error);
            window.retryTinyChartInit = () => {
                return window.tinyChartIntegrator.initialize();
            };
        });
    } else {
        console.log('ℹ️ TinyChart auto-initialization suppressed (disabled).');
    }

    // 提供便利的全局初始化函数（若后续需要重新启用可手动调用并先清除标志）
    window.initTinyCharts = () => {
        if (window.TINYCHART_DISABLED) {
            console.warn('⚠️ Cannot init TinyCharts while disabled. Clear window.TINYCHART_DISABLED first.');
            return Promise.resolve(false);
        }
        return window.tinyChartIntegrator.initialize();
    };

    console.log('🌐 TinyChart HTML integration script loaded (disabled mode:', window.TINYCHART_DISABLED, ')');

})();

/**
 * 便利函数集合
 */

// 等待TinyChart系统准备就绪
window.waitForTinyCharts = function() {
    return new Promise(resolve => {
        if (window.tinyChartIntegrator?.isReady) {
            resolve();
        } else {
            document.addEventListener('tinyChartReady', resolve, { once: true });
        }
    });
};

// 创建新的TinyChart（便利函数）
window.createTinyChart = async function(definition) {
    await window.waitForTinyCharts();
    return window.tinyChartManager.createChart(definition);
};

// 更新TinyChart数据（便利函数）
window.updateTinyChart = async function(chartId, newData) {
    await window.waitForTinyCharts();
    return window.tinyChartManager.updateChart(chartId, newData);
};

// 获取TinyChart统计（便利函数）
window.getTinyChartStats = async function() {
    await window.waitForTinyCharts();
    return window.tinyChartManager.getStatistics();
};

// 销毁TinyChart（便利函数）
window.destroyTinyChart = async function(chartId) {
    await window.waitForTinyCharts();
    return window.tinyChartManager.destroyChart(chartId);
};

console.log('🛠️ TinyChart convenience functions loaded');
