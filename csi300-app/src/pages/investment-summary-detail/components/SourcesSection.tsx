import React from 'react';

interface SourcesSectionProps {
  sources: string | undefined;
}

export const SourcesSection: React.FC<SourcesSectionProps> = ({ sources }) => {
  if (!sources) return null;

  const sourceLines = sources.split('\n').filter(line => line.trim());

  if (sourceLines.length === 0) return null;

  return (
    <div className="investment-summary-section">
      <div className="section-header">Sources</div>
      <div className="section-content">
        <ul className="sources-list">
          {sourceLines.map((line, index) => {
            const urlMatch = line.match(/\[([^\]]+)\]\(([^)]+)\)/);
            if (urlMatch) {
              const fullMatch = urlMatch[0];
              const text = line.replace(fullMatch, '').trim();
              const linkText = urlMatch[1];
              const url = urlMatch[2];
              return (
                <li key={index}>
                  {text} <a href={url} target="_blank" rel="noopener noreferrer">{linkText}</a>
                </li>
              );
            }
            return <li key={index}>{line}</li>;
          })}
        </ul>
      </div>
    </div>
  );
};

