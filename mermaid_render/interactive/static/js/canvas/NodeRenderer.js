/**
 * Node Renderer - Handles SVG node rendering for diagram elements
 * @module canvas/NodeRenderer
 */

class NodeRenderer {
    /**
     * Create a NodeRenderer instance
     * @param {SVGGElement} canvasGroup - The canvas group to render nodes into
     */
    constructor(canvasGroup) {
        this.canvasGroup = canvasGroup;
        this.svgNS = 'http://www.w3.org/2000/svg';
    }

    /**
     * Render a node element on the canvas
     * @param {Object} node - The node data
     * @param {string} node.id - Node ID
     * @param {string} node.type - Node type (rectangle, circle, diamond, hexagon)
     * @param {number} node.x - X position
     * @param {number} node.y - Y position
     * @param {number} node.width - Node width
     * @param {number} node.height - Node height
     * @param {string} node.label - Node label text
     * @param {Function} [onSelect] - Callback when node is selected
     * @returns {SVGGElement} The created SVG group element
     */
    renderNode(node, onSelect) {
        const group = document.createElementNS(this.svgNS, 'g');
        group.setAttribute('class', 'diagram-element');
        group.setAttribute('data-id', node.id);
        group.setAttribute('transform', `translate(${node.x}, ${node.y})`);

        // Create shape based on type
        const shape = this._createShape(node);
        if (shape) {
            group.appendChild(shape);
        }

        // Create text label
        const text = this._createTextLabel(node);
        group.appendChild(text);

        // Add to canvas
        this.canvasGroup.appendChild(group);

        // Add click handler for selection
        if (onSelect) {
            group.addEventListener('click', (e) => {
                e.stopPropagation();
                onSelect(node.id);
            });
        }

        return group;
    }

    /**
     * Create SVG shape based on node type
     * @param {Object} node - The node data
     * @returns {SVGElement|null} The created shape element
     * @private
     */
    _createShape(node) {
        let shape;

        switch (node.type) {
            case 'rectangle':
                shape = this._createRectangle(node);
                break;
            case 'circle':
                shape = this._createEllipse(node);
                break;
            case 'diamond':
                shape = this._createDiamond(node);
                break;
            case 'hexagon':
                shape = this._createHexagon(node);
                break;
            default:
                shape = this._createRectangle(node);
                break;
        }

        return shape;
    }

    /**
     * Create rectangle shape
     * @param {Object} node - The node data
     * @returns {SVGRectElement} Rectangle element
     * @private
     */
    _createRectangle(node) {
        const rect = document.createElementNS(this.svgNS, 'rect');
        rect.setAttribute('class', 'node-rectangle');
        rect.setAttribute('width', node.width);
        rect.setAttribute('height', node.height);
        rect.setAttribute('rx', '4');
        rect.setAttribute('ry', '4');
        return rect;
    }

    /**
     * Create ellipse/circle shape
     * @param {Object} node - The node data
     * @returns {SVGEllipseElement} Ellipse element
     * @private
     */
    _createEllipse(node) {
        const ellipse = document.createElementNS(this.svgNS, 'ellipse');
        ellipse.setAttribute('class', 'node-circle');
        ellipse.setAttribute('cx', node.width / 2);
        ellipse.setAttribute('cy', node.height / 2);
        ellipse.setAttribute('rx', node.width / 2);
        ellipse.setAttribute('ry', node.height / 2);
        return ellipse;
    }

    /**
     * Create diamond shape
     * @param {Object} node - The node data
     * @returns {SVGPolygonElement} Polygon element
     * @private
     */
    _createDiamond(node) {
        const polygon = document.createElementNS(this.svgNS, 'polygon');
        polygon.setAttribute('class', 'node-diamond');
        const points = `${node.width / 2},0 ${node.width},${node.height / 2} ${node.width / 2},${node.height} 0,${node.height / 2}`;
        polygon.setAttribute('points', points);
        return polygon;
    }

    /**
     * Create hexagon shape
     * @param {Object} node - The node data
     * @returns {SVGPolygonElement} Polygon element
     * @private
     */
    _createHexagon(node) {
        const polygon = document.createElementNS(this.svgNS, 'polygon');
        polygon.setAttribute('class', 'node-hexagon');
        const w = node.width;
        const h = node.height;
        const inset = w * 0.2;
        const points = `${inset},0 ${w - inset},0 ${w},${h / 2} ${w - inset},${h} ${inset},${h} 0,${h / 2}`;
        polygon.setAttribute('points', points);
        return polygon;
    }

