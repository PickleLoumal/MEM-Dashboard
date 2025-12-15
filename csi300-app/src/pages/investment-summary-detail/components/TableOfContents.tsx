/**
 * TableOfContents - Sticky navigation for document sections
 * Tracks scroll position and highlights active section
 */
import React, { useEffect, useState, useCallback, useRef } from 'react';

interface TocItem {
  id: string;
  title: string;
}

// Define all sections with their IDs and display titles
const TOC_ITEMS: TocItem[] = [
  { id: 'executiveSummary', title: 'Summary' },
  { id: 'businessPerformance', title: 'Performance' },
  { id: 'industryContext', title: 'Industry' },
  { id: 'financialStability', title: 'Financial Stability' },
  { id: 'keyFinancialsValuation', title: 'Key Financials' },
  { id: 'bigTrendsEvents', title: 'Trends & Events' },
  { id: 'customerSegments', title: 'Customers' },
  { id: 'competitiveLandscape', title: 'Competition' },
  { id: 'forecastOutlook', title: 'Forecast' },
  { id: 'investmentFirmsViews', title: 'Investment Firms' },
  { id: 'recommendedActionDetail', title: 'Action' },
  { id: 'industryRatioAnalysis', title: 'Ratio Analysis' },
  { id: 'tariffsSupplyChainRisks', title: 'Supply Chain' },
  { id: 'keyTakeaways', title: 'Key Takeaways' },
];

interface TableOfContentsProps {
  /** Optional: filter to only show sections that exist */
  visibleSections?: string[];
}

export const TableOfContents: React.FC<TableOfContentsProps> = ({ visibleSections }) => {
  const [activeId, setActiveId] = useState<string>('executiveSummary');

  // Track if user has clicked (disables auto-scroll detection)
  const userHasClickedRef = useRef(false);

  // Filter items based on what sections actually exist in the document
  const items = visibleSections
    ? TOC_ITEMS.filter(item => visibleSections.includes(item.id))
    : TOC_ITEMS;

  // Track scroll position and update active section (only when user scrolls manually)
  const handleScroll = useCallback(() => {
    // If user clicked a nav item, don't auto-update
    if (userHasClickedRef.current) return;

    const scrollPosition = window.scrollY + 150; // Offset for header

    // Find the current section based on scroll position
    let currentSection = items[0]?.id;

    for (const item of items) {
      const element = document.getElementById(item.id);
      if (element) {
        const { top } = element.getBoundingClientRect();
        const absoluteTop = top + window.scrollY;

        if (scrollPosition >= absoluteTop) {
          currentSection = item.id;
        }
      }
    }

    if (currentSection) {
      setActiveId(currentSection);
    }
  }, [items]);

  // Detect manual scroll (wheel or touch) to re-enable auto-detection
  useEffect(() => {
    const handleUserScroll = () => {
      // User is manually scrolling, re-enable auto-detection
      userHasClickedRef.current = false;
    };

    // Listen for wheel and touch events (indicates manual scrolling)
    window.addEventListener('wheel', handleUserScroll, { passive: true });
    window.addEventListener('touchmove', handleUserScroll, { passive: true });

    return () => {
      window.removeEventListener('wheel', handleUserScroll);
      window.removeEventListener('touchmove', handleUserScroll);
    };
  }, []);

  useEffect(() => {
    window.addEventListener('scroll', handleScroll, { passive: true });
    // Initial check
    handleScroll();

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [handleScroll]);

  const scrollToSection = (id: string) => {
    // Mark as user-clicked (disables scroll detection)
    userHasClickedRef.current = true;
    setActiveId(id);

    const element = document.getElementById(id);
    if (element) {
      const headerOffset = 100;
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.scrollY - headerOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  };

  return (
    <nav className="doc-toc no-print" aria-label="Table of contents">
      <ul className="doc-toc-list">
        {items.map((item) => (
          <li key={item.id} className="doc-toc-item">
            <button
              className={`doc-toc-link ${activeId === item.id ? 'doc-toc-link-active' : ''}`}
              onClick={() => scrollToSection(item.id)}
              aria-current={activeId === item.id ? 'location' : undefined}
            >
              {item.title}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default TableOfContents;

