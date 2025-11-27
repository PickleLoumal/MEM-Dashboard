/**
 * CSI300 Column Selector Component
 * A sophisticated multi-select dropdown for managing table columns
 * Features: search, grouping, pinning, drag-to-reorder, view management
 */

import React, { useCallback, useEffect, useRef, useState } from 'react';
import type { ColumnDefinition, ColumnManifest, ColumnSelectorProps } from './types';
import { useColumnSelector } from './useColumnSelector';

// Icons as inline SVG components
const ColumnsIcon = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
  </svg>
);

const ChevronDownIcon = ({ className }: { className?: string }) => (
  <svg className={className} width="12" height="12" viewBox="0 0 12 12" fill="none">
    <path d="M3 5l3 3 3-3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const SaveIcon = () => (
  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
    <path d="M11 1H3a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2V3a2 2 0 00-2-2z" stroke="currentColor" strokeWidth="1.5" />
    <path d="M9 1v4H5V1M7 9v4" stroke="currentColor" strokeWidth="1.5" />
  </svg>
);

const ResetIcon = () => (
  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
    <path d="M1 7a6 6 0 0111.17-3M13 7A6 6 0 011.83 10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    <path d="M1 3v4h4M13 11V7h-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const DragHandleIcon = () => (
  <svg className="drag-handle" width="12" height="12" viewBox="0 0 12 12" fill="none">
    <circle cx="4" cy="3" r="1" fill="currentColor" />
    <circle cx="8" cy="3" r="1" fill="currentColor" />
    <circle cx="4" cy="6" r="1" fill="currentColor" />
    <circle cx="8" cy="6" r="1" fill="currentColor" />
    <circle cx="4" cy="9" r="1" fill="currentColor" />
    <circle cx="8" cy="9" r="1" fill="currentColor" />
  </svg>
);

// Selected column item with drag support
interface SelectedColumnItemProps {
  column: ColumnDefinition;
  isPinned: boolean;
  onDragStart: (e: React.DragEvent, columnId: string) => void;
  onDragEnd: () => void;
  onDragOver: (e: React.DragEvent) => void;
  onDrop: (e: React.DragEvent, targetId: string) => void;
  onDoubleClick: (columnId: string) => void;
}

function SelectedColumnItem({
  column,
  isPinned,
  onDragStart,
  onDragEnd,
  onDragOver,
  onDrop,
  onDoubleClick
}: SelectedColumnItemProps) {
  return (
    <div
      className={`selected-column-item ${isPinned ? 'pinned' : ''}`}
      data-column-id={column.id}
      draggable
      onDragStart={(e) => onDragStart(e, column.id)}
      onDragEnd={onDragEnd}
      onDragOver={onDragOver}
      onDrop={(e) => onDrop(e, column.id)}
      onDoubleClick={() => onDoubleClick(column.id)}
    >
      <DragHandleIcon />
      <span className="column-name" title={column.displayName}>
        {column.displayName}
      </span>
      {isPinned && <span className="pin-indicator">PINNED</span>}
    </div>
  );
}

// Column item in the "All Columns" section
interface ColumnItemProps {
  column: ColumnDefinition;
  isSelected: boolean;
  isPinned: boolean;
  onToggle: (columnId: string, isSelected: boolean) => void;
  onTogglePin: (columnId: string) => void;
}

function ColumnItem({ column, isSelected, isPinned, onToggle, onTogglePin }: ColumnItemProps) {
  const handleClick = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('.pin-btn')) return;
    onToggle(column.id, !isSelected);
  };

  return (
    <div className={`column-item ${isSelected ? 'selected' : ''}`} data-column-id={column.id} onClick={handleClick}>
      <input
        type="checkbox"
        className="column-checkbox"
        checked={isSelected}
        onChange={(e) => onToggle(column.id, e.target.checked)}
      />
      <span className="column-name" title={column.displayName}>
        {column.displayName}
      </span>
      {column.pinnable && isSelected && (
        <button
          className={`pin-btn ${isPinned ? 'pinned' : ''}`}
          onClick={(e) => {
            e.stopPropagation();
            onTogglePin(column.id);
          }}
          title={isPinned ? 'Unpin column' : 'Pin column'}
        >
          PIN
        </button>
      )}
    </div>
  );
}

