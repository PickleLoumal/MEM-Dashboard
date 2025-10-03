/**
 * TinyChart系统测试和验证脚本
 * 用于验证新系统的功能和性能
 */
class TinyChartTester {
    constructor() {
        this.testResults = {
            modules: [],
            dependencies: [],
            initialization: [],
            charts: [],
            performance: [],
            migration: []
        };
        this.isRunning = false;
        
        console.log('🧪 TinyChart tester initialized');
    }

    /**
     * 运行完整的测试套件
     */
    async runFullTestSuite() {
        if (this.isRunning) {
            console.log('⚠️ Test suite already running');
            return;
        }

        this.isRunning = true;
        console.log('🚀 Starting TinyChart full test suite...');

        try {
            // 1. 模块加载测试
            await this.testModuleLoading();

            // 2. 依赖验证测试
            await this.testDependencies();

            // 3. 初始化测试
            await this.testInitialization();

            // 4. Chart创建和渲染测试
            await this.testChartOperations();

            // 5. 性能测试
            await this.testPerformance();

            // 6. 遗留迁移测试
            await this.testLegacyMigration();

            // 7. 生成测试报告
            this.generateTestReport();

        } catch (error) {
            console.error('❌ Test suite failed:', error);
        } finally {
            this.isRunning = false;
        }
    }

    /**
     * 测试模块加载
     */
    async testModuleLoading() {
        console.log('📦 Testing module loading...');
        
        const expectedModules = [
            'TinyChartManager',
            'TinyChartConfig',
            'TinyChartDataManager',
            'TinyChartRenderQueue',
            'TinyChartErrorHandler',
            'TinyChartApplication',
            'TinyChartLegacyAdapter'
        ];

        const results = expectedModules.map(moduleName => {
            const exists = typeof window[moduleName] !== 'undefined';
            const result = {
                module: moduleName,
                loaded: exists,
                type: exists ? typeof window[moduleName] : 'undefined'
            };

            if (exists) {
                console.log(`✅ ${moduleName} loaded successfully`);
            } else {
                console.error(`❌ ${moduleName} not found`);
            }

            return result;
        });

        this.testResults.modules = results;
    }

    /**
     * 测试依赖
     */
    async testDependencies() {
        console.log('🔗 Testing dependencies...');

        const dependencies = [
            { name: 'Chart.js', check: () => typeof Chart !== 'undefined' },
            { name: 'TINYCHART_DEFINITIONS', check: () => Array.isArray(window.TINYCHART_DEFINITIONS) },
            { name: 'COLOR_STRATEGIES', check: () => typeof window.COLOR_STRATEGIES === 'object' },
            { name: 'TINYCHART_CONFIG', check: () => typeof window.TINYCHART_CONFIG === 'object' },
            { name: 'API_CONFIG', check: () => typeof window.API_CONFIG === 'object' }
        ];

        const results = dependencies.map(dep => {
            const available = dep.check();
            const result = {
                dependency: dep.name,
                available: available
            };

            if (available) {
                console.log(`✅ ${dep.name} available`);
            } else {
                console.error(`❌ ${dep.name} not available`);
            }

            return result;
        });

        this.testResults.dependencies = results;
    }

    /**
     * 测试初始化
     */
    async testInitialization() {
        console.log('🚀 Testing initialization...');

        const tests = [
            {
                name: 'TinyChart Integrator',
                test: () => window.tinyChartIntegrator && window.tinyChartIntegrator.isReady
            },
            {
                name: 'TinyChart Application',
                test: () => window.tinyChartApp && window.tinyChartApp.isInitialized
            },
            {
                name: 'TinyChart Manager',
                test: () => window.tinyChartManager && typeof window.tinyChartManager.createChart === 'function'
            }
        ];

        const results = tests.map(test => {
            const passed = test.test();
            const result = {
                test: test.name,
                passed: passed
            };

            if (passed) {
                console.log(`✅ ${test.name} initialized correctly`);
            } else {
                console.error(`❌ ${test.name} initialization failed`);
            }

            return result;
        });

        this.testResults.initialization = results;
    }

