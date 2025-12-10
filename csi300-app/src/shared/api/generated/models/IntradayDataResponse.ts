/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type IntradayDataResponse = {
    success: boolean;
    symbol?: string;
    company_name?: string;
    data_points?: Array<Record<string, any>>;
    previous_close?: number;
    current_price?: number;
    open_price?: number;
    update_time?: string;
    error?: string;
};

