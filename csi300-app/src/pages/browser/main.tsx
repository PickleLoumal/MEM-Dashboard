import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import ReactDOM from 'react-dom/client';
import { GlobalNav } from '@shared/components/GlobalNav';
import { ColumnSelector } from '@shared/components/ColumnSelector/ColumnSelector';
import { columnManifest, Formatters, FieldMap, getCellClass } from '@shared/lib/column-manifest';
import type { ColumnChangeData, ColumnDefinition } from '@shared/components/ColumnSelector/types';
import {
  Csi300Service,
  OpenAPI,
  type CSI300FilterOptions,
  type CSI300CompanyList,
} from '@shared/api/generated';
import '@shared/styles/main.css';
import './styles.css';

// Configure OpenAPI base URL BEFORE any API calls
// Production: empty string (generated paths already include /api prefix, CloudFront proxies /api/* to ALB)
// Development: localhost:8001
OpenAPI.BASE = (
  import.meta.env.VITE_API_BASE ??
  (import.meta.env.MODE === 'development' ? 'http://localhost:8001' : '')
).replace(/\/$/, '');

type Filters = {
  im_sector: string;
  industry: string;
  company_search: string;
  industry_search: string;
  region: string;
};

// Column type now imported from types.ts
// Default columns derived from columnManifest
const DEFAULT_COLUMNS = columnManifest.columns.filter(col => col.defaultVisible);

const SEARCH_DEBOUNCE_MS = 300;

function deriveRegions(data: CSI300FilterOptions | null): string[] {
  if (!data?.regions?.length) {
    return ['Mainland China', 'Hong Kong'];
  }
  return [...new Set(data.regions.filter(Boolean))].sort((a, b) =>
    a.toLowerCase().localeCompare(b.toLowerCase())
  );
}

function deriveSectors(data: CSI300FilterOptions | null): string[] {
  if (!data) return [];
  return data.im_sectors || [];
}

function deriveIndustries(data: CSI300FilterOptions | null): string[] {
  if (!data) return [];
  return data.industries || [];
}