    /**
     * 测试Chart操作
     */
    async testChartOperations() {
        console.log('📊 Testing chart operations...');

        // 测试Chart定义
        const definitions = window.TINYCHART_DEFINITIONS;
        if (!definitions || definitions.length === 0) {
            console.error('❌ No chart definitions found');
            return;
        }

        // 选择前3个定义进行测试
        const testDefinitions = definitions.slice(0, 3);
        const results = [];

        for (const definition of testDefinitions) {
            const result = {
                chartId: definition.id,
                created: false,
                rendered: false,
                updated: false,
                destroyed: false,
                errors: []
            };

            try {
                // 创建测试容器
                const testContainer = this.createTestContainer(definition.id);
                definition.containerId = testContainer.id;

                // 测试创建
                const created = await window.tinyChartManager.createChart(definition);
                result.created = created;
                console.log(`📊 Chart ${definition.id} creation: ${created ? '✅' : '❌'}`);

                if (created) {
                    // 等待渲染
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    result.rendered = true;

                    // 测试更新
                    const updated = await window.tinyChartManager.updateChart(definition.id, {
                        type: 'fallback',
                        data: [1, 2, 3, 4, 5]
                    });
                    result.updated = updated;
                    console.log(`🔄 Chart ${definition.id} update: ${updated ? '✅' : '❌'}`);

                    // 测试销毁
                    const destroyed = window.tinyChartManager.destroyChart(definition.id);
                    result.destroyed = destroyed;
                    console.log(`🗑️ Chart ${definition.id} destruction: ${destroyed ? '✅' : '❌'}`);
                }

                // 清理测试容器
                testContainer.remove();

            } catch (error) {
                result.errors.push(error.message);
                console.error(`❌ Chart ${definition.id} test failed:`, error);
            }

            results.push(result);
        }

        this.testResults.charts = results;
    }

    /**
     * 创建测试容器
     */
    createTestContainer(chartId) {
        const container = document.createElement('div');
        container.id = `test-container-${chartId}`;
        container.style.width = '24px';
        container.style.height = '12px';
        container.style.position = 'absolute';
        container.style.top = '-100px'; // 隐藏在屏幕外
        container.style.left = '-100px';
        
        document.body.appendChild(container);
        return container;
    }

    /**
     * 测试性能
     */
    async testPerformance() {
        console.log('⚡ Testing performance...');

        const performanceTests = [
            {
                name: 'Manager Statistics',
                test: () => {
                    const start = performance.now();
                    const stats = window.tinyChartManager.getStatistics();
                    const duration = performance.now() - start;
                    return { stats, duration };
                }
            },
            {
                name: 'Data Manager Cache',
                test: () => {
                    const start = performance.now();
                    window.tinyChartManager.dataManager.cleanupCache();
                    const duration = performance.now() - start;
                    return { duration };
                }
            },
            {
                name: 'Error Handler Status',
                test: () => {
                    const start = performance.now();
                    const status = window.tinyChartManager.errorHandler.getStatus();
                    const duration = performance.now() - start;
                    return { status, duration };
                }
            }
        ];

        const results = performanceTests.map(test => {
            try {
                const result = test.test();
                console.log(`⚡ ${test.name}: ${result.duration.toFixed(2)}ms`);
                return {
                    test: test.name,
                    duration: result.duration,
                    passed: true,
                    data: result
                };
            } catch (error) {
                console.error(`❌ ${test.name} failed:`, error);
                return {
                    test: test.name,
                    duration: null,
                    passed: false,
                    error: error.message
                };
            }
        });

        this.testResults.performance = results;
    }

    /**
     * 测试遗留迁移
     */
    async testLegacyMigration() {
        console.log('🔄 Testing legacy migration...');

        if (!window.tinyChartLegacyAdapter) {
            console.error('❌ Legacy adapter not found');
            return;
        }

        const tests = [
            {
                name: 'Scan Legacy Charts',
                test: () => {
                    const charts = window.tinyChartLegacyAdapter.scanLegacyCharts();
                    return { count: charts.length, charts };
                }
            },
            {
                name: 'Migration Stats',
                test: () => {
                    return window.tinyChartLegacyAdapter.getMigrationStats();
                }
            },
            {
                name: 'Validation',
                test: () => {
                    return window.tinyChartLegacyAdapter.validateMigration();
                }
            }
        ];

        const results = tests.map(test => {
            try {
                const result = test.test();
                console.log(`🔄 ${test.name}:`, result);
                return {
                    test: test.name,
                    passed: true,
                    data: result
                };
            } catch (error) {
                console.error(`❌ ${test.name} failed:`, error);
                return {
                    test: test.name,
                    passed: false,
                    error: error.message
                };
            }
        });

        this.testResults.migration = results;
    }

