/**
 * CSI300 Column Selector - React Component Library
 * 
 * A sophisticated multi-select dropdown for managing table columns.
 * Features: search, grouping, pinning, drag-to-reorder, view management.
 * 
 * @example
 * ```tsx
 * import { ColumnSelector } from '@/components/ColumnSelector';
 * import { columnManifest } from '@/lib/column-manifest';
 * 
 * function MyTable() {
 *   const handleColumnChange = (data) => {
 *     console.log('Selected columns:', data.columns);
 *   };
 * 
 *   return (
 *     <ColumnSelector
 *       manifest={columnManifest}
 *       onColumnChange={handleColumnChange}
 *     />
 *   );
 * }
 * ```
 */

export { ColumnSelector, default } from './ColumnSelector';
export { useColumnSelector } from './useColumnSelector';
// Re-export from centralized location for convenience
export { columnManifest, Formatters, FieldMap, getCellClass } from '@/lib/column-manifest';
export type {
  ColumnAlign,
  ColumnChangeData,
  ColumnDataType,
  ColumnDefinition,
  ColumnFormat,
  ColumnGroup,
  ColumnManifest,
  ColumnSelectorProps,
  ColumnSelectorState,
  CustomView,
  PresetView
} from './types';

