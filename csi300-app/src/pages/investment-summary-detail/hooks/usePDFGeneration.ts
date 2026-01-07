/**
 * @fileoverview PDF Generation Hook with WebSocket Support
 * @module pages/investment-summary-detail/hooks/usePDFGeneration
 *
 * Provides real-time PDF generation status via WebSocket connection.
 * Falls back to polling if WebSocket is unavailable.
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { logger } from '@shared/lib/logger';
import {
  PdfService,
  PDFTask,
  type PDFTaskCreateResponse,
} from '@shared/api/generated';

// PDFTaskStatusEnum is now PDFTask.status
const PDFTaskStatusEnum = PDFTask.status;

// ==========================================
// Types
// ==========================================

export interface PDFGenerationState {
  /** Whether generation is in progress */
  isGenerating: boolean;
  /** Current task ID */
  taskId: string | null;
  /** Current status */
  status: PDFTask.status | null;
  /** Human-readable status */
  statusDisplay: string;
  /** Progress percentage (0-100) */
  progress: number;
  /** Error message if failed */
  errorMessage: string | null;
  /** Download URL when completed */
  downloadUrl: string | null;
}

export interface UsePDFGenerationOptions {
  /** Company ID for PDF generation */
  companyId: number;
  /** Callback when PDF is ready */
  onComplete?: (downloadUrl: string) => void;
  /** Callback on error */
  onError?: (error: string) => void;
}

export interface UsePDFGenerationReturn extends PDFGenerationState {
  /** Start PDF generation */
  startGeneration: () => Promise<void>;
  /** Cancel/reset generation state */
  cancel: () => void;
}

// ==========================================
// WebSocket Message Types
// ==========================================

/**
 * WebSocket status update message from Django Channels consumer.
 * Matches the format sent by pdf_service/consumers.py
 */
interface WebSocketStatusMessage {
  type: 'status_update' | 'initial_status' | 'pong';
  status: PDFTask.status;
  status_display: string;
  progress: number;
  error_message?: string;
  download_url?: string;
}

// ==========================================
// Status Display Mapping
// ==========================================

const STATUS_MESSAGES: Record<PDFTask.status, string> = {
  [PDFTaskStatusEnum.PENDING]: 'Preparing...',
  [PDFTaskStatusEnum.PROCESSING]: 'Processing data...',
  [PDFTaskStatusEnum.GENERATING_CHARTS]: 'Generating charts...',
  [PDFTaskStatusEnum.COMPILING]: 'Compiling report...',
  [PDFTaskStatusEnum.UPLOADING]: 'Uploading...',
  [PDFTaskStatusEnum.COMPLETED]: 'Ready for download',
  [PDFTaskStatusEnum.FAILED]: 'Generation failed',
};

// ==========================================
// Constants
// ==========================================

const POLL_INTERVAL_MS = 2000;
const MAX_POLL_ATTEMPTS = 150; // 5 minutes timeout

// ==========================================
// Hook Implementation
// ==========================================

