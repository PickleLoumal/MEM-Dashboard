/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type GlobalHealthCheckResponse = {
    status: string;
    timestamp: string;
    service: string;
    environment: string;
    database_available: boolean;
    version: string;
    components: Record<string, any>;
    csi300_companies_count: number;
};

