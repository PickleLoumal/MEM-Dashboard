/**
 * Investment Summary UI Components
 * Professional document-style components for financial reports
 */
import React from 'react';
import {
  BrainCircuit,
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react';

/**
 * Citation component - displays [1] style references with hover tooltips
 */
export const Citation = ({ id, text }: { id: number; text?: string }) => (
  <sup className="citation-ref group">
    [{id}]
    <span className="citation-tooltip">
      {text || `Source reference #${id}`}
      <span className="citation-tooltip-arrow"></span>
    </span>
  </sup>
);

/**
 * Delta component - displays percentage change with color coding
 */
export const Delta = ({ val, suffix = '%' }: { val: number | string | undefined; suffix?: string }) => {
  if (val === undefined || val === null || val === '') return <span className="delta-neutral">-</span>;

  const numVal = typeof val === 'string' ? parseFloat(val) : val;
  if (isNaN(numVal)) return <span className="delta-neutral">{val}</span>;

  const isPositive = numVal > 0;
  const isNegative = numVal < 0;

  return (
    <span className={`delta ${isPositive ? 'delta-positive' : isNegative ? 'delta-negative' : 'delta-neutral'}`}>
      {isPositive && <TrendingUp size={12} className="delta-icon" />}
      {isNegative && <TrendingDown size={12} className="delta-icon" />}
      {!isPositive && !isNegative && <Minus size={12} className="delta-icon" />}
      <span className="delta-value">
        {isPositive ? '+' : ''}{numVal}{suffix}
      </span>
    </span>
  );
};

/**
 * Tag component - minimal styled tag/badge
 */
export const Tag = ({ text, variant = 'default' }: { text: string; variant?: 'default' | 'accent' | 'muted' }) => (
  <span className={`doc-tag doc-tag-${variant}`}>
    {text}
  </span>
);

/**
 * AI Badge component - indicates AI-generated content
 */
export const AiBadge = ({ label = 'AI Insight' }: { label?: string }) => (
  <div className="ai-badge">
    <BrainCircuit size={10} className="ai-badge-icon" />
    <span>{label}</span>
  </div>
);

/**
 * AI Confidence indicator
 */
export const AiConfidence = ({ score }: { score: number }) => (
  <div className="ai-confidence">
    <span className="ai-confidence-label">AI Confidence</span>
    <span className="ai-confidence-value">{score}%</span>
  </div>
);

/**
 * Section Header component for document sections
 */
export const SectionHeader = ({
  title,
  icon: Icon,
  showAiBadge = false,
  subtitle
}: {
  title: string;
  icon?: React.ElementType;
  showAiBadge?: boolean;
  subtitle?: string;
}) => (
  <div className="doc-section-header">
    <div className="doc-section-header-left">
      {Icon && <Icon size={12} className="doc-section-icon" />}
      <h2 className="doc-section-title">{title}</h2>
    </div>
    <div className="doc-section-header-right">
      {subtitle && <span className="doc-section-subtitle">{subtitle}</span>}
      {showAiBadge && <AiBadge />}
    </div>
  </div>
);

/**
 * Metric Row component for key financial metrics
 */
export const MetricRow = ({
  label,
  value,
  unit,
  delta
}: {
  label: string;
  value: string | number;
  unit?: string;
  delta?: number;
}) => (
  <div className="metric-row">
    <div className="metric-row-label">{label}</div>
    <div className="metric-row-content">
      <div className="metric-row-value">
        {value}
        {unit && <span className="metric-row-unit">{unit}</span>}
      </div>
      {delta !== undefined && <Delta val={delta} />}
    </div>
  </div>
);

/**
 * Progress Bar component for segment visualization
 */
export const SegmentBar = ({
  name,
  description,
  percentage,
  margin,
  profitContrib
}: {
  name: string;
  description?: string;
  percentage: number;
  margin?: string;
  profitContrib?: string;
}) => (
  <div className="segment-bar-container">
    <div className="segment-bar-header">
      <div className="segment-bar-name">
        <span className="segment-name">{name}</span>
        {description && <span className="segment-desc">{description}</span>}
      </div>
      <div className="segment-bar-value">{percentage}%</div>
    </div>
    <div className="segment-bar-track">
      <div
        className="segment-bar-fill"
        style={{ width: `${Math.min(percentage, 100)}%` }}
      />
    </div>
    <div className="segment-bar-footer">
      {margin && (
        <span className="segment-meta">
          Margin: <span className="segment-meta-value">{margin}</span>
        </span>
      )}
      {profitContrib && (
        <span className="segment-meta">
          Profit Contrib: <span className="segment-meta-value">{profitContrib}</span>
        </span>
      )}
    </div>
  </div>
);

/**
 * Recommendation Badge with color coding
 */
export const RecommendationBadge = ({ action }: { action: string | undefined }) => {
  if (!action || action === '-') {
    return <span className="recommendation-badge recommendation-neutral">-</span>;
  }

  const normalized = action.toLowerCase().replace(/\s+/g, '_');
  let variant = 'neutral';

  if (normalized.includes('buy') || normalized.includes('bullish')) {
    variant = 'buy';
  } else if (normalized.includes('sell') || normalized.includes('bearish')) {
    variant = 'sell';
  } else if (normalized.includes('hold') || normalized.includes('neutral')) {
    variant = 'hold';
  }

  return (
    <span className={`recommendation-badge recommendation-${variant}`}>
      {action}
    </span>
  );
};

/**
 * Risk Alert Item - Professional "Line" Style
 */
export const RiskAlert = ({
  text,
  severity = 'medium'
}: {
  text: string;
  severity?: 'high' | 'medium' | 'low';
}) => {
  return (
    <div className="risk-alert-item">
      <div className={`risk-alert-line risk-alert-line-${severity}`}></div>
      <div className="risk-alert-content">
        <p className="risk-alert-text">{text}</p>
      </div>
    </div>
  );
};

/**
 * Source Document Item
 */
export const SourceItem = ({
  title,
  hostname,
  url,
  icon
}: {
  title: string;
  hostname: string;
  url?: string;
  icon?: string;
}) => (
  <li className="source-doc-item">
    <div className="source-doc-icon">
      {icon ? (
        <img
          src={icon}
          alt=""
          onError={(e) => {
            (e.target as HTMLImageElement).style.display = 'none';
            (e.target as HTMLImageElement).parentElement?.classList.add('source-doc-icon-fallback');
          }}
        />
      ) : (
        <div className="source-doc-icon-fallback" />
      )}
    </div>
    <div className="source-doc-content">
      {url ? (
        <a href={url} target="_blank" rel="noopener noreferrer" className="source-doc-title">
          {title}
        </a>
      ) : (
        <span className="source-doc-title">{title}</span>
      )}
      <span className="source-doc-hostname">{hostname}</span>
    </div>
  </li>
);

