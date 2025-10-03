/**
 * TinyChart遗留代码迁移适配器
 * 提供与旧代码的兼容性，逐步迁移现有Chart到新系统
 */
class TinyChartLegacyAdapter {
    constructor() {
        this.migrationMap = new Map();
        this.legacyCharts = new Map();
        this.migrationStats = {
            totalLegacy: 0,
            migrated: 0,
            failed: 0,
            pending: 0
        };
        
        console.log('🔄 TinyChart legacy adapter initialized');
    }

    /**
     * 扫描并注册遗留Chart
     */
    scanLegacyCharts() {
        console.log('🔍 Scanning for legacy tinycharts...');
        
        // 查找所有可能的遗留Chart元素
        const legacySelectors = [
            '.tinychart',
            '[data-chart]',
            '[id*="chart"]',
            'canvas[id*="tinychart"]',
            'canvas[id*="mini"]',
            'canvas[width="24"][height="12"]'
        ];

        let foundCharts = new Set();

        legacySelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                if (this.isValidLegacyChart(element)) {
                    foundCharts.add(element);
                }
            });
        });

        // 注册找到的Chart
        foundCharts.forEach(element => {
            this.registerLegacyChart(element);
        });

        this.migrationStats.totalLegacy = foundCharts.size;
        this.migrationStats.pending = foundCharts.size;
        
        console.log(`📊 Found ${foundCharts.size} legacy charts`);
        return Array.from(foundCharts);
    }

    /**
     * 验证是否为有效的遗留Chart
     */
    isValidLegacyChart(element) {
        // Canvas元素
        if (element.tagName === 'CANVAS') {
            const width = parseInt(element.width) || parseInt(element.style.width);
            const height = parseInt(element.height) || parseInt(element.style.height);
            
            // 检查尺寸是否符合TinyChart标准
            if ((width === 24 && height === 12) || 
                (width >= 20 && width <= 50 && height >= 10 && height <= 20)) {
                return true;
            }
        }

        // 检查是否有Chart相关的数据属性
        if (element.dataset.chart || 
            element.dataset.indicator || 
            element.dataset.source ||
            element.id.includes('chart') ||
            element.id.includes('tinychart')) {
            return true;
        }

        // 检查类名
        if (element.classList.contains('tinychart') ||
            element.classList.contains('mini-chart') ||
            element.classList.contains('indicator-chart')) {
            return true;
        }

        return false;
    }

    /**
     * 注册遗留Chart
     */
    registerLegacyChart(element) {
        const legacyInfo = this.extractLegacyInfo(element);
        
        if (legacyInfo.id) {
            this.legacyCharts.set(legacyInfo.id, {
                element: element,
                info: legacyInfo,
                migrated: false,
                migrationDate: null,
                errors: []
            });
            
            console.log(`📝 Registered legacy chart: ${legacyInfo.id}`);
        }
    }

    /**
     * 从遗留元素提取信息
     */
    extractLegacyInfo(element) {
        const info = {
            id: null,
            indicator: null,
            source: null,
            dataUrl: null,
            theme: 'default',
            config: {}
        };

        // 提取ID
        if (element.id) {
            info.id = element.id;
        } else {
            info.id = `legacy_chart_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        }

        // 提取数据属性
        if (element.dataset.chart) {
            info.indicator = element.dataset.chart;
        }
        
        if (element.dataset.indicator) {
            info.indicator = element.dataset.indicator;
        }
        
        if (element.dataset.source) {
            info.source = element.dataset.source;
        }
        
        if (element.dataset.url) {
            info.dataUrl = element.dataset.url;
        }

        // 尝试从ID推断信息
        if (!info.indicator && info.id) {
            const idParts = info.id.split('_');
            if (idParts.length > 1) {
                info.indicator = idParts[idParts.length - 1];
            }
        }

        // 提取配置
        try {
            if (element.dataset.config) {
                info.config = JSON.parse(element.dataset.config);
            }
        } catch (e) {
            console.warn(`⚠️ Failed to parse config for ${info.id}:`, e);
        }

        return info;
    }

    /**
     * 批量迁移遗留Chart
     */
    async migrateAllLegacy() {
        console.log('🚀 Starting bulk legacy migration...');
        
        const migrationPromises = Array.from(this.legacyCharts.keys()).map(id => 
            this.migrateLegacyChart(id)
        );

        const results = await Promise.allSettled(migrationPromises);
        
        // 统计结果
        results.forEach((result, index) => {
            if (result.status === 'fulfilled') {
                this.migrationStats.migrated++;
            } else {
                this.migrationStats.failed++;
                console.error(`❌ Migration failed for chart ${index}:`, result.reason);
            }
        });

        this.migrationStats.pending = 
            this.migrationStats.totalLegacy - 
            this.migrationStats.migrated - 
            this.migrationStats.failed;

        console.log('📊 Bulk migration completed:', this.migrationStats);
        return this.migrationStats;
    }

    /**
     * 迁移单个遗留Chart
     */
    async migrateLegacyChart(legacyId) {
        const legacyChart = this.legacyCharts.get(legacyId);
        if (!legacyChart || legacyChart.migrated) {
            return;
        }

        try {
            console.log(`🔄 Migrating legacy chart: ${legacyId}`);

            // 1. 创建新的Chart定义
            const definition = this.createDefinitionFromLegacy(legacyChart);

            // 2. 在新系统中创建Chart
            const success = await window.tinyChartManager.createChart(definition);

            if (success) {
                // 3. 隐藏或移除遗留元素
                this.handleLegacyElement(legacyChart.element, 'hide');

                // 4. 标记为已迁移
                legacyChart.migrated = true;
                legacyChart.migrationDate = new Date();

                console.log(`✅ Successfully migrated: ${legacyId}`);
                return true;
            } else {
                throw new Error('Chart creation failed in new system');
            }

        } catch (error) {
            console.error(`❌ Failed to migrate ${legacyId}:`, error);
            legacyChart.errors.push({
                timestamp: new Date(),
                error: error.message
            });
            throw error;
        }
    }

    /**
     * 从遗留Chart创建新的定义
     */
    createDefinitionFromLegacy(legacyChart) {
        const info = legacyChart.info;
        
        const definition = {
            id: info.id,
            containerId: this.findOrCreateContainer(legacyChart.element),
            title: info.indicator || info.id,
            dataSource: this.determineLegacyDataSource(info),
            chartType: 'line', // 默认为线图
            colorStrategy: 'trend',
            theme: info.theme || 'default',
            config: {
                responsive: false,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                },
                ...info.config
            }
        };

        console.log(`📋 Created definition for ${info.id}:`, definition);
        return definition;
    }

    /**
     * 确定遗留Chart的数据源
     */
    determineLegacyDataSource(info) {
        // 如果有明确的数据URL
        if (info.dataUrl) {
            return {
                type: 'custom',
                url: info.dataUrl,
                method: 'GET'
            };
        }

        // 如果有source和indicator
        if (info.source && info.indicator) {
            return {
                type: info.source.toLowerCase(),
                indicator: info.indicator,
                period: 'latest',
                count: 20
            };
        }

        // 如果只有indicator，假设为FRED
        if (info.indicator) {
            return {
                type: 'fred',
                indicator: info.indicator,
                period: 'latest',
                count: 20
            };
        }

        // 默认数据源
        return {
            type: 'fallback',
            data: [1, 2, 3, 4, 5, 4, 3, 2, 1]
        };
    }

    /**
     * 查找或创建容器
     */
    findOrCreateContainer(legacyElement) {
        // 如果遗留元素就是Canvas，查找其父容器
        if (legacyElement.tagName === 'CANVAS') {
            const parent = legacyElement.parentElement;
            if (parent && parent.id) {
                return parent.id;
            }
        }

        // 创建新的容器
        const containerId = `container_${legacyElement.id || Date.now()}`;
        const container = document.createElement('div');
        container.id = containerId;
        container.style.width = '24px';
        container.style.height = '12px';
        container.style.position = 'relative';

        // 在遗留元素之后插入容器
        legacyElement.parentNode.insertBefore(container, legacyElement.nextSibling);

        return containerId;
    }

    /**
     * 处理遗留元素
     */
    handleLegacyElement(element, action = 'hide') {
        switch (action) {
            case 'hide':
                element.style.display = 'none';
                element.setAttribute('data-legacy-migrated', 'true');
                break;
            
            case 'remove':
                element.remove();
                break;
                
            case 'preserve':
                element.style.opacity = '0.5';
                element.setAttribute('data-legacy-preserved', 'true');
                break;
        }
    }

    /**
     * 回滚迁移（用于测试）
     */
    rollbackMigration(legacyId) {
        const legacyChart = this.legacyCharts.get(legacyId);
        if (!legacyChart || !legacyChart.migrated) {
            return false;
        }

        try {
            // 1. 从新系统移除Chart
            window.tinyChartManager.destroyChart(legacyId);

            // 2. 恢复遗留元素
            legacyChart.element.style.display = '';
            legacyChart.element.removeAttribute('data-legacy-migrated');

            // 3. 标记为未迁移
            legacyChart.migrated = false;
            legacyChart.migrationDate = null;

            console.log(`↩️ Rolled back migration for: ${legacyId}`);
            return true;

        } catch (error) {
            console.error(`❌ Failed to rollback ${legacyId}:`, error);
            return false;
        }
    }

    /**
     * 获取迁移统计
     */
    getMigrationStats() {
        return {
            ...this.migrationStats,
            legacyCharts: Array.from(this.legacyCharts.keys()),
            migratedCharts: Array.from(this.legacyCharts.entries())
                .filter(([_, chart]) => chart.migrated)
                .map(([id, _]) => id),
            errorCharts: Array.from(this.legacyCharts.entries())
                .filter(([_, chart]) => chart.errors.length > 0)
                .map(([id, chart]) => ({ id, errors: chart.errors }))
        };
    }

    /**
     * 生成迁移报告
     */
    generateMigrationReport() {
        const stats = this.getMigrationStats();
        
        const report = {
            timestamp: new Date(),
            summary: {
                total: stats.totalLegacy,
                migrated: stats.migrated,
                failed: stats.failed,
                pending: stats.pending,
                successRate: stats.totalLegacy > 0 ? 
                    (stats.migrated / stats.totalLegacy * 100).toFixed(1) + '%' : '0%'
            },
            details: {
                migratedCharts: stats.migratedCharts,
                errorCharts: stats.errorCharts,
                legacyCharts: stats.legacyCharts
            }
        };

        console.log('📄 Migration Report Generated:', report);
        return report;
    }

    /**
     * 验证迁移完整性
     */
    validateMigration() {
        console.log('🔍 Validating migration integrity...');
        
        const issues = [];
        
        this.legacyCharts.forEach((chart, id) => {
            if (chart.migrated) {
                // 检查新Chart是否存在
                const newChart = window.tinyChartManager.getChart(id);
                if (!newChart) {
                    issues.push(`Missing new chart for migrated legacy: ${id}`);
                }
                
                // 检查遗留元素是否正确隐藏
                if (chart.element.style.display !== 'none') {
                    issues.push(`Legacy element not hidden: ${id}`);
                }
            }
        });

        if (issues.length === 0) {
            console.log('✅ Migration validation passed');
        } else {
            console.warn('⚠️ Migration validation issues:', issues);
        }

        return {
            isValid: issues.length === 0,
            issues: issues
        };
    }

    /**
     * 清理迁移数据
     */
    cleanup() {
        console.log('🧹 Cleaning up legacy adapter...');
        
        this.legacyCharts.clear();
        this.migrationMap.clear();
        this.migrationStats = {
            totalLegacy: 0,
            migrated: 0,
            failed: 0,
            pending: 0
        };
        
        console.log('✅ Legacy adapter cleanup completed');
    }
}

// 导出到全局作用域
window.TinyChartLegacyAdapter = TinyChartLegacyAdapter;

console.log('🔄 TinyChart legacy adapter loaded');
