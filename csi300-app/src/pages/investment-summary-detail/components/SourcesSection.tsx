import React, { useState } from 'react';

interface SourcesSectionProps {
  sources: string | undefined;
}

export interface ParsedSource {
  title: string;
  url: string;
  hostname: string;
}

function getHostname(url: string): string {
    try {
        // Clean up URL first
        let cleanUrl = url.trim();
        if (!cleanUrl.startsWith('http')) {
            cleanUrl = `https://${cleanUrl}`;
        }
        const urlObj = new URL(cleanUrl);
        return urlObj.hostname.replace(/^www\./, '');
    } catch {
        // Try to extract domain from partial URL
        const domainMatch = url.match(/([a-zA-Z0-9][-a-zA-Z0-9]*\.)+[a-zA-Z]{2,}/);
        return domainMatch ? domainMatch[0].replace(/^www\./, '') : 'source';
    }
}

export function parseSources(sourcesText: string): ParsedSource[] {
    if (!sourcesText) return [];

    const lines = sourcesText.split('\n').filter(line => line.trim().length > 0);
    const parsed: ParsedSource[] = [];

    for (const line of lines) {
        let title = '';
        let url = '';
        let matchedPattern = '';

        // Pattern 0 (PRIMARY): "Title | URL" format (new fixed format from prompt)
        const pipeMatch = line.match(/^(.+?)\s*\|\s*(https?:\/\/[^\s]+|[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}[^\s]*)/);
        if (pipeMatch) {
            title = pipeMatch[1].trim();
            url = pipeMatch[2].trim();
            matchedPattern = 'Pattern0_Pipe';
        }

        // Pattern 1: "Title: [hypothetical link - domain.com/path]" or "Title: [hypothetical link: domain.com/path]"
        if (!url) {
            const hypotheticalMatch = line.match(/^(.+?):\s*\[hypothetical link[\s:-]+([^\]]+)\]/i);
            if (hypotheticalMatch) {
                title = hypotheticalMatch[1].trim();
                url = hypotheticalMatch[2].trim();
                matchedPattern = 'Pattern1_Hypothetical';
            }
        }

        // Pattern 2: Standard Markdown [text](url)
        if (!url) {
            const mdMatch = line.match(/\[([^\]]+)\]\(([^)]+)\)/);
            if (mdMatch) {
                title = line.replace(mdMatch[0], '').trim() || mdMatch[1];
                url = mdMatch[2];
                matchedPattern = 'Pattern2_Markdown';
            }
        }

        // Pattern 3: "Title: https://url" format
        if (!url) {
            const colonUrlMatch = line.match(/^(.+?):\s*(https?:\/\/[^\s]+)/i);
            if (colonUrlMatch) {
                title = colonUrlMatch[1].trim();
                url = colonUrlMatch[2].trim();
                matchedPattern = 'Pattern3_Colon';
            }
        }

        // Pattern 4: Raw URL in line
        if (!url) {
            const rawUrlMatch = line.match(/(https?:\/\/[^\s\]\)]+)/);
            if (rawUrlMatch) {
                url = rawUrlMatch[1];
                title = line.replace(url, '').replace(/[\[\]\(\)|:-]/g, ' ').trim();
                matchedPattern = 'Pattern4_RawURL';
            }
        }

        // Pattern 5: Domain-like pattern without protocol (e.g., "domain.com/path")
        if (!url) {
            const domainMatch = line.match(/([a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}[^\s\]]*)/);
            if (domainMatch) {
                url = domainMatch[1];
                title = line.replace(domainMatch[0], '').replace(/[\[\]\(\)|:-]/g, ' ').replace(/hypothetical link/gi, '').trim();
                matchedPattern = 'Pattern5_Domain';
            }
        }

        // Clean up title
        title = title
            .replace(/^[-*•]\s*/, '')
            .replace(/:$/, '')
            .replace(/\s+/g, ' ')
            .trim();

        if (url) {
            const hostname = getHostname(url);
            parsed.push({
                title: title || hostname,
                url: url,
                hostname: hostname
            });
        }
    }

    return parsed;
}

