/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CompanyInfo } from './CompanyInfo';
/**
 * Request serializer for triggering Forensic Accounting analysis
 */
export type ForensicAccountingTrigger = {
    /**
     * List of companies to analyze, each with 'name' and 'ticker' fields
     */
    companies?: Array<CompanyInfo>;
};

