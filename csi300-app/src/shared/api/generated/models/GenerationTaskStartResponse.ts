/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * 启动生成任务的响应序列化器
 *
 * 用于 POST /generate-summary/ 的响应
 */
export type GenerationTaskStartResponse = {
    /**
     * 响应状态: 'accepted' 表示任务已接受, 'error' 表示错误
     *
     * * `accepted` - accepted
     * * `error` - error
     */
    status: GenerationTaskStartResponse.status;
    /**
     * 响应消息
     */
    message: string;
    /**
     * 任务 UUID (仅当 status='accepted' 时返回)
     */
    task_id?: string | null;
    /**
     * 当前任务状态
     *
     * * `pending` - Pending
     * * `processing` - Processing
     * * `completed` - Completed
     * * `failed` - Failed
     */
    task_status?: GenerationTaskStartResponse.task_status | null;
    /**
     * 进度百分比 (0-100)
     */
    progress_percent?: number;
    /**
     * 进度消息
     */
    progress_message?: string;
};
export namespace GenerationTaskStartResponse {
    /**
     * 响应状态: 'accepted' 表示任务已接受, 'error' 表示错误
     *
     * * `accepted` - accepted
     * * `error` - error
     */
    export enum status {
        ACCEPTED = 'accepted',
        ERROR = 'error',
    }
    /**
     * 当前任务状态
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

