import React, { useEffect, useMemo, useRef, useState } from 'react';
import ReactDOM from 'react-dom/client';
import { GlobalNav } from '@/components/GlobalNav';
import { Formatters, FieldMap, getCellClass } from '@/lib/column-manifest';
import '@/styles/main.css';
import './styles.css';

type FilterOptionsResponse = {
  total_count?: number;
  company_count?: number;
  total_companies?: number;
  im_sectors?: string[];
  im_codes?: string[];
  industries?: string[];
  regions?: string[];
  available_regions?: string[];
  region_options?: string[];
  region_counts?: Record<string, number>;
};

type Filters = {
  im_sector: string;
  industry: string;
  company_search: string;
  industry_search: string;
  region: string;
};

type Company = {
  id: number | string;
  name: string;
  ticker: string;
  region?: string;
  im_sector?: string;
  industry?: string;
  market_cap_usd?: number;
  price?: number;
  pe_ratio_trailing?: number;
  [key: string]: unknown;
};

type Column = {
  id: string;
  displayName: string;
  format?: string;
  align?: 'left' | 'right' | 'center';
  decimals?: number;
  colorize?: boolean;
  maxDisplay?: number;
  tooltip?: string;
};

const DEFAULT_COLUMNS: Column[] = [
  { id: 'name', displayName: 'Company Name', format: 'text-bold', align: 'left' },
  { id: 'ticker', displayName: 'Ticker', format: 'monospace', align: 'left' },
  { id: 'region', displayName: 'Region', format: 'text', align: 'left' },
  { id: 'im_sector', displayName: 'IM Sector', format: 'text', align: 'left' },
  { id: 'market_cap_usd', displayName: 'Market Cap (USD M)', align: 'right', format: 'currency-millions' },
  { id: 'price_local_currency', displayName: 'Price (Local)', align: 'right', format: 'currency' },
  { id: 'pe_ratio_trailing', displayName: 'P/E Ratio', align: 'right', format: 'number', decimals: 1 }
];

declare global {
  interface Window {
    CSI300ColumnManifest?: { columns: Column[]; presetViews?: { id: string; columns: string[]; pinnedColumns?: string[] }[] };
    CSI300ColumnSelector?: new (
      manifest: any,
      options: { container: string; onColumnChange: (data: { columns: Column[]; pinnedColumns: string[] }) => void }
    ) => { getSelectedColumns: () => Column[]; getPinnedColumns: () => Column[] };
  }
}

const API_BASE = (import.meta.env.VITE_API_BASE || 'http://localhost:8001').replace(/\/$/, '');
const FILTER_ENDPOINT = '/api/csi300/api/companies/filter_options/';
const COMPANIES_ENDPOINT = '/api/csi300/api/companies/';
const SEARCH_DEBOUNCE_MS = 300;

function buildFilterOptionsUrl(params?: Record<string, string>) {
  const query = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => value && query.append(key, value));
  }
  const qs = query.toString();
  return `${API_BASE}${FILTER_ENDPOINT}${qs ? `?${qs}` : ''}`;
}

