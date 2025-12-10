/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * 股价数据序列化器。
 */
export type PricingData = {
    /**
     * 收盘价
     */
    price_close?: string | null;
    /**
     * 价格日期
     */
    price_date?: string | null;
    /**
     * 52周最高
     */
    week_52_high?: string | null;
    /**
     * 52周最低
     */
    week_52_low?: string | null;
    /**
     * 市值
     */
    market_cap?: string | null;
    /**
     * 市值显示格式 (e.g., '132.10B CNY')
     */
    market_cap_display?: string | null;
    /**
     * 货币
     */
    currency?: string;
};

