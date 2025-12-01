/**
 * Code Generator - Generates Mermaid code from diagram elements
 * @module code/CodeGenerator
 */

class CodeGenerator {
    /**
     * Create a CodeGenerator instance
     * @param {string} [diagramType='flowchart'] - The diagram type
     */
    constructor(diagramType = 'flowchart') {
        this.diagramType = diagramType;
    }

    /**
     * Set the diagram type
     * @param {string} diagramType - The diagram type
     */
    setDiagramType(diagramType) {
        this.diagramType = diagramType;
    }

    /**
     * Generate Mermaid code from elements and connections
     * @param {Map} elements - Map of element ID to element data
     * @param {Map} connections - Map of connection ID to connection data
     * @returns {string} Generated Mermaid code
     */
    generate(elements, connections) {
        switch (this.diagramType.toLowerCase()) {
            case 'flowchart':
            case 'graph':
                return this._generateFlowchart(elements, connections);
            case 'sequence':
                return this._generateSequence(elements, connections);
            case 'class':
                return this._generateClass(elements, connections);
            case 'state':
                return this._generateState(elements, connections);
            case 'er':
                return this._generateER(elements, connections);
            default:
                return this._generateFlowchart(elements, connections);
        }
    }

    /**
     * Generate flowchart Mermaid code
     * @param {Map} elements - Elements map
     * @param {Map} connections - Connections map
     * @returns {string} Flowchart code
     * @private
     */
    _generateFlowchart(elements, connections) {
        let code = `${this.diagramType} TD\n`;

        // Add nodes
        elements.forEach(element => {
            const shape = this._getNodeShape(element.type, element.label);
            const nodeId = this._sanitizeId(element.id);
            code += `    ${nodeId}${shape}\n`;
        });

        // Add connections
        connections.forEach(connection => {
            const sourceId = this._sanitizeId(connection.source);
            const targetId = this._sanitizeId(connection.target);
            const arrow = this._getFlowchartArrow(connection.type);

            if (connection.label) {
                code += `    ${sourceId} ${arrow}|${connection.label}| ${targetId}\n`;
            } else {
                code += `    ${sourceId} ${arrow} ${targetId}\n`;
            }
        });

        return code;
    }

    /**
     * Generate sequence diagram Mermaid code
     * @param {Map} elements - Elements map
     * @param {Map} connections - Connections map
     * @returns {string} Sequence diagram code
     * @private
     */
    _generateSequence(elements, connections) {
        let code = 'sequenceDiagram\n';

        // Add participants
        elements.forEach(element => {
            const participantId = this._sanitizeId(element.id);
            if (element.label !== participantId) {
                code += `    participant ${participantId} as ${element.label}\n`;
            } else {
                code += `    participant ${participantId}\n`;
            }
        });

        code += '\n';

        // Add messages
        connections.forEach(connection => {
            const sourceId = this._sanitizeId(connection.source);
            const targetId = this._sanitizeId(connection.target);
            const arrow = this._getSequenceArrow(connection.type);
            const label = connection.label || 'message';

            code += `    ${sourceId}${arrow}${targetId}: ${label}\n`;
        });

        return code;
    }

    /**
     * Generate class diagram Mermaid code
     * @param {Map} elements - Elements map
     * @param {Map} connections - Connections map
     * @returns {string} Class diagram code
     * @private
     */
    _generateClass(elements, connections) {
        let code = 'classDiagram\n';

        // Add classes
        elements.forEach(element => {
            const className = this._sanitizeId(element.id);
            code += `    class ${className} {\n`;

            // Add attributes if present
            if (element.attributes && Array.isArray(element.attributes)) {
                element.attributes.forEach(attr => {
                    code += `        ${attr}\n`;
                });
            }

            // Add methods if present
            if (element.methods && Array.isArray(element.methods)) {
                element.methods.forEach(method => {
                    code += `        ${method}\n`;
                });
            }

            code += '    }\n';
        });

        code += '\n';

        // Add relationships
        connections.forEach(connection => {
            const sourceId = this._sanitizeId(connection.source);
            const targetId = this._sanitizeId(connection.target);
            const relationship = this._getClassRelationship(connection.type);

            if (connection.label) {
                code += `    ${sourceId} ${relationship} ${targetId} : ${connection.label}\n`;
            } else {
                code += `    ${sourceId} ${relationship} ${targetId}\n`;
            }
        });

        return code;
    }

    /**
     * Generate state diagram Mermaid code
     * @param {Map} elements - Elements map
     * @param {Map} connections - Connections map
     * @returns {string} State diagram code
     * @private
     */
    _generateState(elements, connections) {
        let code = 'stateDiagram-v2\n';

        // Add states
        elements.forEach(element => {
            const stateId = this._sanitizeId(element.id);
            if (element.label !== stateId) {
                code += `    ${stateId} : ${element.label}\n`;
            }
        });

        code += '\n';

        // Add transitions
        connections.forEach(connection => {
            const sourceId = this._sanitizeId(connection.source);
            const targetId = this._sanitizeId(connection.target);

            if (connection.label) {
                code += `    ${sourceId} --> ${targetId} : ${connection.label}\n`;
            } else {
                code += `    ${sourceId} --> ${targetId}\n`;
            }
        });

        return code;
    }

