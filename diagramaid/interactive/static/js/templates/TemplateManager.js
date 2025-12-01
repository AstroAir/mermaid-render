/**
 * Template Manager - Handles diagram template loading and management
 * @module templates/TemplateManager
 */

class TemplateManager {
    /**
     * Create a TemplateManager instance
     */
    constructor() {
        this.templates = new Map();
        this.selectorElement = document.getElementById('template-selector');
        this.onTemplateLoadCallbacks = [];

        this._loadDefaultTemplates();
        this._initializeEventListeners();
    }

    /**
     * Initialize event listeners
     * @private
     */
    _initializeEventListeners() {
        const loadBtn = document.getElementById('load-template-btn');
        if (loadBtn) {
            loadBtn.addEventListener('click', () => {
                this.loadSelectedTemplate();
            });
        }

        // Double-click on selector to load
        if (this.selectorElement) {
            this.selectorElement.addEventListener('dblclick', () => {
                this.loadSelectedTemplate();
            });
        }
    }

    /**
     * Load default templates
     * @private
     */
    _loadDefaultTemplates() {
        // Simple Flow template
        this.templates.set('simple_flow', {
            id: 'simple_flow',
            name: 'Simple Flow',
            description: 'Basic flowchart with start, process, and end',
            category: 'flowchart',
            elements: [
                { id: 'start', type: 'circle', label: 'Start', x: 100, y: 50, width: 120, height: 60 },
                { id: 'process', type: 'rectangle', label: 'Process', x: 100, y: 150, width: 120, height: 60 },
                { id: 'end', type: 'circle', label: 'End', x: 100, y: 250, width: 120, height: 60 }
            ],
            connections: [
                { id: 'conn1', source: 'start', target: 'process', type: 'arrow' },
                { id: 'conn2', source: 'process', target: 'end', type: 'arrow' }
            ],
            code: `flowchart TD
    start((Start))
    process[Process]
    end_node((End))
    
    start --> process
    process --> end_node`
        });

        // Decision Flow template
        this.templates.set('decision_flow', {
            id: 'decision_flow',
            name: 'Decision Flow',
            description: 'Flowchart with decision point',
            category: 'flowchart',
            elements: [
                { id: 'start', type: 'circle', label: 'Start', x: 200, y: 50, width: 120, height: 60 },
                { id: 'decision', type: 'diamond', label: 'Decision?', x: 200, y: 150, width: 120, height: 60 },
                { id: 'yes_path', type: 'rectangle', label: 'Yes Path', x: 50, y: 250, width: 120, height: 60 },
                { id: 'no_path', type: 'rectangle', label: 'No Path', x: 350, y: 250, width: 120, height: 60 },
                { id: 'end', type: 'circle', label: 'End', x: 200, y: 350, width: 120, height: 60 }
            ],
            connections: [
                { id: 'conn1', source: 'start', target: 'decision', type: 'arrow' },
                { id: 'conn2', source: 'decision', target: 'yes_path', type: 'arrow', label: 'Yes' },
                { id: 'conn3', source: 'decision', target: 'no_path', type: 'arrow', label: 'No' },
                { id: 'conn4', source: 'yes_path', target: 'end', type: 'arrow' },
                { id: 'conn5', source: 'no_path', target: 'end', type: 'arrow' }
            ],
            code: `flowchart TD
    start((Start))
    decision{Decision?}
    yes_path[Yes Path]
    no_path[No Path]
    end_node((End))
    
    start --> decision
    decision -->|Yes| yes_path
    decision -->|No| no_path
    yes_path --> end_node
    no_path --> end_node`
        });

        // Sequence Diagram template
        this.templates.set('sequence_basic', {
            id: 'sequence_basic',
            name: 'Basic Sequence',
            description: 'Simple sequence diagram with two participants',
            category: 'sequence',
            elements: [
                { id: 'alice', type: 'rectangle', label: 'Alice', x: 100, y: 50, width: 120, height: 60 },
                { id: 'bob', type: 'rectangle', label: 'Bob', x: 300, y: 50, width: 120, height: 60 }
            ],
            connections: [
                { id: 'msg1', source: 'alice', target: 'bob', type: 'sync', label: 'Hello Bob' },
                { id: 'msg2', source: 'bob', target: 'alice', type: 'return', label: 'Hello Alice' }
            ],
            code: `sequenceDiagram
    participant Alice
    participant Bob
    
    Alice->>Bob: Hello Bob
    Bob-->>Alice: Hello Alice`
        });

        // Class Diagram template
        this.templates.set('class_basic', {
            id: 'class_basic',
            name: 'Basic Class',
            description: 'Simple class diagram with inheritance',
            category: 'class',
            elements: [
                { id: 'Animal', type: 'rectangle', label: 'Animal', x: 200, y: 50, width: 150, height: 80, attributes: ['+name: string', '+age: int'], methods: ['+eat()', '+sleep()'] },
                { id: 'Dog', type: 'rectangle', label: 'Dog', x: 100, y: 200, width: 150, height: 80, attributes: ['+breed: string'], methods: ['+bark()'] },
                { id: 'Cat', type: 'rectangle', label: 'Cat', x: 300, y: 200, width: 150, height: 80, attributes: ['+color: string'], methods: ['+meow()'] }
            ],
            connections: [
                { id: 'inherit1', source: 'Dog', target: 'Animal', type: 'inheritance' },
                { id: 'inherit2', source: 'Cat', target: 'Animal', type: 'inheritance' }
            ],
            code: `classDiagram
    class Animal {
        +name: string
        +age: int
        +eat()
        +sleep()
    }
    class Dog {
        +breed: string
        +bark()
    }
    class Cat {
        +color: string
        +meow()
    }
    
    Animal <|-- Dog
    Animal <|-- Cat`
        });

        // State Diagram template
        this.templates.set('state_basic', {
            id: 'state_basic',
            name: 'Basic State',
            description: 'Simple state diagram',
            category: 'state',
            elements: [
                { id: 'idle', type: 'rounded', label: 'Idle', x: 100, y: 100, width: 120, height: 60 },
                { id: 'processing', type: 'rounded', label: 'Processing', x: 300, y: 100, width: 120, height: 60 },
                { id: 'completed', type: 'rounded', label: 'Completed', x: 200, y: 250, width: 120, height: 60 }
            ],
            connections: [
                { id: 'trans1', source: 'idle', target: 'processing', type: 'default', label: 'start' },
                { id: 'trans2', source: 'processing', target: 'completed', type: 'default', label: 'finish' },
                { id: 'trans3', source: 'completed', target: 'idle', type: 'default', label: 'reset' }
            ],
            code: `stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : start
    Processing --> Completed : finish
    Completed --> Idle : reset
    Completed --> [*]`
        });

        // Update selector
        this._updateSelector();
    }

