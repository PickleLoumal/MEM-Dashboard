import React from 'react';
import Markdown, { Components } from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { logger } from '@shared/lib/logger';
import { SectionHeader, SegmentBar, AiBadge } from './ui';

/**
 * 提取 children 的文本内容（处理 React 元素数组情况）
 */
function extractText(children: React.ReactNode): string {
  if (typeof children === 'string') return children;
  if (typeof children === 'number') return String(children);
  if (Array.isArray(children)) {
    return children.map(extractText).join('');
  }
  if (React.isValidElement(children)) {
    const props = children.props as { children?: React.ReactNode };
    if (props.children) {
      return extractText(props.children);
    }
  }
  return '';
}

/**
 * 创建自定义 Markdown 组件
 * @param withDropCap 是否启用首字下沉效果（仅第一段）
 */
function createMarkdownComponents(withDropCap: boolean): Components {
  let paragraphIndex = 0;

  return {
    a: ({ href, children, ...props }) => {
      // 提取文本内容（处理嵌套元素情况）
      const text = extractText(children).trim();

      // 检测引用格式: [1], [2], ... (来自 [[1]] markdown 解析)
      const citationMatch = text.match(/^\[(\d+)\]$/);

      if (citationMatch && href) {
        const citationNum = citationMatch[1];
        return (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-citation"
            title={href}
            {...props}
          >
            <sup>[{citationNum}]</sup>
          </a>
        );
      }

      // 普通链接
      return (
        <a href={href} target="_blank" rel="noopener noreferrer" {...props}>
          {children}
        </a>
      );
    },
    // 自定义段落渲染，第一段添加首字下沉效果
    p: ({ children, ...props }) => {
      const currentIndex = paragraphIndex++;
      const isFirstParagraph = currentIndex === 0 && withDropCap;

      if (isFirstParagraph) {
        // 提取第一个字符用于首字下沉
        const textContent = extractText(children);
        if (textContent.length > 0) {
          const firstChar = textContent.charAt(0);
          // 重建 children，将第一个字符替换为 drop-cap span
          return (
            <p {...props}>
              <span className="doc-drop-cap">{firstChar}</span>
              {renderChildrenWithoutFirstChar(children, firstChar)}
            </p>
          );
        }
      }

      return <p {...props}>{children}</p>;
    },
  };
}

/**
 * 移除 children 中的第一个字符（用于首字下沉）
 */
function renderChildrenWithoutFirstChar(children: React.ReactNode, firstChar: string): React.ReactNode {
  if (typeof children === 'string') {
    return children.startsWith(firstChar) ? children.slice(1) : children;
  }
  if (Array.isArray(children)) {
    let firstCharRemoved = false;
    return children.map((child, idx) => {
      if (firstCharRemoved) return child;
      if (typeof child === 'string' && child.startsWith(firstChar)) {
        firstCharRemoved = true;
        return child.slice(1);
      }
      if (React.isValidElement(child)) {
        const props = child.props as { children?: React.ReactNode };
        if (props.children) {
          const textContent = extractText(props.children);
          if (textContent.startsWith(firstChar)) {
            firstCharRemoved = true;
            // 重建元素，移除第一个字符
            return React.cloneElement(child, {
              ...props,
              children: renderChildrenWithoutFirstChar(props.children, firstChar),
            } as React.Attributes);
          }
        }
      }
      return child;
    });
  }
  return children;
}

// 用于非首字下沉场景的标准组件
const standardMarkdownComponents = createMarkdownComponents(false);

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

  // 如果不是 JSON 格式，使用 Markdown 渲染（支持 inline citations + 首字下沉）
  if (!jsonData) {
    logger.info('Rendering Business Overview as Markdown', { length: content.length });
    return (
      <section className="doc-section">
        <SectionHeader title="Executive Summary" showAiBadge />
        <article className="doc-section-content doc-prose">
          <Markdown remarkPlugins={[remarkGfm]} components={createMarkdownComponents(true)}>
            {content}
          </Markdown>
        </article>
      </section>
    );
  }

  const { raw_text, parsed } = jsonData;
  logger.info('Rendering Business Overview from JSON', { hasParsed: !!parsed, fiscalYear: parsed?.fiscal_year });

  // 如果解析失败，使用 Markdown 渲染原始文本（带首字下沉）
  if (!parsed) {
    return (
      <section className="doc-section">
        <SectionHeader title="Executive Summary" showAiBadge />
        <article className="doc-section-content doc-prose">
          <Markdown remarkPlugins={[remarkGfm]} components={createMarkdownComponents(true)}>
            {raw_text}
          </Markdown>
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
            <Markdown remarkPlugins={[remarkGfm]} components={createMarkdownComponents(true)}>
              {raw_text}
            </Markdown>
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

  // Label mapping for known keys
  const labelMap: Record<string, string> = {
    total_revenue: 'Total Revenue',
    operating_income: 'Op. Income',
    net_income: 'Net Income',
    net_interest_margin: 'NIM',
    operating_margin: 'Op. Margin',
    gross_margin: 'Gross Margin',
    roa: 'ROA',
    roe: 'ROE',
  };

  // Preferred order of metrics to display
  const preferredOrder = [
    'total_revenue',
    'operating_income',
    'net_income',
    'operating_margin',
    'net_interest_margin',
    'gross_margin',
    'roa',
    'roe',
  ];

  // Collect all base metrics (keys without _yoy suffix)
  const baseMetricKeys = Object.keys(metrics).filter(
    key => !key.endsWith('_yoy') && metrics[key] && metrics[key] !== 'null'
  );

  // Sort by preferred order, with unknown keys at the end
  baseMetricKeys.sort((a, b) => {
    const aIdx = preferredOrder.indexOf(a);
    const bIdx = preferredOrder.indexOf(b);
    if (aIdx === -1 && bIdx === -1) return 0;
    if (aIdx === -1) return 1;
    if (bIdx === -1) return -1;
    return aIdx - bIdx;
  });

  for (const key of baseMetricKeys) {
    const value = metrics[key];
    if (value) {
      // Try to extract YoY value
      const yoyKey = `${key}_yoy`;
      const yoyValue = metrics[yoyKey];
      let yoy: number | undefined;

      if (yoyValue) {
        // Parse YoY value (e.g., "+5.2%", "-3.1%", "+2.5pp", "-10.9%")
        const yoyMatch = yoyValue.match(/([+-]?[\d.]+)/);
        if (yoyMatch) {
          yoy = parseFloat(yoyMatch[1]);
          // Handle negative sign
          if (yoyValue.startsWith('-') && yoy > 0) {
            yoy = -yoy;
          }
        }
      }

      // Format label: use map if available, otherwise humanize key
      const label = labelMap[key] || key
        .replace(/_/g, ' ')
        .replace(/\b\w/g, c => c.toUpperCase());

      result.push({
        label,
        value,
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
