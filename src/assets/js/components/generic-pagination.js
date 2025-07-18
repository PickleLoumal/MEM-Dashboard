/**
 * Generic Card Pagination System
 * Supports pagination for multiple card types with different configurations
 */

class CardPaginationController {
    constructor() {
        this.initialized = false;
        this.cardConfigs = new Map();
        this.currentPages = new Map();
    }

    /**
     * Register a card with pagination configuration
     * @param {string} cardId - Unique identifier for the card
     * @param {Object} config - Configuration object
     * @param {number} config.itemsPerPage - Number of items per page
     * @param {Array} config.items - Array of item selectors or elements
     * @param {string} config.containerSelector - Container element selector
     * @param {string} config.pageIndicatorSelector - Page indicator element selector
     * @param {string} config.prevButtonSelector - Previous button selector
     * @param {string} config.nextButtonSelector - Next button selector
     * @param {Function} config.onPageChange - Optional callback when page changes
     */
    registerCard(cardId, config) {
        this.cardConfigs.set(cardId, {
            itemsPerPage: config.itemsPerPage || 6,
            items: config.items || [],
            containerSelector: config.containerSelector,
            pageIndicatorSelector: config.pageIndicatorSelector,
            prevButtonSelector: config.prevButtonSelector,
            nextButtonSelector: config.nextButtonSelector,
            onPageChange: config.onPageChange || null,
            totalPages: Math.ceil((config.items?.length || 0) / (config.itemsPerPage || 6))
        });
        
        this.currentPages.set(cardId, 1);
        
        console.log(`[Pagination] Registered card: ${cardId} with ${config.items?.length || 0} items, ${this.cardConfigs.get(cardId).totalPages} pages`);
    }

    /**
     * Initialize pagination for all registered cards
     */
    init() {
        if (this.initialized) {
            console.warn('[Pagination] Already initialized');
            return;
        }

        console.log('[Pagination] Initializing generic pagination system...');
        
        this.cardConfigs.forEach((config, cardId) => {
            this.initializeCard(cardId, config);
        });
        
        this.initialized = true;
        console.log('[Pagination] Generic pagination system initialized');
    }

    /**
     * Initialize pagination for a specific card
     * @param {string} cardId - Card identifier
     * @param {Object} config - Card configuration
     */
    initializeCard(cardId, config) {
        try {
            // Set up navigation buttons
            this.setupNavigationButtons(cardId, config);
            
            // Initialize page display
            this.updatePageDisplay(cardId);
            this.updateNavigationButtons(cardId);
            
            console.log(`[Pagination] Initialized card: ${cardId}`);
        } catch (error) {
            console.error(`[Pagination] Error initializing card ${cardId}:`, error);
        }
    }