    /**
     * Update template selector dropdown
     * @private
     */
    _updateSelector() {
        if (!this.selectorElement) return;

        this.selectorElement.innerHTML = '<option value="">Choose a template...</option>';

        // Group templates by category
        const categories = new Map();
        this.templates.forEach((template, id) => {
            const category = template.category || 'other';
            if (!categories.has(category)) {
                categories.set(category, []);
            }
            categories.get(category).push(template);
        });

        // Add options grouped by category
        categories.forEach((templates, category) => {
            const optgroup = document.createElement('optgroup');
            optgroup.label = this._formatCategoryName(category);

            templates.forEach(template => {
                const option = document.createElement('option');
                option.value = template.id;
                option.textContent = template.name;
                option.title = template.description;
                optgroup.appendChild(option);
            });

            this.selectorElement.appendChild(optgroup);
        });
    }

    /**
     * Format category name for display
     * @param {string} category - Category ID
     * @returns {string} Formatted name
     * @private
     */
    _formatCategoryName(category) {
        return category.charAt(0).toUpperCase() + category.slice(1) + ' Diagrams';
    }

    /**
     * Load selected template
     */
    loadSelectedTemplate() {
        if (!this.selectorElement) return;

        const templateId = this.selectorElement.value;
        if (!templateId) {
            console.warn('No template selected');
            return;
        }

        this.loadTemplate(templateId);
    }

