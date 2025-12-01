/**
 * Mouse Handler - Handles mouse events for canvas interaction
 * @module input/MouseHandler
 */

class MouseHandler {
    /**
     * Create a MouseHandler instance
     * @param {SVGElement} canvas - The SVG canvas element
     * @param {CanvasManager} canvasManager - Canvas manager for coordinate conversion
     */
    constructor(canvas, canvasManager) {
        this.canvas = canvas;
        this.canvasManager = canvasManager;

        this.isDragging = false;
        this.isPanning = false;
        this.isSelecting = false;
        this.isConnecting = false;

        this.dragStart = { x: 0, y: 0 };
        this.dragCurrent = { x: 0, y: 0 };
        this.draggedElement = null;
        this.connectionStart = null;

        this.onClickCallbacks = [];
        this.onDragStartCallbacks = [];
        this.onDragMoveCallbacks = [];
        this.onDragEndCallbacks = [];
        this.onPanCallbacks = [];
        this.onSelectAreaCallbacks = [];
        this.onConnectionCallbacks = [];
        this.onContextMenuCallbacks = [];

        this._initializeEventListeners();
    }

    /**
     * Initialize event listeners
     * @private
     */
    _initializeEventListeners() {
        this.canvas.addEventListener('mousedown', this._onMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this._onMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this._onMouseUp.bind(this));
        this.canvas.addEventListener('mouseleave', this._onMouseLeave.bind(this));
        this.canvas.addEventListener('dblclick', this._onDoubleClick.bind(this));
        this.canvas.addEventListener('contextmenu', this._onContextMenu.bind(this));

        // Touch events for mobile support
        this.canvas.addEventListener('touchstart', this._onTouchStart.bind(this), { passive: false });
        this.canvas.addEventListener('touchmove', this._onTouchMove.bind(this), { passive: false });
        this.canvas.addEventListener('touchend', this._onTouchEnd.bind(this));
    }

    /**
     * Handle mouse down event
     * @param {MouseEvent} e - Mouse event
     * @private
     */
    _onMouseDown(e) {
        const canvasCoords = this.canvasManager.screenToCanvas(e.clientX, e.clientY);
        this.dragStart = { ...canvasCoords };
        this.dragCurrent = { ...canvasCoords };

        // Check if clicking on an element
        const element = this._getElementAtPoint(e.clientX, e.clientY);

        if (e.button === 1 || (e.button === 0 && e.altKey)) {
            // Middle mouse button or Alt+Left click - start panning
            this.isPanning = true;
            this.canvasManager.setGrabbingCursor(true);
        } else if (element) {
            // Clicking on an element - start dragging
            this.isDragging = true;
            this.draggedElement = element;
            this._notifyDragStart(element, canvasCoords);
        } else {
            // Clicking on empty canvas
            this._notifyClick(canvasCoords, e);

            // Start selection rectangle if shift is held
            if (e.shiftKey) {
                this.isSelecting = true;
            }
        }
    }

    /**
     * Handle mouse move event
     * @param {MouseEvent} e - Mouse event
     * @private
     */
    _onMouseMove(e) {
        const canvasCoords = this.canvasManager.screenToCanvas(e.clientX, e.clientY);
        const dx = canvasCoords.x - this.dragCurrent.x;
        const dy = canvasCoords.y - this.dragCurrent.y;

        this.dragCurrent = { ...canvasCoords };

        if (this.isPanning) {
            this.canvasManager.panBy(dx, dy);
            this._notifyPan(dx, dy);
        } else if (this.isDragging && this.draggedElement) {
            this._notifyDragMove(this.draggedElement, canvasCoords, dx, dy);
        } else if (this.isSelecting) {
            this._updateSelectionRect();
        } else if (this.isConnecting) {
            this._updateConnectionLine(canvasCoords);
        }
    }

    /**
     * Handle mouse up event
     * @param {MouseEvent} e - Mouse event
     * @private
     */
    _onMouseUp(e) {
        const canvasCoords = this.canvasManager.screenToCanvas(e.clientX, e.clientY);

        if (this.isPanning) {
            this.isPanning = false;
            this.canvasManager.setGrabbingCursor(false);
        } else if (this.isDragging && this.draggedElement) {
            this._notifyDragEnd(this.draggedElement, canvasCoords);
            this.isDragging = false;
            this.draggedElement = null;
        } else if (this.isSelecting) {
            this._finalizeSelection();
            this.isSelecting = false;
        } else if (this.isConnecting) {
            const targetElement = this._getElementAtPoint(e.clientX, e.clientY);
            if (targetElement && this.connectionStart) {
                this._notifyConnection(this.connectionStart, targetElement);
            }
            this.isConnecting = false;
            this.connectionStart = null;
            this._removeConnectionLine();
        }
    }

