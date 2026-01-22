/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * 任务状态查询响应序列化器
 *
 * 用于 GET /task-status/{task_id}/ 的响应
 */
export type GenerationTaskStatusResponse = {
    /**
     * API 响应状态
     *
     * * `success` - success
     * * `error` - error
     */
    status: GenerationTaskStatusResponse.status;
    /**
     * 任务 UUID
     */
    task_id: string;
    /**
     * 任务执行状态: pending, processing, completed, failed
     *
     * * `pending` - Pending
     * * `processing` - Processing
     * * `completed` - Completed
     * * `failed` - Failed
     */
    task_status: GenerationTaskStatusResponse.task_status;
    /**
     * 进度百分比 (0-100)
     */
    progress_percent: number;
    /**
     * 当前进度消息
     */
    progress_message: string;
    /**
     * 公司 ID
     */
    company_id: number;
    /**
     * 公司名称
     */
    company_name: string;
    /**
     * 公司股票代码
     */
    company_ticker: string;
    /**
     * 交易所代码 (SSE, SZSE, HKEX)
     */
    exchange?: string;
    /**
     * 任务创建时间
     */
    created_at: string;
    /**
     * 任务最后更新时间
     */
    updated_at: string;
    /**
     * 任务完成时间 (仅当任务完成或失败时返回)
     */
    completed_at?: string | null;
    /**
     * 任务结果数据 (仅当 task_status='completed' 时返回)
     */
    result?: any;
    /**
     * 错误消息 (仅当 task_status='failed' 时返回)
     */
    error?: string | null;
};
export namespace GenerationTaskStatusResponse {
    /**
     * API 响应状态
     *
     * * `success` - success
     * * `error` - error
     */
    export enum status {
        SUCCESS = 'success',
        ERROR = 'error',
    }
    /**
     * 任务执行状态: pending, processing, completed, failed
     *
     * * `pending` - Pending
     * * `processing` - Processing
     * * `completed` - Completed
     * * `failed` - Failed
     */
    export enum task_status {
        PENDING = 'pending',
        PROCESSING = 'processing',
        COMPLETED = 'completed',
        FAILED = 'failed',
    }
}

