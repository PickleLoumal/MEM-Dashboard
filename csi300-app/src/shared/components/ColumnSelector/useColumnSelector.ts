/**
 * CSI300 Column Selector Hook
 * Manages column selection state with localStorage persistence
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import type {
  ColumnChangeData,
  ColumnDefinition,
  ColumnManifest,
  ColumnSelectorState,
  CustomView,
  PresetView
} from './types';

const STORAGE_KEY = 'csi300_column_state';
const CUSTOM_VIEWS_KEY = 'csi300_custom_views';

function loadState(manifest: ColumnManifest): ColumnSelectorState {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const state = JSON.parse(saved) as ColumnSelectorState;
      const validIds = new Set(manifest.columns.map((c) => c.id));
      return {
        selectedColumns: (state.selectedColumns || []).filter((id) => validIds.has(id)),
        pinnedColumns: (state.pinnedColumns || []).filter((id) => validIds.has(id)),
        columnOrder: (state.columnOrder || []).filter((id) => validIds.has(id)),
        activeView: state.activeView || 'default'
      };
    }
  } catch (e) {
    console.warn('Failed to load column state from localStorage', e);
  }

  // Fall back to default view
  const defaultView = manifest.presetViews.find((v) => v.id === 'default');
  if (defaultView) {
    return {
      selectedColumns: [...defaultView.columns],
      pinnedColumns: [...defaultView.pinnedColumns],
      columnOrder: [...defaultView.columns],
      activeView: defaultView.id
    };
  }

  return {
    selectedColumns: [],
    pinnedColumns: [],
    columnOrder: [],
    activeView: 'default'
  };
}

function saveState(state: ColumnSelectorState): void {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        ...state,
        lastUpdated: new Date().toISOString()
      })
    );
  } catch (e) {
    console.warn('Failed to save column state to localStorage', e);
  }
}

function loadCustomViews(): CustomView[] {
  try {
    const saved = localStorage.getItem(CUSTOM_VIEWS_KEY);
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
}

function saveCustomViews(views: CustomView[]): void {
  try {
    localStorage.setItem(CUSTOM_VIEWS_KEY, JSON.stringify(views));
  } catch (e) {
    console.warn('Failed to save custom views to localStorage', e);
  }
}

export function useColumnSelector(
  manifest: ColumnManifest,
  options: {
    maxPinnedColumns?: number;
    onColumnChange?: (data: ColumnChangeData) => void;
    onViewChange?: (view: PresetView | CustomView) => void;
  } = {}
) {
  const { maxPinnedColumns = 3, onColumnChange, onViewChange } = options;

  const [state, setState] = useState<ColumnSelectorState>(() => loadState(manifest));
  const [customViews, setCustomViews] = useState<CustomView[]>(() => loadCustomViews());
  const [searchTerm, setSearchTerm] = useState('');
  const [collapsedGroups, setCollapsedGroups] = useState<Set<string>>(
    () => new Set(manifest.groups.filter((g) => g.collapsed).map((g) => g.id))
  );

  // Persist state changes
  useEffect(() => {
    saveState(state);
  }, [state]);

  useEffect(() => {
    saveCustomViews(customViews);
  }, [customViews]);

  // Get ordered columns with full definitions
  const orderedColumns = useMemo((): ColumnDefinition[] => {
    const orderedIds =
      state.columnOrder.length > 0
        ? state.columnOrder.filter((id) => state.selectedColumns.includes(id))
        : state.selectedColumns;

    return orderedIds.map((id) => manifest.columns.find((c) => c.id === id)).filter(Boolean) as ColumnDefinition[];
  }, [state.selectedColumns, state.columnOrder, manifest.columns]);

  // Notify parent of column changes
  useEffect(() => {
    onColumnChange?.({
      selectedColumns: state.selectedColumns,
      pinnedColumns: state.pinnedColumns,
      columnOrder: state.columnOrder,
      columns: orderedColumns
    });
  }, [state.selectedColumns, state.pinnedColumns, state.columnOrder, orderedColumns, onColumnChange]);

  // Toggle column selection
  const toggleColumn = useCallback((columnId: string, isSelected?: boolean) => {
    setState((prev) => {
      const currentlySelected = prev.selectedColumns.includes(columnId);
      const shouldSelect = isSelected ?? !currentlySelected;

      if (shouldSelect && !currentlySelected) {
        return {
          ...prev,
          selectedColumns: [...prev.selectedColumns, columnId],
          columnOrder: [...prev.columnOrder, columnId]
        };
      } else if (!shouldSelect && currentlySelected) {
        return {
          ...prev,
          selectedColumns: prev.selectedColumns.filter((id) => id !== columnId),
          pinnedColumns: prev.pinnedColumns.filter((id) => id !== columnId),
          columnOrder: prev.columnOrder.filter((id) => id !== columnId)
        };
      }
      return prev;
    });
  }, []);

  // Toggle column pin
  const togglePin = useCallback(
    (columnId: string) => {
      const column = manifest.columns.find((c) => c.id === columnId);
      if (!column?.pinnable) return;

      setState((prev) => {
        const isPinned = prev.pinnedColumns.includes(columnId);

        if (isPinned) {
          return {
            ...prev,
            pinnedColumns: prev.pinnedColumns.filter((id) => id !== columnId)
          };
        } else {
          if (prev.pinnedColumns.length >= maxPinnedColumns) {
            alert(`Maximum ${maxPinnedColumns} pinned columns allowed`);
            return prev;
          }
          return {
            ...prev,
            pinnedColumns: [...prev.pinnedColumns, columnId]
          };
        }
      });
    },
    [manifest.columns, maxPinnedColumns]
  );

  // Reorder columns
  const reorderColumns = useCallback((newOrder: string[]) => {
    setState((prev) => ({
      ...prev,
      columnOrder: newOrder
    }));
  }, []);

  // Select all columns
  const selectAll = useCallback(() => {
    const allIds = manifest.columns.map((col) => col.id);
    setState((prev) => ({
      ...prev,
      selectedColumns: allIds,
      columnOrder: allIds
    }));
  }, [manifest.columns]);

  // Deselect all (keep default pinned)
  const deselectAll = useCallback(() => {
    const defaultPinned = manifest.columns.filter((col) => col.defaultPinned).map((col) => col.id);
    setState((prev) => ({
      ...prev,
      selectedColumns: defaultPinned,
      pinnedColumns: defaultPinned,
      columnOrder: defaultPinned
    }));
  }, [manifest.columns]);

  // Load a view
  const loadView = useCallback(
    (viewId: string) => {
      let view: PresetView | CustomView | undefined;

      if (viewId.startsWith('custom_')) {
        view = customViews.find((v) => 'custom_' + v.id === viewId);
      } else {
        view = manifest.presetViews.find((v) => v.id === viewId);
      }

      if (view) {
        setState({
          selectedColumns: [...view.columns],
          pinnedColumns: [...view.pinnedColumns],
          columnOrder: [...view.columns],
          activeView: viewId
        });
        onViewChange?.(view);
      }
    },
    [manifest.presetViews, customViews, onViewChange]
  );

  // Save current state as custom view
  const saveView = useCallback(
    (name: string) => {
      const newView: CustomView = {
        id: Date.now().toString(),
        name,
        columns: [...state.selectedColumns],
        pinnedColumns: [...state.pinnedColumns],
        columnOrder: [...state.columnOrder],
        createdAt: new Date().toISOString()
      };

      setCustomViews((prev) => [...prev, newView]);
      setState((prev) => ({
        ...prev,
        activeView: 'custom_' + newView.id
      }));
    },
    [state]
  );

  // Reset to default view
  const resetToDefault = useCallback(() => {
    loadView('default');
  }, [loadView]);

  // Toggle group collapse
  const toggleGroup = useCallback((groupId: string) => {
    setCollapsedGroups((prev) => {
      const next = new Set(prev);
      if (next.has(groupId)) {
        next.delete(groupId);
      } else {
        next.add(groupId);
      }
      return next;
    });
  }, []);

  // Filter columns by search term
  const filteredGroups = useMemo(() => {
    if (!searchTerm) {
      return manifest.groups.map((group) => ({
        ...group,
        columns: manifest.columns.filter((col) => col.group === group.id)
      }));
    }

    const term = searchTerm.toLowerCase();
    return manifest.groups
      .map((group) => ({
        ...group,
        columns: manifest.columns.filter(
          (col) => col.group === group.id && col.displayName.toLowerCase().includes(term)
        )
      }))
      .filter((group) => group.columns.length > 0);
  }, [manifest.groups, manifest.columns, searchTerm]);

  // All available views (preset + custom)
  const allViews = useMemo(() => {
    return [
      ...manifest.presetViews.map((v) => ({ ...v, type: 'preset' as const })),
      ...customViews.map((v) => ({ ...v, id: 'custom_' + v.id, type: 'custom' as const }))
    ];
  }, [manifest.presetViews, customViews]);

  return {
    // State
    selectedColumns: state.selectedColumns,
    pinnedColumns: state.pinnedColumns,
    columnOrder: state.columnOrder,
    activeView: state.activeView,
    searchTerm,
    collapsedGroups,
    orderedColumns,
    filteredGroups,
    allViews,

    // Actions
    toggleColumn,
    togglePin,
    reorderColumns,
    selectAll,
    deselectAll,
    loadView,
    saveView,
    resetToDefault,
    toggleGroup,
    setSearchTerm
  };
}

