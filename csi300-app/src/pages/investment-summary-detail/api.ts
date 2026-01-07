/**
 * @fileoverview Investment Summary Detail Page API
 * @module pages/investment-summary-detail/api
 *
 * This module provides API functions for the Investment Summary Detail page.
 * It uses generated types from OpenAPI codegen while maintaining custom
 * polling logic with exponential backoff for async task management.
 */

import { logger } from '@shared/lib/logger';
import {
  Csi300Service,
  GenerationTaskStatusResponse,
  type CSI300InvestmentSummary,
  type GenerationTaskStartResponse,
} from '@shared/api/generated';

// Re-export the generated type for use by components
export type { CSI300InvestmentSummary as InvestmentSummary } from '@shared/api/generated';

// TaskStatusEnum is now GenerationTaskStatusResponse.task_status
export const TaskStatusEnum = GenerationTaskStatusResponse.task_status;

// Note: OpenAPI.BASE is configured in main.tsx before this module is imported
// Csi300Service now generates paths with /api prefix (after removing legacy route)

// ==========================================
// Type aliases for backward compatibility
// ==========================================

export type TaskStatus = `${typeof TaskStatusEnum[keyof typeof TaskStatusEnum]}`;

export type StartTaskResponse = GenerationTaskStartResponse;

export type TaskStatusResponse = GenerationTaskStatusResponse;

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
// Polling configuration
// ==========================================

const POLL_INTERVAL_MS = 2000; // 2 seconds polling interval
const MAX_POLL_ATTEMPTS = 180; // Maximum attempts (6 minutes total)

/**
 * Fetch Investment Summary for a company
 *
 * Uses the generated Csi300Service with tracing context.
 *
 * @param companyId - Company ID (string will be converted to number)
 * @returns Promise resolving to investment summary data
 */
export async function fetchInvestmentSummary(
  companyId: string
): Promise<CSI300InvestmentSummary> {
  const trace = logger.startTrace().withContext({
    page: 'investment-summary-detail',
    operation: 'fetchInvestmentSummary',
  });

  const span = trace.startSpan('api.fetchInvestmentSummary', {
    companyId,
    method: 'GET',
  });

  try {
    span.addEvent('request_start');

    // Use generated service
    const data = await Csi300Service.apiCsi300ApiCompaniesInvestmentSummaryRetrieve(
      Number(companyId)
    );

    span.addEvent('response_received', {
      dataKeys: Object.keys(data).length,
      hasBusinessOverview: !!data.business_overview,
    });

    span.end({
      status: 'success',
      businessOverviewLength: data.business_overview?.length || 0,
      recommendedAction: data.recommended_action,
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
 * Start an async generation task
 *
 * @internal
 */
async function startGenerationTask(
  companyId: string,
  trace: ReturnType<typeof logger.startTrace>
): Promise<GenerationTaskStartResponse> {
  trace.info('[Starting generation task]', { companyId });

  // Use generated service
  const response = await Csi300Service.apiCsi300ApiGenerateSummaryCreate({
    company_id: Number(companyId),
  });

  return response;
}

/**
 * Poll task status
 *
 * @internal
 */
async function fetchTaskStatus(
  taskId: string,
  trace: ReturnType<typeof logger.startTrace>
): Promise<GenerationTaskStatusResponse> {
  // Use generated service
  return await Csi300Service.apiCsi300ApiTaskStatusRetrieve(taskId);
}

/**
 * Delay helper for polling
 */
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Generate Investment Summary with async polling
 *
 * Workflow:
 * 1. Send generation request, backend returns task_id immediately
 * 2. Poll task-status API until completion
 * 3. Return final result
 *
 * @param companyId - Company ID
 * @param onProgress - Optional progress callback
 * @returns Promise resolving to generation result
 */
export async function generateInvestmentSummary(
  companyId: string,
  onProgress?: (percent: number, message: string) => void
): Promise<GenerateSummaryResponse> {
  const trace = logger.startTrace().withContext({
    page: 'investment-summary-detail',
    operation: 'generateInvestmentSummary',
  });

  const span = trace.startSpan('api.generateSummary', {
    companyId,
    method: 'POST (async)',
  });

  try {
    // Step 1: Start task
    span.addEvent('task_start', { companyId });
    const startResponse = await startGenerationTask(companyId, trace);

    if (!startResponse.task_id) {
      throw new Error('No task_id returned from server');
    }

    const taskId = startResponse.task_id;
    span.addEvent('task_created', { taskId });
    trace.info('[Task Started]', { taskId, companyId });

    // Report initial progress
    onProgress?.(
      startResponse.progress_percent || 0,
      startResponse.progress_message || '任务已启动...'
    );

    // Step 2: Poll task status
    let attempts = 0;
    let lastStatus: GenerationTaskStatusResponse | null = null;

    while (attempts < MAX_POLL_ATTEMPTS) {
      attempts++;
      await delay(POLL_INTERVAL_MS);

      try {
        lastStatus = await fetchTaskStatus(taskId, trace);

        // Report progress
        onProgress?.(lastStatus.progress_percent, lastStatus.progress_message);

        span.addEvent('poll', {
          attempt: attempts,
          status: lastStatus.task_status,
          percent: lastStatus.progress_percent,
        });

        // Check if completed
        if (lastStatus.task_status === TaskStatusEnum.COMPLETED) {
          span.addEvent('task_completed');
          span.end({
            status: 'success',
            taskId,
            attempts,
            companyName: lastStatus.company_name,
          });

          trace.info('[Generation Complete]', {
            taskId,
            companyId,
            companyName: lastStatus.company_name,
            attempts,
          });

          return {
            status: 'success',
            message: '生成完成',
            data: {
              company_id: lastStatus.company_id,
              company_name: lastStatus.company_name,
              ticker: lastStatus.company_ticker,
              summary_exists: true,
            },
          };
        }

        // Check if failed
        if (lastStatus.task_status === TaskStatusEnum.FAILED) {
          const errorMsg = lastStatus.error || '生成失败';
          span.addEvent('task_failed', { error: errorMsg });
          span.end({ status: 'error', error: errorMsg });
          throw new Error(errorMsg);
        }
      } catch (pollError) {
        // Single poll failure shouldn't terminate immediately
        span.addEvent('poll_error', {
          attempt: attempts,
          error:
            pollError instanceof Error ? pollError.message : String(pollError),
        });

        // If task has failed, throw the error
        if (
          pollError instanceof Error &&
          pollError.message !== 'Network error'
        ) {
          throw pollError;
        }
      }
    }

    // Exceeded max poll attempts
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
 * Create a traced API client for complex scenarios
 * where multiple API calls need to share the same trace context
 */
export function createTracedApiClient(context: Record<string, unknown> = {}) {
  const trace = logger.startTrace().withContext({
    page: 'investment-summary-detail',
    ...context,
  });

  return {
    trace,
    getTraceId: () => trace.getTraceId(),
    getHeaders: () => trace.getTraceHeaders(),

    /**
     * Fetch investment summary with tracing
     */
    async fetchInvestmentSummary(
      companyId: string
    ): Promise<CSI300InvestmentSummary> {
      return trace.traceAsync(
        'fetchInvestmentSummary',
        () =>
          Csi300Service.apiCsi300ApiCompaniesInvestmentSummaryRetrieve(
            Number(companyId)
          ),
        { companyId }
      );
    },

    /**
     * Generate summary with tracing
     */
    async generateSummary(
      companyId: string,
      onProgress?: (percent: number, message: string) => void
    ): Promise<GenerateSummaryResponse> {
      return generateInvestmentSummary(companyId, onProgress);
    },
  };
}
