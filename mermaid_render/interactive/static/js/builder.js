// Builder JavaScript for Mermaid Interactive Builder

class DiagramBuilder {
    constructor() {
        this.canvas = document.getElementById('diagram-canvas');
        this.canvasGroup = document.getElementById('canvas-group');
        this.currentTool = 'select';
        this.elements = new Map();
        this.connections = new Map();
        this.selectedElements = new Set();
        this.isDragging = false;
        this.dragStart = { x: 0, y: 0 };
        this.zoom = 1;
        this.pan = { x: 0, y: 0 };
        
        this.initializeEventListeners();
        this.initializeTools();
        this.loadTemplates();
        this.updateCode();
    }

    initializeEventListeners() {
        // Canvas events
        this.canvas.addEventListener('mousedown', this.onMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.onMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.onMouseUp.bind(this));
        this.canvas.addEventListener('wheel', this.onWheel.bind(this));

        // Tool buttons
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setTool(e.target.dataset.tool);
            });
        });

        // Zoom controls
        document.getElementById('zoom-in').addEventListener('click', () => this.zoomIn());
        document.getElementById('zoom-out').addEventListener('click', () => this.zoomOut());
        document.getElementById('zoom-fit').addEventListener('click', () => this.zoomFit());

        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Code editor
        const codeEditor = document.getElementById('code-editor');
        codeEditor.addEventListener('input', () => {
            this.validateCode();
        });

        // Export functionality
        document.getElementById('export-btn').addEventListener('click', () => {
            this.showExportModal();
        });

        // Template loading
        document.getElementById('load-template-btn').addEventListener('click', () => {
            this.loadSelectedTemplate();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', this.onKeyDown.bind(this));
    }

    initializeTools() {
        const basicTools = document.getElementById('basic-tools');
        const connectionTools = document.getElementById('connection-tools');

        // Basic tools
        const tools = [
            { id: 'rectangle', name: 'Rectangle', icon: '⬜' },
            { id: 'circle', name: 'Circle', icon: '⭕' },
            { id: 'diamond', name: 'Diamond', icon: '🔶' },
            { id: 'hexagon', name: 'Hexagon', icon: '⬡' }
        ];

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
            basicTools.appendChild(toolElement);
        });

        // Connection tools
        const connections = [
            { id: 'arrow', name: 'Arrow', icon: '→' },
            { id: 'line', name: 'Line', icon: '—' },
            { id: 'dotted', name: 'Dotted', icon: '⋯' }
        ];

        connections.forEach(conn => {
            const connElement = document.createElement('div');
            connElement.className = 'tool-item';
            connElement.dataset.tool = conn.id;
            connElement.innerHTML = `
                <div class="tool-icon">${conn.icon}</div>
                <div class="tool-name">${conn.name}</div>
            `;
            connElement.addEventListener('click', () => {
                this.setTool(conn.id);
            });
            connectionTools.appendChild(connElement);
        });
    }

    setTool(toolName) {
        this.currentTool = toolName;
        
        // Update tool button states
        document.querySelectorAll('.tool-btn, .tool-item').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeBtn = document.querySelector(`[data-tool="${toolName}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }

        // Update canvas cursor
        this.updateCanvasCursor();
    }

    updateCanvasCursor() {
        this.canvas.className = 'diagram-canvas';
        switch (this.currentTool) {
            case 'select':
                this.canvas.classList.add('select-mode');
                break;
            case 'pan':
                this.canvas.classList.add('pan-mode');
                break;
            default:
                // Drawing mode
                break;
        }
    }

    onMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left - this.pan.x) / this.zoom;
        const y = (e.clientY - rect.top - this.pan.y) / this.zoom;

        this.dragStart = { x, y };
        this.isDragging = true;

        switch (this.currentTool) {
            case 'select':
                this.handleSelect(x, y);
                break;
            case 'pan':
                this.canvas.style.cursor = 'grabbing';
                break;
            case 'rectangle':
            case 'circle':
            case 'diamond':
            case 'hexagon':
                this.createNode(this.currentTool, x, y);
                break;
        }
    }

    onMouseMove(e) {
        if (!this.isDragging) return;

        const rect = this.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left - this.pan.x) / this.zoom;
        const y = (e.clientY - rect.top - this.pan.y) / this.zoom;

        if (this.currentTool === 'pan') {
            const dx = x - this.dragStart.x;
            const dy = y - this.dragStart.y;
            this.pan.x += dx * this.zoom;
            this.pan.y += dy * this.zoom;
            this.updateTransform();
        }
    }

    onMouseUp(e) {
        this.isDragging = false;
        if (this.currentTool === 'pan') {
            this.canvas.style.cursor = 'grab';
        }
    }

    onWheel(e) {
        e.preventDefault();
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        const newZoom = Math.max(0.1, Math.min(5, this.zoom * delta));

        // Zoom towards mouse position
        this.pan.x = x - (x - this.pan.x) * (newZoom / this.zoom);
        this.pan.y = y - (y - this.pan.y) * (newZoom / this.zoom);
        this.zoom = newZoom;

        this.updateTransform();
        this.updateZoomDisplay();
    }

    updateTransform() {
        this.canvasGroup.setAttribute('transform', 
            `translate(${this.pan.x}, ${this.pan.y}) scale(${this.zoom})`);
    }

    updateZoomDisplay() {
        document.getElementById('zoom-level').textContent = `${Math.round(this.zoom * 100)}%`;
    }

    zoomIn() {
        this.zoom = Math.min(5, this.zoom * 1.2);
        this.updateTransform();
        this.updateZoomDisplay();
    }

    zoomOut() {
        this.zoom = Math.max(0.1, this.zoom / 1.2);
        this.updateTransform();
        this.updateZoomDisplay();
    }

    zoomFit() {
        // Reset zoom and pan to fit all elements
        this.zoom = 1;
        this.pan = { x: 0, y: 0 };
        this.updateTransform();
        this.updateZoomDisplay();
    }

    createNode(type, x, y) {
        const id = `node_${Date.now()}`;
        const node = {
            id,
            type,
            x: x - 60, // Center the node
            y: y - 30,
            width: 120,
            height: 60,
            label: 'New Node'
        };

        this.elements.set(id, node);
        this.renderNode(node);
        this.updateCode();
        this.selectElement(id);
    }

    renderNode(node) {
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.setAttribute('class', 'diagram-element');
        group.setAttribute('data-id', node.id);
        group.setAttribute('transform', `translate(${node.x}, ${node.y})`);

        let shape;
        switch (node.type) {
            case 'rectangle':
                shape = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                shape.setAttribute('class', 'node-rectangle');
                shape.setAttribute('width', node.width);
                shape.setAttribute('height', node.height);
                break;
            case 'circle':
                shape = document.createElementNS('http://www.w3.org/2000/svg', 'ellipse');
                shape.setAttribute('class', 'node-circle');
                shape.setAttribute('cx', node.width / 2);
                shape.setAttribute('cy', node.height / 2);
                shape.setAttribute('rx', node.width / 2);
                shape.setAttribute('ry', node.height / 2);
                break;
            case 'diamond':
                shape = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
                shape.setAttribute('class', 'node-diamond');
                const points = `${node.width/2},0 ${node.width},${node.height/2} ${node.width/2},${node.height} 0,${node.height/2}`;
                shape.setAttribute('points', points);
                break;
        }

        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('class', 'node-text');
        text.setAttribute('x', node.width / 2);
        text.setAttribute('y', node.height / 2);
        text.textContent = node.label;

        group.appendChild(shape);
        group.appendChild(text);
        this.canvasGroup.appendChild(group);

        // Add event listeners
        group.addEventListener('click', (e) => {
            e.stopPropagation();
            this.selectElement(node.id);
        });
    }

    selectElement(id) {
        // Clear previous selection
        this.selectedElements.clear();
        document.querySelectorAll('.diagram-element.selected').forEach(el => {
            el.classList.remove('selected');
        });

        // Select new element
        this.selectedElements.add(id);
        const element = document.querySelector(`[data-id="${id}"]`);
        if (element) {
            element.classList.add('selected');
        }

        this.updatePropertiesPanel();
    }

    updatePropertiesPanel() {
        const propertiesContent = document.getElementById('properties-content');
        
        if (this.selectedElements.size === 0) {
            propertiesContent.innerHTML = '<div class="no-selection"><p>Select an element to edit its properties</p></div>';
            return;
        }

        const elementId = Array.from(this.selectedElements)[0];
        const element = this.elements.get(elementId);
        
        if (!element) return;

        propertiesContent.innerHTML = `
            <div class="property-group">
                <h5>Basic Properties</h5>
                <div class="property-field">
                    <label>Label</label>
                    <input type="text" id="prop-label" value="${element.label}">
                </div>
                <div class="property-field">
                    <label>Width</label>
                    <input type="number" id="prop-width" value="${element.width}">
                </div>
                <div class="property-field">
                    <label>Height</label>
                    <input type="number" id="prop-height" value="${element.height}">
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
        `;

        // Add event listeners for property changes
        ['label', 'width', 'height', 'x', 'y'].forEach(prop => {
            const input = document.getElementById(`prop-${prop}`);
            if (input) {
                input.addEventListener('input', () => {
                    this.updateElementProperty(elementId, prop, input.value);
                });
            }
        });
    }

    updateElementProperty(elementId, property, value) {
        const element = this.elements.get(elementId);
        if (!element) return;

        // Update element data
        if (property === 'label') {
            element.label = value;
        } else {
            element[property] = parseFloat(value) || 0;
        }

        // Re-render element
        const elementNode = document.querySelector(`[data-id="${elementId}"]`);
        if (elementNode) {
            elementNode.remove();
        }
        this.renderNode(element);
        this.selectElement(elementId);
        this.updateCode();
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        // Load content based on tab
        switch (tabName) {
            case 'preview':
                this.updatePreview();
                break;
            case 'validation':
                this.validateCode();
                break;
        }
    }

    updateCode() {
        const code = this.generateMermaidCode();
        document.getElementById('code-editor').value = code;
    }

    generateMermaidCode() {
        let code = `${window.DIAGRAM_TYPE || 'flowchart'} TD\n`;
        
        // Add nodes
        this.elements.forEach(element => {
            const shape = this.getNodeShape(element.type, element.label);
            code += `    ${element.id}${shape}\n`;
        });

        // Add connections
        this.connections.forEach(connection => {
            code += `    ${connection.source} --> ${connection.target}\n`;
        });

        return code;
    }

    getNodeShape(type, label) {
        switch (type) {
            case 'rectangle':
                return `[${label}]`;
            case 'circle':
                return `((${label}))`;
            case 'diamond':
                return `{${label}}`;
            case 'hexagon':
                return `{{${label}}}`;
            default:
                return `[${label}]`;
        }
    }

    updatePreview() {
        const code = document.getElementById('code-editor').value;
        const previewContent = document.getElementById('preview-content');
        
        try {
            // Use Mermaid to render the diagram
            mermaid.render('preview-diagram', code).then(result => {
                previewContent.innerHTML = result.svg;
            }).catch(error => {
                previewContent.innerHTML = `<p style="color: red;">Preview Error: ${error.message}</p>`;
            });
        } catch (error) {
            previewContent.innerHTML = `<p style="color: red;">Preview Error: ${error.message}</p>`;
        }
    }

    validateCode() {
        // This would integrate with the validation API
        const validationResults = document.getElementById('validation-results');
        validationResults.innerHTML = `
            <div class="validation-status valid">
                <span class="status-icon">✅</span>
                <span class="status-text">Diagram is valid</span>
            </div>
        `;
    }

    loadTemplates() {
        // This would load templates from the API
        const templateSelector = document.getElementById('template-selector');
        templateSelector.innerHTML = `
            <option value="">Choose a template...</option>
            <option value="simple_flow">Simple Flow</option>
        `;
    }

    loadSelectedTemplate() {
        const templateId = document.getElementById('template-selector').value;
        if (!templateId) return;

        // This would load the template from the API
        console.log('Loading template:', templateId);
    }

    showExportModal() {
        const modal = document.getElementById('export-modal');
        modal.classList.add('show');

        // Add event listeners
        modal.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                modal.classList.remove('show');
            });
        });

        document.getElementById('export-download').addEventListener('click', () => {
            this.exportDiagram();
        });
    }

    exportDiagram() {
        const format = document.querySelector('input[name="export-format"]:checked').value;
        const filename = document.getElementById('export-filename').value || 'diagram';
        
        console.log('Exporting diagram:', format, filename);
        // This would integrate with the export API
    }

    onKeyDown(e) {
        // Delete selected elements
        if (e.key === 'Delete' && this.selectedElements.size > 0) {
            this.selectedElements.forEach(id => {
                const element = document.querySelector(`[data-id="${id}"]`);
                if (element) {
                    element.remove();
                }
                this.elements.delete(id);
            });
            this.selectedElements.clear();
            this.updatePropertiesPanel();
            this.updateCode();
        }

        // Copy/Paste (Ctrl+C, Ctrl+V)
        if ((e.ctrlKey || e.metaKey) && e.key === 'c' && this.selectedElements.size > 0) {
            // Copy functionality
            console.log('Copy elements');
        }

        if ((e.ctrlKey || e.metaKey) && e.key === 'v') {
            // Paste functionality
            console.log('Paste elements');
        }
    }
}

// Initialize the builder when the page loads
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('diagram-canvas')) {
        window.diagramBuilder = new DiagramBuilder();
    }
});
