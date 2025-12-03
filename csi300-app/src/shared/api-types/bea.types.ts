/**
 * @fileoverview BEA (Bureau of Economic Analysis) API 类型定义
 * @description 定义美国经济分析局指标相关的所有类型
 * @module shared/api-types/bea
 * @version 1.0.0
 *
 * 后端对应:
 * - Model: src/django_api/bea/models.py
 * - Serializer: src/django_api/bea/serializers.py
 * - Views: src/django_api/bea/views.py
 */

import type {
  ISODateString,
  ISODateTimeString,
} from './common.types';

// ============================================================================
// BEA 指标数据类型
// ============================================================================

/**
 * BEA 指标数据
 * 对应 Python Model: BeaIndicator
 * 对应 Serializer: BeaIndicatorSerializer
 */
export interface BeaIndicator {
  id: number;
  series_id: string;
  time_period: string;
  value: number | null;
  data_value_formatted: string | null;
  
  // 计算字段
  yoy_change?: number | null;
  qoq_change?: number | null;
  
  // 元数据
  created_at: ISODateTimeString;
  updated_at: ISODateTimeString;
}

/**
 * BEA 指标配置
 * 对应 Python Model: BeaIndicatorConfig
 */
export interface BeaIndicatorConfig {
  id: number;
  series_id: string;
  display_name: string;
  description: string | null;
  category: string;
  api_endpoint: string;
  
  // BEA API 参数
  bea_dataset: string;
  bea_table_name: string;
  bea_line_number: string | null;
  bea_frequency: string;
  
  // 显示配置
  unit: string | null;
  decimal_places: number;
  display_format: string | null;
  
  // 状态
  is_active: boolean;
  auto_fetch: boolean;
  fetch_interval_hours: number;
  
  // 元数据
  created_at: ISODateTimeString;
  updated_at: ISODateTimeString;
}

/**
 * BEA 系列信息
 * 对应 Python Model: BeaSeriesInfo
 */
export interface BeaSeriesInfo {
  id: number;
  series_id: string;
  title: string;
  dataset_name: string;
  table_name: string;
  line_number: string | null;
  frequency: string;
  unit: string | null;
  description: string | null;
  last_observation_date: ISODateString | null;
  
  created_at: ISODateTimeString;
  updated_at: ISODateTimeString;
}

// ============================================================================
// BEA API 响应类型
// ============================================================================

/**
 * BEA API 索引响应
 */
export interface BeaApiIndexResponse {
  service: string;
  status: 'running' | 'error';
  timestamp: ISODateTimeString;
  dynamic_endpoints: string[];
  management_endpoints: string[];
  legacy_endpoints: string[];
}

/**
 * BEA 指标数据响应
 * 对应 Serializer: BeaApiResponseSerializer
 */
export interface BeaIndicatorResponse {
  success: boolean;
  series_id: string;
  display_name?: string;
  latest_value?: number | null;
  latest_period?: string;
  yoy_change?: number | null;
  qoq_change?: number | null;
  unit?: string;
  data?: BeaIndicator[];
  quarterly_data?: BeaQuarterlyData[];
  error?: string;
}

/**
 * BEA 季度数据
 */
export interface BeaQuarterlyData {
  period: string;
  value: number | null;
  formatted_value: string | null;
  yoy_change?: number | null;
}

/**
 * BEA 所有指标响应
 * 对应 Serializer: BeaAllIndicatorsSerializer
 */
export interface BeaAllIndicatorsResponse {
  success: boolean;
  data: Record<string, BeaIndicatorSummary>;
  total_count: number;
  timestamp: ISODateTimeString;
}

/**
 * BEA 指标摘要
 */
export interface BeaIndicatorSummary {
  series_id: string;
  display_name: string;
  category: string;
  latest_value: number | null;
  latest_period: string | null;
  yoy_change: number | null;
  unit: string | null;
}

/**
 * BEA 配置列表响应
 */
export interface BeaConfigListResponse {
  success: boolean;
  data: BeaIndicatorConfig[];
  count: number;
}

/**
 * BEA 分类列表响应
 */
export interface BeaCategoriesResponse {
  success: boolean;
  data: string[];
  count: number;
}

/**
 * BEA 统计信息响应
 */
export interface BeaStatsResponse {
  success: boolean;
  data: {
    total_indicators: number;
    active_indicators: number;
    categories: string[];
    last_data_update: ISODateTimeString | null;
    auto_fetch_count: number;
    database_size: string;
  };
  timestamp: ISODateTimeString;
}

/**
 * BEA 健康检查响应
 */
export interface BeaHealthCheckResponse {
  service: string;
  status: 'healthy' | 'unhealthy';
  timestamp: ISODateTimeString;
  available_endpoints: number;
  database_connected: boolean;
  dynamic_config_enabled: boolean;
}

// ============================================================================
// BEA 指标类别常量
// ============================================================================

/**
 * BEA 指标类别
 */
export type BeaIndicatorCategory =
  | 'investment'              // 投资指标
  | 'consumption'             // 消费指标
  | 'government'              // 政府支出
  | 'gdp'                     // GDP相关
  | 'trade';                  // 贸易指标

/**
 * 常用 BEA 系列 ID
 */
export type BeaSeriesIdType =
  // 投资指标
  | 'INVESTMENT_TOTAL'        // 国内私人总投资
  | 'INVESTMENT_FIXED'        // 固定投资
  | 'INVESTMENT_NONRESIDENTIAL' // 非住宅投资
  | 'INVESTMENT_STRUCTURES'   // 结构投资
  | 'INVESTMENT_EQUIPMENT'    // 设备投资
  | 'INVESTMENT_IP'           // 知识产权产品投资
  | 'INVESTMENT_RESIDENTIAL'  // 住宅投资
  | 'INVESTMENT_INVENTORIES'  // 私人库存变动
  | 'INVESTMENT_NET'          // 国内私人净投资
  | 'GOVT_INVESTMENT_TOTAL'   // 政府总投资
  // 消费指标
  | 'MOTOR_VEHICLES'          // 机动车辆
  | 'RECREATIONAL_GOODS'      // 娱乐商品
  // 其他
  | string;

// ============================================================================
// BEA 错误响应
// ============================================================================

/**
 * BEA 错误响应
 */
export interface BeaErrorResponse {
  success: false;
  error: string;
  series_id?: string;
  status?: string;
}

// ============================================================================
// 类型守卫
// ============================================================================

/**
 * 检查是否为 BEA 成功响应
 */
export function isBeaSuccessResponse(
  response: BeaIndicatorResponse | BeaErrorResponse
): response is BeaIndicatorResponse {
  return response.success === true;
}

/**
 * 检查是否为 BEA 错误响应
 */
export function isBeaErrorResponse(
  response: BeaIndicatorResponse | BeaErrorResponse
): response is BeaErrorResponse {
  return response.success === false;
}

