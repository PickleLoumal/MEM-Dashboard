/**
 * Sidebar Components for Investment Summary
 * Sticky sidebar with price, metrics, risks, and sources
 */
import React from 'react';
import {
  TrendingUp,
  AlertTriangle,
  FileText,
  ExternalLink,
  Shield
} from 'lucide-react';
import { RecommendationBadge, RiskAlert, MetricRow } from './ui';
import { ParsedSource, parseSources } from './SourcesSection';

interface PriceCardProps {
  price: string | undefined;
  change?: number;
  changePercent?: number;
  reportDate: string;
  recommendation: string | undefined;
  targetPrice?: string;
}

/**
 * Format price to 2 decimal places
 */
function formatPrice(price: string | undefined): string {
  if (!price) return '-';
  const num = parseFloat(price);
  if (isNaN(num)) return price;
  return num.toFixed(2);
}

/**
 * Price & Consensus Card
 */
export const PriceCard: React.FC<PriceCardProps> = ({
  price,
  change = 0,
  changePercent = 0,
  reportDate,
  recommendation,
  targetPrice
}) => {
  const isPositive = change >= 0;
  const formattedPrice = formatPrice(price);
  const hasChange = change !== 0 || changePercent !== 0;

  return (
    <div className="sidebar-card">
      <div className="price-card-header">
        <div className="price-card-main">
          <div className="price-card-value">
            {formattedPrice}
            <span className="price-card-currency">CNY</span>
          </div>
          <div className="price-card-meta">
            {hasChange ? (
              <span className={isPositive ? 'price-positive' : 'price-negative'}>
                {isPositive ? '+' : ''}{change.toFixed(2)} ({changePercent.toFixed(2)}%)
              </span>
            ) : (
              <span className="price-no-change">Previous Close</span>
            )}
            <span className="price-separator">|</span>
            <span className="price-date">{reportDate}</span>
          </div>
        </div>
      </div>

      <div className="price-card-consensus">
        <div className="consensus-header">
          <div className="consensus-label">Consensus</div>
          <div className="consensus-value">
            <RecommendationBadge action={recommendation} />
            <TrendingUp size={16} className="consensus-icon" />
          </div>
        </div>

        {/* Consensus Bar */}
        <div className="consensus-bar">
          <div className="consensus-bar-buy" style={{ width: '20%' }}></div>
          <div className="consensus-bar-hold" style={{ width: '50%' }}></div>
          <div className="consensus-bar-sell" style={{ width: '30%' }}></div>
        </div>

        <div className="consensus-labels">
          <span>Buy</span>
          <span>Hold</span>
          <span>Sell</span>
        </div>

        {targetPrice && (
          <div className="target-price">
            <span className="target-price-label">Target Price</span>
            <span className="target-price-value">{targetPrice} CNY</span>
          </div>
        )}
      </div>
    </div>
  );
};

interface KeyMetricsCardProps {
  metrics: Array<{
    label: string;
    value: string | number;
    unit?: string;
    yoy?: number;
  }>;
  fiscalYear?: string;
}

/**
 * Key Metrics Card
 */
export const KeyMetricsCard: React.FC<KeyMetricsCardProps> = ({ metrics, fiscalYear }) => {
  if (!metrics || metrics.length === 0) return null;

  return (
    <div className="sidebar-card">
      <div className="sidebar-card-header">
        <h3 className="sidebar-card-title">Key Metrics</h3>
        {fiscalYear && <span className="sidebar-card-subtitle">FY{fiscalYear}</span>}
      </div>

      <div className="metrics-list">
        {metrics.map((metric, idx) => (
          <MetricRow
            key={idx}
            label={metric.label}
            value={metric.value}
            unit={metric.unit}
            delta={metric.yoy}
          />
        ))}
      </div>
    </div>
  );
};

interface RiskFactorsCardProps {
  risks: string | undefined;
}

/**
 * Extract key risk points from risk text with severity levels
 * Parses [HIGH], [MEDIUM], [LOW] prefixes from prompt-generated content
 */
