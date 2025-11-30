/**
 * Company Modal Content Manager
 * Handles modal content generation for CSI300 company analysis
 * Based on MEM Dashboard navigation.js structure
 */

/**
 * Helper function to get rank suffix
 * @param {number} rank - The rank number
 * @returns {string} The rank suffix (st, nd, rd, th)
 */
function getRankSuffix(rank) {
    if (rank % 100 >= 11 && rank % 100 <= 13) {
        return 'th';
    }
    switch (rank % 10) {
        case 1: return 'st';
        case 2: return 'nd';
        case 3: return 'rd';
        default: return 'th';
    }
}

class CompanyModalManager {
    constructor() {
        this.initialized = false;
        this.companyData = null;
    }

    /**
     * Get market position description based on percentile
     * @param {number} percentile - Top percentile (higher is better)
     * @returns {string} Market position description
     */
    getMarketPosition(percentile) {
        if (percentile >= 75) return 'Market Leader';
        if (percentile >= 50) return 'Mid-Tier';
        if (percentile >= 25) return 'Competitor';
        return 'Follower';
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
        const imSector = this.getCompanyImSector();
        const marketCap = this.formatCurrency(this.companyData.market_cap_usd);
        const peRatio = this.companyData.pe_ratio_trailing || 'N/A';

        // Special content for Kweichow Moutai Co Ltd
        if (companyName.includes('Kweichow Moutai') || companyName.includes('茅台')) {
            return this.getMoutaiValueChainContent(companyName, imSector, marketCap, peRatio);
        }

        return this.getGenericValueChainContent(companyName, imSector, marketCap, peRatio);
    }

    /**
     * Generate Industry Peers Comparison content
     * @returns {string} HTML content for peers comparison modal
     */
    generatePeersComparisonContent() {
        if (!this.initialized || !this.companyData) {
            return this.getLoadingContent();
        }

        // Return loading content and load real data asynchronously
        setTimeout(() => this.loadIndustryPeersData(), 100);
        
        return `
            <div class="modal-section">
                <div class="modal-row">
                    <span class="modal-label">Company</span>
                    <span class="modal-value">${this.companyData.name || 'Unknown Company'}</span>
                </div>
                <div class="modal-row">
                <span class="modal-label">Industry Matrix Sector</span>
                <span class="modal-value">${this.getCompanyImSector()}</span>
                </div>
            </div>
            <div id="peersComparisonData" style="margin-top: 20px;">
                <div style="text-align: center; padding: 20px;">
                    <div style="display: inline-block; width: 20px; height: 20px; border: 2px solid #f3f3f3; border-top: 2px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                    <p style="margin-top: 10px; color: #666;">Loading IM sector peers comparison...</p>
                </div>
            </div>
        `;
    }

