import { CompanyDetail, PeerComparisonData } from './types';

const API_BASE = (import.meta.env.VITE_API_BASE || 'http://localhost:8001').replace(/\/$/, '');
const COMPANY_DETAIL_ENDPOINT = '/api/csi300/api/companies/{id}/';
const PEERS_COMPARISON_ENDPOINT = '/api/csi300/api/companies/{id}/industry_peers_comparison/';

export async function fetchCompanyDetail(id: string): Promise<CompanyDetail> {
  const url = `${API_BASE}${COMPANY_DETAIL_ENDPOINT.replace('{id}', id)}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  return res.json();
}

export async function fetchPeersComparison(id: string): Promise<PeerComparisonData> {
  const url = `${API_BASE}${PEERS_COMPARISON_ENDPOINT.replace('{id}', id)}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  return res.json();
}

