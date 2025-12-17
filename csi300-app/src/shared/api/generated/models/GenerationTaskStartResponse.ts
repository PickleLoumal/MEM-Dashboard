/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GenerationTaskStartResponseStatusEnum } from './GenerationTaskStartResponseStatusEnum';
import type { NullEnum } from './NullEnum';
import type { TaskStatusEnum } from './TaskStatusEnum';
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
    status: GenerationTaskStartResponseStatusEnum;
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
    task_status?: (TaskStatusEnum | NullEnum) | null;
    /**
     * 进度百分比 (0-100)
     */
    progress_percent?: number;
    /**
     * 进度消息
     */
    progress_message?: string;
};

