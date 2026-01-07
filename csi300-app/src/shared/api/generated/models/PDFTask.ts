/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Serializer for PDF task status responses.
 */
export type PDFTask = {
    /**
     * Unique task identifier
     */
    readonly task_id: string;
    /**
     * Company ticker symbol
     */
    readonly company_ticker: string;
    /**
     * Company name
     */
    readonly company_name: string;
    /**
     * Template display name
     */
    readonly template_name: string;
    /**
     * Current task status
     *
     * * `pending` - Pending
     * * `processing` - Processing
     * * `generating_charts` - Generating Charts
     * * `compiling` - Compiling LaTeX
     * * `uploading` - Uploading to S3
     * * `completed` - Completed
     * * `failed` - Failed
     */
    readonly status: PDFTask.status;
    /**
     * Human-readable status
     */
    readonly status_display: string;
    /**
     * Progress percentage (0-100)
     */
    readonly progress: number;
    /**
     * Error message if task failed
     */
    readonly error_message: string;
    /**
     * Pre-signed S3 download URL
     */
    readonly download_url: string;
    /**
     * Expiration time for the download URL
     */
    readonly download_url_expires_at: string | null;
    readonly created_at: string;
    /**
     * When task completed (success or failure)
     */
    readonly completed_at: string | null;
    /**
     * Total processing time in milliseconds
     */
    readonly processing_time_ms: number | null;
};
export namespace PDFTask {
    /**
     * Current task status
     *
     * * `pending` - Pending
     * * `processing` - Processing
     * * `generating_charts` - Generating Charts
     * * `compiling` - Compiling LaTeX
     * * `uploading` - Uploading to S3
     * * `completed` - Completed
     * * `failed` - Failed
     */
    export enum status {
        PENDING = 'pending',
        PROCESSING = 'processing',
        GENERATING_CHARTS = 'generating_charts',
        COMPILING = 'compiling',
        UPLOADING = 'uploading',
        COMPLETED = 'completed',
        FAILED = 'failed',
    }
}

