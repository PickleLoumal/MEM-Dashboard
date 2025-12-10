/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type HistoricalDataResponse = {
    success: boolean;
    symbol?: string;
    company_name?: string;
    data_points?: Array<Record<string, any>>;
    previous_close?: number;
    open_price?: number;
    current_price?: number;
    latest_close?: number;
    change?: number;
    change_pct?: number;
    day_range?: string;
    volume?: number;
    trading_days?: number;
    price_52w_high?: number;
    price_52w_low?: number;
    stock_score?: Record<string, any>;
    error?: string;
};

