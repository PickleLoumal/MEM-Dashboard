/**
 * CSI300 Column Manifest Configuration
 * Defines all available columns for the Master Database table
 */

import type { ColumnDefinition, ColumnGroup, PresetView } from '@/components/ColumnSelector/types';

export interface ColumnManifest {
  version: string;
  lastUpdated: string;
  groups: ColumnGroup[];
  columns: ColumnDefinition[];
  presetViews: PresetView[];
}

// Format helpers
export const Formatters = {
  'currency-millions': (value: any) => {
    if (value === null || value === undefined || value === '') return '-';
    const numValue = parseFloat(value);
    if (isNaN(numValue)) return '-';
    return (numValue / 1000000).toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  },
  'number-millions': (value: any) => {
    if (value === null || value === undefined || value === '') return '-';
    const numValue = parseFloat(value);
    if (isNaN(numValue)) return '-';
    return (numValue / 1000000).toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  },
  'number-abbreviated': (value: any) => {
    if (value === null || value === undefined || value === '') return '-';
    const numValue = parseFloat(value);
    if (isNaN(numValue)) return '-';
    if (numValue >= 1000000000) return (numValue / 1000000000).toFixed(2) + 'B';
    if (numValue >= 1000000) return (numValue / 1000000).toFixed(2) + 'M';
    if (numValue >= 1000) return (numValue / 1000).toFixed(2) + 'K';
    return numValue.toFixed(0);
  },
  'percentage': (value: any) => {
    if (value === null || value === undefined || value === '') return '-';
    const numValue = parseFloat(value);
    if (isNaN(numValue)) return '-';
    return numValue.toFixed(2) + '%';
  },
  'number': (value: any, decimals = 2) => {
    if (value === null || value === undefined || value === '') return '-';
    const numValue = parseFloat(value);
    if (isNaN(numValue)) return '-';
    return numValue.toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    });
  },
  'currency': (value: any, decimals = 2) => {
    if (value === null || value === undefined || value === '') return '-';
    const numValue = parseFloat(value);
    if (isNaN(numValue)) return '-';
    return numValue.toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    });
  },
  'date': (value: any) => {
    if (!value) return '-';
    return String(value);
  },
  'monospace': (value: any) => value,
  'text-bold': (value: any) => value,
  'chip': (value: any) => value,
  'text': (value: any) => value
};

export const FieldMap: Record<string, string> = {
  // Basic fields
  'ticker': 'ticker',
  'name': 'name',
  'company_name': 'name',
  'region': 'region',
  'im_sector': 'im_sector',
  'sector': 'im_sector',
  'industry': 'industry',
  'sub_industry': 'industry',
  'gics_industry': 'gics_industry',
  'gics_sub_industry': 'gics_sub_industry',
  
  // Market cap & price
  'market_cap': 'market_cap_usd',
  'market_cap_usd': 'market_cap_usd',
  'market_cap_local': 'market_cap_local',
  'price': 'price_local_currency',
  'price_local_currency': 'price_local_currency',
  'currency': 'currency',
  'price_52w_high': 'price_52w_high',
  'price_52w_low': 'price_52w_low',
  'last_trade_date': 'last_trade_date',
  'total_return_2018_to_2025': 'total_return_2018_to_2025',
  
  // Valuation ratios
  'pe_ratio': 'pe_ratio_trailing',
  'pe_ratio_trailing': 'pe_ratio_trailing',
  'pe_ratio_consensus': 'pe_ratio_consensus',
  'peg_ratio': 'peg_ratio',
  
  // Profitability
  'roe': 'roe_trailing',
  'roe_trailing': 'roe_trailing',
  'roa': 'roa_trailing',
  'roa_trailing': 'roa_trailing',
  'operating_margin': 'operating_margin_trailing',
  'operating_margin_trailing': 'operating_margin_trailing',
  'operating_profits_per_share': 'operating_profits_per_share',
  'net_profits_fy0': 'net_profits_fy0',
  
  // EPS
  'eps_trailing': 'eps_trailing',
  'eps_actual_fy0': 'eps_actual_fy0',
  'eps_forecast_fy1': 'eps_forecast_fy1',
  'eps_growth_percent': 'eps_growth_percent',
  
  // Risk metrics
  'debt_equity': 'debt_to_equity',
  'debt_to_equity': 'debt_to_equity',
  'debt_to_total_assets': 'debt_to_total_assets',
  'interest_coverage': 'interest_coverage_ratio',
  'interest_coverage_ratio': 'interest_coverage_ratio',
  'current_ratio': 'current_ratio',
  'quick_ratio': 'quick_ratio',
  'altman_z_score_manufacturing': 'altman_z_score_manufacturing',
  'altman_z_score_non_manufacturing': 'altman_z_score_non_manufacturing',
  
  // Financial data
  'total_revenue_local': 'total_revenue_local',
  'ltm_revenue_local': 'ltm_revenue_local',
  'ntm_revenue_local': 'ntm_revenue_local',
  'total_assets_local': 'total_assets_local',
  'net_assets_local': 'net_assets_local',
  'total_debt_local': 'total_debt_local',
  'ebitda_fy0': 'ebitda_fy0',
  'ebitda_fy_minus_1': 'ebitda_fy_minus_1',
  'cash_flow_operations_fy0': 'cash_flow_operations_fy0',
  'cash_flow_operations_fy_minus_1': 'cash_flow_operations_fy_minus_1',
  'interest_expense_fy0': 'interest_expense_fy0',
  'effective_interest_rate': 'effective_interest_rate',
  'asset_turnover_ltm': 'asset_turnover_ltm',
  'operating_leverage': 'operating_leverage',
  
  // Dividends
  'dividend_yield_fy0': 'dividend_yield_fy0',
  'dividend_payout_ratio': 'dividend_payout_ratio',
  'dividend_local_currency': 'dividend_local_currency',
  'dividend_3yr_cagr': 'dividend_3yr_cagr',
  'dividend_5yr_cagr': 'dividend_5yr_cagr',
  'dividend_10yr_cagr': 'dividend_10yr_cagr'
};

