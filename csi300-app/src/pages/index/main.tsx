import React, { useEffect, useMemo, useState } from 'react';
import ReactDOM from 'react-dom/client';
import { GlobalNav } from '@/components/GlobalNav';
import '@/styles/main.css';
import './styles.css';

type FilterOptionsResponse = {
  total_count?: number;
  company_count?: number;
  total_companies?: number;
  im_sectors?: string[];
  im_codes?: string[];
  industries?: string[];
};

type Filters = {
  im_sector: string;
  industry: string;
  company_search: string;
  industry_search: string;
};

const API_BASE = (import.meta.env.VITE_API_BASE || 'http://localhost:8001').replace(/\/$/, '');

function buildFilterOptionsUrl(params?: Record<string, string>) {
  const query = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value) query.append(key, value);
    });
  }
  const qs = query.toString();
  return `${API_BASE}/api/csi300/api/companies/filter_options/${qs ? `?${qs}` : ''}`;
}

async function fetchFilterOptions(params?: Record<string, string>): Promise<FilterOptionsResponse> {
  const url = buildFilterOptionsUrl(params);
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

function useFilterOptions(initialSector: string) {
  const [data, setData] = useState<FilterOptionsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    fetchFilterOptions(initialSector ? { im_sector: initialSector } : undefined)
      .then((res) => {
        if (ignore) return;
        setData(res);
        setError(null);
      })
      .catch((err: unknown) => {
        if (ignore) return;
        setError(err instanceof Error ? err.message : 'Failed to load filter options');
      })
      .finally(() => {
        if (ignore) return;
        setLoading(false);
      });

    return () => {
      ignore = true;
    };
  }, [initialSector]);

  return { data, loading, error };
}

function getTotalCount(data: FilterOptionsResponse | null) {
  if (!data) return null;
  return data.total_count ?? data.company_count ?? data.total_companies ?? null;
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

function FilterPage() {
  const [filters, setFilters] = useState<Filters>({
    im_sector: '',
    industry: '',
    company_search: '',
    industry_search: ''
  });
  const [industryOptions, setIndustryOptions] = useState<string[]>([]);
  const [industryLoading, setIndustryLoading] = useState(false);
  const { data, loading, error } = useFilterOptions(filters.im_sector);

  const totalCount = useMemo(() => getTotalCount(data), [data]);
  const sectorOptions = useMemo(() => deriveSectors(data), [data]);

  useEffect(() => {
    document.title = 'Chinese Stock Dashboard - Company Filter';
  }, []);

  useEffect(() => {
    setIndustryOptions(deriveIndustries(data));
  }, [data]);

  const onChange = (field: keyof Filters) => (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) =>
    setFilters((prev) => ({ ...prev, [field]: e.target.value }));

  // In Vite dev mode, pages are at /src/pages/xxx/index.html
  // In production build, they're at /xxx.html (or configured output)
  const getBrowserPath = () => {
    const isDev = import.meta.env.DEV;
    return isDev ? '/src/pages/browser/index.html' : '/browser.html';
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const query = new URLSearchParams();
    (Object.keys(filters) as (keyof Filters)[]).forEach((key) => {
      const value = filters[key].trim();
      if (value) query.append(key, value);
    });
    const browserPath = getBrowserPath();
    const target = query.toString() ? `${browserPath}?${query.toString()}` : browserPath;
    window.location.href = target;
  };

  const handleClear = () => {
    window.location.href = getBrowserPath();
  };

  const handleSectorChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setFilters((prev) => ({ ...prev, im_sector: value, industry: '' }));
    setIndustryLoading(true);
    try {
      const res = await fetchFilterOptions(value ? { im_sector: value } : undefined);
      setIndustryOptions(deriveIndustries(res));
    } catch (err) {
      // Keep previous options on error
      console.error('Failed to load industry options', err);
    } finally {
      setIndustryLoading(false);
    }
  };

  return (
    <>
      <GlobalNav />
      <main className="page-shell app-shell">
        <div className="page-header">
        <h1 className="page-title">Chinese Stock Dashboard</h1>
        <p className="page-subtitle">Filter and browse Chinese stock companies</p>
      </div>

      <div className="filter-card-wrapper">
        <div className="filter-container app-card">
          <p className="total-count" id="totalCount">
            {loading ? 'Loading total count...' : totalCount ? `Total ${totalCount} companies in database` : 'Chinese Stock Dashboard filters ready'}
          </p>

          {error ? <div className="error app-notice">{error}</div> : null}

          <form className="filter-form" onSubmit={handleSubmit}>
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
                    <option value={sector} key={sector}>
                      {sector}
                    </option>
                  ))}
                </select>
              </div>

              <div className="filter-group app-form-field">
                <label className="filter-label app-label">Industry within selected sector</label>
                <select
                  name="industry"
                  value={filters.industry}
                  onChange={onChange('industry')}
                  className="filter-select app-select"
                  disabled={industryLoading}
                >
                  <option value="">{industryLoading ? 'Loading...' : 'All Industries'}</option>
                  {industryOptions.map((industry) => (
                    <option value={industry} key={industry}>
                      {industry}
                    </option>
                  ))}
                </select>
              </div>

              <div className="filter-group app-form-field">
                <label className="filter-label app-label">Search Companies</label>
                <input
                  type="text"
                  name="company_search"
                  value={filters.company_search}
                  onChange={onChange('company_search')}
                  className="filter-input app-input"
                  placeholder="Search by company name or ticker..."
                />
              </div>

              <div className="filter-group app-form-field">
                <label className="filter-label app-label">Search by Industry</label>
                <input
                  type="text"
                  name="industry_search"
                  value={filters.industry_search}
                  onChange={onChange('industry_search')}
                  className="filter-input app-input"
                  placeholder="Search by industry name..."
                />
              </div>
            </div>

            <div className="filter-actions app-actions app-actions--center">
              <button type="button" onClick={handleClear} className="btn btn-secondary app-button app-button--secondary">
                Clear Filters
              </button>
              <button type="submit" className="btn btn-primary app-button app-button--primary">
                Apply Filters
              </button>
            </div>
          </form>
        </div>
        </div>
      </main>
    </>
  );
}

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Root element not found');
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <FilterPage />
  </React.StrictMode>
);
