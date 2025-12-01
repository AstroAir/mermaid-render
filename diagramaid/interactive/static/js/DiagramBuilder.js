/**
 * Diagram Builder - Main coordinator for the diagram builder application
 * @module DiagramBuilder
 */

class DiagramBuilder {
    /**
     * Create a DiagramBuilder instance
     */
    constructor() {
        // DOM Elements
        this.canvas = document.getElementById('diagram-canvas');
        this.canvasGroup = document.getElementById('canvas-group');

        if (!this.canvas || !this.canvasGroup) {
            console.error('Canvas elements not found');
            return;
        }

        // Data stores
        this.elements = new Map();
        this.connections = new Map();
        this.selectedElements = new Set();

        // Connection creation state
        this.connectionStartNode = null;
        this.pendingConnectionType = null;

        // Undo/Redo history management
        this._historyStack = [];      // Stack of past states
        this._redoStack = [];         // Stack of undone states
        this._maxHistorySize = 50;    // Maximum history entries
        this._isUndoRedoAction = false; // Flag to prevent recording during undo/redo

        // Initialize sub-modules
        this._initializeModules();

        // Setup event handlers
        this._setupEventHandlers();

        // Initial state
        this.updateCode();
    }

    /**
     * Initialize all sub-modules
     * @private
     */
    _initializeModules() {
        // Canvas management
        this.canvasManager = new CanvasManager(this.canvas, this.canvasGroup);

        // Node rendering
        this.nodeRenderer = new NodeRenderer(this.canvasGroup);

        // Tool management
        this.toolManager = new ToolManager();
        this.toolManager.populateToolGrids();

        // Properties panel
        this.propertiesPanel = new PropertiesPanel();
        this.propertiesPanel.setElements(this.elements);

        // Tab management
        this.tabManager = new TabManager();

        // Code generation and validation
        this.codeGenerator = new CodeGenerator(window.DIAGRAM_TYPE || 'flowchart');
        this.codeValidator = new CodeValidator();

        // Preview management
        this.previewManager = new PreviewManager();

        // Export management
        this.exportManager = new ExportManager(this.previewManager);

        // Template management
        this.templateManager = new TemplateManager();

        // Input handling
        this.keyboardHandler = new KeyboardHandler();
        this.mouseHandler = new MouseHandler(this.canvas, this.canvasManager);
    }