// Reusable Sources Badge Component
export const SourcesBadge: React.FC<{ sources: string | undefined; className?: string }> = ({ sources, className = '' }) => {
    if (!sources) return null;
    const parsedSources = parseSources(sources);
    const lineCount = sources.split('\n').filter(l => l.trim()).length;
    const displayCount = parsedSources.length || lineCount;
    if (displayCount === 0) return null;

    const uniqueHosts = Array.from(new Set(parsedSources.map(s => s.hostname))).slice(0, 4);

    return (
        <div className={`sources-preview-badge ${className}`}>
             <div className="favicon-stack">
                {uniqueHosts.length > 0 ? (
                    uniqueHosts.map((host, i) => (
                        <div key={host} className="source-favicon" style={{ zIndex: 10 - i }}>
                            <img
                                src={`https://www.google.com/s2/favicons?domain=${host}&sz=32`}
                                alt=""
                                onError={(e) => {
                                    const target = e.target as HTMLImageElement;
                                    if (!target.dataset.fallbackAttempted) {
                                        target.dataset.fallbackAttempted = 'true';
                                        target.src = `https://${host}/favicon.ico`;
                                    } else {
                                        target.style.display = 'none';
                                        target.parentElement!.classList.add('favicon-fallback');
                                    }
                                }}
                            />
                        </div>
                    ))
                ) : (
                    // Fallback icons
                    [0, 1, 2].map((i) => (
                        <div key={i} className="source-favicon source-favicon-fallback" style={{ zIndex: 10 - i }}>
                            <svg viewBox="0 0 24 24" fill="#6b7280" width="12" height="12">
                                <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z"/>
                            </svg>
                        </div>
                    ))
                )}
            </div>
            <span className="source-count">{displayCount} sources</span>
        </div>
    );
};

export const SourcesSection: React.FC<SourcesSectionProps> = ({ sources }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!sources) return null;

  const parsedSources = parseSources(sources);
  const lineCount = sources.split('\n').filter(l => l.trim()).length;
  const displayCount = parsedSources.length || lineCount;

  if (displayCount === 0) return null;

  return (
    <div className="investment-summary-section sources-section">
      <div
        className="section-header sources-header"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="sources-title-group">
            <h2>Sources</h2>
            <SourcesBadge sources={sources} />
        </div>

        <div className={`chevron-icon ${isExpanded ? 'expanded' : ''}`}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
        </div>
      </div>

      {isExpanded && (
          <div className="section-content">
            {parsedSources.length > 0 ? (
                <ul className="sources-list-detailed">
                  {parsedSources.map((source, index) => (
                    <li key={index} className="source-item">
                        <div className="source-item-icon">
                            <img
                                src={`https://www.google.com/s2/favicons?domain=${source.hostname}&sz=32`}
                                alt=""
                                onError={(e) => {
                                    const target = e.target as HTMLImageElement;
                                    if (!target.dataset.fallbackAttempted) {
                                        target.dataset.fallbackAttempted = 'true';
                                        target.src = `https://${source.hostname}/favicon.ico`;
                                    } else {
                                        target.style.display = 'none';
                                        target.parentElement!.classList.add('favicon-fallback');
                                    }
                                }}
                            />
                        </div>
                        <div className="source-item-content">
                            <div className="source-item-title">{source.title}</div>
                            <a
                                href={source.url.startsWith('http') ? source.url : `https://${source.url}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="source-item-link"
                            >
                                {source.hostname}
                            </a>
                        </div>
                    </li>
                  ))}
                </ul>
            ) : (
                // Fallback: show raw sources as text
                <div className="sources-raw">
                    {sources.split('\n').filter(l => l.trim()).map((line, i) => (
                        <p key={i}>{line}</p>
                    ))}
                </div>
            )}
          </div>
      )}
    </div>
  );
};
