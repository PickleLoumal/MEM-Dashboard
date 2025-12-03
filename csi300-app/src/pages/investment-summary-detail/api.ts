import { InvestmentSummary } from './types';

const API_BASE = (import.meta.env.VITE_API_BASE || 'http://localhost:8001').replace(/\/$/, '');

export async function fetchInvestmentSummary(companyId: string): Promise<InvestmentSummary> {
  const url = `${API_BASE}/api/csi300/api/companies/${companyId}/investment_summary/`;
  const res = await fetch(url, {
    headers: { 
      'Content-Type': 'application/json', 
      'X-Requested-With': 'XMLHttpRequest' 
    }
  });
  
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  }
  
  return res.json();
}