async function fetchFilterOptions(params?: Record<string, string>): Promise<FilterOptionsResponse> {
  const res = await fetch(buildFilterOptionsUrl(params), {
    headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  return res.json();
}

async function fetchCompanies(filters: Partial<Filters> & { page: number; page_size: number }) {
  const qs = new URLSearchParams();
  if (filters.im_sector) qs.append('im_sector', filters.im_sector);
  if (filters.industry) qs.append('industry', filters.industry);
  if (filters.company_search) qs.append('search', filters.company_search);
  if (filters.industry_search) qs.append('industry_search', filters.industry_search);
  if (filters.region) qs.append('region', filters.region.replace(/\s*\(.*\)$/, ''));
  qs.append('page', String(filters.page));
  qs.append('page_size', String(filters.page_size));
  const url = `${API_BASE}${COMPANIES_ENDPOINT}?${qs.toString()}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  return res.json();
}

function deriveCount(data: FilterOptionsResponse | null) {
  if (!data) return null;
  return data.total_count ?? data.company_count ?? data.total_companies ?? null;
}

function dedupeSorted(values: string[] | undefined) {
  return Array.from(new Set((values || []).filter(Boolean))).sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
}

function deriveRegions(data: FilterOptionsResponse | null) {
  const set = new Set<string>();
  const pushArr = (arr?: string[]) => arr?.forEach((v) => v && set.add(v));
  if (data) {
    pushArr(data.regions);
    pushArr(data.available_regions);
    pushArr(data.region_options);
    if (data.region_counts) Object.keys(data.region_counts).forEach((r) => r && set.add(r));
  }
  if (!set.size) ['Mainland China', 'Hong Kong'].forEach((r) => set.add(r));
  return dedupeSorted(Array.from(set));
}

function deriveSectors(data: FilterOptionsResponse | null) {
  if (!data) return [];
  if (data.im_sectors?.length) return data.im_sectors;
  if (data.im_codes?.length) return data.im_codes;
  if (data.industries?.length) return data.industries;
  return [];
}

function deriveIndustries(data: FilterOptionsResponse | null) {
  if (!data) return [];
  if (data.industries?.length) return data.industries;
  if (data.im_sectors?.length) return data.im_sectors;
  if (data.im_codes?.length) return data.im_codes;
  return [];
}


function renderCellValue(column: Column, company: Company): React.ReactNode {
  const field = FieldMap[column.id] || column.id;
  let rawValue = company[field];
  
  // Fallback for sector
  if (column.id === 'sector' && !rawValue) {
    rawValue = company.industry || (company as any).im_code || '-';
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
  // Legacy behavior: colorize if column.colorize is true OR if it's price column
  if (column.colorize || (column.id.includes('price') && !column.id.includes('high') && !column.id.includes('low'))) {
      const num = parseFloat(String(rawValue));
      if (!isNaN(num)) {
        // Green for positive, Red for negative
        const color = num >= 0 ? '#059669' : '#dc2626';
        return <span style={{ color }}>{formatted}</span>;
      }
  }

  // Handle max display for large values
  if (column.maxDisplay && typeof rawValue === 'number' && rawValue > column.maxDisplay) {
      return <span title={`${formatted} - ${column.tooltip || 'Value exceeds display limit'}`}>{column.maxDisplay}+</span>;
  }

  // Chip format (legacy implementation was inline style)
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

function loadScript(src: string, attrs: Record<string, string> = {}) {
  return new Promise<void>((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = src;
    script.defer = true;
    Object.entries(attrs).forEach(([k, v]) => script.setAttribute(k, v));
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(`Failed to load ${src}`));
    document.body.appendChild(script);
  });
}

// GlobalNav 现在是 React 组件，不再需要动态加载脚本

// 分页组件 - 与旧版一致
function Pagination({ page, pages, onPageChange }: { page: number; pages: number; onPageChange: (p: number) => void }) {
  if (pages <= 1) return null;

  const maxPagesToShow = 5;
  let startPage = Math.max(1, page - Math.floor(maxPagesToShow / 2));
  let endPage = Math.min(pages, startPage + maxPagesToShow - 1);
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

function useColumnSelector(setColumns: (cols: Column[]) => void, setPinned: (ids: string[]) => void) {
  const initialized = useRef(false);
  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;
    (async () => {
      try {
        await loadScript('/config/column-manifest.js');
        await loadScript('/assets/js/components/column-selector.js');
        if (window.CSI300ColumnManifest && window.CSI300ColumnSelector) {
          const selector = new window.CSI300ColumnSelector(window.CSI300ColumnManifest, {
            container: '#columnSelectorContainer',
            onColumnChange: (data) => {
              setColumns(data.columns);
              setPinned(data.pinnedColumns);
            }
          });
          setColumns(selector.getSelectedColumns());
          setPinned(selector.getPinnedColumns().map((c) => c.id));
        }
      } catch (err) {
        console.error('Column selector load failed', err);
      }
    })();
  }, [setColumns, setPinned]);
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
  const [filterData, setFilterData] = useState<FilterOptionsResponse | null>(null);
  const [industryOptions, setIndustryOptions] = useState<string[]>([]);
  const [regions, setRegions] = useState<string[]>([]);
  const [loadingFilters, setLoadingFilters] = useState(false);

  const [companies, setCompanies] = useState<Company[]>([]);
  const [totalResults, setTotalResults] = useState(0);
  const [page, setPage] = useState(1);
  const pageSize = 20;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [columns, setColumns] = useState<Column[]>([]);
  const [pinnedColumns, setPinnedColumns] = useState<string[]>([]);
  useColumnSelector(setColumns, setPinnedColumns);

  // 初始解析 URL
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

  // 拉取筛选项
  useEffect(() => {
    let ignore = false;
    setLoadingFilters(true);
    fetchFilterOptions(filters.im_sector ? { im_sector: filters.im_sector } : undefined)
      .then((data) => {
        if (ignore) return;
        setFilterData(data);
        setIndustryOptions(deriveIndustries(data));
        setRegions(deriveRegions(data));
      })
      .catch((err) => {
        if (ignore) return;
        setError(err instanceof Error ? err.message : '筛选项加载失败');
      })
      .finally(() => {
        if (ignore) return;
        setLoadingFilters(false);
      });
    return () => {
      ignore = true;
    };
  }, [filters.im_sector]);

  // 拉取公司数据
  useEffect(() => {
    let ignore = false;
    setLoading(true);
    setError(null);
    fetchCompanies({ ...filters, page, page_size: pageSize })
      .then((res) => {
        if (ignore) return;
        if (Array.isArray(res)) {
          setCompanies(res);
          setTotalResults(res.length);
        } else if (res?.results) {
          setCompanies(res.results);
          setTotalResults(res.count || 0);
        } else {
          setError('Unexpected response format');
        }
      })
      .catch((err) => {
        if (ignore) return;
        setError(err instanceof Error ? err.message : '加载公司列表失败');
      })
      .finally(() => {
        if (ignore) return;
        setLoading(false);
      });
    return () => {
      ignore = true;
    };
  }, [filters, page]);

  const totalCount = useMemo(() => deriveCount(filterData), [filterData]);

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
      const res = await fetchFilterOptions(value ? { im_sector: value } : undefined);
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
      .filter(Boolean) as Column[];
    const rest = baseColumns.filter((c) => !pinnedColumns.includes(c.id));
    return [...pinned, ...rest];
  }, [columns, pinnedColumns]);

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
            <label className="filter-label app-label">IM Sector</label>
            <select
              name="im_sector"
              value={filters.im_sector}
              onChange={handleSectorChange}
              className="filter-select app-select"
            >
              <option value="">All IM Sectors</option>
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
            <label className="filter-label app-label">Search Companies</label>
            <input
              type="text"
              name="company_search"
              value={pendingCompanySearch}
              onChange={(e) => setPendingCompanySearch(e.target.value)}
              className="filter-input app-input"
              placeholder="Search by company name or ticker..."
            />
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
            <div id="columnSelectorContainer"></div>
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
                      <span className="mobile-company-detail-label">IM Sector</span>
                      <span className="mobile-company-detail-value">{c.im_sector || '-'}</span>
                    </div>
                    <div className="mobile-company-detail">
                      <span className="mobile-company-detail-label">Industry</span>
                      <span className="mobile-company-detail-value">{c.industry || '-'}</span>
                    </div>
                    <div className="mobile-company-detail">
                      <span className="mobile-company-detail-label">Market Cap (USD M)</span>
                      <span className="mobile-company-detail-value">
                        {typeof c.market_cap_usd === 'number'
                          ? c.market_cap_usd.toLocaleString('en-US', { maximumFractionDigits: 0 })
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
