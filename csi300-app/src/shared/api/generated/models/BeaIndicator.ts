/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * BEA指标数据序列化器
 */
export type BeaIndicator = {
    series_id: string;
    time_period: string;
    value: string;
    readonly created_at: string;
    readonly yoy_change: number | null;
    /**
     * 格式化日期显示
     */
    readonly formatted_date: string;
    readonly value_billions: number | null;
};

