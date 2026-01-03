/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Serializer for PDF templates (read-only, for listing available templates).
 */
export type PDFTemplate = {
    readonly id: number;
    /**
     * Template identifier (e.g., 'investment_summary_v1')
     */
    readonly name: string;
    /**
     * Human-readable template name (e.g., 'Investment Summary Report')
     */
    readonly display_name: string;
    /**
     * Template description and usage notes
     */
    readonly description: string;
    /**
     * Template version
     */
    readonly version: string;
    /**
     * Whether this is the default template for new reports
     */
    readonly is_default: boolean;
    /**
     * LaTeX page size (a4paper, letterpaper, etc.)
     */
    readonly page_size: string;
};

