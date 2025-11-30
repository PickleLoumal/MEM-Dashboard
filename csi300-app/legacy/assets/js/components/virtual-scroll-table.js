/**
 * Virtual Scrolling Component for CSI300 Table
 * Optimized for rendering 1000+ rows smoothly
 * Uses Intersection Observer API and buffer management
 */

class VirtualScrollTable {
    constructor(options = {}) {
        this.options = {
            container: options.container || null,
            rowHeight: options.rowHeight || 48,
            bufferSize: options.bufferSize || 10,
            visibleRows: options.visibleRows || 20,
            onRowRender: options.onRowRender || (() => {}),
            onRowClick: options.onRowClick || (() => {}),
            ...options
        };
        
        this.data = [];
        this.columns = [];
        this.visibleStartIndex = 0;
        this.visibleEndIndex = 0;
        this.scrollTop = 0;
        this.containerHeight = 0;
        
        if (this.options.container) {
            this.init();
        }
    }
    
    init() {
        this.container = typeof this.options.container === 'string'
            ? document.querySelector(this.options.container)
            : this.options.container;
            
        if (!this.container) {
            console.error('Virtual scroll container not found');
            return;
        }
        
        this.setupContainer();
        this.bindEvents();
    }
    
    setupContainer() {
        // Ensure container has proper styles for virtual scrolling
        this.container.style.position = 'relative';
        this.container.style.overflow = 'auto';
        this.container.style.willChange = 'transform';
        
        // Create virtual scroll wrapper
        this.scrollWrapper = document.createElement('div');
        this.scrollWrapper.className = 'virtual-scroll-wrapper';
        this.scrollWrapper.style.position = 'relative';
        
        // Create visible content container
        this.contentContainer = document.createElement('div');
        this.contentContainer.className = 'virtual-scroll-content';
        this.contentContainer.style.position = 'absolute';
        this.contentContainer.style.top = '0';
        this.contentContainer.style.left = '0';
        this.contentContainer.style.right = '0';
        this.contentContainer.style.willChange = 'transform';
        
        this.scrollWrapper.appendChild(this.contentContainer);
        
        // Move existing table into content container
        const existingTable = this.container.querySelector('table');
        if (existingTable) {
            this.table = existingTable;
            this.contentContainer.appendChild(this.table);
        } else {
            this.table = this.createTable();
            this.contentContainer.appendChild(this.table);
        }
        
        // Clear and append wrapper
        while (this.container.firstChild) {
            if (this.container.firstChild === existingTable) {
                this.container.firstChild.remove();
            } else {
                this.container.firstChild.remove();
            }
        }
        this.container.appendChild(this.scrollWrapper);
        
        this.containerHeight = this.container.clientHeight;
    }
    
    createTable() {
        const table = document.createElement('table');
        table.className = 'company-table';
        table.innerHTML = `
            <thead></thead>
            <tbody></tbody>
        `;
        return table;
    }
    
    bindEvents() {
        // Scroll event with RAF throttling
        let rafId = null;
        this.container.addEventListener('scroll', () => {
            if (rafId) return;
            
            rafId = requestAnimationFrame(() => {
                this.handleScroll();
                rafId = null;
            });
        });
        
        // Resize observer for responsive updates
        if (typeof ResizeObserver !== 'undefined') {
            this.resizeObserver = new ResizeObserver(() => {
                this.handleResize();
            });
            this.resizeObserver.observe(this.container);
        } else {
            window.addEventListener('resize', () => this.handleResize());
        }
    }
    
    setData(data, columns) {
        this.data = data || [];
        this.columns = columns || [];
        this.render();
    }
    
    render() {
        if (!this.data || this.data.length === 0) {
            this.contentContainer.innerHTML = '<div class="no-results">No data to display</div>';
            return;
        }
        
        // Calculate total height
        const totalHeight = this.data.length * this.options.rowHeight;
        this.scrollWrapper.style.height = `${totalHeight}px`;
        
        // Render header if columns provided
        if (this.columns.length > 0) {
            this.renderHeader();
        }
        
        // Calculate visible range
        this.calculateVisibleRange();
        
        // Render visible rows
        this.renderVisibleRows();
    }
    
    renderHeader() {
        const thead = this.table.querySelector('thead');
        if (!thead) return;
        
        thead.innerHTML = '<tr>' + this.columns.map(col => {
            const alignClass = col.align === 'right' ? 'text-right' : '';
            return `<th class="${alignClass}">${col.displayName || col.name}</th>`;
        }).join('') + '</tr>';
    }
    
    calculateVisibleRange() {
        this.scrollTop = this.container.scrollTop;
        
        // Calculate visible row indices
        const startIndex = Math.floor(this.scrollTop / this.options.rowHeight);
        const visibleCount = Math.ceil(this.containerHeight / this.options.rowHeight);
        
        // Add buffer to reduce flicker during fast scrolling
        this.visibleStartIndex = Math.max(0, startIndex - this.options.bufferSize);
        this.visibleEndIndex = Math.min(
            this.data.length - 1,
            startIndex + visibleCount + this.options.bufferSize
        );
    }
    
