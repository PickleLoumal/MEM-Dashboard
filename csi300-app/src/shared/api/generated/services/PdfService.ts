/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PDFDownloadResponse } from '../models/PDFDownloadResponse';
import type { PDFRequest } from '../models/PDFRequest';
import type { PDFTask } from '../models/PDFTask';
import type { PDFTaskCreateResponse } from '../models/PDFTaskCreateResponse';
import type { PDFTemplate } from '../models/PDFTemplate';
import type { PDFTemplateDetail } from '../models/PDFTemplateDetail';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class PdfService {
    /**
     * Internal callback for LaTeX worker status updates
     * @param requestBody
     * @returns any
     * @throws ApiError
     */
    public static apiPdfInternalCallbackCreate(
        requestBody?: Record<string, any>,
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/pdf/internal/callback/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Get pre-signed download URL for a completed PDF
     * @param taskId Task UUID
     * @returns PDFDownloadResponse
     * @throws ApiError
     */
    public static apiPdfTasksDownloadRetrieve(
        taskId: string,
    ): CancelablePromise<PDFDownloadResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/pdf/tasks/download/{task_id}/',
            path: {
                'task_id': taskId,
            },
        });
    }
    /**
     * List recent PDF generation tasks
     * @param companyId Optional company ID filter
     * @returns PDFTask
     * @throws ApiError
     */
    public static apiPdfTasksHistoryList(
        companyId?: number,
    ): CancelablePromise<Array<PDFTask>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/pdf/tasks/history/',
            query: {
                'company_id': companyId,
            },
        });
    }
    /**
     * Request generation of a PDF report for a company
     * @param requestBody
     * @returns PDFTaskCreateResponse
     * @throws ApiError
     */
    public static apiPdfTasksRequestCreate(
        requestBody: PDFRequest,
    ): CancelablePromise<PDFTaskCreateResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/pdf/tasks/request/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Get current status and progress of a PDF generation task
     * @param taskId Task UUID
     * @returns PDFTask
     * @throws ApiError
     */
    public static apiPdfTasksStatusRetrieve(
        taskId: string,
    ): CancelablePromise<PDFTask> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/pdf/tasks/status/{task_id}/',
            path: {
                'task_id': taskId,
            },
        });
    }
    /**
     * ViewSet for listing available PDF templates.
     *
     * Provides read-only access to active templates for selection.
     * @returns PDFTemplate
     * @throws ApiError
     */
    public static apiPdfTemplatesList(): CancelablePromise<Array<PDFTemplate>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/pdf/templates/',
        });
    }
    /**
     * ViewSet for listing available PDF templates.
     *
     * Provides read-only access to active templates for selection.
     * @param id A unique integer value identifying this PDF Template.
     * @returns PDFTemplateDetail
     * @throws ApiError
     */
    public static apiPdfTemplatesRetrieve(
        id: number,
    ): CancelablePromise<PDFTemplateDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/pdf/templates/{id}/',
            path: {
                'id': id,
            },
        });
    }
}
