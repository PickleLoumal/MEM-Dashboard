/**
 * Company Modal Content Manager
 * Handles modal content generation for CSI300 company analysis
 * Based on MEM Dashboard navigation.js structure
 */

class CompanyModalManager {
    constructor() {
        this.initialized = false;
        this.companyData = null;
    }

    /**
     * Initialize modal manager with company data
     * @param {Object} companyData - Company information
     */
    init(companyData) {
        this.companyData = companyData;
        this.initialized = true;
    }

    /**
     * Generate Value Chain Analysis content
     * @returns {string} HTML content for value chain modal
     */
    generateValueChainContent() {
        if (!this.initialized || !this.companyData) {
            return this.getLoadingContent();
        }

        const companyName = this.companyData.name || 'Unknown Company';
        const industry = this.companyData.industry || 'Unknown Industry';
        const marketCap = this.formatCurrency(this.companyData.market_cap_usd);
        const peRatio = this.companyData.pe_ratio_trailing || 'N/A';

        // Special content for Kweichow Moutai Co Ltd
        if (companyName.includes('Kweichow Moutai') || companyName.includes('茅台')) {
            return this.getMoutaiValueChainContent(companyName, industry, marketCap, peRatio);
        }

        return this.getGenericValueChainContent(companyName, industry, marketCap, peRatio);
    }

    /**
     * Generate Industry Peers Comparison content
     * @returns {string} HTML content for peers comparison modal
     */
    generatePeersComparisonContent() {
        if (!this.initialized || !this.companyData) {
            return this.getLoadingContent();
        }

        const companyName = this.companyData.name || 'Unknown Company';
        const industry = this.companyData.industry || 'Unknown Industry';
        const imCode = this.companyData.im_code || 'N/A';

        // Special content for Kweichow Moutai Co Ltd
        if (companyName.includes('Kweichow Moutai') || companyName.includes('茅台')) {
            return this.getMoutaiPeersContent(companyName, industry, imCode);
        }

        return this.getGenericPeersContent(companyName, industry, imCode);
    }

    /**
     * Specific Value Chain content for Kweichow Moutai
     */
    getMoutaiValueChainContent(companyName, industry, marketCap, peRatio) {
        return `
            <div class="modal-section">
                <div class="modal-row">
                    <span class="modal-label">Company</span>
                    <span class="modal-value">${companyName}</span>
                </div>
                <div class="modal-row">
                    <span class="modal-label">Industry</span>
                    <span class="modal-value">${industry}</span>
                </div>
                <div class="modal-row">
                    <span class="modal-label">Market Cap</span>
                    <span class="modal-value">${marketCap}</span>
                </div>
                <div class="modal-row">
                    <span class="modal-label">P/E Ratio</span>
                    <span class="modal-value">${peRatio}</span>
                </div>
            </div>

            <div class="modal-breakdown">
                <h4 style="color: #1f2937; margin: 0 0 12px 0; font-size: 16px;">Primary Value Chain Activities</h4>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Inbound Logistics</span>
                    <span class="modal-sub-value">Premium sorghum sourcing from local farms</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Operations</span>
                    <span class="modal-sub-value">Traditional fermentation & distillation processes</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Outbound Logistics</span>
                    <span class="modal-sub-value">Controlled distribution network nationwide</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Marketing & Sales</span>
                    <span class="modal-sub-value">Premium brand positioning & cultural heritage</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Service</span>
                    <span class="modal-sub-value">Customer education & brand experience</span>
                </div>
            </div>

            <div class="modal-breakdown">
                <h4 style="color: #1f2937; margin: 0 0 12px 0; font-size: 16px;">Support Activities</h4>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Technology Development</span>
                    <span class="modal-sub-value">Traditional brewing technology & quality control</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Human Resources</span>
                    <span class="modal-sub-value">Master distillers & skilled craftsmen</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Procurement</span>
                    <span class="modal-sub-value">Long-term supplier relationships</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Infrastructure</span>
                    <span class="modal-sub-value">Corporate governance & financial management</span>
                </div>
            </div>

            <div class="modal-description">
                <strong>Value Chain Summary:</strong> Kweichow Moutai's integrated value chain leverages traditional 
                craftsmanship, premium raw materials, and controlled distribution to maintain market leadership. 
                The company's value creation spans from specialized sorghum sourcing through heritage-based production 
                to premium brand positioning, delivering exceptional margins and customer loyalty.
            </div>

            <div style="margin-top: 24px; text-align: center;">
                <button class="button button-secondary" id="viewDetailBtn" onclick="window.app.openValueChainDetail('${industry}')">
                    View Detail
                </button>
            </div>
        `;
    }

