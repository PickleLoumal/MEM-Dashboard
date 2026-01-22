import { DetailSection, FieldRow } from './DetailSection';
import { CompanyDetail } from '../types';
import { formatNumber } from '../utils';

interface SectionProps {
  company: CompanyDetail;
}

export function DebtSection({ company }: SectionProps) {
  const interestCoverage = company.interest_coverage_ratio;
  const interestCoverageClass = interestCoverage && interestCoverage > 5 ? 'positive' : interestCoverage && interestCoverage < 2 ? 'negative' : '';

  const debtToAssets = company.debt_to_total_assets;
  const debtToAssetsClass = debtToAssets && debtToAssets > 0.6 ? 'negative' : debtToAssets && debtToAssets < 0.3 ? 'positive' : '';

  const debtToEquity = company.debt_to_equity;
  const debtToEquityClass = debtToEquity && debtToEquity > 1 ? 'negative' : debtToEquity && debtToEquity < 0.5 ? 'positive' : '';

  return (
    <DetailSection title="Debt & Interest">
      <FieldRow label="Interest Expense (FY0)" value={formatNumber(company.interest_expense_fy0, 0)} />
      <FieldRow 
        label="Effective Interest Rate" 
        value={company.effective_interest_rate ? `${formatNumber(company.effective_interest_rate * 100, 2)}%` : '-'} 
      />
      <FieldRow 
        label="Interest Coverage Ratio" 
        value={formatNumber(interestCoverage, 2)} 
        valueClass={interestCoverageClass}
      />
      <FieldRow 
        label="Debt to Total Assets" 
        value={debtToAssets ? `${formatNumber(debtToAssets * 100, 2)}%` : '-'} 
        valueClass={debtToAssetsClass}
      />
      <FieldRow 
        label="Debt to Equity" 
        value={debtToEquity ? `${formatNumber(debtToEquity * 100, 2)}%` : '-'} 
        valueClass={debtToEquityClass}
      />
    </DetailSection>
  );
}

export function RatioSection({ company }: SectionProps) {
  // Note: roe_trailing, roa_trailing, operating_margin_trailing are already in percentage format
  // e.g., 10.599 means 10.599%, NOT 0.10599
  const roe = company.roe_trailing;
  const roeClass = roe && roe > 15 ? 'positive' : roe && roe < 5 ? 'negative' : '';

  const roa = company.roa_trailing;
  const roaClass = roa && roa > 5 ? 'positive' : roa && roa < 2 ? 'negative' : '';

  const opMargin = company.operating_margin_trailing;
  const opMarginClass = opMargin && opMargin > 10 ? 'positive' : opMargin && opMargin < 5 ? 'negative' : '';

  return (
    <DetailSection title="Valuation & Profitability Ratios">
      <FieldRow label="P/E Ratio (TTM)" value={formatNumber(company.pe_ratio_trailing, 2)} />
      <FieldRow label="P/E Ratio (Consensus)" value={formatNumber(company.pe_ratio_consensus, 2)} />
      <FieldRow label="PEG Ratio" value={formatNumber(company.peg_ratio, 2)} />
      <FieldRow 
        label="ROE (TTM)" 
        value={roe ? `${formatNumber(roe, 2)}%` : '-'} 
        valueClass={roeClass}
      />
      <FieldRow 
        label="ROA (TTM)" 
        value={roa ? `${formatNumber(roa, 2)}%` : '-'} 
        valueClass={roaClass}
      />
      <FieldRow 
        label="Operating Margin (TTM)" 
        value={opMargin ? `${formatNumber(opMargin, 2)}%` : '-'} 
        valueClass={opMarginClass}
      />
      <FieldRow label="Operating Profits/Share" value={formatNumber(company.operating_profits_per_share, 2)} />
      <FieldRow label="Operating Leverage" value={formatNumber(company.operating_leverage, 2)} />
    </DetailSection>
  );
}

export function LiquiditySection({ company }: SectionProps) {
  const currentRatio = company.current_ratio;
  const currentRatioClass = currentRatio && currentRatio > 1.5 ? 'positive' : currentRatio && currentRatio < 1 ? 'negative' : '';

  const quickRatio = company.quick_ratio;
  const quickRatioClass = quickRatio && quickRatio > 1 ? 'positive' : quickRatio && quickRatio < 0.5 ? 'negative' : '';

  return (
    <DetailSection title="Liquidity Ratios">
      <FieldRow 
        label="Current Ratio" 
        value={formatNumber(currentRatio, 2)} 
        valueClass={currentRatioClass}
      />
      <FieldRow 
        label="Quick Ratio" 
        value={formatNumber(quickRatio, 2)} 
        valueClass={quickRatioClass}
      />
    </DetailSection>
  );
}