// Column group with collapsible header
interface ColumnGroupProps {
  group: { id: string; name: string; columns: ColumnDefinition[] };
  isCollapsed: boolean;
  selectedColumns: string[];
  pinnedColumns: string[];
  onToggleGroup: (groupId: string) => void;
  onToggleColumn: (columnId: string, isSelected: boolean) => void;
  onTogglePin: (columnId: string) => void;
}

function ColumnGroup({
  group,
  isCollapsed,
  selectedColumns,
  pinnedColumns,
  onToggleGroup,
  onToggleColumn,
  onTogglePin
}: ColumnGroupProps) {
  return (
    <div className="column-group" data-group={group.id}>
      <div className="column-group-header" onClick={() => onToggleGroup(group.id)}>
        <ChevronDownIcon className={`group-expand-icon ${isCollapsed ? 'collapsed' : ''}`} />
        <span className="group-name">{group.name}</span>
        <span className="group-count">({group.columns.length})</span>
      </div>
      <div className={`column-group-items ${isCollapsed ? 'collapsed' : ''}`}>
        {group.columns.map((column) => (
          <ColumnItem
            key={column.id}
            column={column}
            isSelected={selectedColumns.includes(column.id)}
            isPinned={pinnedColumns.includes(column.id)}
            onToggle={onToggleColumn}
            onTogglePin={onTogglePin}
          />
        ))}
      </div>
    </div>
  );
}

