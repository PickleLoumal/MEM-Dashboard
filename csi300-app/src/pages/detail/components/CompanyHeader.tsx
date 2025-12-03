import { CompanyDetail } from '../types';

interface CompanyHeaderProps {
  company: CompanyDetail;
}

export function CompanyHeader({ company }: CompanyHeaderProps) {
  const imSector = company.im_sector || company.im_code || '';
  const industry = company.industry || '';
  const tags: string[] = [];
  
  if (imSector) tags.push(imSector);
  if (industry && industry !== imSector) tags.push(industry);

  const formatDate = (dateString?: string) => {
    if (!dateString) return '-';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  const formatNumber = (num?: number, decimals = 0) => {
    if (num === undefined || num === null) return '-';
    return num.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  };

  const metaItems = [
    { label: 'Currency', value: company.currency },
    { label: 'Last Trade Date', value: formatDate(company.last_trade_date) },
    { label: 'Current Price', value: formatNumber(company.price_local_currency, 2) },
    { label: 'Market Cap (USD M)', value: formatNumber(company.market_cap_usd, 0) },
  ].filter(item => item.value !== undefined && item.value !== null);

  return (
    <div className="company-header" style={{
        padding: '12px 0 24px',
        textAlign: 'left',
        marginBottom: 0,
        borderBottom: '1px solid var(--app-border)',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px'
    }}>
      <div className="company-header-main" style={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'spaceBetween',
          gap: '28px'
      }}>
        <div className="company-title-block" style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
            flex: '1 1 260px'
        }}>
          <div className="company-title-row" style={{
              display: 'flex',
              flexWrap: 'wrap',
              alignItems: 'baseline',
              gap: '16px'
          }}>
            <h1 className="company-name" style={{
                fontSize: '34px',
                fontWeight: 700,
                color: 'var(--app-heading)',
                margin: 0,
                letterSpacing: '-0.01em'
            }}>
              {company.name || 'Unknown Company'}
            </h1>
            <span className="company-ticker" style={{
                fontSize: '13px',
                fontWeight: 600,
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
                padding: '6px 12px',
                borderRadius: '999px',
                border: '1px solid var(--app-border)',
                color: 'var(--app-text-muted)'
            }}>
              {company.ticker || 'N/A'}
            </span>
          </div>
          {tags.length > 0 && (
            <div className="company-tag-row" style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '10px'
            }}>
              {tags.map((tag, i) => (
                <span key={i} className="company-tag" style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    padding: '6px 12px',
                    borderRadius: '999px',
                    border: '1px solid var(--app-border)',
                    color: 'var(--app-text-muted)',
                    fontSize: '13px',
                    fontWeight: 500
                }}>
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
        
        {metaItems.length > 0 && (
          <div className="company-meta-list" style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
              gap: '12px 24px',
              minWidth: '220px'
          }}>
            {metaItems.map((item, i) => (
              <div key={i} className="company-meta-item" style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px'
              }}>
                <span className="company-meta-label" style={{
                    fontSize: '12px',
                    letterSpacing: '0.08em',
                    textTransform: 'uppercase',
                    color: 'var(--app-text-muted)'
                }}>
                  {item.label}
                </span>
                <span className="company-meta-value" style={{
                    fontSize: '16px',
                    fontWeight: 600,
                    color: 'var(--app-heading)'
                }}>
                  {item.value}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

