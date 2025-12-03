import { DetailSection, FieldRow } from './DetailSection';
import { CompanyDetail } from '../types';
import { formatNumber } from '../utils';

interface SectionProps {
  company: CompanyDetail;
}

export function DividendSection({ company }: SectionProps) {
  return (
    <DetailSection title="Dividend Information">
      <FieldRow 
        label="Dividend Yield (FY0)" 
        value={company.dividend_yield_fy0 ? `${formatNumber(company.dividend_yield_fy0 * 100, 2)}%` : '-'} 
      />
      <FieldRow 
        label="Dividend Payout Ratio" 
        value={company.dividend_payout_ratio ? `${formatNumber(company.dividend_payout_ratio * 100, 2)}%` : '-'} 
      />
      <FieldRow label="Dividend (Local Currency)" value={formatNumber(company.dividend_local_currency, 2)} />
      <FieldRow 
        label="Dividend 3yr CAGR" 
        value={company.dividend_3yr_cagr ? `${formatNumber(company.dividend_3yr_cagr * 100, 2)}%` : '-'} 
      />
      <FieldRow 
        label="Dividend 5yr CAGR" 
        value={company.dividend_5yr_cagr ? `${formatNumber(company.dividend_5yr_cagr * 100, 2)}%` : '-'} 
      />
      <FieldRow 
        label="Dividend 10yr CAGR" 
        value={company.dividend_10yr_cagr ? `${formatNumber(company.dividend_10yr_cagr * 100, 2)}%` : '-'} 
      />
    </DetailSection>
  );
}

export function RiskSection({ company }: SectionProps) {
  const altmanMfg = company.altman_z_score_manufacturing;
  const altmanMfgClass = altmanMfg && altmanMfg > 2.99 ? 'positive' : altmanMfg && altmanMfg < 1.81 ? 'negative' : '';

  const altmanNonMfg = company.altman_z_score_non_manufacturing;
  const altmanNonMfgClass = altmanNonMfg && altmanNonMfg > 2.6 ? 'positive' : altmanNonMfg && altmanNonMfg < 1.1 ? 'negative' : '';

  return (
    <DetailSection title="Risk Assessment (Altman Z-Score)">
      <FieldRow 
        label="Z-Score (Manufacturing)" 
        value={formatNumber(altmanMfg, 2)} 
        valueClass={altmanMfgClass}
      />
      <FieldRow 
        label="Z-Score (Non-Manufacturing)" 
        value={formatNumber(altmanNonMfg, 2)} 
        valueClass={altmanNonMfgClass}
      />
    </DetailSection>
  );
}

