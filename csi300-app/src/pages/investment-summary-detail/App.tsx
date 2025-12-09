import React, { useEffect, useState, useCallback } from 'react';
import { GlobalNav } from '@shared/components/GlobalNav';
import { fetchInvestmentSummary, generateInvestmentSummary } from './api';
import { InvestmentSummary } from './types';
import { SummarySection } from './components/SummarySection';
import { SourcesSection, SourcesBadge } from './components/SourcesSection';
import { BusinessOverviewSection } from './components/BusinessOverviewSection';
import { logger } from '@shared/lib/logger';
import '@shared/styles/main.css';
import './styles.css';

export default function App() {
  const [data, setData] = useState<InvestmentSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [companyId, setCompanyId] = useState<string | null>(null);
  const [companyNameParam, setCompanyNameParam] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);
  const [justGenerated, setJustGenerated] = useState(false);

  useEffect(() => {
    const log = logger.startTrace();
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');
    setCompanyId(id);
    
    if (!id) {
      const msg = 'Company ID not provided in URL';
      log.warn(msg);
      setError('Company ID not provided');
      setLoading(false);
      return;
    }

    const nameParam = params.get('company');
    setCompanyNameParam(nameParam);

    log.info('App mounted', { id, nameParam });

    if (nameParam) {
        document.title = `${nameParam} - Investment Summary - Chinese Stock Dashboard`;
    }

    fetchInvestmentSummary(id)
      .then(summary => {
        log.info('Summary loaded', { 
          company: summary.company_name, 
          hasBusinessOverview: !!summary.business_overview 
        });
        setData(summary);
        document.title = `${summary.company_name || nameParam || 'Company'} - Investment Summary - Chinese Stock Dashboard`;
      })
      .catch(err => {
        log.error('Failed to load summary', { error: err });
        setError(err instanceof Error ? err.message : 'Failed to load investment summary');
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const handleBackToDetail = () => {
    if (companyId) {
      window.location.href = `/detail.html?id=${companyId}`;
    } else {
      window.location.href = '/browser.html';
    }
  };

  const handleRegenerate = useCallback(async () => {
    if (!companyId) return;
    
    const log = logger.startTrace().withContext({ companyId, action: 'regenerate' });
    log.info('User clicked regenerate');
    
    setGenerating(true);
    setGenerateError(null);
    setJustGenerated(false);
    
    try {
      const result = await generateInvestmentSummary(companyId);
      
      if (result.status === 'success') {
        log.info('Generation success, refreshing data');
        const updatedSummary = await fetchInvestmentSummary(companyId);
        setData(updatedSummary);
        setGenerateError(null);
        setGenerating(false);
        setJustGenerated(true);
        // Clear the animation state after animation completes
        setTimeout(() => setJustGenerated(false), 2000);
      } else {
        log.error('Generation returned failure status', { result });
        setGenerateError(result.message || '生成失败');
        setGenerating(false);
      }
    } catch (err) {
      log.error('Regenerate exception', { error: err });
      setGenerateError(err instanceof Error ? err.message : '生成失败，请重试');
      setGenerating(false);
    }
  }, [companyId]);

  const getActionClass = (action: string) => {
      if (!action || action === '-') return 'neutral';
      return action.toLowerCase().replace(/\s+/g, '_'); 
  };

  const formatDate = (dateString: string) => {
      if (!dateString) return '-';
      return new Date(dateString).toLocaleDateString('en-US', {
          year: 'numeric', month: '2-digit', day: '2-digit'
      });
  };

  if (loading) {
    const context = companyId ? {
        id: companyId,
        name: companyNameParam || 'Loading...',
        imSector: undefined
    } : undefined;

    return (
      <>
        <GlobalNav companyContext={context} />
        <div className="container app-shell">
           <div className="loading-spinner">
               <div className="spinner"></div>
           </div>
        </div>
      </>
    );
  }

  if (error || !data) {
    return (
      <>
        <GlobalNav />
        <div className="container app-shell">
           <div className="error-message">
              <h3>Investment Summary Not Available</h3>
              <p>{error || 'No data found'}</p>
           </div>
        </div>
      </>
    );
  }

  // Shimmer skeleton component for generating state
  const ShimmerValue = () => (
    <div className="shimmer-container">
      <div className="shimmer-line"></div>
    </div>
  );

  // Reveal value component for just-generated state
  const RevealValue = ({ children }: { children: React.ReactNode }) => (
    <div className={`reveal-container ${justGenerated ? 'animate' : ''}`}>
      <span className="reveal-content">{children}</span>
      {justGenerated && <div className="laser-scan"></div>}
    </div>
  );

  return (
      <>
        <GlobalNav companyContext={{
            id: companyId!,
            name: data.company_name,
            imSector: data.im_sector
        }} />
        <div className="container app-shell">
            <div className="investment-summary-header">
                <div className="header-top-row">
                    <div className="page-type-badge">Investment Summary</div>
                    <button 
                        className={`regenerate-btn ${generating ? 'generating' : ''}`}
                        onClick={handleRegenerate}
                        disabled={generating}
                        title="Regenerate investment summary using AI"
                    >
                        {generating ? (
                            <>
                                <span className="btn-spinner"></span>
                                Generating...
                            </>
                        ) : (
                            <>
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15" />
                                </svg>
                                Regenerate
                            </>
                        )}
                    </button>
                </div>

                {/* Progress Bar */}
                {(generating || generateError) && (
                    <div className="generation-status">
                        {generating && <div className="progress-bar"><div className="progress-bar-fill"></div></div>}
                        {generateError && (
                            <div className="generation-error">
                                <span>⚠️ {generateError}</span>
                                <button onClick={() => setGenerateError(null)}>Dismiss</button>
                            </div>
                        )}
                    </div>
                )}

                <div className="company-header-main">
                    <div className="company-title-block">
                        <div className="company-title-row">
                            <h1 className="company-name-clickable" onClick={handleBackToDetail}>
                                {data.company_name}
                            </h1>
                            <span className="company-ticker">{data.company_ticker || '-'}</span>
                        </div>
                        
                        <div className="company-tag-row">
                            {data.im_sector && <span className="company-tag">{data.im_sector}</span>}
                            {data.industry && data.industry !== data.im_sector && (
                                <span className="company-tag">{data.industry}</span>
                            )}
                            <SourcesBadge sources={data.sources} className="header-source-badge" />
                        </div>
                    </div>

                    <div className="company-meta-grid">
                        <div className="company-meta-item">
                            <span className="company-meta-label">Report Date</span>
                            {generating ? (
                                <ShimmerValue />
                            ) : (
                                <RevealValue>
                                    <span className="company-meta-value">{formatDate(data.report_date)}</span>
                                </RevealValue>
                            )}
                        </div>
                        <div className="company-meta-item">
                            <span className="company-meta-label">Recommendation</span>
                            {generating ? (
                                <ShimmerValue />
                            ) : (
                                <RevealValue>
                                    <span className={`recommended-action ${getActionClass(data.recommended_action)}`}>
                                        {data.recommended_action || '-'}
                                    </span>
                                </RevealValue>
                            )}
                        </div>
                        <div className="company-meta-item">
                            <span className="company-meta-label">Current Price</span>
                            {generating ? (
                                <ShimmerValue />
                            ) : (
                                <RevealValue>
                                    <span className="company-meta-value">{data.stock_price_previous_close || '-'}</span>
                                </RevealValue>
                            )}
                        </div>
                        <div className="company-meta-item">
                            <span className="company-meta-label">Market Cap (USD M)</span>
                            {generating ? (
                                <ShimmerValue />
                            ) : (
                                <RevealValue>
                                    <span className="company-meta-value">{data.market_cap_display || '-'}</span>
                                </RevealValue>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            <BusinessOverviewSection content={data.business_overview} />
            <SummarySection title="Business Performance" content={data.business_performance} id="businessPerformance" />
            <SummarySection title="Industry Context" content={data.industry_context} id="industryContext" />
            <SummarySection title="Financial Stability and Debt Levels" content={data.financial_stability} id="financialStability" />
            <SummarySection title="Key Financials and Valuation" content={data.key_financials_valuation} id="keyFinancialsValuation" />
            <SummarySection title="Big Trends and Big Events" content={data.big_trends_events} id="bigTrendsEvents" />
            <SummarySection title="Customer Segments and Demand Trends" content={data.customer_segments} id="customerSegments" />
            <SummarySection title="Competitive Landscape" content={data.competitive_landscape} id="competitiveLandscape" />
            <SummarySection title="Risks and Anomalies" content={data.risks_anomalies} id="risksAnomalies" />
            <SummarySection title="Forecast and Outlook" content={data.forecast_outlook} id="forecastOutlook" />
            <SummarySection title="Leading Investment Firms and Views" content={data.investment_firms_views} id="investmentFirmsViews" />
            <SummarySection title="Recommended Action" content={data.recommended_action_detail} id="recommendedActionDetail" />
            <SummarySection title="Industry Ratio and Metric Analysis" content={data.industry_ratio_analysis} id="industryRatioAnalysis" />
             {data.tariffs_supply_chain_risks && (
                <SummarySection title="Tariffs and Supply Chain Risks" content={data.tariffs_supply_chain_risks} id="tariffsSupplyChainRisks" />
            )}
            <SummarySection title="Key Takeaways" content={data.key_takeaways} id="keyTakeaways" />
            
            <SourcesSection sources={data.sources} />
        </div>
      </>
  );
}