function extractRiskPoints(riskText: string | undefined): Array<{ text: string; severity: 'high' | 'medium' | 'low' }> {
  if (!riskText) return [];

  const risks: Array<{ text: string; severity: 'high' | 'medium' | 'low' }> = [];

  // Pattern to match [HIGH], [MEDIUM], [LOW] prefixed risks (with optional ** bold markers)
  const severityPattern = /\*?\*?\[?(HIGH|MEDIUM|LOW)\]?\*?\*?\s*[-:]*\s*([^\n]+)/gi;

  let match;
  while ((match = severityPattern.exec(riskText)) !== null) {
    const severityStr = match[1].toUpperCase();
    let text = match[2].trim();

    // Clean up the text - remove markdown formatting
    text = text.replace(/\*\*/g, '').replace(/^\s*[-•●]\s*/, '').trim();

    if (text.length < 15) continue;

    // Map severity
    let severity: 'high' | 'medium' | 'low';
    if (severityStr === 'HIGH') {
      severity = 'high';
    } else if (severityStr === 'LOW') {
      severity = 'low';
    } else {
      severity = 'medium';
    }

    // Truncate long text
    const displayText = text.length > 120 ? text.slice(0, 120) + '...' : text;

    risks.push({ text: displayText, severity });
  }

  // If no explicit severity markers found, fall back to bullet point extraction
  if (risks.length === 0) {
    const lines = riskText.split(/\n/).filter(l => l.trim().length > 20);

    for (const line of lines.slice(0, 3)) {
      let text = line.trim()
        .replace(/^[-•●■*]\s*/, '')
        .replace(/^\d+\.\s*/, '')
        .replace(/\*\*/g, '');

      if (text.length < 15) continue;

      // Infer severity from keywords
      let severity: 'high' | 'medium' | 'low' = 'medium';
      const lowerText = text.toLowerCase();

      if (lowerText.includes('significant') || lowerText.includes('major') ||
          lowerText.includes('critical') || lowerText.includes('severe')) {
        severity = 'high';
      } else if (lowerText.includes('minor') || lowerText.includes('limited')) {
        severity = 'low';
      }

      const displayText = text.length > 120 ? text.slice(0, 120) + '...' : text;
      risks.push({ text: displayText, severity });
    }
  }

  // Sort by severity: high first, then medium, then low
  const severityOrder = { high: 0, medium: 1, low: 2 };
  risks.sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity]);

  return risks.slice(0, 4); // Limit to 4 risks
}

/**
 * Risk Factors Card
 */
export const RiskFactorsCard: React.FC<RiskFactorsCardProps> = ({ risks }) => {
  const riskPoints = extractRiskPoints(risks);

  if (riskPoints.length === 0) return null;

  return (
    <div className="sidebar-card">
      <h3 className="sidebar-card-title sidebar-card-title-with-icon">
        <AlertTriangle size={12} />
        Risk Factors
      </h3>

      <div className="risk-alerts-list">
        {riskPoints.map((risk, idx) => (
          <RiskAlert key={idx} text={risk.text} severity={risk.severity} />
        ))}
      </div>
    </div>
  );
};

interface SourceDocumentsCardProps {
  sources: string | undefined;
}

/**
 * Source Documents Card
 */
export const SourceDocumentsCard: React.FC<SourceDocumentsCardProps> = ({ sources }) => {
  if (!sources) return null;

  const parsedSources = parseSources(sources);
  const displaySources = parsedSources.slice(0, 5);

  if (displaySources.length === 0) return null;

  return (
    <div className="sidebar-card">
      <h3 className="sidebar-card-title">Source Documents</h3>

      <ul className="source-docs-list">
        {displaySources.map((source, idx) => (
          <li key={idx} className="source-doc-item">
            <FileText size={14} className="source-doc-file-icon" />
            <div className="source-doc-content">
              <a
                href={source.url.startsWith('http') ? source.url : `https://${source.url}`}
                target="_blank"
                rel="noopener noreferrer"
                className="source-doc-title"
              >
                {source.title}
              </a>
            </div>
            <ExternalLink size={12} className="source-doc-external" />
          </li>
        ))}
      </ul>
    </div>
  );
};

/**
 * Company Info Mini Card (optional, for quick reference)
 */
export const CompanyMiniCard: React.FC<{
  marketCap?: string;
  sector?: string;
  industry?: string;
}> = ({ marketCap, sector, industry }) => {
  return (
    <div className="sidebar-card sidebar-card-mini">
      <div className="mini-info-row">
        <span className="mini-info-label">Market Cap</span>
        <span className="mini-info-value">{marketCap || '-'}</span>
      </div>
      {sector && (
        <div className="mini-info-row">
          <span className="mini-info-label">Sector</span>
          <span className="mini-info-value">{sector}</span>
        </div>
      )}
      {industry && industry !== sector && (
        <div className="mini-info-row">
          <span className="mini-info-label">Industry</span>
          <span className="mini-info-value">{industry}</span>
        </div>
      )}
    </div>
  );
};

/**
 * Sidebar Footer with disclaimer
 */
export const SidebarFooter: React.FC = () => (
  <div className="sidebar-footer">
    <div className="sidebar-footer-badge">
      <Shield size={10} />
      <span>Financial AIGC Engine</span>
    </div>
    <p className="sidebar-footer-disclaimer">
      AI-generated analysis. Not financial advice.
    </p>
  </div>
);