export function getCellClass(column: { id: string; format?: string }): string {
  const classes = [];
  
  if (column.format === 'text-bold' || column.id === 'name') {
    classes.push('company-name');
  } else if (column.format === 'monospace' || column.id === 'ticker') {
    classes.push('company-ticker');
  } else if (column.id === 'region') {
    classes.push('region-cell');
  } else if (column.format === 'currency-millions' || column.id.includes('market_cap') || column.id.includes('revenue') || column.id.includes('assets') || column.id.includes('debt') || column.id.includes('ebitda') || column.id.includes('cash_flow') || column.id.includes('expense')) {
    classes.push('market-cap');
  } else if (column.format === 'currency' || column.id.includes('price')) {
    classes.push('price');
  } else if (column.id === 'pe_ratio_trailing' || column.id.includes('pe_ratio') || column.id.includes('ratio')) {
    classes.push('pe-ratio');
  }
  
  return classes.join(' ');
}

export const columnManifest: ColumnManifest = {
  version: '1.0.0',
  lastUpdated: '2025-10-09',

  groups: [
    { id: 'basics', name: 'Basic Information', icon: 'info', collapsed: false },
    { id: 'valuation', name: 'Valuation & Price', icon: 'calculator', collapsed: false },
    { id: 'profitability', name: 'Profitability', icon: 'trending-up', collapsed: true },
    { id: 'trading', name: 'Trading & Returns', icon: 'activity', collapsed: true },
    { id: 'technical', name: 'Earnings & EPS', icon: 'bar-chart', collapsed: true },
    { id: 'risk', name: 'Risk & Leverage', icon: 'shield', collapsed: true },
    { id: 'ownership', name: 'Financial Data', icon: 'users', collapsed: true }
  ],

  columns: [
    // === BASIC INFORMATION ===
    {
      id: 'ticker',
      name: 'Ticker',
      displayName: 'Ticker',
      group: 'basics',
      dataType: 'string',
      width: 100,
      pinnable: true,
      defaultPinned: true,
      defaultVisible: true,
      sortable: true,
      searchable: true,
      format: 'monospace',
      align: 'left'
    },
    {
      id: 'name',
      name: 'Company Name',
      displayName: 'Company Name',
      group: 'basics',
      dataType: 'string',
      width: 250,
      pinnable: true,
      defaultPinned: true,
      defaultVisible: true,
      sortable: true,
      searchable: true,
      format: 'text-bold',
      align: 'left'
    },
    {
      id: 'im_sector',
      name: 'IM Sector',
      displayName: 'IM Sector',
      group: 'basics',
      dataType: 'string',
      width: 180,
      pinnable: false,
      defaultVisible: true,
      sortable: true,
      searchable: true,
      format: 'chip',
      align: 'left'
    },
    {
      id: 'industry',
      name: 'Industry',
      displayName: 'Industry',
      group: 'basics',
      dataType: 'string',
      width: 200,
      pinnable: false,
      defaultVisible: true,
      sortable: true,
      searchable: true,
      format: 'text',
      align: 'left'
    },
    {
      id: 'gics_industry',
      name: 'GICS Industry',
      displayName: 'GICS Industry',
      group: 'basics',
      dataType: 'string',
      width: 180,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: true,
      format: 'text',
      align: 'left'
    },
    {
      id: 'gics_sub_industry',
      name: 'GICS Sub-Industry',
      displayName: 'GICS Sub-Industry',
      group: 'basics',
      dataType: 'string',
      width: 200,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: true,
      format: 'text',
      align: 'left'
    },

    // === VALUATION METRICS ===
    {
      id: 'market_cap_usd',
      name: 'Market Cap USD',
      displayName: 'Market Cap (USD M)',
      group: 'valuation',
      dataType: 'number',
      width: 150,
      pinnable: false,
      defaultVisible: true,
      sortable: true,
      searchable: false,
      format: 'currency-millions',
      align: 'right',
      decimals: 2
    },
    {
      id: 'market_cap_local',
      name: 'Market Cap Local',
      displayName: 'Market Cap (Local M)',
      group: 'valuation',
      dataType: 'number',
      width: 150,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'currency-millions',
      align: 'right',
      decimals: 2
    },
    {
      id: 'price_local_currency',
      name: 'Price',
      displayName: 'Price (Local)',
      group: 'valuation',
      dataType: 'number',
      width: 120,
      pinnable: false,
      defaultVisible: true,
      sortable: true,
      searchable: false,
      format: 'currency',
      align: 'right',
      decimals: 2,
      colorize: true
    },
    {
      id: 'currency',
      name: 'Currency',
      displayName: 'Currency',
      group: 'valuation',
      dataType: 'string',
      width: 80,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'text',
      align: 'center'
    },
    {
      id: 'pe_ratio_trailing',
      name: 'P/E Ratio',
      displayName: 'P/E Ratio (Trailing)',
      group: 'valuation',
      dataType: 'number',
      width: 120,
      pinnable: false,
      defaultVisible: true,
      sortable: true,
      searchable: false,
      format: 'number',
      align: 'right',
      decimals: 2,
      rangeIndicator: true
    },
    {
      id: 'pe_ratio_consensus',
      name: 'P/E Consensus',
      displayName: 'P/E Ratio (Consensus)',
      group: 'valuation',
      dataType: 'number',
      width: 130,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'number',
      align: 'right',
      decimals: 2
    },
    {
      id: 'peg_ratio',
      name: 'PEG Ratio',
      displayName: 'PEG Ratio',
      group: 'valuation',
      dataType: 'number',
      width: 100,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'number',
      align: 'right',
      decimals: 2
    },

    // === PROFITABILITY ===
    {
      id: 'roe_trailing',
      name: 'ROE',
      displayName: 'ROE (%) Trailing',
      group: 'profitability',
      dataType: 'number',
      width: 120,
      pinnable: false,
      defaultVisible: true,
      sortable: true,
      searchable: false,
      format: 'percentage',
      align: 'right',
      decimals: 2,
      colorize: true
    },
    {
      id: 'roa_trailing',
      name: 'ROA',
      displayName: 'ROA (%) Trailing',
      group: 'profitability',
      dataType: 'number',
      width: 120,
      pinnable: false,
      defaultVisible: true,
      sortable: true,
      searchable: false,
      format: 'percentage',
      align: 'right',
      decimals: 2,
      colorize: true
    },
    {
      id: 'operating_margin_trailing',
      name: 'Operating Margin',
      displayName: 'Operating Margin (%) Trailing',
      group: 'profitability',
      dataType: 'number',
      width: 180,
      pinnable: false,
      defaultVisible: true,
      sortable: true,
      searchable: false,
      format: 'percentage',
      align: 'right',
      decimals: 2,
      colorize: true
    },
    {
      id: 'operating_profits_per_share',
      name: 'Operating Profit/Share',
      displayName: 'Operating Profit per Share',
      group: 'profitability',
      dataType: 'number',
      width: 160,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'number',
      align: 'right',
      decimals: 2
    },
    {
      id: 'net_profits_fy0',
      name: 'Net Profits FY0',
      displayName: 'Net Profits FY0 (Local)',
      group: 'profitability',
      dataType: 'number',
      width: 160,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'currency-millions',
      align: 'right',
      decimals: 2
    },

    // === TRADING & PRICE INFO ===
    {
      id: 'price_52w_high',
      name: '52W High',
      displayName: '52-Week High',
      group: 'trading',
      dataType: 'number',
      width: 120,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'currency',
      align: 'right',
      decimals: 2
    },
    {
      id: 'price_52w_low',
      name: '52W Low',
      displayName: '52-Week Low',
      group: 'trading',
      dataType: 'number',
      width: 120,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'currency',
      align: 'right',
      decimals: 2
    },
    {
      id: 'last_trade_date',
      name: 'Last Trade Date',
      displayName: 'Last Trade Date',
      group: 'trading',
      dataType: 'date',
      width: 130,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'date',
      align: 'center'
    },
    {
      id: 'total_return_2018_to_2025',
      name: 'Total Return',
      displayName: 'Total Return 2018-2025',
      group: 'trading',
      dataType: 'number',
      width: 160,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'percentage',
      align: 'right',
      decimals: 2,
      colorize: true
    },

    // === EARNINGS & EPS ===
    {
      id: 'eps_trailing',
      name: 'EPS Trailing',
      displayName: 'EPS (Trailing)',
      group: 'technical',
      dataType: 'number',
      width: 120,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'number',
      align: 'right',
      decimals: 2
    },
    {
      id: 'eps_actual_fy0',
      name: 'EPS Actual FY0',
      displayName: 'EPS Actual FY0',
      group: 'technical',
      dataType: 'number',
      width: 130,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'number',
      align: 'right',
      decimals: 2
    },
    {
      id: 'eps_forecast_fy1',
      name: 'EPS Forecast FY1',
      displayName: 'EPS Forecast FY1',
      group: 'technical',
      dataType: 'number',
      width: 140,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'number',
      align: 'right',
      decimals: 2
    },
    {
      id: 'eps_growth_percent',
      name: 'EPS Growth',
      displayName: 'EPS Growth (%)',
      group: 'technical',
      dataType: 'number',
      width: 120,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'percentage',
      align: 'right',
      decimals: 2,
      colorize: true
    },

    // === RISK METRICS ===
    {
      id: 'debt_to_equity',
      name: 'Debt/Equity',
      displayName: 'Debt/Equity',
      group: 'risk',
      dataType: 'number',
      width: 130,
      pinnable: false,
      defaultVisible: true,
      sortable: true,
      searchable: false,
      format: 'number',
      align: 'right',
      decimals: 2,
      rangeIndicator: true
    },
    {
      id: 'debt_to_total_assets',
      name: 'Debt/Assets',
      displayName: 'Debt to Total Assets',
      group: 'risk',
      dataType: 'number',
      width: 150,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'number',
      align: 'right',
      decimals: 2
    },
    {
      id: 'interest_coverage_ratio',
      name: 'Interest Coverage',
      displayName: 'Interest Coverage Ratio',
      group: 'risk',
      dataType: 'number',
      width: 150,
      pinnable: false,
      defaultVisible: true,
      sortable: true,
      searchable: false,
      format: 'number',
      align: 'right',
      decimals: 2,
      maxDisplay: 999,
      tooltip: 'Values over 999 indicate very strong coverage'
    },
    {
      id: 'current_ratio',
      name: 'Current Ratio',
      displayName: 'Current Ratio',
      group: 'risk',
      dataType: 'number',
      width: 120,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'number',
      align: 'right',
      decimals: 2
    },
    {
      id: 'quick_ratio',
      name: 'Quick Ratio',
      displayName: 'Quick Ratio',
      group: 'risk',
      dataType: 'number',
      width: 120,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'number',
      align: 'right',
      decimals: 2
    },
    {
      id: 'altman_z_score_manufacturing',
      name: 'Altman Z (Mfg)',
      displayName: 'Altman Z-Score (Manufacturing)',
      group: 'risk',
      dataType: 'number',
      width: 170,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'number',
      align: 'right',
      decimals: 2,
      rangeIndicator: true
    },
    {
      id: 'altman_z_score_non_manufacturing',
      name: 'Altman Z (Non-Mfg)',
      displayName: 'Altman Z-Score (Non-Manufacturing)',
      group: 'risk',
      dataType: 'number',
      width: 180,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'number',
      align: 'right',
      decimals: 2,
      rangeIndicator: true
    },

    // === FINANCIAL DATA ===
    {
      id: 'total_revenue_local',
      name: 'Total Revenue',
      displayName: 'Total Revenue (Local M)',
      group: 'ownership',
      dataType: 'number',
      width: 160,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'currency-millions',
      align: 'right',
      decimals: 2
    },
    {
      id: 'ltm_revenue_local',
      name: 'LTM Revenue',
      displayName: 'LTM Revenue (Local M)',
      group: 'ownership',
      dataType: 'number',
      width: 160,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'currency-millions',
      align: 'right',
      decimals: 2
    },
    {
      id: 'ntm_revenue_local',
      name: 'NTM Revenue',
      displayName: 'NTM Revenue (Local M)',
      group: 'ownership',
      dataType: 'number',
      width: 160,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'currency-millions',
      align: 'right',
      decimals: 2
    },
    {
      id: 'total_assets_local',
      name: 'Total Assets',
      displayName: 'Total Assets (Local M)',
      group: 'ownership',
      dataType: 'number',
      width: 160,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'currency-millions',
      align: 'right',
      decimals: 2
    },
    {
      id: 'net_assets_local',
      name: 'Net Assets',
      displayName: 'Net Assets (Local M)',
      group: 'ownership',
      dataType: 'number',
      width: 160,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'currency-millions',
      align: 'right',
      decimals: 2
    },
    {
      id: 'total_debt_local',
      name: 'Total Debt',
      displayName: 'Total Debt (Local M)',
      group: 'ownership',
      dataType: 'number',
      width: 160,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'currency-millions',
      align: 'right',
      decimals: 2
    },
    {
      id: 'ebitda_fy0',
      name: 'EBITDA FY0',
      displayName: 'EBITDA FY0 (Local M)',
      group: 'ownership',
      dataType: 'number',
      width: 150,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'currency-millions',
      align: 'right',
      decimals: 2
    },
    {
      id: 'ebitda_fy_minus_1',
      name: 'EBITDA FY-1',
      displayName: 'EBITDA FY-1 (Local M)',
      group: 'ownership',
      dataType: 'number',
      width: 150,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'currency-millions',
      align: 'right',
      decimals: 2
    },
    {
      id: 'cash_flow_operations_fy0',
      name: 'Cash Flow Ops FY0',
      displayName: 'Cash Flow Operations FY0 (M)',
      group: 'ownership',
      dataType: 'number',
      width: 180,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'currency-millions',
      align: 'right',
      decimals: 2
    },
    {
      id: 'cash_flow_operations_fy_minus_1',
      name: 'Cash Flow Ops FY-1',
      displayName: 'Cash Flow Operations FY-1 (M)',
      group: 'ownership',
      dataType: 'number',
      width: 180,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'currency-millions',
      align: 'right',
      decimals: 2
    },
    {
      id: 'interest_expense_fy0',
      name: 'Interest Expense',
      displayName: 'Interest Expense FY0 (M)',
      group: 'ownership',
      dataType: 'number',
      width: 160,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'currency-millions',
      align: 'right',
      decimals: 2
    },
    {
      id: 'effective_interest_rate',
      name: 'Eff Interest Rate',
      displayName: 'Effective Interest Rate (%)',
      group: 'ownership',
      dataType: 'number',
      width: 160,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'percentage',
      align: 'right',
      decimals: 2
    },
    {
      id: 'asset_turnover_ltm',
      name: 'Asset Turnover',
      displayName: 'Asset Turnover LTM',
      group: 'ownership',
      dataType: 'number',
      width: 150,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'number',
      align: 'right',
      decimals: 2
    },
    {
      id: 'operating_leverage',
      name: 'Operating Leverage',
      displayName: 'Operating Leverage',
      group: 'ownership',
      dataType: 'number',
      width: 150,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'number',
      align: 'right',
      decimals: 2
    },
    {
      id: 'dividend_yield_fy0',
      name: 'Dividend Yield',
      displayName: 'Dividend Yield FY0 (%)',
      group: 'ownership',
      dataType: 'number',
      width: 150,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'percentage',
      align: 'right',
      decimals: 2
    },
    {
      id: 'dividend_payout_ratio',
      name: 'Dividend Payout',
      displayName: 'Dividend Payout Ratio',
      group: 'ownership',
      dataType: 'number',
      width: 160,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'number',
      align: 'right',
      decimals: 2
    },
    {
      id: 'dividend_local_currency',
      name: 'Dividend',
      displayName: 'Dividend (Local Currency)',
      group: 'ownership',
      dataType: 'number',
      width: 150,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'currency',
      align: 'right',
      decimals: 2
    },
    {
      id: 'dividend_3yr_cagr',
      name: 'Dividend 3Y CAGR',
      displayName: 'Dividend 3yr CAGR',
      group: 'ownership',
      dataType: 'number',
      width: 140,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'percentage',
      align: 'right',
      decimals: 2
    },
    {
      id: 'dividend_5yr_cagr',
      name: 'Dividend 5Y CAGR',
      displayName: 'Dividend 5yr CAGR',
      group: 'ownership',
      dataType: 'number',
      width: 140,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'percentage',
      align: 'right',
      decimals: 2
    },
    {
      id: 'dividend_10yr_cagr',
      name: 'Dividend 10Y CAGR',
      displayName: 'Dividend 10yr CAGR',
      group: 'ownership',
      dataType: 'number',
      width: 140,
      pinnable: false,
      defaultVisible: false,
      sortable: true,
      searchable: false,
      format: 'percentage',
      align: 'right',
      decimals: 2
    }
  ],

  presetViews: [
    {
      id: 'default',
      name: 'Default View',
      description: 'Standard view with essential columns',
      isSystem: true,
      columns: ['ticker', 'name', 'im_sector', 'industry', 'market_cap_usd', 'price_local_currency', 'pe_ratio_trailing'],
      pinnedColumns: ['ticker', 'name']
    },
    {
      id: 'valuation',
      name: 'Valuation Analysis',
      description: 'Focus on valuation metrics',
      isSystem: true,
      columns: [
        'ticker',
        'name',
        'im_sector',
        'pe_ratio_trailing',
        'pe_ratio_consensus',
        'peg_ratio',
        'market_cap_usd',
        'price_local_currency'
      ],
      pinnedColumns: ['ticker', 'name']
    },
    {
      id: 'profitability',
      name: 'Profitability Focus',
      description: 'Profitability and margin metrics',
      isSystem: true,
      columns: [
        'ticker',
        'name',
        'im_sector',
        'roe_trailing',
        'roa_trailing',
        'operating_margin_trailing',
        'operating_profits_per_share',
        'net_profits_fy0'
      ],
      pinnedColumns: ['ticker', 'name']
    },
    {
      id: 'risk',
      name: 'Risk Assessment',
      description: 'Risk and leverage metrics',
      isSystem: true,
      columns: [
        'ticker',
        'name',
        'im_sector',
        'debt_to_equity',
        'debt_to_total_assets',
        'interest_coverage_ratio',
        'current_ratio',
        'quick_ratio'
      ],
      pinnedColumns: ['ticker', 'name']
    },
    {
      id: 'earnings',
      name: 'Earnings & EPS',
      description: 'Earnings per share metrics',
      isSystem: true,
      columns: [
        'ticker',
        'name',
        'im_sector',
        'eps_trailing',
        'eps_actual_fy0',
        'eps_forecast_fy1',
        'eps_growth_percent',
        'pe_ratio_trailing'
      ],
      pinnedColumns: ['ticker', 'name']
    },
    {
      id: 'dividends',
      name: 'Dividend Analysis',
      description: 'Dividend-related metrics',
      isSystem: true,
      columns: [
        'ticker',
        'name',
        'im_sector',
        'dividend_yield_fy0',
        'dividend_payout_ratio',
        'dividend_local_currency',
        'dividend_3yr_cagr',
        'dividend_5yr_cagr'
      ],
      pinnedColumns: ['ticker', 'name']
    },
    {
      id: 'financial_health',
      name: 'Financial Health',
      description: 'Balance sheet and cash flow metrics',
      isSystem: true,
      columns: [
        'ticker',
        'name',
        'total_assets_local',
        'total_debt_local',
        'ebitda_fy0',
        'cash_flow_operations_fy0',
        'current_ratio',
        'debt_to_equity'
      ],
      pinnedColumns: ['ticker', 'name']
    }
  ]
};

export default columnManifest;

