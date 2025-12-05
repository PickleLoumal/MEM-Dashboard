import React, { useEffect, useState, useCallback } from 'react';
import { GlobalNav } from '@shared/components/GlobalNav';
import { fetchInvestmentSummary, generateInvestmentSummary } from './api';
import { InvestmentSummary } from './types';
import { SummarySection } from './components/SummarySection';
import { SourcesSection } from './components/SourcesSection';
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
      // In dev mode, this works via vite rewrite. In prod, it works via simple link.
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
    
    try {
      const result = await generateInvestmentSummary(companyId);
      
      if (result.status === 'success') {
        log.info('Generation success, refreshing data');
        // 重新获取更新后的数据
        const updatedSummary = await fetchInvestmentSummary(companyId);
        setData(updatedSummary);
        setGenerateError(null);
      } else {
        log.error('Generation returned failure status', { result });
        setGenerateError(result.message || '生成失败');
      }
    } catch (err) {
      log.error('Regenerate exception', { error: err });
      setGenerateError(err instanceof Error ? err.message : '生成失败，请重试');
    } finally {
      setGenerating(false);
    }
  }, [companyId]);

  const getActionClass = (action: string) => {
      if (!action || action === '-') return 'neutral';
      // Match the CSS classes: strong_buy, strong_sell
      return action.toLowerCase().replace(/\s+/g, '_'); 
  };

  const formatDate = (dateString: string) => {
      if (!dateString) return '-';
      return new Date(dateString).toLocaleDateString('en-US', {
          year: 'numeric', month: '2-digit', day: '2-digit'
      });
  };

  if (loading) {
    // Use companyNameParam if available during loading
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

  return (
      <>
        <GlobalNav companyContext={{
            id: companyId!,
            name: data.company_name,
            imSector: data.im_sector
        }} />
        <div className="container app-shell">
            <div className="investment-summary-header">
                <div className="header-title-row">
                <h1>Investment Summary</h1>
                    <button 
                        className={`regenerate-btn ${generating ? 'generating' : ''}`}
                        onClick={handleRegenerate}
                        disabled={generating}
                        title="Regenerate investment summary using AI"
                    >
                        {generating ? (
                            <>
                                <span className="regenerate-spinner"></span>
                                Regenerating...
                            </>
                        ) : (
                            <>
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15" />
                                </svg>
                                Regenerate
                            </>
                        )}
                    </button>
                </div>
                {generateError && (
                    <div className="generate-error">
                        ⚠️ {generateError}
                    </div>
                )}
                <div className="company-name-link">
                    <button className="company-name-clickable" onClick={handleBackToDetail}>
                        {data.company_name}
                    </button>
                </div>

                <div className="investment-summary-basic-info">
                    <div className="basic-info-item">
                        <span className="basic-info-label">Date</span>
                        <span className="basic-info-value">{formatDate(data.report_date)}</span>
                    </div>
                    <div className="basic-info-item">
                        <span className="basic-info-label">Stock Price (Previous Close)</span>
                        <span className="basic-info-value">
                            {data.stock_price_previous_close ? `CNY ${data.stock_price_previous_close}` : '-'}
                        </span>
                    </div>
                     <div className="basic-info-item">
                        <span className="basic-info-label">Market Cap</span>
                        <span className="basic-info-value">{data.market_cap_display || '-'}</span>
                    </div>
                    <div className="basic-info-item">
                        <span className="basic-info-label">Recommended Action</span>
                        <span className="basic-info-value">
                             <span className={`recommended-action ${getActionClass(data.recommended_action)}`}>
                                 {data.recommended_action || '-'}
                             </span>
                        </span>
                    </div>
                    <div className="basic-info-item">
                        <span className="basic-info-label">Industry</span>
                        <span className="basic-info-value">{data.industry || data.im_sector || '-'}</span>
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