    /**
     * Handle mouse leave event
     * @param {MouseEvent} e - Mouse event
     * @private
     */
    _onMouseLeave(e) {
        // Cancel any ongoing operations
        if (this.isPanning) {
            this.isPanning = false;
            this.canvasManager.setGrabbingCursor(false);
        }
        if (this.isDragging) {
            this.isDragging = false;
            this.draggedElement = null;
        }
        if (this.isSelecting) {
            this.isSelecting = false;
            this._removeSelectionRect();
        }
    }

    /**
     * Handle double click event
     * @param {MouseEvent} e - Mouse event
     * @private
     */
    _onDoubleClick(e) {
        const canvasCoords = this.canvasManager.screenToCanvas(e.clientX, e.clientY);
        const element = this._getElementAtPoint(e.clientX, e.clientY);

        const event = new CustomEvent('canvasDoubleClick', {
            detail: {
                position: canvasCoords,
                element: element,
                originalEvent: e
            }
        });
        document.dispatchEvent(event);
    }

    /**
     * Handle context menu event
     * @param {MouseEvent} e - Mouse event
     * @private
     */
    _onContextMenu(e) {
        e.preventDefault();

        const canvasCoords = this.canvasManager.screenToCanvas(e.clientX, e.clientY);
        const element = this._getElementAtPoint(e.clientX, e.clientY);

        this.onContextMenuCallbacks.forEach(callback => {
            callback({
                position: canvasCoords,
                screenPosition: { x: e.clientX, y: e.clientY },
                element: element
            });
        });
    }

