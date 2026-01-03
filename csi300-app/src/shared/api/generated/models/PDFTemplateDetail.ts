/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Detailed serializer for PDF templates (includes content for preview).
 */
export type PDFTemplateDetail = {
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
    /**
     * Page margins as JSON (e.g., {"top": "2cm", "bottom": "2cm", "left": "2.5cm", "right": "2.5cm"})
     */
    readonly margins: any;
    /**
     * Left header content
     */
    readonly header_left: string;
    /**
     * Right header content
     */
    readonly header_right: string;
    /**
     * Center footer content (e.g., page numbers)
     */
    readonly footer_center: string;
    /**
     * Chart definitions as JSON array
     */
    readonly charts_config: any;
    readonly created_at: string;
    readonly updated_at: string;
};

