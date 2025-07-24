// Modal Content Manager for MEM Dashboard - Hybrid Solution
// Hybrid content manager - Database + JSON backup + Cache

class ModalContentManager {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api/content/modal-content/';
        this.cache = new Map();
        this.isLoading = false;
        this.fallbackData = null;
        this.cacheTimeout = 30 * 60 * 1000; // 30 minutes cache
        
        console.log('🚀 ModalContentManager initializing...');
        console.log('🔗 API Base URL:', this.apiBaseUrl);
    }
    
    /**
     * Initialize content manager
     */
    async initialize() {
        try {
            console.log('🔄 Initializing content manager...');
            
            // First try to load static JSON as backup
            await this.loadFallbackData();
            
            // Then try to load database data
            try {
                await this.loadDatabaseContent();
                console.log('✅ Database content loaded successfully');
            } catch (error) {
                console.warn('⚠️ Database content loading failed, will use backup data:', error);
            }
            
            console.log('✅ Content manager initialization complete');
            
        } catch (error) {
            console.error('❌ Content manager initialization failed:', error);
            // Even if initialization fails, ensure there's emergency data
            this.fallbackData = this.getEmergencyData();
        }
    }
    
    /**
     * Load backup data
     */
    async loadFallbackData() {
        try {
            const response = await fetch('/src/assets/data/modal-content-fallback.json');
            if (response.ok) {
                this.fallbackData = await response.json();
                console.log('📄 Backup data loaded successfully');
            } else {
                console.warn('⚠️ Backup data loading failed');
                this.fallbackData = this.getEmergencyData();
            }
        } catch (error) {
            console.error('❌ Backup data loading error:', error);
            this.fallbackData = this.getEmergencyData();
        }
    }
    
    /**
     * Load database content
     */
    async loadDatabaseContent() {
        if (this.isLoading) return;
        this.isLoading = true;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}all_content/`);
            if (response.ok) {
                const data = await response.json();
                
                // Update cache
                this.cache.clear();
                Object.entries(data).forEach(([modalId, content]) => {
                    this.cache.set(modalId, {
                        ...content,
                        timestamp: Date.now()
                    });
                });
                
                console.log(`📊 Database content loaded successfully: ${Object.keys(data).length} items`);
                return data;
            } else {
                throw new Error(`API response error: ${response.status}`);
            }
        } catch (error) {
            console.error('❌ Database content loading failed:', error);
            throw error;
        } finally {
            this.isLoading = false;
        }
    }
    
    /**
     * Get content for specified modal
     */
    async getContent(modalId) {
        console.log(`📋 Getting content: ${modalId}`);
        console.log(`🔗 Full API URL: ${this.apiBaseUrl}by_modal_id/?modal_id=${modalId}`);
        
        // Check cache
        const cached = this.cache.get(modalId);
        if (cached && (Date.now() - cached.timestamp) < this.cacheTimeout) {
            console.log(`📋 Getting content from cache: ${modalId}`);
            return cached;
        }
        
        // Try to get from API
        try {
            const apiUrl = `${this.apiBaseUrl}by_modal_id/?modal_id=${modalId}`;
            console.log(`🌐 Trying to get from API: ${apiUrl}`);
            
            const response = await fetch(apiUrl);
            console.log(`📡 API response status: ${response.status}`);
            
            if (response.ok) {
                const data = await response.json();
                console.log(`📊 API response data:`, data);
                
                // Update cache
                this.cache.set(modalId, {
                    ...data,
                    timestamp: Date.now()
                });
                
                console.log(`📊 Getting content from API: ${modalId}`);
                return data;
            } else {
                throw new Error(`API response error: ${response.status}`);
            }
        } catch (error) {
            console.warn(`⚠️ API retrieval failed, using backup data: ${modalId}`, error);
            
            // Get from backup data
            if (this.fallbackData && this.fallbackData[modalId]) {
                console.log(`📄 Getting content from backup data: ${modalId}`);
                return this.fallbackData[modalId];
            }
            
            // Return default content
            console.log(`🚨 Returning default content: ${modalId}`);
            return this.getDefaultContent(modalId);
        }
    }
    
    /**
     * Get default content
     */
    getDefaultContent(modalId) {
        return {
            title: 'Content Loading...',
            description: 'Content is loading, please wait...',
            importance: 'This content is currently loading.',
            source: 'System default',
            breakdown: [],
            category: 'Default'
        };
    }
    
    /**
     * Get emergency data
     */
    getEmergencyData() {
        return {
            'motor-vehicles': {
                title: 'Motor Vehicles and Parts',
                description: 'This category encompasses consumer expenditures on motor vehicles and related parts and accessories.',
                importance: 'Motor vehicles and parts represent a major consumer spending category.',
                source: 'Emergency backup data',
                breakdown: [
                    { label: 'New motor vehicles', value: '$406.24B (54.2%)' },
                    { label: 'Net purchases of used motor vehicles', value: '$214.86B (28.6%)' },
                    { label: 'Motor vehicle parts and accessories', value: '$129.04B (17.2%)' }
                ],
                category: 'Durable Goods'
            }
        };
    }
    
    /**
     * Refresh content cache
     */
    async refreshCache() {
        console.log('🔄 Refreshing content cache...');
        this.cache.clear();
        await this.loadDatabaseContent();
    }
    
    /**
     * Clear cache for specified content
     */
    clearCache(modalId) {
        if (modalId) {
            this.cache.delete(modalId);
        } else {
            this.cache.clear();
        }
    }
}

// Expose class to global scope
window.ModalContentManager = ModalContentManager;