    /**
     * Generate ER diagram Mermaid code
     * @param {Map} elements - Elements map
     * @param {Map} connections - Connections map
     * @returns {string} ER diagram code
     * @private
     */
    _generateER(elements, connections) {
        let code = 'erDiagram\n';

        // Add entities
        elements.forEach(element => {
            const entityId = this._sanitizeId(element.id);
            code += `    ${entityId} {\n`;

            // Add attributes if present
            if (element.attributes && Array.isArray(element.attributes)) {
                element.attributes.forEach(attr => {
                    code += `        ${attr}\n`;
                });
            }

            code += '    }\n';
        });

        code += '\n';

        // Add relationships
        connections.forEach(connection => {
            const sourceId = this._sanitizeId(connection.source);
            const targetId = this._sanitizeId(connection.target);
            const relationship = this._getERRelationship(connection.type);
            const label = connection.label || 'relates';

            code += `    ${sourceId} ${relationship} ${targetId} : "${label}"\n`;
        });

        return code;
    }

    /**
     * Get node shape syntax for flowchart
     * @param {string} type - Node type
     * @param {string} label - Node label
     * @returns {string} Shape syntax
     * @private
     */
    _getNodeShape(type, label) {
        const escapedLabel = this._escapeLabel(label);
        switch (type) {
            case 'rectangle':
                return `[${escapedLabel}]`;
            case 'rounded':
                return `(${escapedLabel})`;
            case 'circle':
                return `((${escapedLabel}))`;
            case 'diamond':
                return `{${escapedLabel}}`;
            case 'hexagon':
                return `{{${escapedLabel}}}`;
            case 'parallelogram':
                return `[/${escapedLabel}/]`;
            case 'trapezoid':
                return `[/${escapedLabel}\\]`;
            case 'stadium':
                return `([${escapedLabel}])`;
            case 'subroutine':
                return `[[${escapedLabel}]]`;
            case 'cylinder':
                return `[(${escapedLabel})]`;
            case 'asymmetric':
                return `>${escapedLabel}]`;
            default:
                return `[${escapedLabel}]`;
        }
    }

    /**
     * Get arrow syntax for flowchart
     * @param {string} type - Connection type
     * @returns {string} Arrow syntax
     * @private
     */
    _getFlowchartArrow(type) {
        switch (type) {
            case 'arrow':
            case 'default':
                return '-->';
            case 'line':
                return '---';
            case 'dotted':
                return '-.->';
            case 'thick':
                return '==>';
            case 'invisible':
                return '~~~';
            case 'open':
                return '--o';
            case 'cross':
                return '--x';
            default:
                return '-->';
        }
    }

    /**
     * Get arrow syntax for sequence diagram
     * @param {string} type - Connection type
     * @returns {string} Arrow syntax
     * @private
     */
    _getSequenceArrow(type) {
        switch (type) {
            case 'sync':
            case 'default':
                return '->>';
            case 'async':
            case 'dotted':
                return '-->>';
            case 'return':
                return '-->>';
            case 'solid':
                return '->';
            case 'dashed':
                return '-->';
            default:
                return '->>';
        }
    }

    /**
     * Get relationship syntax for class diagram
     * @param {string} type - Relationship type
     * @returns {string} Relationship syntax
     * @private
     */
    _getClassRelationship(type) {
        switch (type) {
            case 'inheritance':
                return '--|>';
            case 'composition':
                return '--*';
            case 'aggregation':
                return '--o';
            case 'association':
            case 'default':
                return '-->';
            case 'dependency':
                return '..>';
            case 'realization':
                return '..|>';
            default:
                return '-->';
        }
    }

    /**
     * Get relationship syntax for ER diagram
     * @param {string} type - Relationship type
     * @returns {string} Relationship syntax
     * @private
     */
    _getERRelationship(type) {
        switch (type) {
            case 'one-to-one':
                return '||--||';
            case 'one-to-many':
                return '||--o{';
            case 'many-to-one':
                return '}o--||';
            case 'many-to-many':
                return '}o--o{';
            case 'zero-or-one':
                return '|o--o|';
            default:
                return '||--||';
        }
    }

    /**
     * Sanitize ID for Mermaid syntax
     * @param {string} id - Original ID
     * @returns {string} Sanitized ID
     * @private
     */
    _sanitizeId(id) {
        // Remove or replace invalid characters
        return id.replace(/[^a-zA-Z0-9_]/g, '_');
    }

    /**
     * Escape label for Mermaid syntax
     * @param {string} label - Original label
     * @returns {string} Escaped label
     * @private
     */
    _escapeLabel(label) {
        // Escape special characters in labels
        return label
            .replace(/"/g, '\\"')
            .replace(/\[/g, '\\[')
            .replace(/\]/g, '\\]')
            .replace(/\{/g, '\\{')
            .replace(/\}/g, '\\}')
            .replace(/\(/g, '\\(')
            .replace(/\)/g, '\\)');
    }

    /**
     * Update code editor with generated code
     * @param {Map} elements - Elements map
     * @param {Map} connections - Connections map
     * @param {string} [editorId='code-editor'] - Code editor element ID
     */
    updateCodeEditor(elements, connections, editorId = 'code-editor') {
        const code = this.generate(elements, connections);
        const editor = document.getElementById(editorId);
        if (editor) {
            editor.value = code;
        }
        return code;
    }

    /**
     * Get supported diagram types
     * @returns {Array} Array of supported diagram types
     */
    static getSupportedTypes() {
        return [
            { id: 'flowchart', name: 'Flowchart' },
            { id: 'sequence', name: 'Sequence Diagram' },
            { id: 'class', name: 'Class Diagram' },
            { id: 'state', name: 'State Diagram' },
            { id: 'er', name: 'ER Diagram' }
        ];
    }
}

// Export for use in other modules
window.CodeGenerator = CodeGenerator;
