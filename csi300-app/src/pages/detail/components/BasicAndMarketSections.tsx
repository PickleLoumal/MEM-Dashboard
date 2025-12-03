import { DetailSection, FieldRow } from './DetailSection';
import { CompanyDetail } from '../types';
import { formatNumber, formatDate, getImSectorDisplay } from '../utils';

interface SectionProps {
  company: CompanyDetail;
}

export function BasicInfoSection({ company }: SectionProps) {
  return (
    <DetailSection title="Basic Information">
      <FieldRow label="Industry Matrix Sector" value={getImSectorDisplay(company)} />
      <FieldRow label="Industry" value={company.industry} />
      {company.sub_industry && <FieldRow label="Secondary Industry" value={company.sub_industry} />}
      <FieldRow label="GICS Industry" value={company.gics_industry} />
      <FieldRow label="Currency" value={company.currency} />
      <FieldRow label="Last Trade Date" value={formatDate(company.last_trade_date)} />
    </DetailSection>
  );
}

export function MarketDataSection({ company }: SectionProps) {
  const returnValue = company.total_return_2018_to_2025;
  const returnClass = returnValue && returnValue > 0 ? 'positive' : returnValue && returnValue < 0 ? 'negative' : '';

  return (
    <DetailSection title="Market Data">
      <FieldRow label="Current Price" value={formatNumber(company.price_local_currency, 2)} />
      <FieldRow label="Previous Close" value={formatNumber(company.previous_close, 2)} />
      <FieldRow label="Market Cap (Local)" value={formatNumber(company.market_cap_local, 0)} />
      <FieldRow label="Market Cap (USD)" value={formatNumber(company.market_cap_usd, 0)} />
      <FieldRow label="52-Week High" value={formatNumber(company.price_52w_high, 2)} />
      <FieldRow label="52-Week Low" value={formatNumber(company.price_52w_low, 2)} />
      <FieldRow 
        label="Total Return 2018-2025" 
        value={returnValue ? `${formatNumber(returnValue, 2)}%` : '-'} 
        valueClass={returnClass}
      />
    </DetailSection>
  );
}