    /**
     * Set up navigation button event listeners
     * @param {string} cardId - Card identifier
     * @param {Object} config - Card configuration
     */
    setupNavigationButtons(cardId, config) {
        // Previous button
        if (config.prevButtonSelector) {
            const prevBtn = document.querySelector(config.prevButtonSelector);
            if (prevBtn) {
                prevBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.prevPage(cardId);
                });
            }
        }

        // Next button
        if (config.nextButtonSelector) {
            const nextBtn = document.querySelector(config.nextButtonSelector);
            if (nextBtn) {
                nextBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.nextPage(cardId);
                });
            }
        }
    }

    /**
     * Go to next page for a specific card
     * @param {string} cardId - Card identifier
     */
    nextPage(cardId) {
        const config = this.cardConfigs.get(cardId);
        const currentPage = this.currentPages.get(cardId);
        
        if (!config || currentPage >= config.totalPages) return;
        
        this.currentPages.set(cardId, currentPage + 1);
        this.updatePageDisplay(cardId);
        this.updateNavigationButtons(cardId);
        
        if (config.onPageChange) {
            config.onPageChange(this.currentPages.get(cardId), config.totalPages);
        }
        
        console.log(`[Pagination] ${cardId}: Next page -> ${this.currentPages.get(cardId)}`);
    }

    /**
     * Go to previous page for a specific card
     * @param {string} cardId - Card identifier
     */
    prevPage(cardId) {
        const config = this.cardConfigs.get(cardId);
        const currentPage = this.currentPages.get(cardId);
        
        if (!config || currentPage <= 1) return;
        
        this.currentPages.set(cardId, currentPage - 1);
        this.updatePageDisplay(cardId);
        this.updateNavigationButtons(cardId);
        
        if (config.onPageChange) {
            config.onPageChange(this.currentPages.get(cardId), config.totalPages);
        }
        
        console.log(`[Pagination] ${cardId}: Previous page -> ${this.currentPages.get(cardId)}`);
    }

    /**
     * Go to specific page for a card
     * @param {string} cardId - Card identifier
     * @param {number} pageNumber - Page number to go to
     */
    goToPage(cardId, pageNumber) {
        const config = this.cardConfigs.get(cardId);
        
        if (!config || pageNumber < 1 || pageNumber > config.totalPages) return;
        
        this.currentPages.set(cardId, pageNumber);
        this.updatePageDisplay(cardId);
        this.updateNavigationButtons(cardId);
        
        if (config.onPageChange) {
            config.onPageChange(pageNumber, config.totalPages);
        }
        
        console.log(`[Pagination] ${cardId}: Go to page ${pageNumber}`);
    }

    /**
     * Update page display (show/hide items)
     * @param {string} cardId - Card identifier
     */
    updatePageDisplay(cardId) {
        const config = this.cardConfigs.get(cardId);
        const currentPage = this.currentPages.get(cardId);
        
        if (!config) return;
        
        const startIndex = (currentPage - 1) * config.itemsPerPage;
        const endIndex = startIndex + config.itemsPerPage;
        
        // Hide all items first
        config.items.forEach((item, index) => {
            const element = typeof item === 'string' ? document.querySelector(item) : item;
            if (element) {
                element.style.display = 'none';
            }
        });
        
        // Show current page items
        for (let i = startIndex; i < endIndex && i < config.items.length; i++) {
            const element = typeof config.items[i] === 'string' 
                ? document.querySelector(config.items[i]) 
                : config.items[i];
            if (element) {
                element.style.display = '';
            }
        }
        
        // Update page indicator
        this.updatePageIndicator(cardId);
    }

    /**
     * Update page indicator text
     * @param {string} cardId - Card identifier
     */
    updatePageIndicator(cardId) {
        const config = this.cardConfigs.get(cardId);
        const currentPage = this.currentPages.get(cardId);
        
        if (!config || !config.pageIndicatorSelector) return;
        
        const indicator = document.querySelector(config.pageIndicatorSelector);
        if (indicator) {
            indicator.textContent = `Page ${currentPage} of ${config.totalPages}`;
        }
    }

    /**
     * Update navigation button states
     * @param {string} cardId - Card identifier
     */
    updateNavigationButtons(cardId) {
        const config = this.cardConfigs.get(cardId);
        const currentPage = this.currentPages.get(cardId);
        
        if (!config) return;
        
        // Previous button
        if (config.prevButtonSelector) {
            const prevBtn = document.querySelector(config.prevButtonSelector);
            if (prevBtn) {
                if (currentPage <= 1) {
                    prevBtn.style.opacity = '0';
                    prevBtn.style.pointerEvents = 'none';
                } else {
                    prevBtn.style.opacity = '1';
                    prevBtn.style.pointerEvents = 'auto';
                }
            }
        }
        
        // Next button
        if (config.nextButtonSelector) {
            const nextBtn = document.querySelector(config.nextButtonSelector);
            if (nextBtn) {
                if (currentPage >= config.totalPages) {
                    nextBtn.style.opacity = '0';
                    nextBtn.style.pointerEvents = 'none';
                } else {
                    nextBtn.style.opacity = '1';
                    nextBtn.style.pointerEvents = 'auto';
                }
            }
        }
    }

    /**
     * Get current page for a card
     * @param {string} cardId - Card identifier
     * @returns {number} Current page number
     */
    getCurrentPage(cardId) {
        return this.currentPages.get(cardId) || 1;
    }

    /**
     * Get total pages for a card
     * @param {string} cardId - Card identifier
     * @returns {number} Total number of pages
     */
    getTotalPages(cardId) {
        const config = this.cardConfigs.get(cardId);
        return config ? config.totalPages : 0;
    }

    /**
     * Destroy pagination for a specific card
     * @param {string} cardId - Card identifier
     */
    destroyCard(cardId) {
        this.cardConfigs.delete(cardId);
        this.currentPages.delete(cardId);
        console.log(`[Pagination] Destroyed card: ${cardId}`);
    }

    /**
     * Destroy all pagination
     */
    destroy() {
        this.cardConfigs.clear();
        this.currentPages.clear();
        this.initialized = false;
        console.log('[Pagination] Generic pagination system destroyed');
    }
}

// Export the class for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CardPaginationController;
}

// Global instance for immediate use
window.CardPaginationController = CardPaginationController;
