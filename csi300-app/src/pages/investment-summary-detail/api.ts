import { InvestmentSummary } from './types';
import { logger } from '@shared/lib/logger';

const API_BASE = (import.meta.env.VITE_API_BASE || 'http://localhost:8001').replace(/\/$/, '');

export async function fetchInvestmentSummary(companyId: string): Promise<InvestmentSummary> {
  const log = logger.startTrace().withContext({ companyId, operation: 'fetchInvestmentSummary' });
  const url = `${API_BASE}/api/csi300/api/companies/${companyId}/investment_summary/`;
  
  log.info(`Fetching summary`, { url });

  try {
  const res = await fetch(url, {
    headers: { 
      'Content-Type': 'application/json', 
        'X-Requested-With': 'XMLHttpRequest',
        'X-Trace-ID': log.getTraceId() || ''
    }
  });
  
  if (!res.ok) {
      const errorText = await res.text();
      log.error(`API Error: ${res.status}`, { status: res.status, statusText: res.statusText, body: errorText });
    throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  }
  
    const data = await res.json();
    
    // 记录关键数据结构，帮助排查渲染为空的问题
    log.info('Summary fetched successfully', { 
      dataKeys: Object.keys(data),
      businessOverviewLength: data.business_overview?.length || 0,
      recommendedAction: data.recommended_action
    });
    
    return data;
  } catch (error) {
    log.error('Fetch failed', { error });
    throw error;
  }
}

export interface GenerateSummaryResponse {
  status: 'success' | 'error';
  message: string;
  data?: {
    company_id: number;
    company_name: string;
    ticker?: string;
    duration?: number;
    summary_exists?: boolean;
  };
}

export async function generateInvestmentSummary(companyId: string): Promise<GenerateSummaryResponse> {
  const log = logger.startTrace().withContext({ companyId, operation: 'generateInvestmentSummary' });
  const url = `${API_BASE}/api/csi300/api/generate-summary/`;
  
  log.info(`Triggering generation`, { url });

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json', 
        'X-Requested-With': 'XMLHttpRequest',
        'X-Trace-ID': log.getTraceId() || ''
      },
      body: JSON.stringify({ company_id: parseInt(companyId, 10) })
    });
    
    const data = await res.json();
    
    if (!res.ok) {
      log.error(`Generation API Error: ${res.status}`, { data });
      throw new Error(data.message || `HTTP ${res.status}: ${res.statusText}`);
    }
    
    log.info('Generation completed', { status: data.status, duration: data.data?.duration });
    return data;
  } catch (error) {
    log.error('Generation failed', { error });
    throw error;
  }
}