export function usePDFGeneration(
  options: UsePDFGenerationOptions
): UsePDFGenerationReturn {
  const { companyId, onComplete, onError } = options;

  // State
  const [state, setState] = useState<PDFGenerationState>({
    isGenerating: false,
    taskId: null,
    status: null,
    statusDisplay: '',
    progress: 0,
    errorMessage: null,
    downloadUrl: null,
  });

  // Refs for cleanup and avoiding stale closures
  const wsRef = useRef<WebSocket | null>(null);
  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const pollAttemptsRef = useRef(0);
  const stateRef = useRef(state); // Ref to always have latest state in callbacks

  // Keep stateRef in sync with state
  useEffect(() => {
    stateRef.current = state;
  }, [state]);

  // Cleanup function
  const cleanup = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
    pollAttemptsRef.current = 0;
  }, []);

  // Cleanup on unmount
  useEffect(() => cleanup, [cleanup]);

  // Handle status update (from WebSocket or polling)
  const handleStatusUpdate = useCallback(
    (task: PDFTask | WebSocketStatusMessage) => {
      const status = 'type' in task ? task.status : task.status;
      const progress = task.progress;
      const statusDisplay =
        'status_display' in task
          ? task.status_display
          : STATUS_MESSAGES[status] || status;
      const errorMessage =
        'error_message' in task ? task.error_message : task.error_message;
      const downloadUrl =
        'download_url' in task ? task.download_url : task.download_url;

      setState((prev) => ({
        ...prev,
        status,
        statusDisplay,
        progress,
        errorMessage: errorMessage || null,
        downloadUrl: downloadUrl || null,
      }));

      // Handle completion
      if (status === PDFTaskStatusEnum.COMPLETED && downloadUrl) {
        cleanup();
        setState((prev) => ({ ...prev, isGenerating: false }));
        onComplete?.(downloadUrl);
      }

      // Handle failure
      if (status === PDFTaskStatusEnum.FAILED) {
        cleanup();
        setState((prev) => ({ ...prev, isGenerating: false }));
        onError?.(errorMessage || 'PDF generation failed');
      }
    },
    [cleanup, onComplete, onError]
  );

  // Start polling fallback
  const startPolling = useCallback(
    (taskId: string) => {
      const trace = logger.startTrace().withContext({ taskId, mode: 'polling' });
      trace.info('[PDF] Starting polling fallback');

      pollIntervalRef.current = setInterval(async () => {
        pollAttemptsRef.current++;

        if (pollAttemptsRef.current > MAX_POLL_ATTEMPTS) {
          cleanup();
          setState((prev) => ({
            ...prev,
            isGenerating: false,
            errorMessage: 'Generation timed out',
          }));
          onError?.('PDF generation timed out');
          return;
        }

        try {
          const status = await PdfService.apiPdfTasksStatusRetrieve(taskId);
          handleStatusUpdate(status);
        } catch (err) {
          trace.warn('[PDF] Poll error', { attempt: pollAttemptsRef.current, err });
          // Don't fail on single poll error
        }
      }, POLL_INTERVAL_MS);
    },
    [cleanup, handleStatusUpdate, onError]
  );

  // Connect WebSocket
  const connectWebSocket = useCallback(
    (wsUrl: string, taskId: string) => {
      const trace = logger.startTrace().withContext({ taskId, mode: 'websocket' });
      trace.info('[PDF] Connecting WebSocket', { wsUrl });

      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          trace.info('[PDF] WebSocket connected');
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data) as WebSocketStatusMessage;
            // Ignore pong messages (heartbeat responses)
            if (data.type === 'pong') return;
            trace.debug('[PDF] WebSocket message', { data });
            handleStatusUpdate(data);
          } catch (parseErr) {
            trace.warn('[PDF] Failed to parse WebSocket message', { parseErr });
          }
        };

        ws.onerror = (err) => {
          trace.warn('[PDF] WebSocket error, falling back to polling', { err });
          ws.close();
          startPolling(taskId);
        };

        ws.onclose = (event) => {
          trace.info('[PDF] WebSocket closed', {
            code: event.code,
            reason: event.reason,
          });
          // Use ref to get latest state (avoid stale closure)
          const currentState = stateRef.current;
          // If not completed/failed, switch to polling
          if (currentState.isGenerating && !currentState.downloadUrl && !currentState.errorMessage) {
            startPolling(taskId);
          }
        };
      } catch (err) {
        trace.warn('[PDF] Failed to create WebSocket, using polling', { err });
        startPolling(taskId);
      }
    },
    [handleStatusUpdate, startPolling]
  );

  // Start PDF generation
  const startGeneration = useCallback(async () => {
    // Early validation - prevent invalid requests
    if (!companyId || companyId <= 0) {
      const errorMessage = 'Invalid company ID';
      setState((prev) => ({
        ...prev,
        isGenerating: false,
        errorMessage,
      }));
      onError?.(errorMessage);
      return;
    }

    const trace = logger.startTrace().withContext({ companyId });
    trace.info('[PDF] Starting generation');

    // Reset state
    setState({
      isGenerating: true,
      taskId: null,
      status: PDFTaskStatusEnum.PENDING,
      statusDisplay: STATUS_MESSAGES[PDFTaskStatusEnum.PENDING],
      progress: 0,
      errorMessage: null,
      downloadUrl: null,
    });

    try {
      // Request PDF generation
      const response: PDFTaskCreateResponse =
        await PdfService.apiPdfTasksRequestCreate({
          company_id: companyId,
        });

      trace.info('[PDF] Task created', {
        taskId: response.task_id,
        wsUrl: response.websocket_url,
      });

      setState((prev) => ({
        ...prev,
        taskId: response.task_id,
      }));

      // Try WebSocket first, fall back to polling
      if (response.websocket_url) {
        connectWebSocket(response.websocket_url, response.task_id);
      } else {
        startPolling(response.task_id);
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to start PDF generation';
      trace.error('[PDF] Failed to start generation', { err });

      setState((prev) => ({
        ...prev,
        isGenerating: false,
        errorMessage,
      }));
      onError?.(errorMessage);
    }
  }, [companyId, connectWebSocket, startPolling, onError]);

  // Validate companyId on mount
  useEffect(() => {
    if (companyId <= 0) {
      logger.startTrace().warn('[PDF] Hook initialized with invalid companyId', { companyId });
    }
  }, [companyId]);

  // Cancel generation
  const cancel = useCallback(() => {
    cleanup();
    setState({
      isGenerating: false,
      taskId: null,
      status: null,
      statusDisplay: '',
      progress: 0,
      errorMessage: null,
      downloadUrl: null,
    });
  }, [cleanup]);

  return {
    ...state,
    startGeneration,
    cancel,
  };
}

export default usePDFGeneration;

