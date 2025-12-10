/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * 分析师一致预期序列化器。
 */
export type AnalystConsensus = {
    /**
     * 共识评级 (Buy/Hold/Sell)
     */
    consensus_rating?: string | null;
    /**
     * 买入评级占比
     */
    buy_pct?: number | null;
    /**
     * 持有评级占比
     */
    hold_pct?: number | null;
    /**
     * 卖出评级占比
     */
    sell_pct?: number | null;
    /**
     * 分析师数量
     */
    num_analysts?: number | null;
    /**
     * 目标价最低
     */
    target_price_low?: string | null;
    /**
     * 目标价最高
     */
    target_price_high?: string | null;
    /**
     * 目标价平均
     */
    target_price_avg?: string | null;
    /**
     * 目标价中位数
     */
    target_price_median?: string | null;
    /**
     * 上涨潜力百分比
     */
    upside_pct?: string | null;
};

