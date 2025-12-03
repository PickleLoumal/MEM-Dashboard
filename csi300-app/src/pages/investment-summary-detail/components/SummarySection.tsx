import React from 'react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface SummarySectionProps {
  title: string;
  content: string | undefined;
  id?: string;
}

export const SummarySection: React.FC<SummarySectionProps> = ({ title, content, id }) => {
  if (!content) return null;

  return (
    <div className="investment-summary-section" id={id}>
      <div className="section-header">{title}</div>
      <div className="section-content">
        <Markdown remarkPlugins={[remarkGfm]}>{content}</Markdown>
      </div>
    </div>
  );
};