    /**
     * Load a template by ID
     * @param {string} templateId - Template ID
     * @returns {Object|null} Template data
     */
    loadTemplate(templateId) {
        const template = this.templates.get(templateId);
        if (!template) {
            console.warn(`Template "${templateId}" not found`);
            return null;
        }

        // Notify callbacks
        this.onTemplateLoadCallbacks.forEach(callback => {
            callback(template);
        });

        return template;
    }

    /**
     * Get template by ID
     * @param {string} templateId - Template ID
     * @returns {Object|null} Template data
     */
    getTemplate(templateId) {
        return this.templates.get(templateId) || null;
    }

    /**
     * Get all templates
     * @returns {Array} Array of all templates
     */
    getAllTemplates() {
        return Array.from(this.templates.values());
    }

    /**
     * Get templates by category
     * @param {string} category - Category name
     * @returns {Array} Array of templates in category
     */
    getTemplatesByCategory(category) {
        return Array.from(this.templates.values()).filter(t => t.category === category);
    }

    /**
     * Get all categories
     * @returns {Array} Array of category names
     */
    getCategories() {
        const categories = new Set();
        this.templates.forEach(template => {
            if (template.category) {
                categories.add(template.category);
            }
        });
        return Array.from(categories);
    }

    /**
     * Register a custom template
     * @param {Object} template - Template configuration
     */
    registerTemplate(template) {
        if (!template.id) {
            console.error('Template must have an ID');
            return;
        }
        this.templates.set(template.id, template);
        this._updateSelector();
    }

    /**
     * Unregister a template
     * @param {string} templateId - Template ID
     * @returns {boolean} True if template was removed
     */
    unregisterTemplate(templateId) {
        const result = this.templates.delete(templateId);
        if (result) {
            this._updateSelector();
        }
        return result;
    }

    /**
     * Register callback for template load events
     * @param {Function} callback - Callback function (template) => void
     */
    onTemplateLoad(callback) {
        this.onTemplateLoadCallbacks.push(callback);
    }

    /**
     * Remove template load callback
     * @param {Function} callback - The callback to remove
     */
    offTemplateLoad(callback) {
        const index = this.onTemplateLoadCallbacks.indexOf(callback);
        if (index > -1) {
            this.onTemplateLoadCallbacks.splice(index, 1);
        }
    }

    /**
     * Load templates from API
     * @param {string} apiUrl - API endpoint URL
     * @returns {Promise<void>}
     */
    async loadFromApi(apiUrl) {
        try {
            const response = await fetch(apiUrl);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const templates = await response.json();

            templates.forEach(template => {
                this.templates.set(template.id, template);
            });

            this._updateSelector();
        } catch (error) {
            console.error('Failed to load templates from API:', error);
        }
    }

    /**
     * Save template to API
     * @param {Object} template - Template to save
     * @param {string} apiUrl - API endpoint URL
     * @returns {Promise<boolean>}
     */
    async saveToApi(template, apiUrl) {
        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(template)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return true;
        } catch (error) {
            console.error('Failed to save template to API:', error);
            return false;
        }
    }

    /**
     * Create template from current diagram state
     * @param {string} id - Template ID
     * @param {string} name - Template name
     * @param {string} description - Template description
     * @param {string} category - Template category
     * @param {Map} elements - Current elements
     * @param {Map} connections - Current connections
     * @param {string} code - Current Mermaid code
     * @returns {Object} Created template
     */
    createFromCurrentState(id, name, description, category, elements, connections, code) {
        const template = {
            id,
            name,
            description,
            category,
            elements: Array.from(elements.values()),
            connections: Array.from(connections.values()),
            code
        };

        this.registerTemplate(template);
        return template;
    }
}

// Export for use in other modules
window.TemplateManager = TemplateManager;
