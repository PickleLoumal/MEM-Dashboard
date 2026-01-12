import React, { useEffect, useState } from 'react';
import { GlobalNav } from '@shared/components/GlobalNav';
import { CompanyDetail } from './types';
import { fetchCompanyDetail } from './api';
import { CompanyHeader } from './components/CompanyHeader';
import { BasicInfoSection, MarketDataSection } from './components/BasicAndMarketSections';
import { FinancialMetricsSection, EPSSection, CashFlowSection } from './components/FinancialSections';
import { DebtSection, RatioSection, LiquiditySection } from './components/DebtAndRatioSections';
import { DividendSection, RiskSection } from './components/DividendAndRiskSections';
import { ValueChainModal } from './components/ValueChainModal';
import { PeersComparisonModal } from './components/PeersComparisonModal';
import { DetailSection } from './components/DetailSection';
import '@shared/styles/main.css';

// Add some specific styles for the detail page
import './styles.css';

export default function App() {
  const [company, setCompany] = useState<CompanyDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [isValueChainOpen, setIsValueChainOpen] = useState(false);
  const [isPeersOpen, setIsPeersOpen] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');

    if (!id) {
      setError('No company ID provided');
      setLoading(false);
      return;
    }

    fetchCompanyDetail(id)
      .then(data => {
        setCompany(data);
        document.title = `${data.name || 'Company'} - Chinese Stock Dashboard`;
      })
      .catch(err => {
        setError(err instanceof Error ? err.message : 'Failed to load company details');
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const handleInvestmentSummary = () => {
    if (!company) return;
    window.location.href = `/investment-summary-detail.html?company=${encodeURIComponent(company.name)}&id=${company.id}`;
  };

  if (loading) {
    return (
      <>
        <GlobalNav companyContext={company ? {
            id: String(company.id),
            name: company.name,
            imSector: company.im_sector
        } : undefined} />
        <div className="container app-shell">
          <div className="loading" style={{ textAlign: 'center', padding: '48px', color: 'var(--app-text-muted)' }}>
            <p>Loading company details...</p>
          </div>
        </div>
      </>
    );
  }

  if (error || !company) {
    return (
      <>
        <GlobalNav companyContext={company ? {
            id: String(company.id),
            name: company.name,
            imSector: company.im_sector
        } : undefined} />
        <div className="container app-shell">
          <div className="error app-notice" style={{ marginBottom: '16px' }}>
            {error || 'Company not found'}
          </div>
        </div>
      </>
    );
  }

  const hasEPSData = company.eps_trailing || company.eps_actual_fy0 || company.eps_forecast_fy1 || company.eps_growth_percent;
  const hasCashFlowData = company.ebitda_fy0 || company.ebitda_fy_minus_1 || company.cash_flow_operations_fy0 || company.cash_flow_operations_fy_minus_1;
  const hasLiquidityData = company.current_ratio || company.quick_ratio;
  const hasDebtData = company.interest_expense_fy0 || company.effective_interest_rate || company.interest_coverage_ratio || company.debt_to_total_assets || company.debt_to_equity;
  const hasDividendData = company.dividend_yield_fy0 || company.dividend_payout_ratio || company.dividend_local_currency || company.dividend_3yr_cagr || company.dividend_5yr_cagr || company.dividend_10yr_cagr;
  const hasRiskData = company.altman_z_score_manufacturing || company.altman_z_score_non_manufacturing;

  return (
    <>
      <GlobalNav companyContext={company ? {
          id: String(company.id),
          name: company.name,
          imSector: company.im_sector
      } : undefined} />
      <div className="container app-shell" style={{ padding: '80px 24px 48px', maxWidth: '1536px', margin: '0 auto' }}>

        <CompanyHeader company={company} />

        {company.business_description && (
          <div className="company-description-wrapper" style={{ marginBottom: '32px', padding: '24px 0' }}>
            <div className="company-description-section" style={{
                background: 'var(--app-surface)',
                borderRadius: 'var(--app-radius-md)',
                padding: '22px 24px 24px',
                boxShadow: 'var(--app-shadow-subtle)'
            }}>
              <h3 className="company-description-header" style={{
                  fontSize: '16px',
                  fontWeight: 600,
                  color: 'var(--app-heading)',
                  margin: '0 0 16px 0'
              }}>Company Description</h3>
              <p className="company-description-text" style={{
                  lineHeight: 1.6,
                  color: 'var(--app-text)',
                  margin: 0,
                  fontSize: '14px'
              }}>{company.business_description}</p>
            </div>
          </div>
        )}

        <div className="company-actions-section app-actions" style={{
            margin: '24px 0 32px',
            display: 'flex',
            flexWrap: 'wrap',
            gap: '12px',
            justifyContent: 'flex-start'
        }}>
          <button className="button button-primary app-button app-button--primary" onClick={() => setIsValueChainOpen(true)}>Value Chain Analysis</button>
          <button className="button button-primary app-button app-button--primary" onClick={handleInvestmentSummary}>Investment Summary</button>
          <button className="button button-primary app-button app-button--primary" onClick={() => setIsPeersOpen(true)}>Industry Matrix Sector Peers Comparison</button>
        </div>

        <div className="details-grid" style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
            gap: '28px',
            alignItems: 'stretch'
        }}>
          <BasicInfoSection company={company} />
          <MarketDataSection company={company} />
          <FinancialMetricsSection company={company} />
          {hasEPSData && <EPSSection company={company} />}
          {hasCashFlowData && <CashFlowSection company={company} />}
          <RatioSection company={company} />
          {hasLiquidityData && <LiquiditySection company={company} />}
          {hasDebtData && <DebtSection company={company} />}
          {hasDividendData && <DividendSection company={company} />}
          {hasRiskData && <RiskSection company={company} />}
        </div>

        <ValueChainModal
            isOpen={isValueChainOpen}
            onClose={() => setIsValueChainOpen(false)}
            company={company}
        />

        <PeersComparisonModal
            isOpen={isPeersOpen}
            onClose={() => setIsPeersOpen(false)}
            company={company}
        />

      </div>
    </>
  );
}

