/**
 * @fileoverview 通用 API 类型定义
 * @description 定义所有 API 共享的基础类型，包括响应格式、分页、错误处理等
 * @module shared/api-types/common
 * @version 1.0.0
 *
 * TypeScript 类型映射说明 (Python -> TypeScript):
 * - str -> string
 * - int -> number
 * - float -> number
 * - bool -> boolean
 * - None -> null
 * - Optional[T] -> T | null
 * - List[T] -> T[]
 * - Dict[str, T] -> Record<string, T>
 * - datetime -> string (ISO 8601 format)
 * - Decimal -> number (注意精度问题)
 */

// ============================================================================
// API 响应基础类型
// ============================================================================

/**
 * 成功响应的基础结构
 * @template T - 数据类型
 */
export interface ApiSuccessResponse<T> {
  success: true;
  data: T;
  metadata?: ApiMetadata;
}

/**
 * 错误响应结构
 * 对应 Python: FredUsErrorResponseSerializer, etc.
 */
export interface ApiErrorResponse {
  success: false;
  error: string;
  details?: Record<string, unknown>;
  timestamp?: string;
  country?: string;
}

/**
 * 通用 API 响应类型
 */
export type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;

/**
 * API 元数据
 */
export interface ApiMetadata {
  country?: string;
  source?: string;
  api_version?: string;
  total_records?: number;
  series_id?: string;
}

// ============================================================================
// 分页类型
// ============================================================================

/**
 * 分页请求参数
 */
export interface PaginationParams {
  page?: number;
  page_size?: number;
}

/**
 * 分页响应结构
 * 对应 Django REST Framework 的 PageNumberPagination
 */
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ============================================================================
// 筛选选项类型
// ============================================================================

/**
 * CSI300 筛选选项
 * 对应 Python: CSI300FilterOptionsSerializer
 */
export interface FilterOptions {
  regions: string[];
  im_sectors: string[];
  industries: string[];
  gics_industries: string[];
  market_cap_range: MarketCapRange;
  filtered_by_region?: boolean;
  region_filter?: string | null;
  filtered_by_sector?: boolean;
  sector_filter?: string | null;
}

/**
 * 市值范围
 */
export interface MarketCapRange {
  min: number;
  max: number;
}

// ============================================================================
// 健康检查类型
// ============================================================================

/**
 * 健康检查响应
 * 对应 Python: FredUsHealthCheckSerializer
 */
export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy' | 'error';
  database_connection?: boolean;
  api_connection?: boolean;
  country?: string;
  timestamp: string;
  service?: string;
  total_companies?: number;
  database_available?: boolean;
}

/**
 * 服务状态响应
 * 对应 Python: FredUsStatusSerializer
 */
export interface ServiceStatusResponse {
  status: string;
  database: string;
  country: string;
  total_indicators: number;
  last_updated: string | null;
  api_key_configured: boolean;
}

// ============================================================================
// 日期时间类型
// ============================================================================

/**
 * ISO 8601 日期字符串类型
 * 格式: "YYYY-MM-DD"
 */
export type ISODateString = string;

/**
 * ISO 8601 日期时间字符串类型
 * 格式: "YYYY-MM-DDTHH:mm:ss.sssZ"
 */
export type ISODateTimeString = string;

/**
 * 格式化的日期显示
 * 格式: "Jan 2025", "Feb 2025"
 */
export type FormattedDateString = string;

// ============================================================================
// 数值显示类型
// ============================================================================

/**
 * 货币/数值显示格式
 * 例如: "2.50T", "1.25B", "500M"
 */
export type FormattedNumberString = string;

/**
 * 百分比显示格式
 * 例如: "35.50%", "-2.30%"
 */
export type PercentageString = string;

// ============================================================================
// 类型守卫
// ============================================================================

/**
 * 检查是否为成功响应
 */
export function isSuccessResponse<T>(
  response: ApiResponse<T>
): response is ApiSuccessResponse<T> {
  return response.success === true;
}

/**
 * 检查是否为错误响应
 */
export function isErrorResponse<T>(
  response: ApiResponse<T>
): response is ApiErrorResponse {
  return response.success === false;
}

/**
 * 检查是否为分页响应
 */
export function isPaginatedResponse<T>(
  response: unknown
): response is PaginatedResponse<T> {
  return (
    typeof response === 'object' &&
    response !== null &&
    'count' in response &&
    'results' in response &&
    Array.isArray((response as PaginatedResponse<T>).results)
  );
}

