/**
 * CSI300 Column Selector Types
 * TypeScript definitions for column manifest and selector state
 */

export type ColumnDataType = 'string' | 'number' | 'date';

export type ColumnFormat =
  | 'text'
  | 'text-bold'
  | 'monospace'
  | 'chip'
  | 'number'
  | 'currency'
  | 'currency-millions'
  | 'percentage'
  | 'date';

export type ColumnAlign = 'left' | 'center' | 'right';

export interface ColumnDefinition {
  id: string;
  name: string;
  displayName: string;
  group: string;
  dataType: ColumnDataType;
  width: number;
  pinnable: boolean;
  defaultPinned?: boolean;
  defaultVisible: boolean;
  sortable: boolean;
  searchable: boolean;
  format: ColumnFormat;
  align: ColumnAlign;
  decimals?: number;
  colorize?: boolean;
  rangeIndicator?: boolean;
  maxDisplay?: number;
  tooltip?: string;
}

export interface ColumnGroup {
  id: string;
  name: string;
  icon: string;
  collapsed: boolean;
}

export interface PresetView {
  id: string;
  name: string;
  description: string;
  isSystem: boolean;
  columns: string[];
  pinnedColumns: string[];
}

export interface CustomView {
  id: string;
  name: string;
  columns: string[];
  pinnedColumns: string[];
  columnOrder: string[];
  createdAt: string;
}

export interface ColumnManifest {
  version: string;
  lastUpdated: string;
  groups: ColumnGroup[];
  columns: ColumnDefinition[];
  presetViews: PresetView[];
}

export interface ColumnSelectorState {
  selectedColumns: string[];
  pinnedColumns: string[];
  columnOrder: string[];
  activeView: string;
}

export interface ColumnChangeData {
  selectedColumns: string[];
  pinnedColumns: string[];
  columnOrder: string[];
  columns: ColumnDefinition[];
}

export interface ColumnSelectorProps {
  manifest: ColumnManifest;
  maxPinnedColumns?: number;
  onColumnChange?: (data: ColumnChangeData) => void;
  onViewChange?: (view: PresetView | CustomView) => void;
}

