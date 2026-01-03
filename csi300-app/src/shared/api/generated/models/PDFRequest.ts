/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Serializer for PDF generation request.
 *
 * Note: Validation only checks existence, actual objects are fetched in the view
 * to avoid duplicate queries. View handles race conditions with try-except.
 */
export type PDFRequest = {
    /**
     * ID of the company for which to generate PDF
     */
    company_id: number;
    /**
     * Optional template ID (uses default template if not specified)
     */
    template_id?: number | null;
};

