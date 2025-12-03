/**
 * @fileoverview API 类型定义统一导出
 * @description 集中导出所有 API 类型定义，方便其他模块引用
 * @module shared/api-types
 * @version 1.0.0
 *
 * 使用方式:
 * ```typescript
 * import type {
 *   ApiResponse,
 *   CSI300Company,
 *   FredUsIndicatorResponse,
 *   BeaIndicatorResponse,
 * } from '@/shared/api-types';
 * ```
 */

// ============================================================================
// 通用类型
// ============================================================================
export type {
  // 响应类型
  ApiSuccessResponse,
  ApiErrorResponse,
  ApiResponse,
  ApiMetadata,
  
  // 分页类型
  PaginationParams,
  PaginatedResponse,
  
  // 筛选选项
  FilterOptions,
  MarketCapRange,
  
  // 健康检查
  HealthCheckResponse,
  ServiceStatusResponse,
  
  // 日期时间类型
  ISODateString,
  ISODateTimeString,
  FormattedDateString,
  
  // 数值显示类型
  FormattedNumberString,
  PercentageString,
} from './common.types';

export {
  isSuccessResponse,
  isErrorResponse,
  isPaginatedResponse,
} from './common.types';

// ============================================================================
// CSI300 类型
// ============================================================================
export type {
  // 公司类型
  CSI300Company,
  CSI300CompanyListItem,
  CSI300HSharesCompany,
  
  // 投资摘要
  CSI300InvestmentSummary,
  
  // 同行业对比
  CSI300PeerComparisonItem,
  CSI300IndustryPeersComparisonResponse,
  
  // API 响应
  CSI300CompanyListResponse,
  CSI300SearchResponse,
  CSI300ApiIndexResponse,
  
  // 查询参数
  CSI300CompanyListParams,
  CSI300CompanyDetailParams,
} from './csi300.types';

// ============================================================================
// FRED 类型
// ============================================================================
export type {
  // 通用 FRED 类型
  FredObservation,
  FredObservationExtended,
  FredLatestValue,
  FredIndicatorSummary,
  
  // 美国 FRED 类型
  FredUsIndicatorResponse,
  FredUsApiIndexResponse,
  FredUsStatusResponse,
  FredUsAllIndicatorsResponse,
  FredUsHealthCheckResponse,
  FredUsErrorResponse,
  
  // 日本 FRED 类型
  FredJpIndicatorResponse,
  FredJpErrorResponse,
  
  // 指标类别
  FredUsIndicatorCategory,
  FredUsSeriesId,
  
  // 查询参数
  FredIndicatorParams,
  FredFetchDataParams,
} from './fred.types';

export {
  isFredSuccessResponse,
  isFredErrorResponse,
} from './fred.types';

// ============================================================================
// BEA 类型
// ============================================================================
export type {
  // 数据类型
  BeaIndicator,
  BeaIndicatorConfig,
  BeaSeriesInfo,
  BeaQuarterlyData,
  BeaIndicatorSummary,
  
  // API 响应
  BeaApiIndexResponse,
  BeaIndicatorResponse,
  BeaAllIndicatorsResponse,
  BeaConfigListResponse,
  BeaCategoriesResponse,
  BeaStatsResponse,
  BeaHealthCheckResponse,
  BeaErrorResponse,
  
  // 指标类别
  BeaIndicatorCategory,
  BeaSeriesIdType,
} from './bea.types';

export {
  isBeaSuccessResponse,
  isBeaErrorResponse,
} from './bea.types';

