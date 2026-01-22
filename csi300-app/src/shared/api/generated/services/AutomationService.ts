/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AutomationTask } from '../models/AutomationTask';
import type { DailyBriefingTrigger } from '../models/DailyBriefingTrigger';
import type { ForensicAccountingTrigger } from '../models/ForensicAccountingTrigger';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AutomationService {
    /**
     * ViewSet for managing automation tasks.
     *
     * Provides endpoints for triggering automation workflows and querying task status.
     * @returns AutomationTask
     * @throws ApiError
     */
    public static apiAutomationTasksList(): CancelablePromise<Array<AutomationTask>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/automation/tasks/',
        });
    }
    /**
     * ViewSet for managing automation tasks.
     *
     * Provides endpoints for triggering automation workflows and querying task status.
     * @param id A unique integer value identifying this automation task.
     * @returns AutomationTask
     * @throws ApiError
     */
    public static apiAutomationTasksRetrieve(
        id: number,
    ): CancelablePromise<AutomationTask> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/automation/tasks/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * Trigger only Stage 2 (AI Report Generation, skipping scraping delay)
     * @param requestBody
     * @returns AutomationTask Generation task successfully created and queued
     * @throws ApiError
     */
    public static apiAutomationTasksDailyBriefingGenerateCreate(
        requestBody?: DailyBriefingTrigger,
    ): CancelablePromise<AutomationTask> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/automation/tasks/daily-briefing/generate/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Invalid request parameters`,
            },
        });
    }
    /**
     * Trigger only Stage 1 (Scraping from Briefing.com to database). By default, scrape_only=True so Stage 2 will NOT be triggered. Set scrape_only=False to auto-trigger Stage 2 after 10 minutes.
     * @param requestBody
     * @returns AutomationTask Scraping task successfully created and queued
     * @throws ApiError
     */
    public static apiAutomationTasksDailyBriefingScrapeCreate(
        requestBody?: DailyBriefingTrigger,
    ): CancelablePromise<AutomationTask> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/automation/tasks/daily-briefing/scrape/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Invalid request parameters`,
            },
        });
    }
    /**
     * Trigger full Daily Briefing workflow (Stage 1: Scraping + Stage 2: AI Generation)
     * @param requestBody
     * @returns AutomationTask Task successfully created and queued
     * @throws ApiError
     */
    public static apiAutomationTasksDailyBriefingTriggerCreate(
        requestBody?: DailyBriefingTrigger,
    ): CancelablePromise<AutomationTask> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/automation/tasks/daily-briefing/trigger/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Invalid request parameters`,
            },
        });
    }
    /**
     * Trigger Forensic Accounting analysis for a list of companies
     * @param requestBody
     * @returns AutomationTask Forensic Accounting task successfully created and queued
     * @throws ApiError
     */
    public static apiAutomationTasksForensicAccountingTriggerCreate(
        requestBody?: ForensicAccountingTrigger,
    ): CancelablePromise<AutomationTask> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/automation/tasks/forensic-accounting/trigger/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Invalid request parameters or no companies provided`,
            },
        });
    }
}
