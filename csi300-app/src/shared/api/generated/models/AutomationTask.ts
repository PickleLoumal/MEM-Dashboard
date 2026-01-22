/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Serializer for AutomationTask model.
 * Used for task status responses in all automation endpoints.
 */
export type AutomationTask = {
    readonly id: number;
    /**
     * Type of automation task: daily_briefing or forensic_accounting
     *
     * * `daily_briefing` - Daily Briefing
     * * `forensic_accounting` - Forensic Accounting
     */
    task_type: AutomationTask.task_type;
    readonly celery_task_id: string | null;
    /**
     * Current task status: pending, scraping, waiting_stage2, generating, uploading, completed, or failed
     *
     * * `pending` - Pending
     * * `scraping` - Scraping Data
     * * `waiting_stage2` - Waiting for Stage 2
     * * `generating` - Generating Report
     * * `uploading` - Uploading
     * * `completed` - Completed
     * * `failed` - Failed
     */
    readonly status: AutomationTask.status;
    readonly started_at: string | null;
    readonly stage1_completed_at: string | null;
    readonly stage2_scheduled_at: string | null;
    /**
     * Seconds remaining until Stage 2 starts (only present when status is waiting_stage2)
     */
    readonly stage2_countdown_remaining: number;
    readonly completed_at: string | null;
    readonly error_message: string | null;
    readonly result_urls: any;
    readonly created_by: string;
    readonly created_at: string;
};
export namespace AutomationTask {
    /**
     * Type of automation task: daily_briefing or forensic_accounting
     *
     * * `daily_briefing` - Daily Briefing
     * * `forensic_accounting` - Forensic Accounting
     */
    export enum task_type {
        DAILY_BRIEFING = 'daily_briefing',
        FORENSIC_ACCOUNTING = 'forensic_accounting',
    }
    /**
     * Current task status: pending, scraping, waiting_stage2, generating, uploading, completed, or failed
     *
     * * `pending` - Pending
     * * `scraping` - Scraping Data
     * * `waiting_stage2` - Waiting for Stage 2
     * * `generating` - Generating Report
     * * `uploading` - Uploading
     * * `completed` - Completed
     * * `failed` - Failed
     */
    export enum status {
        PENDING = 'pending',
        SCRAPING = 'scraping',
        WAITING_STAGE2 = 'waiting_stage2',
        GENERATING = 'generating',
        UPLOADING = 'uploading',
        COMPLETED = 'completed',
        FAILED = 'failed',
    }
}