    /**
     * Generate Industry Peers Comparison content asynchronously (optimized for smooth modal opening)
     * @returns {Promise<string>} HTML content for peers comparison modal
     */
    async generatePeersComparisonContentAsync() {
        if (!this.initialized || !this.companyData) {
            throw new Error('Company data not initialized');
        }

        try {
            const data = await window.csi300ApiClient.getIndustryPeersComparison(this.companyData.id);
            const imSector = data.industry || data.im_sector || this.getCompanyImSector();
            
            // Calculate ranking metrics
            const currentRank = data.target_company.rank;
            const totalCompanies = data.total_companies_in_industry;
            // Calculate percentile: what percentage of companies this company beats
            const percentileBeat = Math.round(((totalCompanies - currentRank) / (totalCompanies - 1)) * 100);
            const positionPercent = Math.round(((currentRank - 1) / (totalCompanies - 1)) * 100);
            
            // Determine rank color based on percentile
            let rankColor = '#e74c3c'; // Red for bottom tier
            if (percentileBeat >= 75) rankColor = '#27ae60'; // Green for top 25%
            else if (percentileBeat >= 50) rankColor = '#f39c12'; // Orange for middle tier
            else if (percentileBeat >= 25) rankColor = '#f1c40f'; // Yellow for lower-middle tier
            
            // Create comparison table HTML
            let html = `
                <div class="modal-section">
                    <div class="modal-row">
                        <span class="modal-label">Company</span>
                        <span class="modal-value">${this.companyData.name || 'Unknown Company'}</span>
                    </div>
                    <div class="modal-row">
                        <span class="modal-label">Industry Matrix Sector</span>
                        <span class="modal-value">${imSector}</span>
                    </div>
                    
                    <!-- Industry Matrix Sector Ranking Indicator - Bar Chart Style -->
                    <div style="margin-top: 20px; padding: 15px 0;">
                        <!-- Professional Ranking Display -->
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <!-- Rank Badge -->
                                <div style="background: ${rankColor}; color: white; padding: 4px 10px; border-radius: 4px; font-weight: 600; font-size: 13px;">
                                    #${currentRank} / ${totalCompanies}
                                </div>
                                <!-- Market Position -->
                                <div>
                                    <span style="font-weight: 600; color: #2c3e50; font-size: 14px;">Industry Matrix Sector Ranking</span>
                                    <span style="font-size: 12px; color: #6c757d; margin-left: 8px;">${this.getMarketPosition(percentileBeat)} Position</span>
                                </div>
                            </div>
                            <!-- Percentile Display -->
                            <div style="text-align: right;">
                                <span style="font-size: 11px; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">Percentile</span>
                                <div style="font-size: 14px; font-weight: 600; color: ${rankColor};">${percentileBeat === 100 ? 'Market Leader' : percentileBeat === 0 ? 'Last Position' : percentileBeat < 50 ? `Bottom ${percentileBeat}%` : `Top ${100 - percentileBeat}%`}</div>
                            </div>
                        </div>
                        
                        <!-- Bar Chart Ranking Indicator with Smooth Transition -->
                        <div style="display: flex; align-items: end; height: 35px; width: 100%;">
                            ${Array.from({length: totalCompanies}, (_, index) => {
                                const rank = totalCompanies - index; // Reverse order: best rank on the right
                                const isCurrentCompany = rank === currentRank;
                                const distanceFromCurrent = Math.abs(rank - currentRank);
                                
                                // Calculate height with smooth transition
                                let barHeight;
                                if (isCurrentCompany) {
                                    barHeight = 35; // Peak height
                                } else if (distanceFromCurrent === 1) {
                                    barHeight = 22; // Adjacent bars
                                } else if (distanceFromCurrent === 2) {
                                    barHeight = 14; // Second-level neighbors
                                } else {
                                    barHeight = 8; // Base height
                                }
                                
                                // Calculate color with transition
                                let barColor;
                                if (isCurrentCompany) {
                                    barColor = rankColor;
                                } else if (distanceFromCurrent === 1) {
                                    barColor = `${rankColor}80`; // 50% opacity
                                } else if (distanceFromCurrent === 2) {
                                    barColor = `${rankColor}40`; // 25% opacity
                                } else {
                                    barColor = '#e0e0e0';
                                }
                                
                                // Calculate width to fill the container
                                const barWidth = `calc((100% - ${(totalCompanies - 1) * 2}px) / ${totalCompanies})`;
                                
                                return `<div style="width: ${barWidth}; height: ${barHeight}px; background: ${barColor}; border-radius: ${isCurrentCompany ? '4px' : '2px'}; margin-right: ${index < totalCompanies - 1 ? '2px' : '0'}; transition: all 0.4s ease; ${isCurrentCompany ? 'box-shadow: 0 2px 12px rgba(0,0,0,0.15);' : ''}"></div>`;
                            }).join('')}
                        </div>
                        
                        <!-- Scale labels -->
                        <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 11px; color: #95a5a6; font-weight: 500;">
                            <span>Followers</span>
                            <span>Mid-Tier</span>
                            <span>Market Leader</span>
                        </div>
                    </div>
                </div>
                
                <!-- Company Data Rows -->
                <div class="modal-section" style="margin-top: 20px;">
                    <!-- Header Labels -->
                    <div style="display: grid; grid-template-columns: 1fr 90px 80px 80px 90px; gap: 15px; padding: 10px 0; border-bottom: 1px solid rgba(0,0,0,0.08); font-weight: 600; color: #495057; font-size: 12px; align-items: center;">
                        <div>Company</div>
                        <div style="text-align: right;">Market Cap</div>
                        <div style="text-align: right;">P/E Ratio</div>
                        <div style="text-align: right;">ROE (%)</div>
                        <div style="text-align: right;">OM (% TTM)</div>
                    </div>
            `;
            
            let subtitleAdded = false; // Track if subtitle has been added
            data.comparison_data.forEach((company, index) => {
                const isCurrentCompany = company.is_current_company;
                
                // Generate ranking badge
                let rankBadge = '';
                if (isCurrentCompany) {
                    // For current company, show real rank
                    const rank = company.rank;
                    rankBadge = `<span style="background: #666; color: white; font-size: 10px; font-weight: 600; padding: 3px 8px; border-radius: 3px; line-height: 1; margin-right: 8px;">${rank}${getRankSuffix(rank)}</span>`;
                } else {
                    // For peer companies, show 1st, 2nd, 3rd
                    const rank = company.rank;
                    const rankings = ['1st', '2nd', '3rd'];
                    const colors = ['#e74c3c', '#f39c12', '#27ae60']; // Red, Orange, Green
                    
                    if (rank <= 3) {
                        rankBadge = `<span style="background: ${colors[rank-1]}; color: white; font-size: 10px; font-weight: 600; padding: 3px 8px; border-radius: 3px; line-height: 1; margin-right: 8px;">${rankings[rank-1]}</span>`;
                    }
                }
                
                html += `
                    <div style="padding: 15px 0; border-bottom: 1px solid rgba(0,0,0,0.08);">
                        <!-- First row: Company name and financial data -->
                        <div style="display: grid; grid-template-columns: 1fr 90px 80px 80px 90px; gap: 15px; align-items: center; margin-bottom: 8px;">
                            <strong style="color: #2c3e50; font-size: 14px;">${company.name}</strong>
                            <span style="text-align: right; font-weight: 500; color: #2c3e50; font-size: 13px;">${company.market_cap_display || '-'}</span>
                            <span style="text-align: right; font-weight: 500; color: #2c3e50; font-size: 13px;">${company.pe_ratio_display || '-'}</span>
                            <span style="text-align: right; font-weight: 500; color: #2c3e50; font-size: 13px;">${company.roe_display || '-'}</span>
                            <span style="text-align: right; font-weight: 500; color: #2c3e50; font-size: 13px;">${company.operating_margin_display || '-'}</span>
                        </div>
                        
                        <!-- Second row: Rank badge and ticker -->
                        <div style="display: flex; align-items: center; gap: 8px;">
                            ${rankBadge}
                            <span style="color: #7f8c8d; font-weight: 500; font-size: 13px;">${company.ticker}</span>
                            ${isCurrentCompany ? '<span style="color: #2196f3; font-size: 11px; font-weight: 600; margin-left: 10px;"><span style="display: inline-block; width: 6px; height: 6px; background: #2196f3; border-radius: 50%; margin-right: 6px; box-shadow: 0 0 8px rgba(33, 150, 243, 0.4), 0 0 3px rgba(33, 150, 243, 0.6);"></span>Current Company</span>' : ''}
                        </div>
                    </div>
                `;
                
                // Add "Top 3 in sector" subtitle after the first Current Company only
                if (isCurrentCompany && !subtitleAdded) {
                    html += `
                        <div style="margin: 15px 0 10px 0; padding: 8px 0; color: #666; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                            Top 3 in ${imSector} sector
                        </div>
                    `;
                    subtitleAdded = true;
                }
            });
            
            html += `
                </div>
            `;
            
            return html;
            
        } catch (error) {
            throw new Error(`Failed to load peer comparison data: ${error.message}`);
        }
    }

