/**
 * @fileoverview FRED 经济指标 API 类型定义
 * @description 定义美国/日本 FRED 经济指标相关的所有类型
 * @module shared/api-types/fred
 * @version 1.0.0
 *
 * 后端对应:
 * - US Model: src/django_api/fred_us/models.py
 * - US Serializer: src/django_api/fred_us/serializers.py
 * - US Views: src/django_api/fred_us/views.py
 * - JP Model: src/django_api/fred_jp/models.py
 * - JP Views: src/django_api/fred_jp/views.py
 */

import type {
  ISODateString,
  ISODateTimeString,
  FormattedDateString,
} from './common.types';

// ============================================================================
// 通用 FRED 类型
// ============================================================================

/**
 * FRED 指标观测数据
 * 对应 Python: FredUsObservationSerializer
 */
export interface FredObservation {
  date: ISODateString;
  value: string;
  realtime_start?: ISODateString;
  realtime_end?: ISODateString;
}

/**
 * 扩展的 FRED 观测数据 (包含更多元数据)
 */
export interface FredObservationExtended extends FredObservation {
  indicator_name: string;
  indicator_type: string | null;
  unit: string | null;
  frequency: string | null;
  created_at: ISODateTimeString | null;
  country: 'US' | 'JP';
}

/**
 * FRED 指标最新值数据
 * 对应 Python: FredUsLatestValueSerializer
 */
export interface FredLatestValue {
  value: number;
  date: ISODateString;
  formatted_date: FormattedDateString;
  yoy_change: number | null;
  unit: string;
  indicator_name: string;
  series_id: string;
  country: 'US' | 'JP';
  source: string;
  last_updated: ISODateTimeString | null;
}

// ============================================================================
// 美国 FRED 类型
// ============================================================================

/**
 * 美国 FRED 指标响应
 * 对应 Python: FredUsIndicatorResponseSerializer
 */
export interface FredUsIndicatorResponse {
  success: true;
  data: FredLatestValue;
  observations: FredObservation[];
  series_id: string;
  count: number;
  limit: number;
  country: 'US';
}

/**
 * 美国 FRED API 索引响应
 */
export interface FredUsApiIndexResponse {
  api_name: string;
  country: 'US';
  version: string;
  total_indicators: number;
  last_updated: ISODateTimeString | null;
  available_endpoints: {
    indicator: string;
    status: string;
    all_indicators: string;
    health: string;
    fetch_data: string;
  };
  description: string;
}

/**
 * 美国 FRED 状态响应
 * 对应 Python: FredUsStatusSerializer
 */
export interface FredUsStatusResponse {
  status: string;
  database: string;
  country: 'US';
  total_indicators: number;
  last_updated: ISODateTimeString | null;
  api_key_configured: boolean;
}

/**
 * 美国 FRED 所有指标响应
 * 对应 Python: FredUsAllIndicatorsSerializer
 */
export interface FredUsAllIndicatorsResponse {
  success: true;
  data: Record<string, FredIndicatorSummary>;
  country: 'US';
  total_count: number;
}

/**
 * FRED 指标摘要
 */
export interface FredIndicatorSummary {
  series_id: string;
  indicator_name: string;
  latest_value: number | null;
  latest_date: ISODateString | null;
  unit: string | null;
  frequency: string | null;
}

/**
 * 美国 FRED 健康检查响应
 * 对应 Python: FredUsHealthCheckSerializer
 */
export interface FredUsHealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  database_connection: boolean;
  api_connection: boolean;
  country: 'US';
  timestamp: ISODateTimeString;
}

/**
 * 美国 FRED 错误响应
 * 对应 Python: FredUsErrorResponseSerializer
 */
export interface FredUsErrorResponse {
  success: false;
  error: string;
  country: 'US';
  details?: Record<string, unknown>;
  timestamp: ISODateTimeString;
}

// ============================================================================
// 日本 FRED 类型
// ============================================================================

/**
 * 日本 FRED 指标响应 (结构与美国相同，country 不同)
 */
export interface FredJpIndicatorResponse {
  success: true;
  data: FredLatestValue;
  observations: FredObservation[];
  series_id: string;
  count: number;
  limit: number;
  country: 'JP';
}

/**
 * 日本 FRED 错误响应
 */
export interface FredJpErrorResponse {
  success: false;
  error: string;
  country: 'JP';
  details?: Record<string, unknown>;
  timestamp: ISODateTimeString;
}

// ============================================================================
// 指标类别常量类型
// ============================================================================

/**
 * 美国 FRED 指标类别
 */
export type FredUsIndicatorCategory =
  | 'debt'                    // 债务指标
  | 'money_supply'            // 货币供应
  | 'employment'              // 就业指标
  | 'inflation'               // 通胀指标
  | 'banking'                 // 银行业指标
  | 'trade'                   // 贸易指标
  | 'government_deficit'      // 政府赤字
  | 'corporate_debt'          // 企业债务
  | 'consumer_debt';          // 消费者债务

/**
 * 常用美国 FRED 系列 ID
 */
export type FredUsSeriesId =
  // 债务与GDP
  | 'GFDEGDQ188S'    // 联邦债务占GDP比例
  | 'GFDEBTN'        // 联邦债务总额
  // 货币供应
  | 'M2SL'           // M2货币供应量
  | 'M1SL'           // M1货币供应量
  | 'M2V'            // M2货币流通速度
  | 'BOGMBASE'       // 货币基础
  // 利率
  | 'FEDFUNDS'       // 联邦基金利率
  | 'DGS10'          // 10年期国债利率
  | 'DGS2'           // 2年期国债利率
  | 'TB3MS'          // 3个月国债利率
  | 'MORTGAGE30US'   // 30年固定抵押贷款利率
  // 就业
  | 'UNRATE'         // 失业率
  | 'PAYEMS'         // 非农就业人数
  | 'CIVPART'        // 劳动力参与率
  | 'ICSA'           // 首次申请失业救济人数
  // 通胀
  | 'CPIAUCSL'       // 消费者价格指数
  | 'PCEPI'          // PCE价格指数
  | 'PCEPILFE'       // 核心PCE价格指数
  // 其他常用指标
  | string;          // 允许其他自定义指标

// ============================================================================
// 查询参数类型
// ============================================================================

/**
 * FRED 指标查询参数
 */
export interface FredIndicatorParams {
  name?: string;
  limit?: number;
}

/**
 * FRED 数据获取参数
 */
export interface FredFetchDataParams {
  indicator?: string;
  limit?: number;
}

// ============================================================================
// 类型守卫
// ============================================================================

/**
 * 检查是否为 FRED 成功响应
 */
export function isFredSuccessResponse(
  response: FredUsIndicatorResponse | FredUsErrorResponse
): response is FredUsIndicatorResponse {
  return response.success === true;
}

/**
 * 检查是否为 FRED 错误响应
 */
export function isFredErrorResponse(
  response: FredUsIndicatorResponse | FredUsErrorResponse
): response is FredUsErrorResponse {
  return response.success === false;
}