    renderVisibleRows() {
        const tbody = this.table.querySelector('tbody');
        if (!tbody) return;
        
        // Clear existing rows
        tbody.innerHTML = '';
        
        // Get visible data slice
        const visibleData = this.data.slice(this.visibleStartIndex, this.visibleEndIndex + 1);
        
        // Create document fragment for batch rendering
        const fragment = document.createDocumentFragment();
        
        visibleData.forEach((rowData, index) => {
            const actualIndex = this.visibleStartIndex + index;
            const row = this.createRow(rowData, actualIndex);
            fragment.appendChild(row);
        });
        
        tbody.appendChild(fragment);
        
        // Position the content container
        const offsetY = this.visibleStartIndex * this.options.rowHeight;
        this.contentContainer.style.transform = `translateY(${offsetY}px)`;
    }
    
    createRow(rowData, index) {
        const row = document.createElement('tr');
        row.className = 'clickable-row';
        row.dataset.index = index;
        row.dataset.companyId = rowData.id;
        
        // Create cells based on columns
        if (this.columns.length > 0) {
            this.columns.forEach(col => {
                const cell = document.createElement('td');
                const value = this.options.onRowRender
                    ? this.options.onRowRender(rowData, col, index)
                    : rowData[col.id] || '-';
                
                cell.innerHTML = value;
                
                if (col.align === 'right') {
                    cell.classList.add('text-right');
                }
                
                row.appendChild(cell);
            });
        } else {
            // Fallback: create cell with JSON data
            const cell = document.createElement('td');
            cell.textContent = JSON.stringify(rowData);
            row.appendChild(cell);
        }
        
        // Add click handler
        row.addEventListener('click', (e) => {
            if (this.options.onRowClick) {
                this.options.onRowClick(rowData, index, e);
            }
        });
        
        return row;
    }
    
    handleScroll() {
        const newScrollTop = this.container.scrollTop;
        
        // Only re-render if scrolled beyond buffer zone
        const scrollDelta = Math.abs(newScrollTop - this.scrollTop);
        const bufferThreshold = this.options.bufferSize * this.options.rowHeight;
        
        if (scrollDelta > bufferThreshold) {
            this.calculateVisibleRange();
            this.renderVisibleRows();
        }
    }
    
    handleResize() {
        this.containerHeight = this.container.clientHeight;
        this.calculateVisibleRange();
        this.renderVisibleRows();
    }
    
    scrollToIndex(index) {
        if (index < 0 || index >= this.data.length) return;
        
        const targetScroll = index * this.options.rowHeight;
        this.container.scrollTop = targetScroll;
    }
    
    scrollToTop() {
        this.container.scrollTop = 0;
    }
    
    update() {
        this.render();
    }
    
    destroy() {
        if (this.resizeObserver) {
            this.resizeObserver.disconnect();
        }
        
        // Clean up event listeners
        this.container.removeEventListener('scroll', this.handleScroll);
        
        // Restore original content
        if (this.scrollWrapper && this.scrollWrapper.parentNode) {
            this.scrollWrapper.parentNode.removeChild(this.scrollWrapper);
        }
    }
}

/**
 * Performance Monitor for Virtual Scrolling
 * Tracks FPS and rendering performance
 */
class VirtualScrollPerformanceMonitor {
    constructor() {
        this.frames = [];
        this.lastTime = performance.now();
        this.fps = 0;
        this.monitoring = false;
    }
    
    start() {
        this.monitoring = true;
        this.measure();
    }
    
    stop() {
        this.monitoring = false;
    }
    
    measure() {
        if (!this.monitoring) return;
        
        const now = performance.now();
        const delta = now - this.lastTime;
        
        this.frames.push(delta);
        if (this.frames.length > 60) {
            this.frames.shift();
        }
        
        // Calculate average FPS
        const averageDelta = this.frames.reduce((a, b) => a + b, 0) / this.frames.length;
        this.fps = Math.round(1000 / averageDelta);
        
        this.lastTime = now;
        requestAnimationFrame(() => this.measure());
    }
    
    getFPS() {
        return this.fps;
    }
    
    getAverageFrameTime() {
        if (this.frames.length === 0) return 0;
        return this.frames.reduce((a, b) => a + b, 0) / this.frames.length;
    }
}

// Export to window for browser usage
if (typeof window !== 'undefined') {
    window.VirtualScrollTable = VirtualScrollTable;
    window.VirtualScrollPerformanceMonitor = VirtualScrollPerformanceMonitor;
}

// Export for use in Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { VirtualScrollTable, VirtualScrollPerformanceMonitor };
}
