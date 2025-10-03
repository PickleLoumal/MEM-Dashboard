/**
 * TinyChart配置管理器
 * 统一管理所有Chart的配置和主题
 */
class TinyChartConfig {
    constructor() {
        this.defaultConfig = {
            type: 'line',
            options: {
                responsive: false,
                maintainAspectRatio: false,
                animation: false, // 禁用动画提升性能
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                },
                scales: {
                    y: { display: false },
                    x: { display: false }
                },
                elements: {
                    point: { radius: 0 },
                    line: {
                        borderWidth: 1,
                        tension: 0.3
                    }
                }
            }
        };

        this.themes = {
            default: {
                colors: {
                    positive: '#22c55e',  // 绿色 - 积极趋势
                    negative: '#ef4444',  // 红色 - 消极趋势
                    neutral: '#6b7280'    // 灰色 - 中性趋势
                }
            },
            bloomberg: {
                colors: {
                    positive: '#00d4aa',
                    negative: '#ff6b6b',
                    neutral: '#8b949e'
                }
            },
            minimal: {
                colors: {
                    positive: '#10b981',
                    negative: '#f87171',
                    neutral: '#9ca3af'
                }
            }
        };

        this.currentTheme = 'default';
        console.log('🎨 TinyChartConfig initialized with default theme');
    }

    /**
     * 构建Chart配置
     * @param {Array} values - 数据值数组
     * @param {string} color - 线条颜色
     * @param {Object} customConfig - 自定义配置
     */
    buildConfig(values, color, customConfig = {}) {
        const config = this.deepClone(this.defaultConfig);
        
        // 设置数据
        config.data = {
            labels: values.map(() => ''),
            datasets: [{
                data: values,
                borderColor: color,
                backgroundColor: 'transparent',
                fill: false,
                pointRadius: 0,
                pointHoverRadius: 0
            }]
        };

        // 应用自定义配置
        return this.mergeConfig(config, customConfig);
    }

    /**
     * 设置主题
     * @param {string} themeName - 主题名称
     */
    setTheme(themeName) {
        if (this.themes[themeName]) {
            this.currentTheme = themeName;
            console.log(`🎨 TinyChart theme changed to: ${themeName}`);
        } else {
            console.warn(`⚠️ Unknown theme: ${themeName}`);
        }
    }

    /**
     * 获取当前主题颜色
     * @param {string} type - 颜色类型 (positive/negative/neutral)
     */
    getThemeColor(type) {
        return this.themes[this.currentTheme].colors[type] || this.themes.default.colors[type];
    }

    /**
     * 深度克隆对象
     */
    deepClone(obj) {
        return JSON.parse(JSON.stringify(obj));
    }

    /**
     * 合并配置对象
     */
    mergeConfig(target, source) {
        if (!source || typeof source !== 'object') return target;
        
        const result = { ...target };
        
        for (const key in source) {
            if (source.hasOwnProperty(key)) {
                if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key])) {
                    result[key] = this.mergeConfig(result[key] || {}, source[key]);
                } else {
                    result[key] = source[key];
                }
            }
        }
        
        return result;
    }

    /**
     * 添加自定义主题
     * @param {string} name - 主题名称
     * @param {Object} theme - 主题配置
     */
    addTheme(name, theme) {
        if (theme && theme.colors) {
            this.themes[name] = theme;
            console.log(`🎨 Custom theme added: ${name}`);
        } else {
            console.warn(`⚠️ Invalid theme configuration for: ${name}`);
        }
    }

    /**
     * 获取所有可用主题
     */
    getAvailableThemes() {
        return Object.keys(this.themes);
    }

    /**
     * 验证配置完整性
     */
    validateConfig(config) {
        const required = ['type', 'data', 'options'];
        return required.every(key => config.hasOwnProperty(key));
    }
}

// 导出到全局作用域
window.TinyChartConfig = TinyChartConfig;