    /**
     * 生成测试报告
     */
    generateTestReport() {
        const report = {
            timestamp: new Date(),
            summary: {
                modules: this.testResults.modules.filter(r => r.loaded).length + '/' + this.testResults.modules.length,
                dependencies: this.testResults.dependencies.filter(r => r.available).length + '/' + this.testResults.dependencies.length,
                initialization: this.testResults.initialization.filter(r => r.passed).length + '/' + this.testResults.initialization.length,
                charts: this.testResults.charts.filter(r => r.created).length + '/' + this.testResults.charts.length,
                performance: this.testResults.performance.filter(r => r.passed).length + '/' + this.testResults.performance.length,
                migration: this.testResults.migration.filter(r => r.passed).length + '/' + this.testResults.migration.length
            },
            details: this.testResults,
            overallStatus: this.calculateOverallStatus()
        };

        console.log('📄 TinyChart Test Report Generated:');
        console.log('Summary:', report.summary);
        console.log('Overall Status:', report.overallStatus);
        console.log('Full Report:', report);

        // 保存到全局变量以便查看
        window.tinyChartTestReport = report;

        return report;
    }

    /**
     * 计算总体状态
     */
    calculateOverallStatus() {
        const allTests = [
            ...this.testResults.modules,
            ...this.testResults.dependencies,
            ...this.testResults.initialization,
            ...this.testResults.charts,
            ...this.testResults.performance,
            ...this.testResults.migration
        ];

        const passedTests = allTests.filter(test => {
            return test.loaded || test.available || test.passed || test.created;
        });

        const passRate = (passedTests.length / allTests.length) * 100;

        if (passRate >= 90) return 'EXCELLENT';
        if (passRate >= 75) return 'GOOD';
        if (passRate >= 50) return 'FAIR';
        return 'POOR';
    }

    /**
     * 快速健康检查
     */
    async quickHealthCheck() {
        console.log('🩺 Running quick health check...');

        const checks = [
            { name: 'Integrator Ready', check: () => window.tinyChartIntegrator?.isReady },
            { name: 'App Initialized', check: () => window.tinyChartApp?.isInitialized },
            { name: 'Manager Available', check: () => !!window.tinyChartManager },
            { name: 'Chart Definitions', check: () => Array.isArray(window.TINYCHART_DEFINITIONS) && window.TINYCHART_DEFINITIONS.length > 0 },
            { name: 'Chart.js Available', check: () => typeof Chart !== 'undefined' }
        ];

        const results = checks.map(check => {
            const passed = check.check();
            console.log(`${passed ? '✅' : '❌'} ${check.name}`);
            return { name: check.name, passed };
        });

        const allPassed = results.every(r => r.passed);
        console.log(`🩺 Health check ${allPassed ? 'PASSED' : 'FAILED'}`);

        return { allPassed, results };
    }

    /**
     * 获取系统信息
     */
    getSystemInfo() {
        const info = {
            timestamp: new Date(),
            browser: navigator.userAgent,
            tinychartVersion: '2.0.0',
            chartjsVersion: typeof Chart !== 'undefined' ? Chart.version : 'Not loaded',
            definitions: window.TINYCHART_DEFINITIONS?.length || 0,
            colorStrategies: Object.keys(window.COLOR_STRATEGIES || {}),
            managerStats: window.tinyChartManager?.getStatistics?.() || null,
            applicationStatus: window.tinyChartApp?.getApplicationStatus?.() || null
        };

        console.log('ℹ️ System Information:', info);
        return info;
    }
}

// 导出到全局作用域
window.TinyChartTester = TinyChartTester;

// 创建全局测试实例
window.tinyChartTester = new TinyChartTester();

// 便利函数
window.testTinyCharts = () => window.tinyChartTester.runFullTestSuite();
window.checkTinyChartHealth = () => window.tinyChartTester.quickHealthCheck();
window.getTinyChartSystemInfo = () => window.tinyChartTester.getSystemInfo();

console.log('🧪 TinyChart testing system loaded');