export function ColumnSelector({ manifest, maxPinnedColumns = 3, onColumnChange, onViewChange }: ColumnSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [draggedColumn, setDraggedColumn] = useState<string | null>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const {
    selectedColumns,
    pinnedColumns,
    columnOrder,
    activeView,
    searchTerm,
    collapsedGroups,
    orderedColumns,
    filteredGroups,
    allViews,
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
  } = useColumnSelector(manifest, { maxPinnedColumns, onColumnChange, onViewChange });

  // Position dropdown relative to trigger
  const repositionDropdown = useCallback(() => {
    if (!isOpen || !triggerRef.current || !dropdownRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const dropdownHeight = Math.min(900, window.innerHeight * 0.7);
    const dropdownWidth = Math.min(920, window.innerWidth * 0.92);

    let top = triggerRect.bottom + 8;
    if (top + dropdownHeight > window.innerHeight) {
      top = triggerRect.top - dropdownHeight - 8;
      if (top < 0) top = 8;
    }

    let right = window.innerWidth - triggerRect.right;
    if (triggerRect.right - dropdownWidth < 0) {
      right = 8;
    }

    dropdownRef.current.style.top = `${top}px`;
    dropdownRef.current.style.right = `${right}px`;
  }, [isOpen]);

  // Reposition on scroll/resize
  useEffect(() => {
    if (!isOpen) return;

    repositionDropdown();

    const handleScroll = () => repositionDropdown();
    const handleResize = () => repositionDropdown();

    window.addEventListener('scroll', handleScroll, true);
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('scroll', handleScroll, true);
      window.removeEventListener('resize', handleResize);
    };
  }, [isOpen, repositionDropdown]);

  // Close on outside click
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!dropdownRef.current?.contains(target) && !triggerRef.current?.contains(target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [isOpen]);

  // Drag and drop handlers
  const handleDragStart = useCallback((e: React.DragEvent, columnId: string) => {
    setDraggedColumn(columnId);
    (e.target as HTMLElement).classList.add('dragging');
  }, []);

  const handleDragEnd = useCallback(() => {
    setDraggedColumn(null);
    document.querySelectorAll('.dragging').forEach((el) => el.classList.remove('dragging'));
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent, targetId: string) => {
      e.preventDefault();
      if (!draggedColumn || draggedColumn === targetId) return;

      const currentOrder = [...columnOrder];
      const draggedIndex = currentOrder.indexOf(draggedColumn);
      const targetIndex = currentOrder.indexOf(targetId);

      if (draggedIndex === -1 || targetIndex === -1) return;

      currentOrder.splice(draggedIndex, 1);
      currentOrder.splice(targetIndex, 0, draggedColumn);

      reorderColumns(currentOrder);
      setDraggedColumn(null);
    },
    [draggedColumn, columnOrder, reorderColumns]
  );

  const handleSaveView = useCallback(() => {
    const name = prompt('Enter a name for this view:');
    if (name) {
      saveView(name);
      alert('View saved successfully!');
    }
  }, [saveView]);

  const handleResetToDefault = useCallback(() => {
    if (confirm('Reset to default view? This will discard current column selection.')) {
      resetToDefault();
    }
  }, [resetToDefault]);

  const handleRemoveColumn = useCallback(
    (columnId: string) => {
      toggleColumn(columnId, false);
    },
    [toggleColumn]
  );

  return (
    <div className="column-selector-wrapper">
      <button
        ref={triggerRef}
        className={`column-selector-trigger ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <ColumnsIcon />
        <span>Columns</span>
        <span className="column-count">{selectedColumns.length}</span>
        <ChevronDownIcon className="dropdown-arrow" />
      </button>

      {isOpen && (
        <div ref={dropdownRef} className="column-selector-dropdown" style={{ display: 'flex' }}>
          <div className="column-selector-content">
            {/* Top bar: search, view selector, quick actions */}
            <div className="column-selector-top">
              <div className="column-selector-search">
                <input
                  type="text"
                  placeholder="Search columns..."
                  className="column-search-input"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              <div className="view-management">
                <select className="view-selector" value={activeView} onChange={(e) => loadView(e.target.value)}>
                  {allViews.map((view) => (
                    <option key={view.id} value={view.id}>
                      {view.name}
                      {view.type === 'preset' && 'isSystem' in view && view.isSystem ? ' (System)' : ''}
                    </option>
                  ))}
                </select>

                <div className="view-actions">
                  <button className="view-action-btn" onClick={handleSaveView} title="Save current view">
                    <SaveIcon />
                  </button>
                  <button className="view-action-btn" onClick={handleResetToDefault} title="Reset to default">
                    <ResetIcon />
                  </button>
                </div>
              </div>

              <div className="quick-actions">
                <button className="quick-action-btn" onClick={selectAll}>
                  Select All
                </button>
                <button className="quick-action-btn" onClick={deselectAll}>
                  Deselect All
                </button>
              </div>
            </div>

            <div className="column-selector-divider" />

            {/* Body: Selected columns sidebar + All columns */}
            <div className="column-selector-body">
              {/* Selected columns panel */}
              <section className="column-panel column-panel--selected">
                <header className="column-panel__header">
                  <span className="column-panel__title">Selected Columns</span>
                  <span className="column-panel__badge">{selectedColumns.length}</span>
                </header>
                <div className="column-panel__content column-panel__content--selected">
                  <div className="selected-columns-list">
                    {orderedColumns.length === 0 ? (
                      <div className="no-columns-selected">No columns selected</div>
                    ) : (
                      orderedColumns.map((column) => (
                        <SelectedColumnItem
                          key={column.id}
                          column={column}
                          isPinned={pinnedColumns.includes(column.id)}
                          onDragStart={handleDragStart}
                          onDragEnd={handleDragEnd}
                          onDragOver={handleDragOver}
                          onDrop={handleDrop}
                          onDoubleClick={handleRemoveColumn}
                        />
                      ))
                    )}
                  </div>
                </div>
              </section>

              {/* All columns panel */}
              <section className="column-panel-all">
                <header className="column-panel-all__header">
                  <span className="column-panel__title">All Columns</span>
                </header>
                <div className="column-panel-all__content">
                  <div className="column-groups">
                    {filteredGroups.map((group) => (
                      <ColumnGroup
                        key={group.id}
                        group={group}
                        isCollapsed={collapsedGroups.has(group.id)}
                        selectedColumns={selectedColumns}
                        pinnedColumns={pinnedColumns}
                        onToggleGroup={toggleGroup}
                        onToggleColumn={toggleColumn}
                        onTogglePin={togglePin}
                      />
                    ))}
                  </div>
                </div>
              </section>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ColumnSelector;

