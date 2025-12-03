import React, { useEffect, useState } from 'react';
import { GlobalNav } from '@shared/components/GlobalNav';
import { fetchInvestmentSummary } from './api';
import { InvestmentSummary } from './types';
import { SummarySection } from './components/SummarySection';
import { SourcesSection } from './components/SourcesSection';
import { BusinessOverviewSection } from './components/BusinessOverviewSection';
import '@shared/styles/main.css';
import './styles.css';

export default function App() {
  const [data, setData] = useState<InvestmentSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [companyId, setCompanyId] = useState<string | null>(null);
  const [companyNameParam, setCompanyNameParam] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');
    setCompanyId(id);
    
    if (!id) {
      setError('Company ID not provided');
      setLoading(false);
      return;
    }

    const nameParam = params.get('company');
    setCompanyNameParam(nameParam);

    if (nameParam) {
        document.title = `${nameParam} - Investment Summary - Chinese Stock Dashboard`;
    }

    fetchInvestmentSummary(id)
      .then(summary => {
        setData(summary);
        document.title = `${summary.company_name || nameParam || 'Company'} - Investment Summary - Chinese Stock Dashboard`;
      })
      .catch(err => {
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
                <h1>Investment Summary</h1>
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
                        <span className="basic-info-value">{data.im_sector || data.industry || '-'}</span>
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
