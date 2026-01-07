/**
 * @fileoverview Type definitions for Investment Summary Detail page
 * @module pages/investment-summary-detail/types
 *
 * Re-exports auto-generated types from OpenAPI codegen.
 * This ensures frontend types stay in sync with backend API schema.
 */

// Re-export the auto-generated type from OpenAPI codegen
export type { CSI300InvestmentSummary as InvestmentSummary } from '@shared/api/generated';

// Re-export task-related types (AI generation)
export type {
  GenerationTaskStartResponse as StartTaskResponse,
  GenerationTaskStatusResponse as TaskStatusResponse,
} from '@shared/api/generated';

// TaskStatusEnum is now GenerationTaskStatusResponse.task_status
// Re-export is handled in api.ts

// Legacy type alias for backward compatibility
export type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed';

// ==========================================
// PDF Generation Types
// ==========================================

// Re-export PDF-related types from OpenAPI codegen
export type {
  PDFTask,
  PDFTaskCreateResponse,
  PDFRequest,
  PDFDownloadResponse,
  PDFTemplate,
  PDFTemplateDetail,
} from '@shared/api/generated';

// PDFTaskStatusEnum is now PDFTask.status
// Use: import { PDFTask } from '@shared/api/generated'; then PDFTask.status
