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

// ==========================================
// 异步生成任务类型定义
// ==========================================

export type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface StartTaskResponse {
  status: 'accepted' | 'error';
  message: string;
  task_id?: string;
  task_status?: TaskStatus;
  progress_percent?: number;
  progress_message?: string;
}

export interface TaskStatusResponse {
  status: 'success' | 'error';
  task_id: string;
  task_status: TaskStatus;
  progress_percent: number;
  progress_message: string;
  company_id: number;
  company_name: string;
  company_ticker: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  result?: Record<string, unknown>;
  error?: string;
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

// ==========================================
// 轮询配置
// ==========================================

const POLL_INTERVAL_MS = 2000; // 2秒轮询一次
const MAX_POLL_ATTEMPTS = 180; // 最大轮询次数 (6分钟)

/**
 * 启动异步生成任务
 */
async function startGenerationTask(companyId: string, trace: ReturnType<typeof logger.startTrace>): Promise<StartTaskResponse> {
  const url = `${API_BASE}/csi300/api/generate-summary/`;

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
      ...trace.getTraceHeaders()
    },
    body: JSON.stringify({ company_id: parseInt(companyId, 10) })
  });

  const data = await res.json();

  if (!res.ok && res.status !== 202) {
    throw new Error(data.message || `HTTP ${res.status}: ${res.statusText}`);
  }

  return data;
}

/**
 * 查询任务状态
 */
async function fetchTaskStatus(taskId: string, trace: ReturnType<typeof logger.startTrace>): Promise<TaskStatusResponse> {
  const url = `${API_BASE}/csi300/api/task-status/${taskId}/`;

  const res = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
      ...trace.getTraceHeaders()
    }
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.message || `HTTP ${res.status}: ${res.statusText}`);
  }

  return data;
}

/**
 * 等待指定毫秒数
 */
function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 触发生成 Investment Summary（异步轮询模式）
 *
 * 工作流程：
 * 1. 发起生成请求，后端立即返回 task_id
 * 2. 轮询 task-status API 直到任务完成
 * 3. 返回最终结果
 *
 * @param companyId 公司 ID
 * @param onProgress 可选的进度回调函数
 */
export async function generateInvestmentSummary(
  companyId: string,
  onProgress?: (percent: number, message: string) => void
): Promise<GenerateSummaryResponse> {
  // 创建追踪上下文
  const trace = logger.startTrace().withContext({
    page: 'investment-summary-detail',
    operation: 'generateInvestmentSummary'
  });

  // 创建 span 追踪生成操作
  const span = trace.startSpan('api.generateSummary', {
    companyId,
    method: 'POST (async)'
  });

  try {
    // Step 1: 启动任务
    span.addEvent('task_start', { companyId });
    const startResponse = await startGenerationTask(companyId, trace);

    if (!startResponse.task_id) {
      throw new Error('No task_id returned from server');
    }

    const taskId = startResponse.task_id;
    span.addEvent('task_created', { taskId });
    trace.info('[Task Started]', { taskId, companyId });

    // 报告初始进度
    onProgress?.(startResponse.progress_percent || 0, startResponse.progress_message || '任务已启动...');

    // Step 2: 轮询任务状态
    let attempts = 0;
    let lastStatus: TaskStatusResponse | null = null;

    while (attempts < MAX_POLL_ATTEMPTS) {
      attempts++;
      await delay(POLL_INTERVAL_MS);

      try {
        lastStatus = await fetchTaskStatus(taskId, trace);

        // 报告进度
        onProgress?.(lastStatus.progress_percent, lastStatus.progress_message);

        span.addEvent('poll', {
          attempt: attempts,
          status: lastStatus.task_status,
          percent: lastStatus.progress_percent
        });

        // 检查是否完成
        if (lastStatus.task_status === 'completed') {
          span.addEvent('task_completed');
          span.end({
            status: 'success',
            taskId,
            attempts,
            companyName: lastStatus.company_name
          });

          trace.info('[Generation Complete]', {
            taskId,
            companyId,
            companyName: lastStatus.company_name,
            attempts
          });

          return {
            status: 'success',
            message: '生成完成',
            data: {
              company_id: lastStatus.company_id,
              company_name: lastStatus.company_name,
              ticker: lastStatus.company_ticker,
              summary_exists: true
            }
          };
        }

        // 检查是否失败
        if (lastStatus.task_status === 'failed') {
          const errorMsg = lastStatus.error || '生成失败';
          span.addEvent('task_failed', { error: errorMsg });
          span.end({ status: 'error', error: errorMsg });
          throw new Error(errorMsg);
        }

      } catch (pollError) {
        // 单次轮询失败不应立即终止，记录并继续
        span.addEvent('poll_error', {
          attempt: attempts,
          error: pollError instanceof Error ? pollError.message : String(pollError)
        });

        // 如果是任务已失败，则抛出错误
        if (pollError instanceof Error && pollError.message !== 'Network error') {
          throw pollError;
        }
      }
    }

    // 超过最大轮询次数
    const timeoutError = `任务超时：已等待 ${(MAX_POLL_ATTEMPTS * POLL_INTERVAL_MS) / 1000} 秒`;
    span.addEvent('timeout', { attempts });
    span.end({ status: 'error', error: timeoutError });
    throw new Error(timeoutError);

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