    /**
     * Handle touch start event
     * @param {TouchEvent} e - Touch event
     * @private
     */
    _onTouchStart(e) {
        if (e.touches.length === 1) {
            e.preventDefault();
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousedown', {
                clientX: touch.clientX,
                clientY: touch.clientY,
                button: 0
            });
            this._onMouseDown(mouseEvent);
        } else if (e.touches.length === 2) {
            // Two finger touch - start pinch zoom
            this._startPinchZoom(e);
        }
    }

    /**
     * Handle touch move event
     * @param {TouchEvent} e - Touch event
     * @private
     */
    _onTouchMove(e) {
        if (e.touches.length === 1) {
            e.preventDefault();
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousemove', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            this._onMouseMove(mouseEvent);
        } else if (e.touches.length === 2) {
            this._handlePinchZoom(e);
        }
    }

    /**
     * Handle touch end event
     * @param {TouchEvent} e - Touch event
     * @private
     */
    _onTouchEnd(e) {
        if (e.touches.length === 0) {
            const mouseEvent = new MouseEvent('mouseup', {
                clientX: this.dragCurrent.x,
                clientY: this.dragCurrent.y,
                button: 0
            });
            this._onMouseUp(mouseEvent);
        }
    }

    /**
     * Start pinch zoom
     * @param {TouchEvent} e - Touch event
     * @private
     */
    _startPinchZoom(e) {
        this.pinchStartDistance = this._getTouchDistance(e.touches[0], e.touches[1]);
        this.pinchStartZoom = this.canvasManager.getZoom();
    }

    /**
     * Handle pinch zoom
     * @param {TouchEvent} e - Touch event
     * @private
     */
    _handlePinchZoom(e) {
        if (!this.pinchStartDistance) return;

        const currentDistance = this._getTouchDistance(e.touches[0], e.touches[1]);
        const scale = currentDistance / this.pinchStartDistance;
        const newZoom = this.pinchStartZoom * scale;

        this.canvasManager.setZoom(newZoom);
    }

    /**
     * Get distance between two touch points
     * @param {Touch} touch1 - First touch
     * @param {Touch} touch2 - Second touch
     * @returns {number} Distance
     * @private
     */
    _getTouchDistance(touch1, touch2) {
        const dx = touch1.clientX - touch2.clientX;
        const dy = touch1.clientY - touch2.clientY;
        return Math.sqrt(dx * dx + dy * dy);
    }

    /**
     * Get element at screen point
     * @param {number} x - Screen X
     * @param {number} y - Screen Y
     * @returns {Object|null} Element data or null
     * @private
     */
    _getElementAtPoint(x, y) {
        const elements = document.elementsFromPoint(x, y);
        for (const el of elements) {
            const diagramElement = el.closest('.diagram-element');
            if (diagramElement) {
                return {
                    element: diagramElement,
                    id: diagramElement.dataset.id
                };
            }
        }
        return null;
    }

    /**
     * Update selection rectangle
     * @private
     */
    _updateSelectionRect() {
        let rect = document.getElementById('selection-rect');
        if (!rect) {
            rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.id = 'selection-rect';
            rect.setAttribute('class', 'selection-rectangle');
            this.canvas.appendChild(rect);
        }

        const x = Math.min(this.dragStart.x, this.dragCurrent.x);
        const y = Math.min(this.dragStart.y, this.dragCurrent.y);
        const width = Math.abs(this.dragCurrent.x - this.dragStart.x);
        const height = Math.abs(this.dragCurrent.y - this.dragStart.y);

        rect.setAttribute('x', x);
        rect.setAttribute('y', y);
        rect.setAttribute('width', width);
        rect.setAttribute('height', height);
    }

    /**
     * Remove selection rectangle
     * @private
     */
    _removeSelectionRect() {
        const rect = document.getElementById('selection-rect');
        if (rect) {
            rect.remove();
        }
    }

    /**
     * Finalize selection
     * @private
     */
    _finalizeSelection() {
        const bounds = {
            x: Math.min(this.dragStart.x, this.dragCurrent.x),
            y: Math.min(this.dragStart.y, this.dragCurrent.y),
            width: Math.abs(this.dragCurrent.x - this.dragStart.x),
            height: Math.abs(this.dragCurrent.y - this.dragStart.y)
        };

        this._removeSelectionRect();

        this.onSelectAreaCallbacks.forEach(callback => {
            callback(bounds);
        });
    }

    /**
     * Update connection line during connection creation
     * @param {Object} currentPos - Current position
     * @private
     */
    _updateConnectionLine(currentPos) {
        let line = document.getElementById('connection-preview');
        if (!line) {
            line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.id = 'connection-preview';
            line.setAttribute('class', 'connection-preview-line');
            this.canvas.appendChild(line);
        }

        if (this.connectionStart) {
            line.setAttribute('x1', this.connectionStart.x);
            line.setAttribute('y1', this.connectionStart.y);
            line.setAttribute('x2', currentPos.x);
            line.setAttribute('y2', currentPos.y);
        }
    }

    /**
     * Remove connection preview line
     * @private
     */
    _removeConnectionLine() {
        const line = document.getElementById('connection-preview');
        if (line) {
            line.remove();
        }
    }

    /**
     * Start connection creation
     * @param {Object} startElement - Starting element
     * @param {Object} position - Start position
     */
    startConnection(startElement, position) {
        this.isConnecting = true;
        this.connectionStart = position;
        this.connectionStartElement = startElement;
    }

    /**
     * Notify click callbacks
     * @param {Object} position - Click position
     * @param {MouseEvent} event - Original event
     * @private
     */
    _notifyClick(position, event) {
        this.onClickCallbacks.forEach(callback => {
            callback(position, event);
        });
    }

    /**
     * Notify drag start callbacks
     * @param {Object} element - Dragged element
     * @param {Object} position - Start position
     * @private
     */
    _notifyDragStart(element, position) {
        this.onDragStartCallbacks.forEach(callback => {
            callback(element, position);
        });
    }

    /**
     * Notify drag move callbacks
     * @param {Object} element - Dragged element
     * @param {Object} position - Current position
     * @param {number} dx - Delta X
     * @param {number} dy - Delta Y
     * @private
     */
    _notifyDragMove(element, position, dx, dy) {
        this.onDragMoveCallbacks.forEach(callback => {
            callback(element, position, dx, dy);
        });
    }

    /**
     * Notify drag end callbacks
     * @param {Object} element - Dragged element
     * @param {Object} position - End position
     * @private
     */
    _notifyDragEnd(element, position) {
        this.onDragEndCallbacks.forEach(callback => {
            callback(element, position);
        });
    }

    /**
     * Notify pan callbacks
     * @param {number} dx - Delta X
     * @param {number} dy - Delta Y
     * @private
     */
    _notifyPan(dx, dy) {
        this.onPanCallbacks.forEach(callback => {
            callback(dx, dy);
        });
    }

    /**
     * Notify connection callbacks
     * @param {Object} source - Source element
     * @param {Object} target - Target element
     * @private
     */
    _notifyConnection(source, target) {
        this.onConnectionCallbacks.forEach(callback => {
            callback(source, target);
        });
    }

    // Callback registration methods
    onClick(callback) { this.onClickCallbacks.push(callback); }
    onDragStart(callback) { this.onDragStartCallbacks.push(callback); }
    onDragMove(callback) { this.onDragMoveCallbacks.push(callback); }
    onDragEnd(callback) { this.onDragEndCallbacks.push(callback); }
    onPan(callback) { this.onPanCallbacks.push(callback); }
    onSelectArea(callback) { this.onSelectAreaCallbacks.push(callback); }
    onConnection(callback) { this.onConnectionCallbacks.push(callback); }
    onContextMenu(callback) { this.onContextMenuCallbacks.push(callback); }

    /**
     * Get current drag state
     * @returns {Object} Drag state
     */
    getDragState() {
        return {
            isDragging: this.isDragging,
            isPanning: this.isPanning,
            isSelecting: this.isSelecting,
            isConnecting: this.isConnecting,
            dragStart: { ...this.dragStart },
            dragCurrent: { ...this.dragCurrent }
        };
    }
}

// Export for use in other modules
window.MouseHandler = MouseHandler;
