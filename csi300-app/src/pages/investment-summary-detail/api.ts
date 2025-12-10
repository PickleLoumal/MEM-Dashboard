import { InvestmentSummary } from './types';
import { logger, Span } from '@shared/lib/logger';

// 生产环境使用 /api（CloudFront 代理 /api/* -> ALB），开发环境默认 localhost:8001
const API_BASE = (import.meta.env.VITE_API_BASE ?? (import.meta.env.MODE === 'development' ? 'http://localhost:8001' : '/api')).replace(/\/$/, '');

/**
 * 获取公司的 Investment Summary
 * 
 * 完整追踪链路：
 * 1. 前端创建 trace + span
 * 2. 通过 X-Trace-ID header 传递到后端
 * 3. 后端日志会带上同样的 trace_id
 * 4. 可以通过 trace_id 关联前后端日志
 */
export async function fetchInvestmentSummary(companyId: string): Promise<InvestmentSummary> {
  // 创建追踪上下文
  const trace = logger.startTrace().withContext({ 
    page: 'investment-summary-detail',
    operation: 'fetchInvestmentSummary' 
  });
  
  const url = `${API_BASE}/csi300/api/companies/${companyId}/investment_summary/`;
  
  // 创建 span 追踪这次 API 调用
  const span = trace.startSpan('http.fetch', { 
    companyId, 
    url,
    method: 'GET'
  });

  try {
    span.addEvent('request_start');
    
    const res = await fetch(url, {
      headers: { 
        'Content-Type': 'application/json', 
        'X-Requested-With': 'XMLHttpRequest',
        // 传递 trace context 到后端
        ...trace.getTraceHeaders()
      }
    });
    
    span.addEvent('response_received', { status: res.status });
    
    if (!res.ok) {
      const errorText = await res.text();
      span.setAttribute('error.status', res.status);
      span.setAttribute('error.body', errorText.slice(0, 200));
      span.end({ status: 'error', httpStatus: res.status });
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    
    const data = await res.json();
    
    span.addEvent('json_parsed', { 
      dataKeys: Object.keys(data).length,
      hasBusinessOverview: !!data.business_overview 
    });
    
    // 记录成功
    span.end({ 
      status: 'success',
      httpStatus: res.status,
      businessOverviewLength: data.business_overview?.length || 0,
      recommendedAction: data.recommended_action
    });
    
    return data;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    span.addEvent('error', { message: errorMessage });
    span.end({ status: 'error', error: errorMessage });
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

/**
 * 触发生成 Investment Summary
 * 
 * 这是一个长时间运行的操作，会调用 AI 服务
 * 追踪链路可以帮助排查：
 * - AI 调用耗时
 * - 数据库保存耗时
 * - 超时或失败的原因
 */
export async function generateInvestmentSummary(companyId: string): Promise<GenerateSummaryResponse> {
  // 创建追踪上下文
  const trace = logger.startTrace().withContext({ 
    page: 'investment-summary-detail',
    operation: 'generateInvestmentSummary' 
  });
  
  const url = `${API_BASE}/csi300/api/generate-summary/`;
  
  // 创建 span 追踪生成操作
  const span = trace.startSpan('api.generateSummary', { 
    companyId,
    url,
    method: 'POST'
  });

  try {
    span.addEvent('request_start', { companyId });
    
    const res = await fetch(url, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json', 
        'X-Requested-With': 'XMLHttpRequest',
        // 传递 trace context 到后端
        ...trace.getTraceHeaders()
      },
      body: JSON.stringify({ company_id: parseInt(companyId, 10) })
    });
    
    span.addEvent('response_received', { status: res.status });
    
    const data = await res.json();
    
    if (!res.ok) {
      span.setAttribute('error.status', res.status);
      span.setAttribute('error.message', data.message || 'Unknown error');
      span.end({ status: 'error', httpStatus: res.status, message: data.message });
      throw new Error(data.message || `HTTP ${res.status}: ${res.statusText}`);
    }
    
    // 记录成功
    span.end({ 
      status: 'success',
      httpStatus: res.status,
      generationStatus: data.status,
      duration: data.data?.duration,
      companyName: data.data?.company_name
    });
    
    trace.info('[Generation Complete]', {
      companyId,
      companyName: data.data?.company_name,
      duration: `${data.data?.duration?.toFixed(2)}s`
    });
    
    return data;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    span.addEvent('error', { message: errorMessage });
    span.end({ status: 'error', error: errorMessage });
    throw error;
  }
}

/**
 * 创建一个带追踪的 API 客户端
 * 用于更复杂的场景，需要在多个 API 调用之间共享同一个 trace
 */
export function createTracedApiClient(context: Record<string, unknown> = {}) {
  const trace = logger.startTrace().withContext({
    page: 'investment-summary-detail',
    ...context
  });
  
  return {
    trace,
    getTraceId: () => trace.getTraceId(),
    getHeaders: () => trace.getTraceHeaders(),
    
    /**
     * 追踪一个 fetch 请求
     */
    async tracedFetch<T>(
      url: string, 
      options: RequestInit = {},
      spanName: string = 'http.fetch'
    ): Promise<T> {
      return trace.traceAsync(spanName, async () => {
        const res = await fetch(url, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...trace.getTraceHeaders(),
            ...options.headers,
          }
        });
        
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        }
        
        return res.json();
      }, { url, method: options.method || 'GET' });
    }
  };
}
