/**
 * PCE Pagination Component
 * Handles pagination for Personal Consumption Expenditures data
 */

class PCEPagination {
    constructor() {
        this.currentPage = 1;
        this.itemsPerPage = 20;
        this.totalItems = 0;
        this.initialized = false;
    }

    /**
     * Initialize PCE pagination
     */
    init() {
        if (this.initialized) {
            return;
        }

        console.log('📄 Initializing PCE Pagination...');
        this.setupEventListeners();
        this.initialized = true;
        console.log('✅ PCE Pagination initialized');
    }

    /**
     * Setup event listeners for pagination controls
     */
    setupEventListeners() {
        // Add pagination event listeners when pagination controls are present
        document.addEventListener('click', (event) => {
            if (event.target.matches('.pce-pagination-btn')) {
                const page = parseInt(event.target.dataset.page);
                if (page && page !== this.currentPage) {
                    this.goToPage(page);
                }
            }
        });
    }

    /**
     * Navigate to specific page
     */
    goToPage(page) {
        if (page < 1 || page > this.getTotalPages()) {
            return;
        }

        this.currentPage = page;
        this.updatePaginationDisplay();
        this.loadPageData(page);
    }

    /**
     * Get total number of pages
     */
    getTotalPages() {
        return Math.ceil(this.totalItems / this.itemsPerPage);
    }

    /**
     * Update pagination display
     */
    updatePaginationDisplay() {
        const paginationContainer = document.querySelector('.pce-pagination-container');
        if (!paginationContainer) {
            return;
        }

        // Update pagination UI
        const totalPages = this.getTotalPages();
        let paginationHTML = '';

        // Previous button
        if (this.currentPage > 1) {
            paginationHTML += `<button class="pce-pagination-btn" data-page="${this.currentPage - 1}">‹ Previous</button>`;
        }

        // Page numbers
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(totalPages, this.currentPage + 2);

        for (let i = startPage; i <= endPage; i++) {
            const activeClass = i === this.currentPage ? 'active' : '';
            paginationHTML += `<button class="pce-pagination-btn ${activeClass}" data-page="${i}">${i}</button>`;
        }

        // Next button
        if (this.currentPage < totalPages) {
            paginationHTML += `<button class="pce-pagination-btn" data-page="${this.currentPage + 1}">Next ›</button>`;
        }

        paginationContainer.innerHTML = paginationHTML;
    }

    /**
     * Load data for specific page
     */
    async loadPageData(page) {
        try {
            // This would typically load PCE data for the specific page
            console.log(`📊 Loading PCE data for page ${page}...`);
            // Implementation would depend on the specific PCE data structure
        } catch (error) {
            console.error('Error loading PCE page data:', error);
        }
    }

    /**
     * Set total items and update pagination
     */
    setTotalItems(total) {
        this.totalItems = total;
        this.updatePaginationDisplay();
    }
}

// Make class available globally
window.PCEPagination = PCEPagination;

// Initialize PCE Pagination when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.pcePagination = new PCEPagination();
    window.pcePagination.init();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PCEPagination;
}
