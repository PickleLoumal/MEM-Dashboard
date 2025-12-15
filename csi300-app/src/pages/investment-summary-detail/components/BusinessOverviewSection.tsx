import React from 'react';
import { logger } from '@shared/lib/logger';
import { SectionHeader, SegmentBar, AiBadge } from './ui';

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
  } catch {
    return null;
  }
}

// Parse percentage string to number
function parsePercentage(val: string | null): number {
  if (!val) return 0;
  const num = parseFloat(val.replace('%', ''));
  return isNaN(num) ? 0 : num;
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
      <section className="doc-section">
        <SectionHeader title="Executive Summary" showAiBadge />
        <article className="doc-section-content doc-prose">
          <p>
            <span className="doc-drop-cap">{content.charAt(0)}</span>
            {content.slice(1)}
          </p>
        </article>
      </section>
    );
  }

  const { raw_text, parsed } = jsonData;
  logger.info('Rendering Business Overview from JSON', { hasParsed: !!parsed, fiscalYear: parsed?.fiscal_year });

  // 如果解析失败，显示原始文本
  if (!parsed) {
    return (
      <section className="doc-section">
        <SectionHeader title="Executive Summary" showAiBadge />
        <article className="doc-section-content doc-prose">
          <p>
            <span className="doc-drop-cap">{raw_text.charAt(0)}</span>
            {raw_text.slice(1)}
          </p>
        </article>
      </section>
    );
  }

  const hasDivisions = parsed.divisions.length > 0;
  const hasDivisionMetrics = hasDivisions && parsed.divisions.some(
    d => d.sales_percentage || d.gross_profit_margin || d.profit_percentage
  );

  return (
    <>
      {/* Executive Summary Section */}
      <section className="doc-section">
        <div className="doc-section-header-row">
          <SectionHeader title="Executive Summary" showAiBadge />
        </div>
        <article className="doc-section-content doc-prose">
          {raw_text && (
            <p>
              <span className="doc-drop-cap">{raw_text.charAt(0)}</span>
              {raw_text.slice(1)}
            </p>
          )}
        </article>
      </section>

      {/* Segment Performance Section */}
      {hasDivisionMetrics && (
        <section className="doc-section">
          <SectionHeader
            title="Segment Performance"
            subtitle={parsed.fiscal_year ? `FY${parsed.fiscal_year}` : undefined}
          />
          <div className="doc-section-content">
            <div className="segment-bars-container">
              {parsed.divisions.map((div, idx) => (
                <SegmentBar
                  key={idx}
                  name={div.name}
                  description={div.description}
                  percentage={parsePercentage(div.sales_percentage)}
                  margin={div.gross_profit_margin || undefined}
                  profitContrib={div.profit_percentage || undefined}
                />
              ))}
            </div>
          </div>
        </section>
      )}
    </>
  );
};

/**
 * Export key metrics for sidebar usage
 */
export function extractKeyMetrics(content: string | undefined): Array<{
  label: string;
  value: string;
  unit?: string;
  yoy?: number;
}> {
  if (!content) return [];

  const jsonData = tryParseJSON(content);
  if (!jsonData?.parsed?.key_metrics) return [];

  const metrics = jsonData.parsed.key_metrics as Record<string, string | undefined>;
  const result: Array<{ label: string; value: string; unit?: string; yoy?: number }> = [];

  const labelMap: Record<string, string> = {
    total_revenue: 'Total Revenue',
    operating_income: 'Op. Income',
    net_income: 'Net Income',
    net_interest_margin: 'NIM',
    operating_margin: 'Op. Margin',
  };

  // List of base metric keys (without _yoy suffix)
  const baseMetrics = ['total_revenue', 'operating_income', 'net_income', 'net_interest_margin', 'operating_margin'];

  for (const key of baseMetrics) {
    const value = metrics[key];
    if (value) {
      // Try to extract YoY value
      const yoyKey = `${key}_yoy`;
      const yoyValue = metrics[yoyKey];
      let yoy: number | undefined;

      if (yoyValue) {
        // Parse YoY value (e.g., "+5.2%", "-3.1%", "+2.5pp")
        const yoyMatch = yoyValue.match(/([+-]?[\d.]+)/);
        if (yoyMatch) {
          yoy = parseFloat(yoyMatch[1]);
        }
      }

      result.push({
        label: labelMap[key] || key.replace(/_/g, ' '),
        value: value,
        yoy,
      });
    }
  }

  return result.slice(0, 4); // Limit to 4 metrics for sidebar
}

/**
 * Export fiscal year for sidebar
 */
export function extractFiscalYear(content: string | undefined): string | undefined {
  if (!content) return undefined;
  const jsonData = tryParseJSON(content);
  return jsonData?.parsed?.fiscal_year || undefined;
}
