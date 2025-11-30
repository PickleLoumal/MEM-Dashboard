/**
 * CSI300 Error Handler
 * Centralized error handling and user feedback for CSI300 application
 */

class CSI300ErrorHandler {
    constructor() {
        this.errorContainer = null;
        this.loadingStates = new Map();
        this.retryAttempts = new Map();
        this.maxRetryAttempts = 3;
    }

    /**
     * Initialize error handling
     */
    init() {
        this.createErrorContainer();
        this.setupGlobalErrorHandlers();
    }

    /**
     * Create error display container
     */
    createErrorContainer() {
        if (this.errorContainer) return;

        this.errorContainer = document.createElement('div');
        this.errorContainer.id = 'csi300-error-container';
        this.errorContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            min-width: 300px;
            max-width: 500px;
            pointer-events: none;
        `;

        document.body.appendChild(this.errorContainer);
    }

    /**
     * Setup global error handlers
     */
    setupGlobalErrorHandlers() {
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError('Unhandled promise rejection', event.reason);
            event.preventDefault();
        });

        // Handle global JavaScript errors
        window.addEventListener('error', (event) => {
            this.handleError('JavaScript error', {
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno
            });
        });
    }

    /**
     * Handle API errors
     */
    handleApiError(error, operation, context = {}) {
        console.error('CSI300 API Error:', error);

        let userMessage = '操作失败，请稍后重试';
        let canRetry = false;
        let retryDelay = 1000;

        // Determine error type and user message
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            userMessage = '网络连接失败，请检查网络连接';
            canRetry = true;
            retryDelay = 2000;
        } else if (error.message.includes('HTTP 401')) {
            userMessage = '访问权限不足';
            canRetry = false;
        } else if (error.message.includes('HTTP 403')) {
            userMessage = '访问被拒绝';
            canRetry = false;
        } else if (error.message.includes('HTTP 404')) {
            userMessage = '请求的资源不存在';
            canRetry = false;
        } else if (error.message.includes('HTTP 500')) {
            userMessage = '服务器内部错误，请稍后重试';
            canRetry = true;
            retryDelay = 5000;
        } else if (error.message.includes('HTTP 502') || error.message.includes('HTTP 503')) {
            userMessage = '服务暂时不可用，请稍后重试';
            canRetry = true;
            retryDelay = 3000;
        } else if (error.message.includes('timeout')) {
            userMessage = '请求超时，请稍后重试';
            canRetry = true;
            retryDelay = 2000;
        }

        this.showErrorMessage(userMessage, canRetry, retryDelay, operation, context);
    }

    /**
     * Handle general errors
     */
    handleError(title, error) {
        console.error('CSI300 Error:', title, error);

        let userMessage = '发生未知错误，请稍后重试';

        if (error && typeof error === 'object') {
            if (error.message) {
                userMessage = error.message;
            }
        } else if (typeof error === 'string') {
            userMessage = error;
        }

        this.showErrorMessage(userMessage, false, 0, title);
    }

    /**
     * Show error message to user
     */
    showErrorMessage(message, canRetry = false, retryDelay = 0, operation = '', context = {}) {
        const errorElement = document.createElement('div');
        errorElement.style.cssText = `
            background: #ef4444;
            color: white;
            padding: 12px 16px;
            border-radius: 6px;
            margin-bottom: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            pointer-events: auto;
            animation: slideIn 0.3s ease-out;
        `;

        let errorHtml = `
            <div style="font-weight: 500; margin-bottom: 4px;">错误</div>
            <div>${message}</div>
        `;

        if (canRetry && retryDelay > 0) {
            errorHtml += `
                <div style="margin-top: 8px;">
                    <button onclick="this.parentElement.parentElement.remove()"
                            style="background: rgba(255,255,255,0.2); border: none; color: white; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                        关闭
                    </button>
                    <button onclick="this.parentElement.parentElement.remove(); window.csi300ErrorHandler.retryOperation('${operation}', ${JSON.stringify(context)})"
                            style="background: white; color: #ef4444; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px; margin-left: 8px;">
                        重试
                    </button>
                </div>
            `;
        } else {
            errorHtml += `
                <div style="margin-top: 8px;">
                    <button onclick="this.parentElement.remove()"
                            style="background: rgba(255,255,255,0.2); border: none; color: white; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                        关闭
                    </button>
                </div>
            `;
        }

        errorElement.innerHTML = errorHtml;
        this.errorContainer.appendChild(errorElement);

        // Auto remove after 10 seconds if not closed
        setTimeout(() => {
            if (errorElement.parentNode) {
                errorElement.remove();
            }
        }, 10000);

        // Add CSS animation
        if (!document.getElementById('error-animations')) {
            const style = document.createElement('style');
            style.id = 'error-animations';
            style.textContent = `
                @keyframes slideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    /**
     * Retry operation
     */
    async retryOperation(operation, context) {
        const retryKey = `${operation}_${JSON.stringify(context)}`;

        if (!this.retryAttempts.has(retryKey)) {
            this.retryAttempts.set(retryKey, 0);
        }

        const attempts = this.retryAttempts.get(retryKey) + 1;

        if (attempts > this.maxRetryAttempts) {
            this.showErrorMessage('已达到最大重试次数，请稍后手动重试', false, 0, operation);
            return;
        }

        this.retryAttempts.set(retryKey, attempts);

        try {
            await this.executeOperation(operation, context);
        } catch (error) {
            console.error(`Retry ${attempts} failed:`, error);
            this.handleApiError(error, operation, context);
        }
    }

    /**
     * Execute operation
     */
    async executeOperation(operation, context) {
        switch (operation) {
            case 'get_companies':
                return await window.csi300ApiClient.getCompanies(context);
            case 'get_company_detail':
                return await window.csi300ApiClient.getCompanyDetail(context.companyId);
            case 'get_filter_options':
                return await window.csi300ApiClient.getFilterOptions();
            case 'search_companies':
                return await window.csi300ApiClient.searchCompanies(context.query);
            case 'get_industry_peers':
                return await window.csi300ApiClient.getIndustryPeersComparison(context.companyId);
            default:
                throw new Error(`Unknown operation: ${operation}`);
        }
    }

    /**
     * Show loading state
     */
    showLoading(elementId, message = '加载中...') {
        const element = document.getElementById(elementId);
        if (!element) return;

        this.loadingStates.set(elementId, element.innerHTML);

        element.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; padding: 20px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; border: 2px solid #e5e7eb; border-top: 2px solid #3b82f6; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                    <span>${message}</span>
                </div>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;
    }

    /**
     * Hide loading state
     */
    hideLoading(elementId) {
        const element = document.getElementById(elementId);
        if (!element || !this.loadingStates.has(elementId)) return;

        element.innerHTML = this.loadingStates.get(elementId);
        this.loadingStates.delete(elementId);
    }

    /**
     * Show success message
     */
    showSuccess(message, duration = 3000) {
        const successElement = document.createElement('div');
        successElement.style.cssText = `
            background: #10b981;
            color: white;
            padding: 12px 16px;
            border-radius: 6px;
            margin-bottom: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            pointer-events: auto;
            animation: slideIn 0.3s ease-out;
        `;

        successElement.innerHTML = `
            <div style="font-weight: 500; margin-bottom: 4px;">成功</div>
            <div>${message}</div>
            <div style="margin-top: 8px;">
                <button onclick="this.parentElement.parentElement.remove()"
                        style="background: rgba(255,255,255,0.2); border: none; color: white; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                    关闭
                </button>
            </div>
        `;

        this.errorContainer.appendChild(successElement);

        setTimeout(() => {
            if (successElement.parentNode) {
                successElement.remove();
            }
        }, duration);
    }

    /**
     * Clear all messages
     */
    clearMessages() {
        this.errorContainer.innerHTML = '';
    }
}

// Create global error handler instance
window.csi300ErrorHandler = new CSI300ErrorHandler();

// Initialize error handling when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.csi300ErrorHandler.init();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CSI300ErrorHandler;
}
