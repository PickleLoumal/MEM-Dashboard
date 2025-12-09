import React from 'react';
import { logger } from '@shared/lib/logger';

interface DivisionData {
  name: string;
  description: string;
  sales_percentage: string | null;
  gross_profit_margin: string | null;
  profit_percentage: string | null;
}

interface ParsedBusinessOverview {
  company_name: string;
  fiscal_year: string | null;
  fiscal_year_end: string | null;
  key_metrics: {
    total_revenue?: string;
    operating_income?: string;
    net_income?: string;
    net_interest_margin?: string;
    operating_margin?: string;
    [key: string]: string | undefined;
  };
  divisions: DivisionData[];
}

interface BusinessOverviewData {
  raw_text: string;
  parsed: ParsedBusinessOverview | null;
}

interface BusinessOverviewSectionProps {
  content: string | undefined;
}

// 尝试解析 JSON，如果失败则返回 null
function tryParseJSON(content: string): BusinessOverviewData | null {
  if (!content) return null;
  try {
    const data = JSON.parse(content);
    // 验证是否符合预期结构
    if (typeof data === 'object' && 'raw_text' in data) {
      return data as BusinessOverviewData;
    }
    
    logger.warn('JSON parsed but missing raw_text or not an object', { dataKeys: Object.keys(data || {}) });
    
    // 兼容性处理：如果缺失 raw_text 但有 key_metrics，我们构造一个
    if (typeof data === 'object' && 'key_metrics' in data) {
        return {
            raw_text: '', // 缺失 raw_text
            parsed: data as ParsedBusinessOverview
        };
    }
    return null;
  } catch (e) {
    return null;
  }
}

// 格式化指标名称
function formatMetricName(key: string): string {
  const nameMap: Record<string, string> = {
    total_revenue: 'Total Revenue / Sales',
    operating_income: 'Operating Income',
    net_income: 'Net Income',
    net_interest_margin: 'Net Interest Margin (NIM)',
    operating_margin: 'Operating Margin',
  };
  return nameMap[key] || key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

export const BusinessOverviewSection: React.FC<BusinessOverviewSectionProps> = ({ content }) => {
  if (!content) {
      logger.warn('BusinessOverviewSection received empty content');
      return null;
  }

  const jsonData = tryParseJSON(content);

  // 如果不是 JSON 格式，使用原有的纯文本渲染
  if (!jsonData) {
    logger.info('Rendering Business Overview as plain text', { length: content.length });
    return (
      <div className="investment-summary-section" id="businessOverview">
        <div className="section-header">
          <h2>Business Overview</h2>
        </div>
        <div className="section-content">
          <p>{content}</p>
        </div>
      </div>
    );
  }

  const { raw_text, parsed } = jsonData;
  logger.info('Rendering Business Overview from JSON', { hasParsed: !!parsed, fiscalYear: parsed?.fiscal_year });

  // 如果解析失败，显示原始文本
  if (!parsed) {
    return (
      <div className="investment-summary-section" id="businessOverview">
        <div className="section-header">
          <h2>Business Overview</h2>
        </div>
        <div className="section-content">
          <p>{raw_text}</p>
        </div>
      </div>
    );
  }

  const hasKeyMetrics = Object.keys(parsed.key_metrics).length > 0;
  const hasDivisions = parsed.divisions.length > 0;
  const hasDivisionMetrics = hasDivisions && parsed.divisions.some(
    d => d.sales_percentage || d.gross_profit_margin || d.profit_percentage
  );

  return (
    <div className="investment-summary-section" id="businessOverview">
      <div className="section-header"><h2>Business Overview</h2></div>
      <div className="section-content">
        {/* 原始描述文本 */}
        <p className="business-overview-text">{raw_text}</p>

        {/* 关键财务指标表格 */}
        {hasKeyMetrics && (
          <div className="business-overview-metrics">
            <h4 className="metrics-title">
              Key Financial Metrics
              {parsed.fiscal_year && ` (FY${parsed.fiscal_year})`}
            </h4>
            <table className="metrics-table">
              <thead>
                <tr>
                  <th>Metric</th>
                  <th>Value</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(parsed.key_metrics).map(([key, value]) => (
                  value && (
                    <tr key={key}>
                      <td>{formatMetricName(key)}</td>
                      <td className="metric-value">{value}</td>
                    </tr>
                  )
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* 业务部门贡献表格 */}
        {hasDivisionMetrics && (
          <div className="business-overview-divisions">
            <h4 className="metrics-title">Division Breakdown</h4>
            <table className="divisions-table">
              <thead>
                <tr>
                  <th>Division</th>
                  <th>% of Sales</th>
                  <th>Gross Margin</th>
                  <th>% of Profits</th>
                </tr>
              </thead>
              <tbody>
                {parsed.divisions.map((div, idx) => (
                  <tr key={idx}>
                    <td>
                      <strong>{div.name}</strong>
                      {div.description && (
                        <span className="division-desc"> - {div.description}</span>
                      )}
                    </td>
                    <td className="metric-value">{div.sales_percentage || '-'}</td>
                    <td className="metric-value">{div.gross_profit_margin || '-'}</td>
                    <td className="metric-value">{div.profit_percentage || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

