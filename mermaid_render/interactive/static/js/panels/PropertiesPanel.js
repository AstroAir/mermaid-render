/**
 * Properties Panel - Handles element property editing UI
 * @module panels/PropertiesPanel
 */

class PropertiesPanel {
    /**
     * Create a PropertiesPanel instance
     * @param {string} containerId - The ID of the properties content container
     */
    constructor(containerId = 'properties-content') {
        this.container = document.getElementById(containerId);
        this.selectedElementId = null;
        this.elements = null;
        this.onPropertyChangeCallbacks = [];
    }

    /**
     * Set the elements map reference
     * @param {Map} elements - Map of element ID to element data
     */
    setElements(elements) {
        this.elements = elements;
    }

    /**
     * Update the properties panel for selected element(s)
     * @param {Set|null} selectedElements - Set of selected element IDs
     */
    update(selectedElements) {
        if (!this.container) return;

        if (!selectedElements || selectedElements.size === 0) {
            this._showNoSelection();
            this.selectedElementId = null;
            return;
        }

        // Get first selected element
        const elementId = Array.from(selectedElements)[0];
        this.selectedElementId = elementId;

        if (!this.elements) {
            this._showNoSelection();
            return;
        }

        const element = this.elements.get(elementId);
        if (!element) {
            this._showNoSelection();
            return;
        }

        this._renderProperties(element);
    }

    /**
     * Show no selection message
     * @private
     */
    _showNoSelection() {
        this.container.innerHTML = `
            <div class="no-selection">
                <p>Select an element to edit its properties</p>
            </div>
        `;
    }

    /**
     * Render properties for an element
     * @param {Object} element - The element data
     * @private
     */
    _renderProperties(element) {
        this.container.innerHTML = `
            <div class="property-group">
                <h5>Basic Properties</h5>
                <div class="property-field">
                    <label>Label</label>
                    <input type="text" id="prop-label" value="${this._escapeHtml(element.label)}">
                </div>
                <div class="property-field">
                    <label>Width</label>
                    <input type="number" id="prop-width" value="${element.width}" min="20" max="500">
                </div>
                <div class="property-field">
                    <label>Height</label>
                    <input type="number" id="prop-height" value="${element.height}" min="20" max="500">
                </div>
            </div>
            <div class="property-group">
                <h5>Position</h5>
                <div class="property-field">
                    <label>X</label>
                    <input type="number" id="prop-x" value="${Math.round(element.x)}">
                </div>
                <div class="property-field">
                    <label>Y</label>
                    <input type="number" id="prop-y" value="${Math.round(element.y)}">
                </div>
            </div>
            <div class="property-group">
                <h5>Style</h5>
                <div class="property-field">
                    <label>Shape</label>
                    <select id="prop-shape">
                        <option value="rectangle" ${element.type === 'rectangle' ? 'selected' : ''}>Rectangle</option>
                        <option value="circle" ${element.type === 'circle' ? 'selected' : ''}>Circle</option>
                        <option value="diamond" ${element.type === 'diamond' ? 'selected' : ''}>Diamond</option>
                        <option value="hexagon" ${element.type === 'hexagon' ? 'selected' : ''}>Hexagon</option>
                    </select>
                </div>
            </div>
            <div class="property-group">
                <h5>Actions</h5>
                <button id="prop-delete" class="btn btn-small btn-danger">Delete Element</button>
                <button id="prop-duplicate" class="btn btn-small">Duplicate</button>
            </div>
        `;

        this._attachEventListeners(element.id);
    }

    /**
     * Attach event listeners to property inputs
     * @param {string} elementId - The element ID
     * @private
     */
    _attachEventListeners(elementId) {
        // Property inputs
        const properties = ['label', 'width', 'height', 'x', 'y'];
        properties.forEach(prop => {
            const input = document.getElementById(`prop-${prop}`);
            if (input) {
                input.addEventListener('input', () => {
                    this._handlePropertyChange(elementId, prop, input.value);
                });
            }
        });

        // Shape select
        const shapeSelect = document.getElementById('prop-shape');
        if (shapeSelect) {
            shapeSelect.addEventListener('change', () => {
                this._handlePropertyChange(elementId, 'type', shapeSelect.value);
            });
        }

        // Delete button
        const deleteBtn = document.getElementById('prop-delete');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => {
                this._handleDelete(elementId);
            });
        }

        // Duplicate button
        const duplicateBtn = document.getElementById('prop-duplicate');
        if (duplicateBtn) {
            duplicateBtn.addEventListener('click', () => {
                this._handleDuplicate(elementId);
            });
        }
    }

    /**
     * Handle property change
     * @param {string} elementId - The element ID
     * @param {string} property - The property name
     * @param {*} value - The new value
     * @private
     */
    _handlePropertyChange(elementId, property, value) {
        // Notify callbacks
        this.onPropertyChangeCallbacks.forEach(callback => {
            callback(elementId, property, value);
        });
    }

    /**
     * Handle element deletion
     * @param {string} elementId - The element ID
     * @private
     */
    _handleDelete(elementId) {
        this.onPropertyChangeCallbacks.forEach(callback => {
            callback(elementId, '_delete', true);
        });
    }

    /**
     * Handle element duplication
     * @param {string} elementId - The element ID
     * @private
     */
    _handleDuplicate(elementId) {
        this.onPropertyChangeCallbacks.forEach(callback => {
            callback(elementId, '_duplicate', true);
        });
    }

    /**
     * Register callback for property changes
     * @param {Function} callback - Callback function (elementId, property, value) => void
     */
    onPropertyChange(callback) {
        this.onPropertyChangeCallbacks.push(callback);
    }

    /**
     * Remove property change callback
     * @param {Function} callback - The callback to remove
     */
    offPropertyChange(callback) {
        const index = this.onPropertyChangeCallbacks.indexOf(callback);
        if (index > -1) {
            this.onPropertyChangeCallbacks.splice(index, 1);
        }
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     * @private
     */
    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Refresh the panel with current element data
     */
    refresh() {
        if (this.selectedElementId && this.elements) {
            const element = this.elements.get(this.selectedElementId);
            if (element) {
                this._renderProperties(element);
            } else {
                this._showNoSelection();
            }
        }
    }

    /**
     * Clear the properties panel
     */
    clear() {
        this.selectedElementId = null;
        this._showNoSelection();
    }

    /**
     * Get currently selected element ID
     * @returns {string|null} Selected element ID
     */
    getSelectedElementId() {
        return this.selectedElementId;
    }
}

// Export for use in other modules
window.PropertiesPanel = PropertiesPanel;
