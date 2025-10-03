/**
 * TinyChart定义配置文件
 * 集中管理所有Chart的配置信息
 */

/**
 * TinyChart定义数组
 * 每个定义包含Chart的完整配置信息
 */
const TINYCHART_DEFINITIONS = [
    {
        id: 'debt-to-gdp',
        canvasId: 'tinyDebtToGdpChart',
        dataSource: {
            type: 'fred',
            endpoint: 'debt-to-gdp',
            processor: 'standard'
        },
        colorStrategy: 'economic-debt', // 债务指标特殊颜色策略
        customConfig: {
            elements: {
                line: {
                    borderWidth: 1.2 // 稍粗的线条
                }
            }
        }
    },
    {
        id: 'motor-vehicles',
        canvasId: 'tinyMotorVehiclesChart',
        dataSource: {
            type: 'bea',
            endpoint: 'motor_vehicles',
            processor: 'bea-quarterly'
        },
        colorStrategy: 'economic-positive',
        customConfig: {}
    },
    {
        id: 'unemployment-rate',
        canvasId: 'tinyUnemploymentChart',
        dataSource: {
            type: 'fred',
            endpoint: 'unemployment',
            processor: 'percentage'
        },
        colorStrategy: 'economic-negative', // 失业率上升是负面的
        customConfig: {
            elements: {
                line: {
                    tension: 0.4 // 更平滑的曲线
                }
            }
        }
    },
    {
        id: 'inflation-rate',
        canvasId: 'tinyInflationChart',
        dataSource: {
            type: 'fred',
            endpoint: 'cpi',
            processor: 'percentage'
        },
        colorStrategy: 'economic-negative',
        customConfig: {}
    },
    {
        id: 'interest-rates',
        canvasId: 'tinyInterestRatesChart',
        dataSource: {
            type: 'fred',
            endpoint: 'fed-funds-rate',
            processor: 'percentage'
        },
        colorStrategy: 'economic-neutral',
        customConfig: {}
    }
    // 可以轻松扩展到1000+个定义
];

/**
 * 颜色策略定义
 * 定义不同经济指标的颜色逻辑
 */
const COLOR_STRATEGIES = {
    'economic-positive': (data) => {
        // 上升=好，下降=坏
        const isIncreasing = data.values[data.values.length - 1] > data.values[data.values.length - 2];
        return isIncreasing ? '#22c55e' : '#ef4444';
    },
    'economic-negative': (data) => {
        // 上升=坏，下降=好（如失业率）
        const isIncreasing = data.values[data.values.length - 1] > data.values[data.values.length - 2];
        return isIncreasing ? '#ef4444' : '#22c55e';
    },
    'economic-debt': (data) => {
        // 债务类指标特殊处理
        if (data.yoyChange !== undefined) {
            return data.yoyChange >= 0 ? '#ef4444' : '#22c55e';
        }
        const isIncreasing = data.values[data.values.length - 1] > data.values[data.values.length - 2];
        return isIncreasing ? '#ef4444' : '#22c55e';
    },
    'economic-neutral': () => '#6b7280', // 中性指标用灰色
    'neutral': () => '#6b7280'
};

/**
 * TinyChart主题配置
 */
const TINYCHART_THEMES = {
    default: {
        name: 'Default',
        colors: {
            positive: '#22c55e',
            negative: '#ef4444',
            neutral: '#6b7280'
        }
    },
    bloomberg: {
        name: 'Bloomberg Style',
        colors: {
            positive: '#00d4aa',
            negative: '#ff6b6b',
            neutral: '#8b949e'
        }
    },
    minimal: {
        name: 'Minimal',
        colors: {
            positive: '#10b981',
            negative: '#f87171',
            neutral: '#9ca3af'
        }
    },
    dark: {
        name: 'Dark Mode',
        colors: {
            positive: '#34d399',
            negative: '#f87171',
            neutral: '#9ca3af'
        }
    }
};

/**
 * TinyChart配置选项
 */
const TINYCHART_CONFIG = {
    // 渲染设置
    rendering: {
        batchSize: 10,
        batchDelay: 16, // 16ms for 60fps
        enableViewportOptimization: true,
        enableMemoryOptimization: true
    },
    
    // 缓存设置
    cache: {
        timeout: 5 * 60 * 1000, // 5分钟
        maxEntries: 100,
        enablePersistence: false
    },
    
    // 错误处理设置
    errorHandling: {
        maxRetries: 3,
        retryDelay: 1000,
        enableCircuitBreaker: true,
        circuitBreakerTimeout: 5 * 60 * 1000, // 5分钟
        enableFallback: true
    },
    
    // 性能监控设置
    monitoring: {
        enabled: true,
        collectInterval: 30000, // 30秒
        memoryThreshold: 0.8, // 80%
        enableConsoleOutput: true
    },
    
    // API设置
    api: {
        maxConcurrentRequests: 10,
        requestTimeout: 10000, // 10秒
        enableRetry: true
    }
};

/**
 * 获取Chart定义通过ID
 * @param {string} chartId - Chart ID
 * @returns {Object|null} Chart定义
 */
function getTinyChartDefinition(chartId) {
    return TINYCHART_DEFINITIONS.find(def => def.id === chartId) || null;
}

/**
 * 获取所有Chart定义
 * @returns {Array} 所有Chart定义
 */
function getAllTinyChartDefinitions() {
    return [...TINYCHART_DEFINITIONS];
}

