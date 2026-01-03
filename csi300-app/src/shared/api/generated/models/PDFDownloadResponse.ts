/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Response serializer for download URL endpoint.
 */
export type PDFDownloadResponse = {
    /**
     * Task identifier
     */
    task_id: string;
    /**
     * Pre-signed S3 URL for downloading the PDF
     */
    download_url: string;
    /**
     * Expiration time for the download URL
     */
    expires_at: string;
    /**
     * Suggested filename for the download
     */
    filename: string;
};

