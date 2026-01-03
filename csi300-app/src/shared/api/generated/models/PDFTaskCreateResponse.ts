/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Response serializer for task creation endpoint.
 */
export type PDFTaskCreateResponse = {
    /**
     * Unique task identifier for tracking
     */
    task_id: string;
    /**
     * Initial task status (pending)
     */
    status: string;
    /**
     * Confirmation message
     */
    message: string;
    /**
     * WebSocket URL for real-time status updates
     */
    websocket_url: string;
};