/**
 * 按数据源类型过滤Chart定义
 * @param {string} sourceType - 数据源类型 (fred, bea, custom)
 * @returns {Array} 过滤后的Chart定义
 */
function getTinyChartDefinitionsBySource(sourceType) {
    return TINYCHART_DEFINITIONS.filter(def => def.dataSource.type === sourceType);
}

/**
 * 按颜色策略过滤Chart定义
 * @param {string} colorStrategy - 颜色策略
 * @returns {Array} 过滤后的Chart定义
 */
function getTinyChartDefinitionsByColorStrategy(colorStrategy) {
    return TINYCHART_DEFINITIONS.filter(def => def.colorStrategy === colorStrategy);
}

/**
 * 添加新的Chart定义
 * @param {Object} definition - Chart定义
 * @returns {boolean} 添加是否成功
 */
function addTinyChartDefinition(definition) {
    // 验证定义的完整性
    if (!definition.id || !definition.canvasId || !definition.dataSource) {
        console.error('❌ Invalid chart definition:', definition);
        return false;
    }
    
    // 检查ID是否已存在
    if (getTinyChartDefinition(definition.id)) {
        console.error(`❌ Chart definition already exists: ${definition.id}`);
        return false;
    }
    
    TINYCHART_DEFINITIONS.push(definition);
    console.log(`✅ Chart definition added: ${definition.id}`);
    return true;
}

/**
 * 移除Chart定义
 * @param {string} chartId - Chart ID
 * @returns {boolean} 移除是否成功
 */
function removeTinyChartDefinition(chartId) {
    const index = TINYCHART_DEFINITIONS.findIndex(def => def.id === chartId);
    if (index !== -1) {
        TINYCHART_DEFINITIONS.splice(index, 1);
        console.log(`✅ Chart definition removed: ${chartId}`);
        return true;
    }
    console.warn(`⚠️ Chart definition not found: ${chartId}`);
    return false;
}

/**
 * 验证Chart定义
 * @param {Object} definition - Chart定义
 * @returns {Object} 验证结果
 */
function validateTinyChartDefinition(definition) {
    const errors = [];
    const warnings = [];
    
    // 必需字段检查
    if (!definition.id) errors.push('Missing required field: id');
    if (!definition.canvasId) errors.push('Missing required field: canvasId');
    if (!definition.dataSource) errors.push('Missing required field: dataSource');
    
    // 数据源验证
    if (definition.dataSource) {
        if (!definition.dataSource.type) errors.push('Missing dataSource.type');
        if (!definition.dataSource.endpoint) errors.push('Missing dataSource.endpoint');
        
        const validTypes = ['fred', 'bea', 'custom'];
        if (definition.dataSource.type && !validTypes.includes(definition.dataSource.type)) {
            errors.push(`Invalid dataSource.type: ${definition.dataSource.type}`);
        }
    }
    
    // 颜色策略验证
    if (definition.colorStrategy && !COLOR_STRATEGIES[definition.colorStrategy]) {
        warnings.push(`Unknown color strategy: ${definition.colorStrategy}`);
    }
    
    // Canvas元素存在性检查
    if (definition.canvasId && !document.getElementById(definition.canvasId)) {
        warnings.push(`Canvas element not found: ${definition.canvasId}`);
    }
    
    return {
        isValid: errors.length === 0,
        errors: errors,
        warnings: warnings
    };
}

/**
 * 获取配置统计信息
 * @returns {Object} 统计信息
 */
function getTinyChartConfigStats() {
    const sourceTypes = {};
    const colorStrategies = {};
    
    TINYCHART_DEFINITIONS.forEach(def => {
        // 统计数据源类型
        const sourceType = def.dataSource.type;
        sourceTypes[sourceType] = (sourceTypes[sourceType] || 0) + 1;
        
        // 统计颜色策略
        const colorStrategy = def.colorStrategy || 'none';
        colorStrategies[colorStrategy] = (colorStrategies[colorStrategy] || 0) + 1;
    });
    
    return {
        totalDefinitions: TINYCHART_DEFINITIONS.length,
        sourceTypes: sourceTypes,
        colorStrategies: colorStrategies,
        availableThemes: Object.keys(TINYCHART_THEMES).length,
        configSections: Object.keys(TINYCHART_CONFIG).length
    };
}

// 导出到全局作用域
window.TINYCHART_DEFINITIONS = TINYCHART_DEFINITIONS;
window.COLOR_STRATEGIES = COLOR_STRATEGIES;
window.TINYCHART_THEMES = TINYCHART_THEMES;
window.TINYCHART_CONFIG = TINYCHART_CONFIG;

// 导出工具函数
window.getTinyChartDefinition = getTinyChartDefinition;
window.getAllTinyChartDefinitions = getAllTinyChartDefinitions;
window.getTinyChartDefinitionsBySource = getTinyChartDefinitionsBySource;
window.getTinyChartDefinitionsByColorStrategy = getTinyChartDefinitionsByColorStrategy;
window.addTinyChartDefinition = addTinyChartDefinition;
window.removeTinyChartDefinition = removeTinyChartDefinition;
window.validateTinyChartDefinition = validateTinyChartDefinition;
window.getTinyChartConfigStats = getTinyChartConfigStats;

console.log('📋 TinyChart definitions and utilities loaded');
console.log(`📊 Configuration stats:`, getTinyChartConfigStats());