    /**
     * Specific Peers Comparison content for Kweichow Moutai
     */
    getMoutaiPeersContent(companyName, industry, imCode) {
        return `
            <div class="modal-section">
                <div class="modal-row">
                    <span class="modal-label">Company</span>
                    <span class="modal-value">${companyName}</span>
                </div>
                <div class="modal-row">
                    <span class="modal-label">Industry</span>
                    <span class="modal-value">${industry}</span>
                </div>
                <div class="modal-row">
                    <span class="modal-label">IM Code</span>
                    <span class="modal-value">${imCode}</span>
                </div>
            </div>

            <div class="modal-breakdown">
                <h4 style="color: #1f2937; margin: 0 0 12px 0; font-size: 16px;">Key Industry Peers</h4>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Wuliangye Yibin Co Ltd</span>
                    <span class="modal-sub-value">Premium baijiu competitor</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Jiannanchun Group Co Ltd</span>
                    <span class="modal-sub-value">Regional premium brand</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Luzhou Laojiao Co Ltd</span>
                    <span class="modal-sub-value">Traditional baijiu producer</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Shanxi Xinghuacun Fen Wine</span>
                    <span class="modal-sub-value">Northern China competitor</span>
                </div>
            </div>

            <div class="modal-breakdown">
                <h4 style="color: #1f2937; margin: 0 0 12px 0; font-size: 16px;">Competitive Position</h4>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Market Leadership</span>
                    <span class="modal-sub-value status-good">Strong - Premium market leader</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Brand Strength</span>
                    <span class="modal-sub-value status-good">Excellent - National prestige brand</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Pricing Power</span>
                    <span class="modal-sub-value status-good">Superior - Premium pricing sustained</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Distribution Network</span>
                    <span class="modal-sub-value status-good">Comprehensive - Nationwide coverage</span>
                </div>
            </div>

            <div class="modal-description">
                <strong>Competitive Advantage:</strong> Moutai maintains market leadership through premium brand positioning, 
                cultural significance, limited production capacity, and superior margins compared to peers. 
                The company benefits from strong pricing power and loyal customer base.
            </div>
        `;
    }

    /**
     * Generic Value Chain content for other companies
     */
    getGenericValueChainContent(companyName, industry, marketCap, peRatio) {
        return `
            <div class="modal-section">
                <div class="modal-row">
                    <span class="modal-label">Company</span>
                    <span class="modal-value">${companyName}</span>
                </div>
                <div class="modal-row">
                    <span class="modal-label">Industry</span>
                    <span class="modal-value">${industry}</span>
                </div>
                <div class="modal-row">
                    <span class="modal-label">Market Cap</span>
                    <span class="modal-value">${marketCap}</span>
                </div>
                <div class="modal-row">
                    <span class="modal-label">P/E Ratio</span>
                    <span class="modal-value">${peRatio}</span>
                </div>
            </div>

            <div class="modal-breakdown">
                <h4 style="color: #1f2937; margin: 0 0 12px 0; font-size: 16px;">Value Chain Stages</h4>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Upstream Activities</span>
                    <span class="modal-sub-value">Raw material sourcing and supplier relationships</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Core Operations</span>
                    <span class="modal-sub-value">Production processes and operational efficiency</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Midstream Processing</span>
                    <span class="modal-sub-value">Value-added processing and quality control</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Downstream Distribution</span>
                    <span class="modal-sub-value">Market channels and customer delivery</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">End Customer Markets</span>
                    <span class="modal-sub-value">Final consumption and customer satisfaction</span>
                </div>
            </div>

            <div class="modal-description">
                <strong>Value Chain Summary:</strong> Comprehensive analysis of ${companyName}'s value creation process 
                from upstream activities to end customer delivery. This summary provides an overview of key operational 
                stages, competitive positioning, and strategic value drivers within the ${industry} sector.
            </div>

            <div style="margin-top: 24px; text-align: center;">
                <button class="button button-secondary" id="viewDetailBtn" onclick="window.app.openValueChainDetail('${industry}')">
                    View Detail
                </button>
            </div>
        `;
    }

    /**
     * Generic Peers Comparison content for other companies
     */
    getGenericPeersContent(companyName, industry, imCode) {
        return `
            <div class="modal-section">
                <div class="modal-row">
                    <span class="modal-label">Company</span>
                    <span class="modal-value">${companyName}</span>
                </div>
                <div class="modal-row">
                    <span class="modal-label">Industry</span>
                    <span class="modal-value">${industry}</span>
                </div>
                <div class="modal-row">
                    <span class="modal-label">IM Code</span>
                    <span class="modal-value">${imCode}</span>
                </div>
            </div>

            <div class="modal-breakdown">
                <h4 style="color: #1f2937; margin: 0 0 12px 0; font-size: 16px;">Comparison Framework</h4>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Market Capitalization</span>
                    <span class="modal-sub-value">Size-based comparison</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Valuation Metrics</span>
                    <span class="modal-sub-value">P/E, P/B, EV/EBITDA ratios</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Profitability</span>
                    <span class="modal-sub-value">Margin analysis</span>
                </div>
                
                <div class="modal-sub-item">
                    <span class="modal-sub-label">Growth Metrics</span>
                    <span class="modal-sub-value">Revenue & earnings growth</span>
                </div>
            </div>

            <div class="modal-description">
                <strong>Industry Analysis:</strong> Comprehensive peer comparison for ${companyName} 
                within the ${industry} sector. Analysis should include key performance indicators 
                and competitive positioning metrics.
            </div>
        `;
    }

    /**
     * Loading content placeholder
     */
    getLoadingContent() {
        return `
            <div class="modal-section">
                <div style="text-align: center; padding: 20px; color: #6b7280;">
                    <p>Loading company data...</p>
                </div>
            </div>
        `;
    }

    /**
     * Format currency values
     * @param {string|number} value - Currency value to format
     * @returns {string} Formatted currency string
     */
    formatCurrency(value) {
        if (!value || value === 'N/A') return 'N/A';
        
        const numValue = parseFloat(value);
        if (isNaN(numValue)) return value;
        
        if (numValue >= 1e12) {
            return `$${(numValue / 1e12).toFixed(2)}T`;
        } else if (numValue >= 1e9) {
            return `$${(numValue / 1e9).toFixed(2)}B`;
        } else if (numValue >= 1e6) {
            return `$${(numValue / 1e6).toFixed(2)}M`;
        } else {
            return `$${numValue.toLocaleString()}`;
        }
    }
}

// Make CompanyModalManager available globally
window.CompanyModalManager = CompanyModalManager;

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CompanyModalManager;
}
