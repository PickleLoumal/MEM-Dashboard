/**
 * @fileoverview Type definitions for Investment Summary Detail page
 * @module pages/investment-summary-detail/types
 *
 * Re-exports auto-generated types from OpenAPI codegen.
 * This ensures frontend types stay in sync with backend API schema.
 */

// Re-export the auto-generated type from OpenAPI codegen
export type { CSI300InvestmentSummary as InvestmentSummary } from '@shared/api/generated';

// Re-export task-related types
export type {
  GenerationTaskStartResponse as StartTaskResponse,
  GenerationTaskStatusResponse as TaskStatusResponse,
} from '@shared/api/generated';

export { TaskStatusEnum } from '@shared/api/generated';

// Legacy type alias for backward compatibility
export type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed';