    /**
     * Create text label for node
     * @param {Object} node - The node data
     * @returns {SVGTextElement} Text element
     * @private
     */
    _createTextLabel(node) {
        const text = document.createElementNS(this.svgNS, 'text');
        text.setAttribute('class', 'node-text');
        text.setAttribute('x', node.width / 2);
        text.setAttribute('y', node.height / 2);
        text.textContent = node.label;
        return text;
    }

    /**
     * Update an existing node on the canvas
     * @param {string} nodeId - The node ID to update
     * @param {Object} node - The updated node data
     * @param {Function} [onSelect] - Callback when node is selected
     */
    updateNode(nodeId, node, onSelect) {
        const existingElement = document.querySelector(`[data-id="${nodeId}"]`);
        if (existingElement) {
            existingElement.remove();
        }
        this.renderNode(node, onSelect);
    }

    /**
     * Remove a node from the canvas
     * @param {string} nodeId - The node ID to remove
     * @returns {boolean} True if node was removed
     */
    removeNode(nodeId) {
        const element = document.querySelector(`[data-id="${nodeId}"]`);
        if (element) {
            element.remove();
            return true;
        }
        return false;
    }

    /**
     * Select a node visually
     * @param {string} nodeId - The node ID to select
     */
    selectNode(nodeId) {
        // Clear previous selections
        document.querySelectorAll('.diagram-element.selected').forEach(el => {
            el.classList.remove('selected');
        });

        // Select new element
        const element = document.querySelector(`[data-id="${nodeId}"]`);
        if (element) {
            element.classList.add('selected');
        }
    }

    /**
     * Clear all selections
     */
    clearSelection() {
        document.querySelectorAll('.diagram-element.selected').forEach(el => {
            el.classList.remove('selected');
        });
    }

    /**
     * Render a connection line between two nodes
     * @param {Object} connection - The connection data
     * @param {string} connection.id - Connection ID
     * @param {Object} connection.source - Source node position
     * @param {Object} connection.target - Target node position
     * @param {string} [connection.type='arrow'] - Connection type
     * @param {string} [connection.label] - Connection label
     * @returns {SVGGElement} The created connection group
     */
    renderConnection(connection) {
        const group = document.createElementNS(this.svgNS, 'g');
        group.setAttribute('class', 'connection-group');
        group.setAttribute('data-connection-id', connection.id);

        // Create line
        const line = document.createElementNS(this.svgNS, 'line');
        line.setAttribute('class', 'connection-line');
        line.setAttribute('x1', connection.source.x);
        line.setAttribute('y1', connection.source.y);
        line.setAttribute('x2', connection.target.x);
        line.setAttribute('y2', connection.target.y);

        // Add arrow marker if needed (not for plain line type)
        if (connection.type === 'arrow' || connection.type === 'default') {
            line.setAttribute('marker-end', 'url(#arrowhead)');
        }

        // Set line style based on type
        if (connection.type === 'dotted') {
            line.setAttribute('stroke-dasharray', '5,5');
            line.setAttribute('marker-end', 'url(#arrowhead)');
        } else if (connection.type === 'line') {
            // Plain line without arrow - no marker needed
            line.removeAttribute('marker-end');
        }

        group.appendChild(line);

        // Add label if present
        if (connection.label) {
            const midX = (connection.source.x + connection.target.x) / 2;
            const midY = (connection.source.y + connection.target.y) / 2;

            const text = document.createElementNS(this.svgNS, 'text');
            text.setAttribute('class', 'connection-label');
            text.setAttribute('x', midX);
            text.setAttribute('y', midY - 5);
            text.textContent = connection.label;
            group.appendChild(text);
        }

        this.canvasGroup.appendChild(group);
        return group;
    }

    /**
     * Remove a connection from the canvas
     * @param {string} connectionId - The connection ID to remove
     * @returns {boolean} True if connection was removed
     */
    removeConnection(connectionId) {
        const element = document.querySelector(`[data-connection-id="${connectionId}"]`);
        if (element) {
            element.remove();
            return true;
        }
        return false;
    }

    /**
     * Clear all elements from the canvas
     */
    clearCanvas() {
        while (this.canvasGroup.firstChild) {
            this.canvasGroup.removeChild(this.canvasGroup.firstChild);
        }
    }
}

// Export for use in other modules
window.NodeRenderer = NodeRenderer;