function renderCellValue(column: ColumnDefinition, company: CSI300CompanyList): React.ReactNode {
  const field = FieldMap[column.id] || column.id;
  let rawValue = (company as Record<string, unknown>)[field];

  // Fallback for sector
  if (column.id === 'sector' && !rawValue) {
    rawValue = company.industry || '-';
  }

  if (rawValue === null || rawValue === undefined || rawValue === '') {
    return <span style={{ color: '#9ca3af' }}>-</span>;
  }

  if (column.id === 'region') {
    const { label, attr } = getRegionBadge(rawValue as string);
    return <span className="region-badge" data-region={attr}>{label}</span>;
  }

  // Apply Formatting using Legacy Formatters
  let formatted = String(rawValue);
  const formatterName = column.format;

  if (formatterName && Formatters[formatterName as keyof typeof Formatters]) {
    formatted = Formatters[formatterName as keyof typeof Formatters](rawValue, column.decimals);
  }

  // Apply colorization for price and profitability metrics
  if (column.colorize || (column.id.includes('price') && !column.id.includes('high') && !column.id.includes('low'))) {
    const num = parseFloat(String(rawValue));
    if (!isNaN(num)) {
      const color = num >= 0 ? '#059669' : '#dc2626';
      return <span style={{ color }}>{formatted}</span>;
    }
  }

  // Handle max display for large values
  if (column.maxDisplay && typeof rawValue === 'number' && rawValue > column.maxDisplay) {
    return <span title={`${formatted} - ${column.tooltip || 'Value exceeds display limit'}`}>{column.maxDisplay}+</span>;
  }

  // Chip format
  if (column.format === 'chip') {
    return <span style={{ background: '#f3f4f6', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>{formatted}</span>;
  }

  return formatted;
}

function getRegionBadge(region?: string) {
  if (!region) return { label: 'All Regions', attr: 'all' };
  const normalized = region.toLowerCase();
  if (normalized.includes('hong')) return { label: 'Hong Kong', attr: 'hong-kong' };
  if (normalized.includes('china')) return { label: 'Mainland China', attr: 'mainland-china' };
  return { label: region, attr: 'unknown' };
}

// Pagination component
function Pagination({ page, pages, onPageChange }: { page: number; pages: number; onPageChange: (p: number) => void }) {
  if (pages <= 1) return null;

  const maxPagesToShow = 5;
  let startPage = Math.max(1, page - Math.floor(maxPagesToShow / 2));
  const endPage = Math.min(pages, startPage + maxPagesToShow - 1);
  if (endPage - startPage + 1 < maxPagesToShow) {
    startPage = Math.max(1, endPage - maxPagesToShow + 1);
  }

  const pageNumbers = [];
  for (let i = startPage; i <= endPage; i++) {
    pageNumbers.push(i);
  }

  return (
    <div className="pagination" id="pagination">
      <button onClick={() => onPageChange(page - 1)} disabled={page <= 1}>
        ← Previous
      </button>
      {pageNumbers.map((p) => (
        <button
          key={p}
          className={p === page ? 'current-page' : ''}
          onClick={() => onPageChange(p)}
        >
          {p}
        </button>
      ))}
      <button onClick={() => onPageChange(page + 1)} disabled={page >= pages}>
        Next →
      </button>
    </div>
  );
}


function BrowserPage() {
  const [filters, setFilters] = useState<Filters>({
    im_sector: '',
    industry: '',
    company_search: '',
    industry_search: '',
    region: ''
  });
  const [pendingCompanySearch, setPendingCompanySearch] = useState('');
  const [pendingIndustrySearch, setPendingIndustrySearch] = useState('');
  const searchDebounceRef = useRef<number | null>(null);
  const industrySearchDebounceRef = useRef<number | null>(null);
  const [filterData, setFilterData] = useState<CSI300FilterOptions | null>(null);
  const [industryOptions, setIndustryOptions] = useState<string[]>([]);
  const [regions, setRegions] = useState<string[]>([]);
  const [loadingFilters, setLoadingFilters] = useState(false);

  const [companies, setCompanies] = useState<CSI300CompanyList[]>([]);
  const [totalResults, setTotalResults] = useState(0);
  const [page, setPage] = useState(1);
  const pageSize = 20;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [columns, setColumns] = useState<ColumnDefinition[]>(DEFAULT_COLUMNS);
  const [pinnedColumns, setPinnedColumns] = useState<string[]>(() =>
    columnManifest.columns.filter(c => c.defaultPinned).map(c => c.id)
  );

  // Handle column changes from ColumnSelector
  const handleColumnChange = useCallback((data: ColumnChangeData) => {
    setColumns(data.columns);
    setPinnedColumns(data.pinnedColumns);
  }, []);

  // Parse URL on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const next: Filters = {
      im_sector: params.get('im_sector') || params.get('im_code') || '',
      industry: params.get('industry') || params.get('sub_industry') || '',
      company_search: params.get('company_search') || params.get('search') || '',
      industry_search: params.get('industry_search') || '',
      region: params.get('region') || ''
    };
    setFilters(next);
    setPendingCompanySearch(next.company_search);
    setPendingIndustrySearch(next.industry_search);
  }, []);

  // Fetch filter options using generated API
  useEffect(() => {
    let ignore = false;
    setLoadingFilters(true);

    Csi300Service.apiCsi300ApiCompaniesFilterOptionsRetrieve(
      filters.im_sector || undefined,
      undefined // region
    )
      .then((data) => {
        if (ignore) return;
        setFilterData(data);
        setIndustryOptions(deriveIndustries(data));
        setRegions(deriveRegions(data));
      })
      .catch((err) => {
        if (ignore) return;
        setError(err instanceof Error ? err.message : 'Failed to load filter options');
      })
      .finally(() => {
        if (ignore) return;
        setLoadingFilters(false);
      });

    return () => {
      ignore = true;
    };
  }, [filters.im_sector]);

  // Fetch companies using generated API
  useEffect(() => {
    let ignore = false;
    setLoading(true);
    setError(null);

    // Clean region value (remove count suffix like "Hong Kong (123)")
    const cleanRegion = filters.region ? filters.region.replace(/\s*\(.*\)$/, '') : undefined;

    Csi300Service.apiCsi300ApiCompaniesList(
      undefined, // gicsIndustry
      filters.im_sector || undefined,
      filters.industry || undefined,
      filters.industry_search || undefined,
      undefined, // marketCapMax
      undefined, // marketCapMin
      page,
      pageSize,
      cleanRegion,
      filters.company_search || undefined
    )
      .then((res) => {
        if (ignore) return;
        setCompanies(res.results || []);
        setTotalResults(res.count || 0);
      })
      .catch((err) => {
        if (ignore) return;
        setError(err instanceof Error ? err.message : 'Failed to load companies');
      })
      .finally(() => {
        if (ignore) return;
        setLoading(false);
      });

    return () => {
      ignore = true;
    };
  }, [filters, page]);

  const sectorOptions = useMemo(() => deriveSectors(filterData), [filterData]);

  const onFilterChange =
    (field: keyof Filters) => (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
      setFilters((prev) => ({ ...prev, [field]: e.target.value }));
      if (field !== 'industry') setPage(1);
    };

  const handleSectorChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setFilters((prev) => ({ ...prev, im_sector: value, industry: '' }));
    setPage(1);
    try {
      setLoadingFilters(true);
      const res = await Csi300Service.apiCsi300ApiCompaniesFilterOptionsRetrieve(
        value || undefined,
        undefined
      );
      setFilterData(res);
      setIndustryOptions(deriveIndustries(res));
      setRegions(deriveRegions(res));
    } catch (err) {
      console.error('Sector change load failed', err);
    } finally {
      setLoadingFilters(false);
    }
  };

  const resultsCount = loading ? 'Loading...' : `${totalResults} companies`;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    const params = new URLSearchParams();
    (Object.keys(filters) as (keyof Filters)[]).forEach((k) => {
      const v = filters[k].trim();
      if (v) params.append(k, v);
    });
    const qs = params.toString();
    window.history.replaceState({}, '', qs ? `?${qs}` : window.location.pathname);
  };

  const handleClear = () => {
    setFilters({ im_sector: '', industry: '', company_search: '', industry_search: '', region: '' });
    setPendingCompanySearch('');
    setPendingIndustrySearch('');
    setPage(1);
    window.history.replaceState({}, '', window.location.pathname);
  };

  const pages = Math.max(1, Math.ceil(totalResults / pageSize));
  const orderedColumns = useMemo(() => {
    const baseColumns = columns?.length ? columns : DEFAULT_COLUMNS;
    if (!pinnedColumns.length) return baseColumns;
    const pinned = pinnedColumns
      .map((id) => baseColumns.find((c) => c.id === id))
      .filter(Boolean) as ColumnDefinition[];
    const rest = baseColumns.filter((c) => !pinnedColumns.includes(c.id));
    return [...pinned, ...rest];
  }, [columns, pinnedColumns]);

  // Debounce company search
  useEffect(() => {
    if (searchDebounceRef.current) window.clearTimeout(searchDebounceRef.current);
    searchDebounceRef.current = window.setTimeout(() => {
      setFilters((prev) => ({ ...prev, company_search: pendingCompanySearch }));
      setPage(1);
    }, SEARCH_DEBOUNCE_MS);
    return () => {
      if (searchDebounceRef.current) window.clearTimeout(searchDebounceRef.current);
    };
  }, [pendingCompanySearch]);

  // Debounce industry search
  useEffect(() => {
    if (industrySearchDebounceRef.current) window.clearTimeout(industrySearchDebounceRef.current);
    industrySearchDebounceRef.current = window.setTimeout(() => {
      setFilters((prev) => ({ ...prev, industry_search: pendingIndustrySearch }));
      setPage(1);
    }, SEARCH_DEBOUNCE_MS);
    return () => {
      if (industrySearchDebounceRef.current) window.clearTimeout(industrySearchDebounceRef.current);
    };
  }, [pendingIndustrySearch]);

  return (
    <>
      <GlobalNav />
      <div className="container app-shell">
        <div className="page-header">
          <h1 className="page-title">Chinese Stock Search Results</h1>
        </div>

        {error ? <div className="error app-notice">{error}</div> : null}

        <form className="filter-section app-card" onSubmit={handleSubmit}>
          <div className="filter-grid app-form-grid app-form-grid--two">
            <div className="filter-group app-form-field">
              <label className="filter-label app-label">Industry Matrix Sector</label>
              <select
                name="im_sector"
                value={filters.im_sector}
                onChange={handleSectorChange}
                className="filter-select app-select"
              >
                <option value="">All Industry Matrix Sectors</option>
                {sectorOptions.map((sector) => (
                  <option key={sector} value={sector}>
                    {sector}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-group app-form-field">
              <label className="filter-label app-label">Region</label>
              <select
                name="region"
                value={filters.region}
                onChange={onFilterChange('region')}
                className="filter-select app-select"
              >
                <option value="">All Regions</option>
                {regions.map((region) => (
                  <option key={region} value={region}>
                    {region}
                  </option>
                ))}
              </select>
              <p className="filter-help">Hong Kong reflects the latest H-shares dataset.</p>
            </div>

            <div className="filter-group app-form-field">
              <label className="filter-label app-label">Industry within selected sector</label>
              <select
                name="industry"
                value={filters.industry}
                onChange={onFilterChange('industry')}
                className="filter-select app-select"
                disabled={loadingFilters}
              >
                <option value="">{loadingFilters ? 'Loading...' : 'All Industries'}</option>
                {industryOptions.map((ind) => (
                  <option key={ind} value={ind}>
                    {ind}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-group app-form-field">
              <label className="filter-label app-label">Search by Industry</label>
              <input
                type="text"
                name="industry_search"
                value={pendingIndustrySearch}
                onChange={(e) => setPendingIndustrySearch(e.target.value)}
                className="filter-input app-input"
                placeholder="Search by industry name..."
              />
            </div>
          </div>

          <label className="filter-label app-label">Search Companies</label>
          <input
            type="text"
            name="company_search"
            value={pendingCompanySearch}
            onChange={(e) => setPendingCompanySearch(e.target.value)}
            className="filter-input app-input"
            placeholder="Search by company name or ticker..."
          />

          <div className="filter-actions app-actions">
            <button type="button" onClick={handleClear} className="btn btn-secondary app-button app-button--secondary">
              Clear Filters
            </button>
            <button type="submit" className="btn btn-primary app-button app-button--primary">
              Apply Filters
            </button>
          </div>
        </form>

        <div className="results-section app-card">
          <div className="results-header">
            <div>
              <h2 className="results-title">Search Results</h2>
              <p className="results-count" id="resultsCount">
                {resultsCount}
              </p>
            </div>
            <div className="results-meta">
              {(() => {
                const badge = getRegionBadge(filters.region);
                return (
                  <span className="region-badge" data-region={badge.attr}>
                    {badge.label}
                  </span>
                );
              })()}
              <ColumnSelector
                manifest={columnManifest}
                onColumnChange={handleColumnChange}
                maxPinnedColumns={3}
              />
            </div>
          </div>

          {loading ? (
            <div className="loading">
              <p>Loading companies...</p>
            </div>
          ) : companies.length === 0 ? (
            <div className="no-results">
              <p>No companies found matching the criteria</p>
            </div>
          ) : (
            <div id="resultsContainer">
              <table className="company-table app-table" id="companyTable">
                <thead>
                  <tr>
                    {orderedColumns.map((col) => {
                      const isPinned = pinnedColumns.includes(col.id);
                      const alignClass = col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left';
                      const pinnedClass = isPinned ? 'pinned-column' : '';
                      const finalClass = `${alignClass} ${pinnedClass}`.trim();
                      return (
                        <th key={col.id} className={finalClass}>
                          {col.displayName}
                        </th>
                      );
                    })}
                  </tr>
                </thead>
                <tbody id="companyTableBody">
                  {companies.map((c) => (
                    <tr key={c.id} className="clickable-row" onClick={() => (window.location.href = `detail.html?id=${c.id}`)}>
                      {orderedColumns.map((col) => {
                        const isPinned = pinnedColumns.includes(col.id);
                        const alignClass = col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left';
                        const cellClass = getCellClass(col);
                        const pinnedClass = isPinned ? 'pinned-column' : '';
                        const finalClass = `${alignClass} ${cellClass} ${pinnedClass}`.trim();
                        return (
                          <td
                            key={col.id}
                            className={finalClass}
                          >
                            {renderCellValue(col, c)}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>

              <div className="mobile-company-list" id="mobileCompanyList">
                {companies.map((c) => (
                  <div key={c.id} className="mobile-company-card" onClick={() => (window.location.href = `detail.html?id=${c.id}`)}>
                    <div className="mobile-company-header">
                      <div className="mobile-company-name">{c.name}</div>
                      <div className="mobile-company-ticker">{c.ticker}</div>
                    </div>
                    <div className="mobile-company-details">
                      <div className="mobile-company-detail">
                        <span className="mobile-company-detail-label">Region</span>
                        <span className="mobile-company-detail-value">{c.region || '-'}</span>
                      </div>
                      <div className="mobile-company-detail">
                        <span className="mobile-company-detail-label">Industry Matrix Sector</span>
                        <span className="mobile-company-detail-value">{c.im_sector || '-'}</span>
                      </div>
                      <div className="mobile-company-detail">
                        <span className="mobile-company-detail-label">Industry</span>
                        <span className="mobile-company-detail-value">{c.industry || '-'}</span>
                      </div>
                      <div className="mobile-company-detail">
                        <span className="mobile-company-detail-label">Market Cap (USD M)</span>
                        <span className="mobile-company-detail-value">
                          {typeof (c as Record<string, unknown>).market_cap_usd === 'number'
                            ? ((c as Record<string, unknown>).market_cap_usd as number).toLocaleString('en-US', { maximumFractionDigits: 0 })
                            : '-'}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <Pagination page={page} pages={pages} onPageChange={setPage} />
            </div>
          )}
        </div>
      </div>
    </>
  );
}

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Root element not found');
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <BrowserPage />
  </React.StrictMode>
);
