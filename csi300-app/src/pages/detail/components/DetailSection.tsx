import React, { ReactNode } from 'react';

interface DetailSectionProps {
  title: string;
  children: ReactNode;
  className?: string;
}

export function DetailSection({ title, children, className = '' }: DetailSectionProps) {
  return (
    <div className={`detail-section app-card ${className}`} style={{
        overflow: 'hidden',
        border: '1px solid var(--app-border)'
    }}>
      <div className="section-header" style={{
          background: 'var(--app-surface-muted)',
          padding: '18px 24px',
          borderBottom: '1px solid var(--app-border)',
          fontWeight: 600,
          color: 'var(--app-heading)',
          fontSize: '16px',
          letterSpacing: '0.02em'
      }}>
        {title}
      </div>
      <div className="section-content" style={{ padding: '22px 24px 24px' }}>
        {children}
      </div>
    </div>
  );
}

interface FieldRowProps {
  label: string;
  value: string | number | undefined | null;
  valueClass?: string;
}

export function FieldRow({ label, value, valueClass = '' }: FieldRowProps) {
  const displayValue = value === null || value === undefined || value === '' ? '-' : value;

  return (
    <div className="field-row" style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(0, 1.3fr) minmax(0, 1fr)',
        gap: '14px',
        alignItems: 'baseline',
        padding: '12px 0',
        borderBottom: '1px solid var(--app-border)'
    }}>
      <span className="field-label" style={{
          color: 'var(--app-text-muted)',
          fontSize: '13px',
          fontWeight: 600,
          letterSpacing: '0.02em',
          textTransform: 'uppercase'
      }}>
        {label}
      </span>
      <span className={`field-value ${valueClass}`} style={{
          fontWeight: 600,
          color: valueClass === 'positive' ? 'var(--app-success)' : valueClass === 'negative' ? '#dc2626' : 'var(--app-heading)',
          textAlign: 'right',
          minWidth: 0,
          fontSize: '15px'
      }}>
        {displayValue}
      </span>
    </div>
  );
}

