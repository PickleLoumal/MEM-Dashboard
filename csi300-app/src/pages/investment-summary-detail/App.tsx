import React, { useEffect, useState, useCallback } from 'react';
import {
  RefreshCw,
  Printer,
  Share2,
  Shield,
  ArrowLeft
} from 'lucide-react';
import { GlobalNav } from '@shared/components/GlobalNav';
import { fetchInvestmentSummary, generateInvestmentSummary } from './api';
import { InvestmentSummary } from './types';
import { SummarySection } from './components/SummarySection';
import { SourcesBadge } from './components/SourcesSection';
import { BusinessOverviewSection, extractKeyMetrics, extractFiscalYear } from './components/BusinessOverviewSection';
import {
  PriceCard,
  KeyMetricsCard,
  RiskFactorsCard,
  SourceDocumentsCard
} from './components/Sidebar';
import { Tag, AiBadge } from './components/ui';
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
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
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
      document.title = `${nameParam} - Investment Summary`;
    }

    fetchInvestmentSummary(id)
      .then(summary => {
        log.info('Summary loaded', {
          company: summary.company_name,
          hasBusinessOverview: !!summary.business_overview
        });
        setData(summary);
        document.title = `${summary.company_name || nameParam || 'Company'} - Investment Summary`;
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
        setTimeout(() => setJustGenerated(false), 2000);
      } else {
        log.error('Generation returned failure status', { result });
        setGenerateError(result.message || 'Generation failed');
        setGenerating(false);
      }
    } catch (err) {
      log.error('Regenerate exception', { error: err });
      setGenerateError(err instanceof Error ? err.message : 'Generation failed, please retry');
      setGenerating(false);
    }
  }, [companyId]);

  const handlePrint = () => {
    window.print();
  };

  const handleShare = async () => {
    const url = window.location.href;
    if (navigator.share) {
      await navigator.share({
        title: data?.company_name ? `${data.company_name} - Investment Summary` : 'Investment Summary',
        url
      });
    } else {
      await navigator.clipboard.writeText(url);
      // Could add a toast notification here
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric', month: '2-digit', day: '2-digit'
    });
  };

  // Loading state
  if (loading) {
    const context = companyId ? {
      id: companyId,
      name: companyNameParam || 'Loading...',
      imSector: undefined
    } : undefined;

    return (
      <>
        <GlobalNav companyContext={context} />
        <div className="doc-layout">
          <div className="doc-loading">
            <div className="doc-loading-spinner"></div>
            <span>Loading investment analysis...</span>
          </div>
        </div>
      </>
    );
  }

  // Error state
  if (error || !data) {
    return (
      <>
        <GlobalNav />
        <div className="doc-layout">
          <div className="doc-error">
            <h3>Investment Summary Not Available</h3>
            <p>{error || 'No data found'}</p>
            <button onClick={handleBackToDetail} className="doc-error-btn">
              <ArrowLeft size={14} />
              Back to Company
            </button>
          </div>
        </div>
      </>
    );
  }

  // Extract metrics for sidebar
  const keyMetrics = extractKeyMetrics(data.business_overview);
  const fiscalYear = extractFiscalYear(data.business_overview);

  return (
    <>
      <GlobalNav companyContext={{
        id: companyId!,
        name: data.company_name,
        imSector: data.im_sector
      }} />

      <div className={`doc-layout ${mounted ? 'doc-layout-visible' : ''}`}>
        {/* Two Column Layout */}
        <div className="doc-grid animate-enter">

          {/* LEFT COLUMN: Main Document */}
          <div className="doc-main-column">

            {/* Actions Header (outside paper) */}
            <div className="doc-actions-header no-print">
              <div className="doc-live-indicator">
                <span className="doc-live-dot ai-dot"></span>
                <span>Live Analysis • v2.4</span>
              </div>
              <div className="doc-actions">
                <button
                  className="doc-action-btn"
                  onClick={handlePrint}
                  title="Print"
                >
                  <Printer size={16} />
                </button>
                <button
                  className="doc-action-btn"
                  onClick={handleShare}
                  title="Share"
                >
                  <Share2 size={16} />
                </button>
                <div className="doc-action-divider"></div>
                <button
                  className={`doc-regenerate-btn ${generating ? 'generating' : ''}`}
                  onClick={handleRegenerate}
                  disabled={generating}
                >
                  {generating ? (
                    <>
                      <span className="doc-btn-spinner"></span>
                      Generating...
                    </>
                  ) : (
                    <>
                      <RefreshCw size={11} />
                      Regenerate
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Progress/Error Bar */}
            {(generating || generateError) && (
              <div className="doc-generation-status no-print">
                {generating && (
                  <div className="doc-progress-bar">
                    <div className="doc-progress-bar-fill"></div>
                  </div>
                )}
                {generateError && (
                  <div className="doc-generation-error">
                    <span>⚠️ {generateError}</span>
                    <button onClick={() => setGenerateError(null)}>Dismiss</button>
                  </div>
                )}
              </div>
            )}

            {/* PAPER CARD */}
            <main className={`paper-card ${justGenerated ? 'just-generated' : ''}`}>

              {/* Document Header */}
              <header className="doc-header">
                <div className="doc-header-content">
                  <div className="doc-header-left">
                    <div className="doc-title-row">
                      <h1
                        className="doc-company-name"
                        onClick={handleBackToDetail}
                      >
                        {data.company_name}
                      </h1>
                      <span className="doc-ticker">{data.company_ticker || '-'}</span>
                    </div>

                    <div className="doc-tags-row">
                      {data.im_sector && <Tag text={data.im_sector} />}
                      {data.industry && data.industry !== data.im_sector && (
                        <Tag text={data.industry} variant="muted" />
                      )}
                      <SourcesBadge sources={data.sources} />
                    </div>
                  </div>
                </div>
              </header>

              {/* Document Body */}
              <div className="doc-body">

                {/* Business Overview / Executive Summary */}
                <BusinessOverviewSection content={data.business_overview} />

                {/* Other Sections */}
                <SummarySection
                  title="Business Performance"
                  content={data.business_performance}
                  id="businessPerformance"
                />
                <SummarySection
                  title="Industry Context"
                  content={data.industry_context}
                  id="industryContext"
                />
                <SummarySection
                  title="Financial Stability and Debt Levels"
                  content={data.financial_stability}
                  id="financialStability"
                />
                <SummarySection
                  title="Key Financials and Valuation"
                  content={data.key_financials_valuation}
                  id="keyFinancialsValuation"
                />
                <SummarySection
                  title="Big Trends and Big Events"
                  content={data.big_trends_events}
                  id="bigTrendsEvents"
                />
                <SummarySection
                  title="Customer Segments and Demand Trends"
                  content={data.customer_segments}
                  id="customerSegments"
                />
                <SummarySection
                  title="Competitive Landscape"
                  content={data.competitive_landscape}
                  id="competitiveLandscape"
                />
                {/* Risks and Anomalies moved to sidebar - RiskFactorsCard */}
                <SummarySection
                  title="Forecast and Outlook"
                  content={data.forecast_outlook}
                  id="forecastOutlook"
                />
                <SummarySection
                  title="Leading Investment Firms and Views"
                  content={data.investment_firms_views}
                  id="investmentFirmsViews"
                />
                <SummarySection
                  title="Recommended Action"
                  content={data.recommended_action_detail}
                  id="recommendedActionDetail"
                />
                <SummarySection
                  title="Industry Ratio and Metric Analysis"
                  content={data.industry_ratio_analysis}
                  id="industryRatioAnalysis"
                />
                {data.tariffs_supply_chain_risks && (
                  <SummarySection
                    title="Tariffs and Supply Chain Risks"
                    content={data.tariffs_supply_chain_risks}
                    id="tariffsSupplyChainRisks"
                  />
                )}
                <SummarySection
                  title="Key Takeaways"
                  content={data.key_takeaways}
                  id="keyTakeaways"
                />

                {/* Document Footer */}
                <footer className="doc-footer">
                  <div className="doc-footer-badge">
                    <Shield size={12} />
                    <span>Financial AIGC Engine</span>
                  </div>
                  <p className="doc-footer-disclaimer">
                    Disclaimer: AI-generated analysis based on public filings. Not financial advice.
                  </p>
                </footer>
              </div>
            </main>
          </div>

          {/* RIGHT COLUMN: Sticky Sidebar */}
          <aside className="doc-sidebar no-print">

            {/* Price & Consensus Card */}
            <PriceCard
              price={data.stock_price_previous_close}
              change={0}
              changePercent={0}
              reportDate={formatDate(data.report_date)}
              recommendation={data.recommended_action}
            />

            {/* Key Metrics Card */}
            {keyMetrics.length > 0 && (
              <KeyMetricsCard
                metrics={keyMetrics.map(m => ({
                  label: m.label,
                  value: m.value,
                  unit: m.unit,
                  yoy: m.yoy
                }))}
                fiscalYear={fiscalYear}
              />
            )}

            {/* Risk Factors Card */}
            <RiskFactorsCard risks={data.risks_anomalies} />

            {/* Source Documents Card */}
            <SourceDocumentsCard sources={data.sources} />
          </aside>
        </div>
      </div>
    </>
  );
}
