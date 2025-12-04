/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * 日本FRED指标最新值序列化器 - 对应Flask API的data字段格式
 */
export type FredJpLatestValue = {
    value: string;
    date: string;
    formatted_date: string;
    yoy_change: number | null;
    unit: string;
    indicator_name: string;
    series_id: string;
    source?: string;
    last_updated: string | null;
};