    /**
     * Setup event handlers for all modules
     * @private
     */
    _setupEventHandlers() {
        // Tool change handler
        this.toolManager.onToolChange((newTool, previousTool) => {
            this.canvasManager.updateCursor(newTool);
        });

        // Mouse handlers
        this.mouseHandler.onClick((position, event) => {
            this._handleCanvasClick(position, event);
        });

        this.mouseHandler.onDragStart((element, position) => {
            if (element) {
                this.selectElement(element.id);
            }
        });

        this.mouseHandler.onDragMove((element, position, dx, dy) => {
            if (element && this.elements.has(element.id)) {
                const el = this.elements.get(element.id);
                el.x += dx;
                el.y += dy;
                this.nodeRenderer.updateNode(element.id, el, (id) => this.selectElement(id));
            }
        });

        this.mouseHandler.onDragEnd((element, position) => {
            this.updateCode();
            // Update any connections involving this element
            if (element) {
                this._updateConnectionsForElement(element.id);
            }
        });

        // Connection creation callback
        this.mouseHandler.onConnection((source, target) => {
            this._handleConnectionCreated(source, target);
        });

        // Properties panel handler
        this.propertiesPanel.onPropertyChange((elementId, property, value) => {
            this._handlePropertyChange(elementId, property, value);
        });

        // Tab change handler
        this.tabManager.onTabChange((newTab, previousTab) => {
            this._handleTabChange(newTab);
        });

        // Template load handler
        this.templateManager.onTemplateLoad((template) => {
            this._loadTemplate(template);
        });

        // Keyboard shortcuts
        this._setupKeyboardShortcuts();

        // Code editor input
        const codeEditor = document.getElementById('code-editor');
        if (codeEditor) {
            codeEditor.addEventListener('input', () => {
                this.codeValidator.validateAndDisplay(codeEditor.value);
            });
        }

        // Copy code button
        const copyCodeBtn = document.getElementById('copy-code');
        if (copyCodeBtn) {
            copyCodeBtn.addEventListener('click', () => {
                this._copyCode();
            });
        }

        // Apply code button
        const applyCodeBtn = document.getElementById('apply-code');
        if (applyCodeBtn) {
            applyCodeBtn.addEventListener('click', () => {
                this._applyCode();
            });
        }

        // Save button
        const saveBtn = document.getElementById('save-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this._saveDiagram();
            });
        }

        // Undo/Redo buttons
        const undoBtn = document.getElementById('undo');
        const redoBtn = document.getElementById('redo');
        if (undoBtn) {
            undoBtn.addEventListener('click', () => this._undo());
        }
        if (redoBtn) {
            redoBtn.addEventListener('click', () => this._redo());
        }
    }

    /**
     * Setup keyboard shortcuts
     * @private
     */
    _setupKeyboardShortcuts() {
        // Delete selected elements
        this.keyboardHandler.setActionHandler('deleteSelected', () => {
            this._deleteSelectedElements();
        });

        // Copy
        this.keyboardHandler.setActionHandler('copy', () => {
            this._copyElements();
        });

        // Paste
        this.keyboardHandler.setActionHandler('paste', () => {
            this._pasteElements();
        });

        // Select all
        this.keyboardHandler.setActionHandler('selectAll', () => {
            this._selectAllElements();
        });

        // Deselect
        this.keyboardHandler.setActionHandler('deselect', () => {
            this._deselectAll();
        });

        // Zoom
        this.keyboardHandler.setActionHandler('zoomIn', () => {
            this.canvasManager.zoomIn();
        });

        this.keyboardHandler.setActionHandler('zoomOut', () => {
            this.canvasManager.zoomOut();
        });

        this.keyboardHandler.setActionHandler('zoomReset', () => {
            this.canvasManager.zoomFit();
        });

        // Tools
        this.keyboardHandler.setActionHandler('selectTool', () => {
            this.toolManager.setTool('select');
        });

        this.keyboardHandler.setActionHandler('panTool', () => {
            this.toolManager.setTool('pan');
        });

        this.keyboardHandler.setActionHandler('rectangleTool', () => {
            this.toolManager.setTool('rectangle');
        });

        this.keyboardHandler.setActionHandler('circleTool', () => {
            this.toolManager.setTool('circle');
        });

        this.keyboardHandler.setActionHandler('diamondTool', () => {
            this.toolManager.setTool('diamond');
        });

        // Save
        this.keyboardHandler.setActionHandler('save', () => {
            this._saveDiagram();
        });

        // Export
        this.keyboardHandler.setActionHandler('export', () => {
            this.exportManager.showModal();
        });

        // Movement
        const moveAmount = 5;
        const moveLargeAmount = 20;

        this.keyboardHandler.setActionHandler('moveUp', () => {
            this._moveSelectedElements(0, -moveAmount);
        });

        this.keyboardHandler.setActionHandler('moveDown', () => {
            this._moveSelectedElements(0, moveAmount);
        });

        this.keyboardHandler.setActionHandler('moveLeft', () => {
            this._moveSelectedElements(-moveAmount, 0);
        });

        this.keyboardHandler.setActionHandler('moveRight', () => {
            this._moveSelectedElements(moveAmount, 0);
        });

        this.keyboardHandler.setActionHandler('moveUpLarge', () => {
            this._moveSelectedElements(0, -moveLargeAmount);
        });

        this.keyboardHandler.setActionHandler('moveDownLarge', () => {
            this._moveSelectedElements(0, moveLargeAmount);
        });

        this.keyboardHandler.setActionHandler('moveLeftLarge', () => {
            this._moveSelectedElements(-moveLargeAmount, 0);
        });

        this.keyboardHandler.setActionHandler('moveRightLarge', () => {
            this._moveSelectedElements(moveLargeAmount, 0);
        });
    }

    /**
     * Handle canvas click
     * @param {Object} position - Click position
     * @param {MouseEvent} event - Original event
     * @private
     */
    _handleCanvasClick(position, event) {
        const currentTool = this.toolManager.getCurrentTool();

        if (this.toolManager.isShapeTool()) {
            this.createNode(currentTool, position.x, position.y);
        } else if (this.toolManager.isConnectionTool()) {
            // Connection tool clicked on empty canvas - cancel any pending connection
            this._cancelPendingConnection();
        } else if (currentTool === 'select') {
            // Deselect if clicking on empty canvas
            this._deselectAll();
        }
    }

    /**
     * Handle node click for connection creation
     * @param {string} nodeId - The clicked node ID
     * @private
     */
    _handleNodeClickForConnection(nodeId) {
        const currentTool = this.toolManager.getCurrentTool();
        
        if (!this.toolManager.isConnectionTool()) {
            return false;
        }

        const node = this.elements.get(nodeId);
        if (!node) {
            return false;
        }

        // Calculate node center position
        const nodeCenterX = node.x + (node.width || 120) / 2;
        const nodeCenterY = node.y + (node.height || 60) / 2;

        if (!this.connectionStartNode) {
            // First click - start connection
            this.connectionStartNode = nodeId;
            this.pendingConnectionType = currentTool;
            
            // Start visual connection preview
            this.mouseHandler.startConnection(
                { id: nodeId, element: document.querySelector(`[data-id="${nodeId}"]`) },
                { x: nodeCenterX, y: nodeCenterY }
            );

            // Highlight the source node
            this.nodeRenderer.selectNode(nodeId);

            if (window.notificationManager) {
                window.notificationManager.info('Click another node to complete the connection');
            }
            return true;
        } else {
            // Second click - complete connection
            if (this.connectionStartNode !== nodeId) {
                this.addConnection(
                    this.connectionStartNode,
                    nodeId,
                    '',
                    this.pendingConnectionType
                );
            }
            this._cancelPendingConnection();
            return true;
        }
    }

    /**
     * Cancel pending connection creation
     * @private
     */
    _cancelPendingConnection() {
        this.connectionStartNode = null;
        this.pendingConnectionType = null;
        this.nodeRenderer.clearSelection();
    }

    /**
     * Handle connection created from mouse handler
     * @param {Object} source - Source element info
     * @param {Object} target - Target element info
     * @private
     */
    _handleConnectionCreated(source, target) {
        if (source && target && source.id && target.id && source.id !== target.id) {
            const connectionType = this.pendingConnectionType || this.toolManager.getCurrentTool();
            this.addConnection(source.id, target.id, '', connectionType);
        }
        this._cancelPendingConnection();
    }

    /**
     * Handle property change from properties panel
     * @param {string} elementId - Element ID
     * @param {string} property - Property name
     * @param {*} value - New value
     * @private
     */
    _handlePropertyChange(elementId, property, value) {
        if (property === '_delete') {
            this.removeElement(elementId);
            return;
        }

        if (property === '_duplicate') {
            this._duplicateElement(elementId);
            return;
        }

        this.updateElementProperty(elementId, property, value);
    }

    /**
     * Handle tab change
     * @param {string} newTab - New tab name
     * @private
     */
    _handleTabChange(newTab) {
        switch (newTab) {
            case 'preview':
                this._updatePreview();
                break;
            case 'validation':
                const code = document.getElementById('code-editor')?.value || '';
                this.codeValidator.validateAndDisplay(code);
                break;
        }
    }

    /**
     * Create a new node
     * @param {string} type - Node type
     * @param {number} x - X position
     * @param {number} y - Y position
     */
    createNode(type, x, y) {
        // Save state before creating node
        this._saveStateToHistory();

        const id = `node_${Date.now()}`;
        const node = {
            id,
            type,
            x: x - 60,
            y: y - 30,
            width: 120,
            height: 60,
            label: 'New Node'
        };

        this.elements.set(id, node);
        this.nodeRenderer.renderNode(node, (nodeId) => this.selectElement(nodeId));
        this.updateCode();
        this.selectElement(id);
    }

    /**
     * Select an element
     * @param {string} id - Element ID
     */
    selectElement(id) {
        // Check if we're in connection mode
        if (this.toolManager.isConnectionTool()) {
            if (this._handleNodeClickForConnection(id)) {
                return;
            }
        }

        this.selectedElements.clear();
        this.nodeRenderer.clearSelection();

        this.selectedElements.add(id);
        this.nodeRenderer.selectNode(id);

        this.propertiesPanel.update(this.selectedElements);
    }

    /**
     * Update element property
     * @param {string} elementId - Element ID
     * @param {string} property - Property name
     * @param {*} value - New value
     */
    updateElementProperty(elementId, property, value) {
        const element = this.elements.get(elementId);
        if (!element) return;

        if (property === 'label') {
            element.label = value;
        } else if (property === 'type') {
            element.type = value;
        } else {
            element[property] = parseFloat(value) || 0;
        }

        this.nodeRenderer.updateNode(elementId, element, (id) => this.selectElement(id));
        this.selectElement(elementId);
        this.updateCode();
    }

    /**
     * Remove an element
     * @param {string} elementId - Element ID
     */
    removeElement(elementId) {
        // Save state before removing element
        this._saveStateToHistory();

        this.nodeRenderer.removeNode(elementId);
        this.elements.delete(elementId);
        this.selectedElements.delete(elementId);

        // Remove associated connections
        const connectionsToRemove = [];
        this.connections.forEach((conn, connId) => {
            if (conn.source === elementId || conn.target === elementId) {
                connectionsToRemove.push(connId);
            }
        });
        connectionsToRemove.forEach(connId => {
            this.removeConnection(connId);
        });

        this.propertiesPanel.update(this.selectedElements);
        this.updateCode();
    }

    /**
     * Add a connection between two elements
     * @param {string} sourceId - Source element ID
     * @param {string} targetId - Target element ID
     * @param {string} [label=''] - Connection label
     * @param {string} [type='arrow'] - Connection type (arrow, line, dotted)
     * @returns {Object|null} The created connection or null if invalid
     */
    addConnection(sourceId, targetId, label = '', type = 'arrow') {
        // Save state before adding connection
        this._saveStateToHistory();

        // Validate that both elements exist
        if (!this.elements.has(sourceId) || !this.elements.has(targetId)) {
            console.warn('Cannot create connection: source or target element not found');
            return null;
        }

        // Prevent duplicate connections
        let isDuplicate = false;
        this.connections.forEach(conn => {
            if (conn.source === sourceId && conn.target === targetId) {
                isDuplicate = true;
            }
        });
        if (isDuplicate) {
            if (window.notificationManager) {
                window.notificationManager.warning('Connection already exists');
            }
            return null;
        }

        const id = `conn_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
        const connection = {
            id,
            source: sourceId,
            target: targetId,
            label: label,
            type: type
        };

        this.connections.set(id, connection);
        this._renderConnection(connection);
        this.updateCode();

        if (window.notificationManager) {
            window.notificationManager.success('Connection created');
        }

        return connection;
    }

    /**
     * Remove a connection
     * @param {string} connectionId - Connection ID
     * @returns {boolean} True if connection was removed
     */
    removeConnection(connectionId) {
        if (!this.connections.has(connectionId)) {
            return false;
        }

        // Save state before removing connection
        this._saveStateToHistory();

        this.nodeRenderer.removeConnection(connectionId);
        this.connections.delete(connectionId);
        this.updateCode();
        return true;
    }

    /**
     * Render a connection on the canvas
     * @param {Object} connection - Connection data
     * @private
     */
    _renderConnection(connection) {
        const sourceNode = this.elements.get(connection.source);
        const targetNode = this.elements.get(connection.target);

        if (!sourceNode || !targetNode) {
            return;
        }

        // Calculate center positions
        const sourceCenter = {
            x: sourceNode.x + (sourceNode.width || 120) / 2,
            y: sourceNode.y + (sourceNode.height || 60) / 2
        };
        const targetCenter = {
            x: targetNode.x + (targetNode.width || 120) / 2,
            y: targetNode.y + (targetNode.height || 60) / 2
        };

        // Calculate edge intersection points for cleaner connections
        const sourceEdge = this._getEdgePoint(sourceNode, sourceCenter, targetCenter);
        const targetEdge = this._getEdgePoint(targetNode, targetCenter, sourceCenter);

        this.nodeRenderer.renderConnection({
            id: connection.id,
            source: sourceEdge,
            target: targetEdge,
            type: connection.type || 'arrow',
            label: connection.label
        });
    }

    /**
     * Calculate the edge point where a connection should attach to a node
     * @param {Object} node - Node data
     * @param {Object} nodeCenter - Node center position
     * @param {Object} otherCenter - Other node center position
     * @returns {Object} Edge point {x, y}
     * @private
     */
    _getEdgePoint(node, nodeCenter, otherCenter) {
        const width = node.width || 120;
        const height = node.height || 60;
        const halfWidth = width / 2;
        const halfHeight = height / 2;

        // Calculate direction vector
        const dx = otherCenter.x - nodeCenter.x;
        const dy = otherCenter.y - nodeCenter.y;

        if (dx === 0 && dy === 0) {
            return nodeCenter;
        }

        // Calculate intersection with rectangle edges
        const absDx = Math.abs(dx);
        const absDy = Math.abs(dy);

        let scale;
        if (absDx * halfHeight > absDy * halfWidth) {
            // Intersects left or right edge
            scale = halfWidth / absDx;
        } else {
            // Intersects top or bottom edge
            scale = halfHeight / absDy;
        }

        return {
            x: nodeCenter.x + dx * scale,
            y: nodeCenter.y + dy * scale
        };
    }

    /**
     * Update all connections for a specific element (after it moves)
     * @param {string} elementId - Element ID
     * @private
     */
    _updateConnectionsForElement(elementId) {
        this.connections.forEach((conn, connId) => {
            if (conn.source === elementId || conn.target === elementId) {
                // Remove old rendering and re-render
                this.nodeRenderer.removeConnection(connId);
                this._renderConnection(conn);
            }
        });
    }

    /**
     * Render all connections (used after loading)
     * @private
     */
    _renderAllConnections() {
        this.connections.forEach(conn => {
            this._renderConnection(conn);
        });
    }

    /**
     * Update generated code
     */
    updateCode() {
        const code = this.codeGenerator.updateCodeEditor(this.elements, this.connections);
        this.codeValidator.validateAndDisplay(code);
    }

    /**
     * Update preview
     * @private
     */
    _updatePreview() {
        const code = document.getElementById('code-editor')?.value || '';
        this.previewManager.update(code);
    }

    /**
     * Load template
     * @param {Object} template - Template data
     * @private
     */
    _loadTemplate(template) {
        // Clear existing elements
        this.elements.clear();
        this.connections.clear();
        this.nodeRenderer.clearCanvas();

        // Load elements
        if (template.elements) {
            template.elements.forEach(el => {
                this.elements.set(el.id, el);
                this.nodeRenderer.renderNode(el, (id) => this.selectElement(id));
            });
        }

        // Load connections
        if (template.connections) {
            template.connections.forEach(conn => {
                this.connections.set(conn.id, conn);
            });
            // Render all connections after elements are loaded
            this._renderAllConnections();
        }

        // Update code
        if (template.code) {
            const codeEditor = document.getElementById('code-editor');
            if (codeEditor) {
                codeEditor.value = template.code;
            }
        } else {
            this.updateCode();
        }

        // Show notification
        if (window.notificationManager) {
            window.notificationManager.success(`Template "${template.name}" loaded`);
        }
    }

    /**
     * Delete selected elements
     * @private
     */
    _deleteSelectedElements() {
        this.selectedElements.forEach(id => {
            this.removeElement(id);
        });
        this.selectedElements.clear();
        this.propertiesPanel.update(this.selectedElements);
    }

    /**
     * Deselect all elements
     * @private
     */
    _deselectAll() {
        this.selectedElements.clear();
        this.nodeRenderer.clearSelection();
        this.propertiesPanel.update(this.selectedElements);
    }

    /**
     * Select all elements
     * @private
     */
    _selectAllElements() {
        this.elements.forEach((el, id) => {
            this.selectedElements.add(id);
            this.nodeRenderer.selectNode(id);
        });
        this.propertiesPanel.update(this.selectedElements);
    }

    /**
     * Move selected elements
     * @param {number} dx - Delta X
     * @param {number} dy - Delta Y
     * @private
     */
    _moveSelectedElements(dx, dy) {
        if (this.selectedElements.size === 0) return;

        // Save state before moving elements
        this._saveStateToHistory();

        this.selectedElements.forEach(id => {
            const element = this.elements.get(id);
            if (element) {
                element.x += dx;
                element.y += dy;
                this.nodeRenderer.updateNode(id, element, (nodeId) => this.selectElement(nodeId));
            }
        });
        this.updateCode();
    }

    /**
     * Duplicate element
     * @param {string} elementId - Element ID to duplicate
     * @private
     */
    _duplicateElement(elementId) {
        const original = this.elements.get(elementId);
        if (!original) return;

        // Save state before duplicating
        this._saveStateToHistory();

        const newId = `node_${Date.now()}`;
        const duplicate = {
            ...original,
            id: newId,
            x: original.x + 20,
            y: original.y + 20
        };

        this.elements.set(newId, duplicate);
        this.nodeRenderer.renderNode(duplicate, (id) => this.selectElement(id));
        this.selectElement(newId);
        this.updateCode();
    }

    /**
     * Copy elements to clipboard
     * @private
     */
    _copyElements() {
        const elementsToCopy = [];
        this.selectedElements.forEach(id => {
            const element = this.elements.get(id);
            if (element) {
                elementsToCopy.push({ ...element });
            }
        });
        this.clipboard = elementsToCopy;

        if (window.notificationManager) {
            window.notificationManager.info(`Copied ${elementsToCopy.length} element(s)`);
        }
    }

    /**
     * Paste elements from clipboard
     * @private
     */
    _pasteElements() {
        if (!this.clipboard || this.clipboard.length === 0) return;

        // Save state before pasting
        this._saveStateToHistory();

        this._deselectAll();

        this.clipboard.forEach(el => {
            const newId = `node_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
            const newElement = {
                ...el,
                id: newId,
                x: el.x + 30,
                y: el.y + 30
            };

            this.elements.set(newId, newElement);
            this.nodeRenderer.renderNode(newElement, (id) => this.selectElement(id));
            this.selectedElements.add(newId);
        });

        this.propertiesPanel.update(this.selectedElements);
        this.updateCode();

        if (window.notificationManager) {
            window.notificationManager.info(`Pasted ${this.clipboard.length} element(s)`);
        }
    }

    /**
     * Copy code to clipboard
     * @private
     */
    _copyCode() {
        const codeEditor = document.getElementById('code-editor');
        if (codeEditor) {
            navigator.clipboard.writeText(codeEditor.value).then(() => {
                if (window.notificationManager) {
                    window.notificationManager.success('Code copied to clipboard');
                }
            });
        }
    }

    /**
     * Apply code changes
     * @private
     */
    _applyCode() {
        // This would parse the code and update the visual elements
        // For now, just update the preview
        this._updatePreview();

        if (window.notificationManager) {
            window.notificationManager.info('Code applied');
        }
    }

    /**
     * Save diagram
     * @private
     */
    _saveDiagram() {
        const data = {
            diagramType: window.DIAGRAM_TYPE || 'flowchart',
            elements: Array.from(this.elements.values()),
            connections: Array.from(this.connections.values()),
            code: document.getElementById('code-editor')?.value || ''
        };

        // Save to localStorage for now
        localStorage.setItem('mermaid_diagram', JSON.stringify(data));

        if (window.notificationManager) {
            window.notificationManager.success('Diagram saved');
        }
    }

    /**
     * Save current state to history for undo functionality
     * @private
     */
    _saveStateToHistory() {
        if (this._isUndoRedoAction) {
            return; // Don't record state changes during undo/redo
        }

        const state = this._captureState();
        this._historyStack.push(state);

        // Limit history size
        if (this._historyStack.length > this._maxHistorySize) {
            this._historyStack.shift();
        }

        // Clear redo stack when new action is performed
        this._redoStack = [];

        // Update button states
        this._updateUndoRedoButtons();
    }

    /**
     * Capture current diagram state
     * @returns {Object} State snapshot
     * @private
     */
    _captureState() {
        return {
            elements: new Map(Array.from(this.elements.entries()).map(
                ([id, el]) => [id, { ...el }]
            )),
            connections: new Map(Array.from(this.connections.entries()).map(
                ([id, conn]) => [id, { ...conn }]
            )),
            timestamp: Date.now()
        };
    }

    /**
     * Restore diagram state from snapshot
     * @param {Object} state - State snapshot to restore
     * @private
     */
    _restoreState(state) {
        this._isUndoRedoAction = true;

        try {
            // Clear current state
            this.elements.clear();
            this.connections.clear();
            this.nodeRenderer.clearCanvas();
            this.selectedElements.clear();

            // Restore elements
            state.elements.forEach((el, id) => {
                this.elements.set(id, { ...el });
                this.nodeRenderer.renderNode({ ...el }, (nodeId) => this.selectElement(nodeId));
            });

            // Restore connections
            state.connections.forEach((conn, id) => {
                this.connections.set(id, { ...conn });
            });

            // Render all connections
            this._renderAllConnections();

            // Update code editor
            this.updateCode();

            // Update properties panel
            this.propertiesPanel.update(this.selectedElements);
        } finally {
            this._isUndoRedoAction = false;
        }
    }

    /**
     * Update undo/redo button states
     * @private
     */
    _updateUndoRedoButtons() {
        const undoBtn = document.getElementById('undo');
        const redoBtn = document.getElementById('redo');

        if (undoBtn) {
            undoBtn.disabled = this._historyStack.length === 0;
            undoBtn.classList.toggle('disabled', this._historyStack.length === 0);
        }
        if (redoBtn) {
            redoBtn.disabled = this._redoStack.length === 0;
            redoBtn.classList.toggle('disabled', this._redoStack.length === 0);
        }
    }

    /**
     * Undo last action
     * @private
     */
    _undo() {
        if (this._historyStack.length === 0) {
            if (window.notificationManager) {
                window.notificationManager.info('Nothing to undo');
            }
            return;
        }

        // Save current state to redo stack before undoing
        const currentState = this._captureState();
        this._redoStack.push(currentState);

        // Pop and restore previous state
        const previousState = this._historyStack.pop();
        this._restoreState(previousState);

        // Update button states
        this._updateUndoRedoButtons();

        if (window.notificationManager) {
            window.notificationManager.info('Undo successful');
        }
    }

    /**
     * Redo last undone action
     * @private
     */
    _redo() {
        if (this._redoStack.length === 0) {
            if (window.notificationManager) {
                window.notificationManager.info('Nothing to redo');
            }
            return;
        }

        // Save current state to history stack before redoing
        const currentState = this._captureState();
        this._historyStack.push(currentState);

        // Pop and restore redo state
        const redoState = this._redoStack.pop();
        this._restoreState(redoState);

        // Update button states
        this._updateUndoRedoButtons();

        if (window.notificationManager) {
            window.notificationManager.info('Redo successful');
        }
    }

    /**
     * Load from state (for WebSocket sync)
     * @param {Object} state - State object
     */
    loadFromState(state) {
        this.elements.clear();
        this.connections.clear();
        this.nodeRenderer.clearCanvas();

        if (state.elements) {
            Object.entries(state.elements).forEach(([id, el]) => {
                this.elements.set(id, el);
                this.nodeRenderer.renderNode(el, (nodeId) => this.selectElement(nodeId));
            });
        }

        if (state.connections) {
            Object.entries(state.connections).forEach(([id, conn]) => {
                this.connections.set(id, conn);
            });
            // Render all connections after elements are loaded
            this._renderAllConnections();
        }

        this.updateCode();
    }

    /**
     * Update element from remote
     * @param {string} elementId - Element ID
     * @param {Object} updates - Updates to apply
     */
    updateElementFromRemote(elementId, updates) {
        const element = this.elements.get(elementId);
        if (element) {
            Object.assign(element, updates);
            this.nodeRenderer.updateNode(elementId, element, (id) => this.selectElement(id));
            this.updateCode();
        }
    }

    /**
     * Update connection from remote
     * @param {string} connectionId - Connection ID
     * @param {Object} updates - Updates to apply
     */
    updateConnectionFromRemote(connectionId, updates) {
        const connection = this.connections.get(connectionId);
        if (connection) {
            Object.assign(connection, updates);
            // Re-render the connection
            this.nodeRenderer.removeConnection(connectionId);
            this._renderConnection(connection);
            this.updateCode();
        }
    }

    /**
     * Add connection from remote
     * @param {Object} connectionData - Connection data
     */
    addConnectionFromRemote(connectionData) {
        if (!this.connections.has(connectionData.id)) {
            this.connections.set(connectionData.id, connectionData);
            this._renderConnection(connectionData);
            this.updateCode();
        }
    }

    /**
     * Remove connection from remote
     * @param {string} connectionId - Connection ID
     */
    removeConnectionFromRemote(connectionId) {
        if (this.connections.has(connectionId)) {
            this.nodeRenderer.removeConnection(connectionId);
            this.connections.delete(connectionId);
            this.updateCode();
        }
    }

    /**
     * Sync with remote state
     * @param {Object} state - Remote state
     */
    syncWithRemoteState(state) {
        this.loadFromState(state);
    }

    /**
     * Get current state
     * @returns {Object} Current state
     */
    getState() {
        return {
            elements: Object.fromEntries(this.elements),
            connections: Object.fromEntries(this.connections)
        };
    }
}

// Initialize the builder when the page loads
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('diagram-canvas')) {
        window.diagramBuilder = new DiagramBuilder();
    }
});

// Export for use in other modules
window.DiagramBuilder = DiagramBuilder;
