import { DetailSection, FieldRow } from './DetailSection';
import { CompanyDetail } from '../types';
import { formatNumber } from '../utils';

interface SectionProps {
  company: CompanyDetail;
}

export function FinancialMetricsSection({ company }: SectionProps) {
  return (
    <DetailSection title="Financial Metrics">
      <FieldRow label="Total Revenue" value={formatNumber(company.total_revenue_local, 0)} />
      <FieldRow label="LTM Revenue" value={formatNumber(company.ltm_revenue_local, 0)} />
      <FieldRow label="NTM Revenue" value={formatNumber(company.ntm_revenue_local, 0)} />
      <FieldRow label="Net Profits (FY0)" value={formatNumber(company.net_profits_fy0, 0)} />
      <FieldRow label="Total Assets" value={formatNumber(company.total_assets_local, 0)} />
      <FieldRow label="Net Assets" value={formatNumber(company.net_assets_local, 0)} />
      <FieldRow label="Total Debt" value={formatNumber(company.total_debt_local, 0)} />
      <FieldRow label="Asset Turnover (LTM)" value={formatNumber(company.asset_turnover_ltm, 2)} />
    </DetailSection>
  );
}

export function EPSSection({ company }: SectionProps) {
  const epsGrowth = company.eps_growth_percent;
  const epsGrowthClass = epsGrowth && epsGrowth > 0 ? 'positive' : epsGrowth && epsGrowth < 0 ? 'negative' : '';

  return (
    <DetailSection title="Earnings Per Share">
      <FieldRow label="EPS (Trailing)" value={formatNumber(company.eps_trailing, 2)} />
      <FieldRow label="EPS Actual (FY0)" value={formatNumber(company.eps_actual_fy0, 2)} />
      <FieldRow label="EPS Forecast (FY1)" value={formatNumber(company.eps_forecast_fy1, 2)} />
      <FieldRow 
        label="EPS Growth (%)" 
        value={epsGrowth ? `${formatNumber(epsGrowth * 100, 2)}%` : '-'} 
        valueClass={epsGrowthClass}
      />
    </DetailSection>
  );
}

export function CashFlowSection({ company }: SectionProps) {
  return (
    <DetailSection title="Cash Flow & EBITDA">
      <FieldRow label="EBITDA (FY0)" value={formatNumber(company.ebitda_fy0, 0)} />
      <FieldRow label="EBITDA (FY-1)" value={formatNumber(company.ebitda_fy_minus_1, 0)} />
      <FieldRow label="Cash Flow Ops (FY0)" value={formatNumber(company.cash_flow_operations_fy0, 0)} />
      <FieldRow label="Cash Flow Ops (FY-1)" value={formatNumber(company.cash_flow_operations_fy_minus_1, 0)} />
    </DetailSection>
  );
}

