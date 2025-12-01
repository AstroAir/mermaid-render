/**
 * Tool Manager - Handles tool initialization, switching, and state management
 * @module tools/ToolManager
 */

class ToolManager {
    /**
     * Create a ToolManager instance
     */
    constructor() {
        this.currentTool = 'select';
        this.tools = new Map();
        this.onToolChangeCallbacks = [];

        this._initializeDefaultTools();
        this._initializeEventListeners();
    }

    /**
     * Initialize default tools configuration
     * @private
     */
    _initializeDefaultTools() {
        // Basic shape tools
        this.basicTools = [
            { id: 'rectangle', name: 'Rectangle', icon: '⬜', category: 'shape' },
            { id: 'circle', name: 'Circle', icon: '⭕', category: 'shape' },
            { id: 'diamond', name: 'Diamond', icon: '🔶', category: 'shape' },
            { id: 'hexagon', name: 'Hexagon', icon: '⬡', category: 'shape' }
        ];

        // Connection tools
        this.connectionTools = [
            { id: 'arrow', name: 'Arrow', icon: '→', category: 'connection' },
            { id: 'line', name: 'Line', icon: '—', category: 'connection' },
            { id: 'dotted', name: 'Dotted', icon: '⋯', category: 'connection' }
        ];

        // Register all tools
        [...this.basicTools, ...this.connectionTools].forEach(tool => {
            this.tools.set(tool.id, tool);
        });

        // Add built-in tools
        this.tools.set('select', { id: 'select', name: 'Select', icon: '🖱️', category: 'control' });
        this.tools.set('pan', { id: 'pan', name: 'Pan', icon: '✋', category: 'control' });
    }

    /**
     * Initialize event listeners for tool buttons
     * @private
     */
    _initializeEventListeners() {
        // Tool buttons in toolbar
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tool = e.target.dataset.tool || e.target.closest('.tool-btn')?.dataset.tool;
                if (tool) {
                    this.setTool(tool);
                }
            });
        });
    }

    /**
     * Populate tool grids in the UI
     */
    populateToolGrids() {
        const basicToolsContainer = document.getElementById('basic-tools');
        const connectionToolsContainer = document.getElementById('connection-tools');

        if (basicToolsContainer) {
            this._populateToolGrid(basicToolsContainer, this.basicTools);
        }

        if (connectionToolsContainer) {
            this._populateToolGrid(connectionToolsContainer, this.connectionTools);
        }
    }

    /**
     * Populate a tool grid container
     * @param {HTMLElement} container - The container element
     * @param {Array} tools - Array of tool configurations
     * @private
     */
    _populateToolGrid(container, tools) {
        container.innerHTML = '';

        tools.forEach(tool => {
            const toolElement = document.createElement('div');
            toolElement.className = 'tool-item';
            toolElement.dataset.tool = tool.id;
            toolElement.innerHTML = `
                <div class="tool-icon">${tool.icon}</div>
                <div class="tool-name">${tool.name}</div>
            `;
            toolElement.addEventListener('click', () => {
                this.setTool(tool.id);
            });
            container.appendChild(toolElement);
        });
    }

    /**
     * Set the current active tool
     * @param {string} toolName - The tool ID to activate
     */
    setTool(toolName) {
        const previousTool = this.currentTool;
        this.currentTool = toolName;

        // Update tool button states
        this._updateToolButtonStates();

        // Notify callbacks
        this.onToolChangeCallbacks.forEach(callback => {
            callback(toolName, previousTool);
        });
    }

    /**
     * Update visual state of tool buttons
     * @private
     */
    _updateToolButtonStates() {
        // Remove active class from all tool buttons and items
        document.querySelectorAll('.tool-btn, .tool-item').forEach(btn => {
            btn.classList.remove('active');
        });

        // Add active class to current tool
        const activeBtn = document.querySelector(`[data-tool="${this.currentTool}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
    }

    /**
     * Get the current active tool
     * @returns {string} Current tool ID
     */
    getCurrentTool() {
        return this.currentTool;
    }

    /**
     * Get tool configuration by ID
     * @param {string} toolId - The tool ID
     * @returns {Object|undefined} Tool configuration
     */
    getTool(toolId) {
        return this.tools.get(toolId);
    }

    /**
     * Check if current tool is a shape tool
     * @returns {boolean} True if current tool creates shapes
     */
    isShapeTool() {
        const tool = this.tools.get(this.currentTool);
        return tool && tool.category === 'shape';
    }

    /**
     * Check if current tool is a connection tool
     * @returns {boolean} True if current tool creates connections
     */
    isConnectionTool() {
        const tool = this.tools.get(this.currentTool);
        return tool && tool.category === 'connection';
    }

    /**
     * Check if current tool is a control tool (select, pan)
     * @returns {boolean} True if current tool is a control tool
     */
    isControlTool() {
        const tool = this.tools.get(this.currentTool);
        return tool && tool.category === 'control';
    }

    /**
     * Register callback for tool change events
     * @param {Function} callback - Callback function (newTool, previousTool) => void
     */
    onToolChange(callback) {
        this.onToolChangeCallbacks.push(callback);
    }

    /**
     * Remove tool change callback
     * @param {Function} callback - The callback to remove
     */
    offToolChange(callback) {
        const index = this.onToolChangeCallbacks.indexOf(callback);
        if (index > -1) {
            this.onToolChangeCallbacks.splice(index, 1);
        }
    }

    /**
     * Register a custom tool
     * @param {Object} tool - Tool configuration
     * @param {string} tool.id - Unique tool ID
     * @param {string} tool.name - Display name
     * @param {string} tool.icon - Icon (emoji or HTML)
     * @param {string} tool.category - Tool category
     */
    registerTool(tool) {
        this.tools.set(tool.id, tool);
    }

    /**
     * Unregister a tool
     * @param {string} toolId - The tool ID to remove
     * @returns {boolean} True if tool was removed
     */
    unregisterTool(toolId) {
        return this.tools.delete(toolId);
    }

    /**
     * Get all tools in a category
     * @param {string} category - The category to filter by
     * @returns {Array} Array of tools in the category
     */
    getToolsByCategory(category) {
        return Array.from(this.tools.values()).filter(tool => tool.category === category);
    }

    /**
     * Get all registered tools
     * @returns {Array} Array of all tools
     */
    getAllTools() {
        return Array.from(this.tools.values());
    }
}

// Export for use in other modules
window.ToolManager = ToolManager;