    /**
     * Load industry peers comparison data asynchronously
     */
    async loadIndustryPeersData() {
        try {
            const data = await window.csi300ApiClient.getIndustryPeersComparison(this.companyData.id);
            const comparisonContainer = document.getElementById('peersComparisonData');
            const imSector = data.industry || data.im_sector || this.getCompanyImSector();
            
            if (!comparisonContainer) return;
            
            // Create comparison table HTML
            let html = `
                <div style="margin-bottom: 15px; padding: 10px; background-color: #f8f9fa; border-radius: 4px;">
                    <strong>Industry Matrix Sector:</strong> ${imSector}<br>
                    <small style="color: #666;">Comparing with top ${data.total_peers_found} companies by market capitalization</small>
                </div>
                
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; border: 1px solid #dee2e6; border-radius: 4px; overflow: hidden; font-size: 14px;">
                        <thead>
                            <tr style="background-color: #f8f9fa;">
                                <th style="padding: 12px 8px; text-align: left; border-bottom: 2px solid #dee2e6; font-weight: 600; color: #495057;">Company</th>
                                <th style="padding: 12px 8px; text-align: left; border-bottom: 2px solid #dee2e6; font-weight: 600; color: #495057;">Market Cap</th>
                                <th style="padding: 12px 8px; text-align: left; border-bottom: 2px solid #dee2e6; font-weight: 600; color: #495057;">P/E Ratio</th>
                                <th style="padding: 12px 8px; text-align: left; border-bottom: 2px solid #dee2e6; font-weight: 600; color: #495057;">ROE (%)</th>
                                <th style="padding: 12px 8px; text-align: left; border-bottom: 2px solid #dee2e6; font-weight: 600; color: #495057;">EPS Growth (%)</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            data.comparison_data.forEach((company, index) => {
                const isCurrentCompany = company.is_current_company;
                const rowStyle = isCurrentCompany ? 'background-color: #e3f2fd;' : '';
                
                // Generate ranking badge for table view
                let rankBadge = '';
                if (isCurrentCompany) {
                    const rank = company.rank;
                    rankBadge = `<span style="background: #666; color: white; font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 3px; margin-left: 8px;">${rank}${getRankSuffix(rank)}</span>`;
                } else {
                    const rank = company.rank;
                    const rankings = ['1st', '2nd', '3rd'];
                    const colors = ['#e74c3c', '#f39c12', '#27ae60'];
                    
                    if (rank <= 3) {
                        rankBadge = `<span style="background: ${colors[rank-1]}; color: white; font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 3px; margin-left: 8px;">${rankings[rank-1]}</span>`;
                    }
                }
                
                html += `
                    <tr style="${rowStyle} border-bottom: 1px solid #dee2e6;">
                        <td style="padding: 12px 8px; vertical-align: middle;">
                            <div>
                                <!-- Company name on first line -->
                                <div style="margin-bottom: 6px;">
                                    <strong style="font-size: 14px;">${company.name}</strong>
                                </div>
                                <!-- Rank badge and ticker on second line -->
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    ${rankBadge}
                                    <span style="color: #666; font-size: 13px;">${company.ticker}</span>
                                    ${isCurrentCompany ? '<span style="color: #1976d2; font-size: 11px; font-weight: 600; margin-left: 8px;">● Current Company</span>' : ''}
                                </div>
                            </div>
                        </td>
                        <td style="padding: 12px 8px; vertical-align: middle; text-align: right; font-weight: 500;">${company.market_cap_display || '-'}</td>
                        <td style="padding: 12px 8px; vertical-align: middle; text-align: right; font-weight: 500;">${company.pe_ratio_display || '-'}</td>
                        <td style="padding: 12px 8px; vertical-align: middle; text-align: right; font-weight: 500;">${company.roe_display || '-'}</td>
                        <td style="padding: 12px 8px; vertical-align: middle; text-align: right; font-weight: 500;">${company.eps_growth_display || '-'}</td>
                    </tr>
                `;
            });
            
            html += `
                        </tbody>
                    </table>
                </div>
                
                <div style="margin-top: 15px; padding: 10px; background-color: #f0f8ff; border-radius: 4px; border-left: 4px solid #2196f3;">
                    <strong>Analysis Framework:</strong>
                    <ul style="margin: 5px 0 0 20px; color: #666;">
                        <li><strong>Market Capitalization:</strong> Size-based comparison within IM sector</li>
                        <li><strong>P/E Ratio:</strong> Valuation relative to earnings</li>
                        <li><strong>ROE:</strong> Return on Equity - profitability efficiency</li>
                        <li><strong>EPS Growth:</strong> Earnings per share growth rate</li>
                    </ul>
                </div>
            `;
            
            comparisonContainer.innerHTML = html;
            
        } catch (error) {
            console.error('Error loading industry peers comparison:', error);
            const comparisonContainer = document.getElementById('peersComparisonData');
            if (comparisonContainer) {
                comparisonContainer.innerHTML = `
                    <div style="text-align: center; padding: 20px; color: #dc3545;">
                        <p><strong>Unable to load IM sector peers comparison</strong></p>
                        <small>${error.message}</small>
                        <br><br>
                        <button onclick="window.app.modalManager.loadIndustryPeersData()" 
                                style="padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
                            Retry
                        </button>
                    </div>
                `;
            }
        }
    }

    /**
     * Specific Value Chain content for Kweichow Moutai
     */
    getMoutaiValueChainContent(companyName, imSector, marketCap, peRatio) {
        const sectorDisplay = imSector || 'Unknown Industry Matrix Sector';
        return `
            <div class="modal-section">
                <div class="modal-row">
                    <span class="modal-label">Company</span>
                    <span class="modal-value">${companyName}</span>
                </div>
                <div class="modal-row">
                    <span class="modal-label">Industry Matrix Sector</span>
                    <span class="modal-value">${sectorDisplay}</span>
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
                <button class="button button-secondary" id="viewDetailBtn" onclick="window.app.openValueChainDetail('${imSector || ''}')">
                    View Detail
                </button>
            </div>
        `;
    }

    /**
     * Specific Peers Comparison content for Kweichow Moutai
     */
    getMoutaiPeersContent(companyName, industry, imCode) {
        const sectorDisplay = industry || imCode || 'Unknown Industry Matrix Sector';
        return `
            <div class="modal-section">
                <div class="modal-row">
                    <span class="modal-label">Company</span>
                    <span class="modal-value">${companyName}</span>
                </div>
                <div class="modal-row">
                    <span class="modal-label">Industry Matrix Sector</span>
                    <span class="modal-value">${sectorDisplay}</span>
                </div>
            </div>

            <div class="modal-breakdown">
                <h4 style="color: #1f2937; margin: 0 0 12px 0; font-size: 16px;">Key Industry Matrix Sector Peers</h4>
                
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
        const sectorDisplay = industry || 'Unknown Industry Matrix Sector';
        return `
            <div class="modal-section">
                <div class="modal-row">
                    <span class="modal-label">Company</span>
                    <span class="modal-value">${companyName}</span>
                </div>
                <div class="modal-row">
                    <span class="modal-label">Industry Matrix Sector</span>
                    <span class="modal-value">${sectorDisplay}</span>
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
                stages, competitive positioning, and strategic value drivers within the ${sectorDisplay} sector.
            </div>

            <div style="margin-top: 24px; text-align: center;">
                <button class="button button-secondary" id="viewDetailBtn" onclick="window.app.openValueChainDetail('${industry || ''}')">
                    View Detail
                </button>
            </div>
        `;
    }

    /**
     * Generic Peers Comparison content for other companies
     */
    getGenericPeersContent(companyName, industry, imCode) {
        const sectorDisplay = industry || imCode || 'Unknown Industry Matrix Sector';
        return `
            <div class="modal-section">
                <div class="modal-row">
                    <span class="modal-label">Company</span>
                    <span class="modal-value">${companyName}</span>
                </div>
                <div class="modal-row">
                    <span class="modal-label">Industry Matrix Sector</span>
                    <span class="modal-value">${sectorDisplay}</span>
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

    /**
     * Retrieve company's IM sector with legacy fallback
     * @param {Object} company - Optional company override
     * @returns {string} Display-ready IM sector
     */
    getCompanyImSector(company = null) {
        const source = company || this.companyData;
        if (!source) return 'Unknown Industry Matrix Sector';
        return source.im_sector || source.industry || source.im_code || 'Unknown Industry Matrix Sector';
    }
}

// Make CompanyModalManager available globally
window.CompanyModalManager = CompanyModalManager;

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CompanyModalManager;
}
