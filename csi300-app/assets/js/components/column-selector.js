/**
 * CSI300 Column Selector Component
 * A sophisticated multi-select dropdown for managing table columns
 * Features: search, grouping, pinning, drag-to-reorder, view management
 */

class CSI300ColumnSelector {
    constructor(manifest, options = {}) {
        this.manifest = manifest;
        this.options = {
            container: options.container || document.body,
            onColumnChange: options.onColumnChange || (() => {}),
            onViewChange: options.onViewChange || (() => {}),
            maxPinnedColumns: options.maxPinnedColumns || 3,
            ...options
        };
        
        this.selectedColumns = [];
        this.pinnedColumns = [];
        this.columnOrder = [];
        this.activeView = 'default';
        this.searchTerm = '';
        this.isOpen = false;
        this.draggedColumn = null;
        
        this.init();
    }
    
    init() {
        this.createSelectorUI();
        this.loadDefaultView();
        this.bindEvents();
    }
    
    createSelectorUI() {
        const container = typeof this.options.container === 'string' 
            ? document.querySelector(this.options.container)
            : this.options.container;
            
        const selectorHTML = `
            <div class="column-selector-wrapper">
                <button class="column-selector-trigger" id="columnSelectorTrigger">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    <span>Columns</span>
                    <span class="column-count" id="columnCount">0</span>
                    <svg class="dropdown-arrow" width="12" height="12" viewBox="0 0 12 12" fill="none">
                        <path d="M3 5l3 3 3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </button>
                
                <div class="column-selector-dropdown" id="columnSelectorDropdown" style="display: none;">
                    <div class="column-selector-content">
                        <div class="column-selector-top">
                            <div class="column-selector-search">
                                <input 
                                    type="text" 
                                    id="columnSearchInput" 
                                    placeholder="Search columns..."
                                    class="column-search-input"
                                />
                            </div>
                            <div class="view-management">
                                <select id="viewSelector" class="view-selector"></select>
                                <div class="view-actions">
                                    <button class="view-action-btn" id="saveViewBtn" title="Save current view">
                                        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                                            <path d="M11 1H3a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2V3a2 2 0 00-2-2z" stroke="currentColor" stroke-width="1.5"/>
                                            <path d="M9 1v4H5V1M7 9v4" stroke="currentColor" stroke-width="1.5"/>
                                        </svg>
                                    </button>
                                    <button class="view-action-btn" id="resetViewBtn" title="Reset to default">
                                        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                                            <path d="M1 7a6 6 0 0111.17-3M13 7A6 6 0 011.83 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                                            <path d="M1 3v4h4M13 11V7h-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                        </svg>
                                    </button>
                                </div>
                            </div>
                            <div class="quick-actions">
                                <button class="quick-action-btn" id="selectAllBtn">Select All</button>
                                <button class="quick-action-btn" id="deselectAllBtn">Deselect All</button>
                            </div>
                        </div>
                        
                        <div class="column-selector-divider"></div>

                        <div class="column-selector-body">
                            <section class="column-panel column-panel--selected">
                                <header class="column-panel__header">
                                    <span class="column-panel__title">Selected Columns</span>
                                    <span class="column-panel__badge" id="sidebarCount">0</span>
                                </header>
                                <div class="column-panel__content column-panel__content--selected">
                                    <div class="selected-columns-list" id="selectedColumnsList"></div>
                                </div>
                            </section>

                            <section class="column-panel-all">
                                <header class="column-panel-all__header">
                                    <span class="column-panel__title">All Columns</span>
                                </header>
                                <div class="column-panel-all__content">
                                    <div class="column-groups" id="columnGroups">
                                        <!-- Groups will be dynamically inserted here -->
                                    </div>
                                </div>
                            </section>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.insertAdjacentHTML('beforeend', selectorHTML);
        this.renderGroups();
        this.renderPresetViews();
    }
    
    renderGroups() {
        const groupsContainer = document.getElementById('columnGroups');
        groupsContainer.innerHTML = '';
        
        this.manifest.groups.forEach(group => {
            const groupColumns = this.manifest.columns.filter(col => col.group === group.id);
            
            const groupHTML = `
                <div class="column-group" data-group="${group.id}">
                    <div class="column-group-header" data-group-id="${group.id}">
                        <svg class="group-expand-icon ${group.collapsed ? 'collapsed' : ''}" width="12" height="12" viewBox="0 0 12 12" fill="none">
                            <path d="M3 5l3 3 3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                        <span class="group-name">${group.name}</span>
                        <span class="group-count">(${groupColumns.length})</span>
                    </div>
                    <div class="column-group-items ${group.collapsed ? 'collapsed' : ''}" data-group-items="${group.id}">
                        ${groupColumns.map(col => this.renderColumnItem(col)).join('')}
                    </div>
                </div>
            `;
            
            groupsContainer.insertAdjacentHTML('beforeend', groupHTML);
        });
    }
    
    renderColumnItem(column) {
        const isSelected = this.selectedColumns.includes(column.id);
        const isPinned = this.pinnedColumns.includes(column.id);
        
        return `
            <div class="column-item ${isSelected ? 'selected' : ''}" data-column-id="${column.id}">
                <input 
                    type="checkbox" 
                    class="column-checkbox" 
                    value="${column.id}"
                    ${isSelected ? 'checked' : ''}
                />
                <span class="column-name" title="${column.displayName}">${column.displayName}</span>
                ${column.pinnable && isSelected ? `
                    <button 
                        class="pin-btn ${isPinned ? 'pinned' : ''}" 
                        data-column-id="${column.id}"
                        title="${isPinned ? 'Unpin' : 'Pin'} column"
                    >
                        PIN
                    </button>
                ` : ''}
            </div>
        `;
    }
    
    renderPresetViews() {
        const viewSelector = document.getElementById('viewSelector');
        if (!viewSelector) return;

        viewSelector.innerHTML = '';
        
        this.manifest.presetViews.forEach(view => {
            const option = document.createElement('option');
            option.value = view.id;
            option.textContent = view.name + (view.isSystem ? ' (System)' : '');
            if (this.activeView === view.id) {
                option.selected = true;
            }
            viewSelector.appendChild(option);
        });
        
        // Add custom views from localStorage
        const customViews = this.loadCustomViews();
        if (customViews.length > 0) {
            const optgroup = document.createElement('optgroup');
            optgroup.label = 'Custom Views';
            customViews.forEach(view => {
                const option = document.createElement('option');
                option.value = 'custom_' + view.id;
                option.textContent = view.name;
                if (this.activeView === option.value) {
                    option.selected = true;
                }
                optgroup.appendChild(option);
            });
            viewSelector.appendChild(optgroup);
        }

        if (!viewSelector.value) {
            viewSelector.value = this.activeView || 'default';
        }
    }
    
    renderSelectedColumns() {
        const container = document.getElementById('selectedColumnsList');
        if (this.selectedColumns.length === 0) {
            container.innerHTML = '<div class="no-columns-selected">No columns selected</div>';
            return;
        }
        
        // Sort by current order
        const orderedColumns = this.columnOrder.length > 0
            ? this.columnOrder
                .filter(id => this.selectedColumns.includes(id))
                .concat(this.selectedColumns.filter(id => !this.columnOrder.includes(id)))
            : this.selectedColumns;
        
        container.innerHTML = orderedColumns.map(columnId => {
            const column = this.manifest.columns.find(c => c.id === columnId);
            const isPinned = this.pinnedColumns.includes(columnId);
            
            return `
                <div class="selected-column-item ${isPinned ? 'pinned' : ''}" 
                     data-column-id="${columnId}"
                     draggable="true">
                    <svg class="drag-handle" width="12" height="12" viewBox="0 0 12 12" fill="none">
                        <circle cx="4" cy="3" r="1" fill="currentColor"/>
                        <circle cx="8" cy="3" r="1" fill="currentColor"/>
                        <circle cx="4" cy="6" r="1" fill="currentColor"/>
                        <circle cx="8" cy="6" r="1" fill="currentColor"/>
                        <circle cx="4" cy="9" r="1" fill="currentColor"/>
                        <circle cx="8" cy="9" r="1" fill="currentColor"/>
                    </svg>
                    <span class="column-name" title="${column.displayName}">${column.displayName}</span>
                    ${isPinned ? '<span class="pin-indicator">PINNED</span>' : ''}
                </div>
            `;
        }).join('');
        
        this.updateColumnCount();
    }
    
    bindEvents() {
        // Toggle dropdown
        document.getElementById('columnSelectorTrigger').addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleDropdown();
        });
        
        // Close on outside click
        document.addEventListener('click', (e) => {
            const dropdown = document.getElementById('columnSelectorDropdown');
            const trigger = document.getElementById('columnSelectorTrigger');
            if (!dropdown.contains(e.target) && !trigger.contains(e.target)) {
                this.closeDropdown();
            }
        });
        
        // Reposition dropdown on scroll and resize
        window.addEventListener('scroll', () => {
            if (this.isOpen) {
                this.repositionDropdown();
            }
        }, true); // Use capture phase to catch all scroll events
        
        window.addEventListener('resize', () => {
            if (this.isOpen) {
                this.repositionDropdown();
            }
        });
        
        // Search functionality
        document.getElementById('columnSearchInput').addEventListener('input', (e) => {
            this.searchTerm = e.target.value.toLowerCase();
            this.filterColumns();
        });
        
        // Group toggle
        document.getElementById('columnGroups').addEventListener('click', (e) => {
            const header = e.target.closest('.column-group-header');
            if (header) {
                this.toggleGroup(header.dataset.groupId);
            }
        });
        
        // Column selection - handle clicks on entire row
        document.getElementById('columnGroups').addEventListener('click', (e) => {
            // Skip if clicking on pin button
            if (e.target.closest('.pin-btn')) {
                return;
            }
            
            const columnItem = e.target.closest('.column-item');
            if (columnItem) {
                const checkbox = columnItem.querySelector('.column-checkbox');
                if (checkbox && e.target !== checkbox) {
                    // Toggle checkbox when clicking anywhere on the row (except the checkbox itself)
                    checkbox.checked = !checkbox.checked;
                    this.toggleColumn(checkbox.value, checkbox.checked);
                }
            }
        });
        
        // Column selection - handle direct checkbox clicks
        document.getElementById('columnGroups').addEventListener('change', (e) => {
            if (e.target.classList.contains('column-checkbox')) {
                this.toggleColumn(e.target.value, e.target.checked);
            }
        });
        
        // Pin button
        document.getElementById('columnGroups').addEventListener('click', (e) => {
            const pinBtn = e.target.closest('.pin-btn');
            if (pinBtn) {
                e.preventDefault();
                this.togglePin(pinBtn.dataset.columnId);
            }
        });
        
        // Quick actions
        document.getElementById('selectAllBtn').addEventListener('click', () => this.selectAll());
        document.getElementById('deselectAllBtn').addEventListener('click', () => this.deselectAll());
        
        // View management
        document.getElementById('viewSelector').addEventListener('change', (e) => {
            this.loadView(e.target.value);
        });
        
        document.getElementById('saveViewBtn').addEventListener('click', () => this.saveView());
        document.getElementById('resetViewBtn').addEventListener('click', () => this.resetToDefault());
        
        // Double-click to remove from Selected Columns
        document.getElementById('selectedColumnsList').addEventListener('dblclick', (e) => {
            const columnItem = e.target.closest('.selected-column-item');
            if (columnItem) {
                const columnId = columnItem.dataset.columnId;
                this.toggleColumn(columnId);
            }
        });
        
        // Drag and drop for reordering
        this.bindDragEvents();
    }
    
    bindDragEvents() {
        const container = document.getElementById('selectedColumnsList');
        
        container.addEventListener('dragstart', (e) => {
            if (e.target.classList.contains('selected-column-item')) {
                this.draggedColumn = e.target.dataset.columnId;
                e.target.classList.add('dragging');
            }
        });
        
        container.addEventListener('dragend', (e) => {
            if (e.target.classList.contains('selected-column-item')) {
                e.target.classList.remove('dragging');
                this.draggedColumn = null;
            }
        });
        
        container.addEventListener('dragover', (e) => {
            e.preventDefault();
            const afterElement = this.getDragAfterElement(container, e.clientY);
            const dragging = document.querySelector('.dragging');
            
            if (afterElement == null) {
                container.appendChild(dragging);
            } else {
                container.insertBefore(dragging, afterElement);
            }
        });
        
        container.addEventListener('drop', (e) => {
            e.preventDefault();
            this.updateColumnOrder();
        });
    }
    
    getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.selected-column-item:not(.dragging)')];
        
        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }
    
    repositionDropdown() {
        if (!this.isOpen) return;
        
        const dropdown = document.getElementById('columnSelectorDropdown');
        const trigger = document.getElementById('columnSelectorTrigger');
        
        if (!dropdown || !trigger) return;
        
        // Calculate position relative to trigger button
        const triggerRect = trigger.getBoundingClientRect();
        const dropdownHeight = Math.min(900, window.innerHeight * 0.7);
        const dropdownWidth = Math.min(920, window.innerWidth * 0.92);
        
        // Calculate top position (below the trigger)
        let top = triggerRect.bottom + 8;
        
        // Check if dropdown would go below viewport
        if (top + dropdownHeight > window.innerHeight) {
            // Position above the trigger instead
            top = triggerRect.top - dropdownHeight - 8;
            
            // If still doesn't fit, align to top with some padding
            if (top < 0) {
                top = 8;
            }
        }
        
        // Calculate right position
        let right = window.innerWidth - triggerRect.right;
        
        // Ensure dropdown doesn't go off left edge
        if (triggerRect.right - dropdownWidth < 0) {
            right = 8; // Align to right edge with padding
        }
        
        dropdown.style.top = `${top}px`;
        dropdown.style.right = `${right}px`;
    }
    
    toggleDropdown() {
        this.isOpen = !this.isOpen;
        const dropdown = document.getElementById('columnSelectorDropdown');
        const trigger = document.getElementById('columnSelectorTrigger');
        
        if (this.isOpen) {
            dropdown.style.display = 'flex';
            trigger.classList.add('open');
            this.repositionDropdown();
        } else {
            dropdown.style.display = 'none';
            trigger.classList.remove('open');
        }
    }
    
    closeDropdown() {
        this.isOpen = false;
        const dropdown = document.getElementById('columnSelectorDropdown');
        if (dropdown) {
            dropdown.style.display = 'none';
        }
        const trigger = document.getElementById('columnSelectorTrigger');
        if (trigger) {
            trigger.classList.remove('open');
        }
    }
    
    toggleGroup(groupId) {
        const header = document.querySelector(`[data-group-id="${groupId}"]`);
        const items = document.querySelector(`[data-group-items="${groupId}"]`);
        const icon = header.querySelector('.group-expand-icon');
        
        items.classList.toggle('collapsed');
        icon.classList.toggle('collapsed');
    }
    
    toggleColumn(columnId, isSelected) {
        if (isSelected) {
            if (!this.selectedColumns.includes(columnId)) {
                this.selectedColumns.push(columnId);
            }
            if (!this.columnOrder.includes(columnId)) {
                this.columnOrder.push(columnId);
            }
        } else {
            this.selectedColumns = this.selectedColumns.filter(id => id !== columnId);
            this.pinnedColumns = this.pinnedColumns.filter(id => id !== columnId);
            this.columnOrder = this.columnOrder.filter(id => id !== columnId);
        }
        
        // Update visual state in All Columns section
        this.updateColumnItemState(columnId, isSelected);
        
        this.renderSelectedColumns();
        this.saveCurrentState();
        this.notifyColumnChange();
    }
    
    updateColumnItemState(columnId, isSelected) {
        const columnItem = document.querySelector(`.column-item[data-column-id="${columnId}"]`);
        if (columnItem) {
            if (isSelected) {
                columnItem.classList.add('selected');
            } else {
                columnItem.classList.remove('selected');
            }
            
            // Update pin button visibility
            const pinBtn = columnItem.querySelector('.pin-btn');
            const column = this.manifest.columns.find(c => c.id === columnId);
            if (column && column.pinnable) {
                if (isSelected && !pinBtn) {
                    const isPinned = this.pinnedColumns.includes(columnId);
                    const pinBtnHTML = `
                        <button 
                            class="pin-btn ${isPinned ? 'pinned' : ''}" 
                            data-column-id="${columnId}"
                            title="${isPinned ? 'Unpin' : 'Pin'} column"
                        >
                            PIN
                        </button>
                    `;
                    columnItem.insertAdjacentHTML('beforeend', pinBtnHTML);
                } else if (!isSelected && pinBtn) {
                    pinBtn.remove();
                }
            }
        }
    }
    
    togglePin(columnId) {
        const column = this.manifest.columns.find(c => c.id === columnId);
        if (!column || !column.pinnable) return;
        
        if (this.pinnedColumns.includes(columnId)) {
            this.pinnedColumns = this.pinnedColumns.filter(id => id !== columnId);
        } else {
            if (this.pinnedColumns.length >= this.options.maxPinnedColumns) {
                alert(`Maximum ${this.options.maxPinnedColumns} pinned columns allowed`);
                return;
            }
            this.pinnedColumns.push(columnId);
        }
        
        this.renderGroups();
        this.renderSelectedColumns();
        this.saveCurrentState();
        this.notifyColumnChange();
    }
    
    filterColumns() {
        const groups = document.querySelectorAll('.column-group');
        
        groups.forEach(group => {
            const items = group.querySelectorAll('.column-item');
            let visibleCount = 0;
            
            items.forEach(item => {
                const label = item.querySelector('.column-name').textContent.toLowerCase();
                const matches = label.includes(this.searchTerm);
                item.style.display = matches ? 'flex' : 'none';
                if (matches) visibleCount++;
            });
            
            // Hide group if no matches
            group.style.display = visibleCount > 0 ? 'block' : 'none';
        });
    }
    
    selectAll() {
        this.selectedColumns = this.manifest.columns.map(col => col.id);
        this.columnOrder = [...this.selectedColumns];
        this.renderGroups();
        this.renderSelectedColumns();
        this.saveCurrentState();
        this.notifyColumnChange();
    }
    
    deselectAll() {
        const defaultPinned = this.manifest.columns
            .filter(col => col.defaultPinned)
            .map(col => col.id);
        
        this.selectedColumns = defaultPinned;
        this.pinnedColumns = defaultPinned;
        this.columnOrder = [...defaultPinned];
        this.renderGroups();
        this.renderSelectedColumns();
        this.saveCurrentState();
        this.notifyColumnChange();
    }
    
    loadView(viewId) {
        if (!viewId) return;
        
        let view;
        if (viewId.startsWith('custom_')) {
            const customViews = this.loadCustomViews();
            view = customViews.find(v => 'custom_' + v.id === viewId);
        } else {
            view = this.manifest.presetViews.find(v => v.id === viewId);
        }
        
        if (view) {
            this.selectedColumns = [...view.columns];
            this.pinnedColumns = [...(view.pinnedColumns || [])];
            this.columnOrder = [...view.columns];
            this.activeView = viewId;
            this.renderGroups();
            this.renderSelectedColumns();
            this.saveCurrentState();
            const selector = document.getElementById('viewSelector');
            if (selector) {
                selector.value = viewId;
            }
            this.notifyColumnChange();
            this.options.onViewChange(view);
        }
    }
    
    loadDefaultView() {
        const savedState = localStorage.getItem('csi300_column_state');
        
        if (savedState) {
            const state = JSON.parse(savedState);
            this.selectedColumns = state.selectedColumns || [];
            this.pinnedColumns = state.pinnedColumns || [];
            this.columnOrder = state.columnOrder || [];
            this.activeView = state.activeView || 'default';
        } else {
            const defaultView = this.manifest.presetViews.find(v => v.id === 'default');
            if (defaultView) {
                this.selectedColumns = [...defaultView.columns];
                this.pinnedColumns = [...defaultView.pinnedColumns];
                this.columnOrder = [...defaultView.columns];
                this.activeView = defaultView.id;
            }
        }
        
        this.renderGroups();
        this.renderPresetViews();
        this.renderSelectedColumns();
        const selector = document.getElementById('viewSelector');
        if (selector) {
            selector.value = this.activeView;
        }
        this.notifyColumnChange();
    }
    
    saveView() {
        const viewName = prompt('Enter a name for this view:');
        if (!viewName) return;
        
        const customViews = this.loadCustomViews();
        const newView = {
            id: Date.now().toString(),
            name: viewName,
            columns: [...this.selectedColumns],
            pinnedColumns: [...this.pinnedColumns],
            columnOrder: [...this.columnOrder],
            createdAt: new Date().toISOString()
        };
        
        customViews.push(newView);
        localStorage.setItem('csi300_custom_views', JSON.stringify(customViews));
        
        this.activeView = 'custom_' + newView.id;
        this.renderPresetViews();
        const selector = document.getElementById('viewSelector');
        if (selector) {
            selector.value = this.activeView;
        }
        alert('View saved successfully!');
    }
    
    resetToDefault() {
        if (confirm('Reset to default view? This will discard current column selection.')) {
            this.loadView('default');
        }
    }
    
    updateColumnOrder() {
        const items = document.querySelectorAll('.selected-column-item');
        this.columnOrder = Array.from(items).map(item => item.dataset.columnId);
        this.saveCurrentState();
        this.notifyColumnChange();
    }
    
    saveCurrentState() {
        const state = {
            selectedColumns: this.selectedColumns,
            pinnedColumns: this.pinnedColumns,
            columnOrder: this.columnOrder,
            activeView: this.activeView,
            lastUpdated: new Date().toISOString()
        };
        localStorage.setItem('csi300_column_state', JSON.stringify(state));
    }
    
    loadCustomViews() {
        const saved = localStorage.getItem('csi300_custom_views');
        return saved ? JSON.parse(saved) : [];
    }
    
    updateColumnCount() {
        const count = this.selectedColumns.length;
        document.getElementById('columnCount').textContent = count;
        
        // Update sidebar count
        const sidebarCount = document.getElementById('sidebarCount');
        if (sidebarCount) {
            sidebarCount.textContent = count;
        }
    }
    
    notifyColumnChange() {
        const data = {
            selectedColumns: this.selectedColumns,
            pinnedColumns: this.pinnedColumns,
            columnOrder: this.columnOrder,
            columns: this.getOrderedColumns()
        };
        console.log('[ColumnSelector] notifyColumnChange called with:', {
            selectedCount: data.selectedColumns.length,
            pinnedCount: data.pinnedColumns.length,
            columnsCount: data.columns.length,
            columns: data.columns.map(c => c.id)
        });
        this.options.onColumnChange(data);
    }
    
    getOrderedColumns() {
        const orderedIds = this.columnOrder.length > 0
            ? this.columnOrder.filter(id => this.selectedColumns.includes(id))
            : this.selectedColumns;
        
        return orderedIds.map(id => this.manifest.columns.find(c => c.id === id)).filter(Boolean);
    }
    
    getSelectedColumns() {
        return this.getOrderedColumns();
    }
    
    getPinnedColumns() {
        return this.pinnedColumns
            .map(id => this.manifest.columns.find(c => c.id === id))
            .filter(Boolean);
    }
}

// Export to window for browser usage
if (typeof window !== 'undefined') {
    window.CSI300ColumnSelector = CSI300ColumnSelector;
}

// Export for use in Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CSI300ColumnSelector;
}
