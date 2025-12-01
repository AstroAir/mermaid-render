/**
 * Keyboard Handler - Handles keyboard shortcuts and input
 * @module input/KeyboardHandler
 */

class KeyboardHandler {
    /**
     * Create a KeyboardHandler instance
     */
    constructor() {
        this.shortcuts = new Map();
        this.enabled = true;
        this.modifierState = {
            ctrl: false,
            shift: false,
            alt: false,
            meta: false
        };

        this._registerDefaultShortcuts();
        this._initializeEventListeners();
    }

    /**
     * Initialize event listeners
     * @private
     */
    _initializeEventListeners() {
        document.addEventListener('keydown', this._onKeyDown.bind(this));
        document.addEventListener('keyup', this._onKeyUp.bind(this));

        // Reset modifier state when window loses focus
        window.addEventListener('blur', () => {
            this.modifierState = {
                ctrl: false,
                shift: false,
                alt: false,
                meta: false
            };
        });
    }

    /**
     * Register default keyboard shortcuts
     * @private
     */
    _registerDefaultShortcuts() {
        // Selection shortcuts
        this.registerShortcut('Delete', 'deleteSelected', 'Delete selected elements');
        this.registerShortcut('Backspace', 'deleteSelected', 'Delete selected elements');

        // Clipboard shortcuts
        this.registerShortcut('Ctrl+C', 'copy', 'Copy selected elements');
        this.registerShortcut('Ctrl+V', 'paste', 'Paste elements');
        this.registerShortcut('Ctrl+X', 'cut', 'Cut selected elements');
        this.registerShortcut('Ctrl+A', 'selectAll', 'Select all elements');

        // Undo/Redo
        this.registerShortcut('Ctrl+Z', 'undo', 'Undo last action');
        this.registerShortcut('Ctrl+Y', 'redo', 'Redo last action');
        this.registerShortcut('Ctrl+Shift+Z', 'redo', 'Redo last action');

        // View shortcuts
        this.registerShortcut('Ctrl++', 'zoomIn', 'Zoom in');
        this.registerShortcut('Ctrl+=', 'zoomIn', 'Zoom in');
        this.registerShortcut('Ctrl+-', 'zoomOut', 'Zoom out');
        this.registerShortcut('Ctrl+0', 'zoomReset', 'Reset zoom');

        // Tool shortcuts
        this.registerShortcut('V', 'selectTool', 'Select tool');
        this.registerShortcut('H', 'panTool', 'Pan tool');
        this.registerShortcut('R', 'rectangleTool', 'Rectangle tool');
        this.registerShortcut('O', 'circleTool', 'Circle tool');
        this.registerShortcut('D', 'diamondTool', 'Diamond tool');

        // File shortcuts
        this.registerShortcut('Ctrl+S', 'save', 'Save diagram');
        this.registerShortcut('Ctrl+E', 'export', 'Export diagram');

        // Navigation
        this.registerShortcut('Escape', 'deselect', 'Deselect all');
        this.registerShortcut('Ctrl+K', 'quickNav', 'Quick navigation');

        // Arrow key movement
        this.registerShortcut('ArrowUp', 'moveUp', 'Move selection up');
        this.registerShortcut('ArrowDown', 'moveDown', 'Move selection down');
        this.registerShortcut('ArrowLeft', 'moveLeft', 'Move selection left');
        this.registerShortcut('ArrowRight', 'moveRight', 'Move selection right');

        // Shift+Arrow for larger movement
        this.registerShortcut('Shift+ArrowUp', 'moveUpLarge', 'Move selection up (large)');
        this.registerShortcut('Shift+ArrowDown', 'moveDownLarge', 'Move selection down (large)');
        this.registerShortcut('Shift+ArrowLeft', 'moveLeftLarge', 'Move selection left (large)');
        this.registerShortcut('Shift+ArrowRight', 'moveRightLarge', 'Move selection right (large)');
    }

    /**
     * Handle keydown event
     * @param {KeyboardEvent} e - Keyboard event
     * @private
     */
    _onKeyDown(e) {
        if (!this.enabled) return;

        // Update modifier state
        this.modifierState.ctrl = e.ctrlKey;
        this.modifierState.shift = e.shiftKey;
        this.modifierState.alt = e.altKey;
        this.modifierState.meta = e.metaKey;

        // Don't handle shortcuts when typing in input fields
        if (this._isInputFocused()) {
            // Allow some shortcuts even in input fields
            const allowedInInput = ['Escape'];
            if (!allowedInInput.includes(e.key)) {
                return;
            }
        }

        // Build shortcut string
        const shortcutString = this._buildShortcutString(e);

        // Check if shortcut is registered
        const shortcut = this.shortcuts.get(shortcutString);
        if (shortcut) {
            e.preventDefault();
            this._executeShortcut(shortcut);
        }
    }

    /**
     * Handle keyup event
     * @param {KeyboardEvent} e - Keyboard event
     * @private
     */
    _onKeyUp(e) {
        // Update modifier state
        this.modifierState.ctrl = e.ctrlKey;
        this.modifierState.shift = e.shiftKey;
        this.modifierState.alt = e.altKey;
        this.modifierState.meta = e.metaKey;
    }

    /**
     * Check if an input element is focused
     * @returns {boolean} True if input is focused
     * @private
     */
    _isInputFocused() {
        const activeElement = document.activeElement;
        if (!activeElement) return false;

        const tagName = activeElement.tagName.toLowerCase();
        return tagName === 'input' || tagName === 'textarea' || activeElement.isContentEditable;
    }

    /**
     * Build shortcut string from keyboard event
     * @param {KeyboardEvent} e - Keyboard event
     * @returns {string} Shortcut string
     * @private
     */
    _buildShortcutString(e) {
        const parts = [];

        if (e.ctrlKey || e.metaKey) parts.push('Ctrl');
        if (e.shiftKey) parts.push('Shift');
        if (e.altKey) parts.push('Alt');

        // Normalize key name
        let key = e.key;
        if (key === ' ') key = 'Space';
        if (key.length === 1) key = key.toUpperCase();

        parts.push(key);

        return parts.join('+');
    }

    /**
     * Execute a shortcut action
     * @param {Object} shortcut - Shortcut configuration
     * @private
     */
    _executeShortcut(shortcut) {
        if (shortcut.handler) {
            shortcut.handler();
        } else if (shortcut.action) {
            // Emit event for action
            const event = new CustomEvent('shortcut', {
                detail: {
                    action: shortcut.action,
                    description: shortcut.description
                }
            });
            document.dispatchEvent(event);
        }
    }

    /**
     * Register a keyboard shortcut
     * @param {string} keys - Key combination (e.g., 'Ctrl+C')
     * @param {string|Function} actionOrHandler - Action name or handler function
     * @param {string} [description] - Shortcut description
     */
    registerShortcut(keys, actionOrHandler, description = '') {
        const shortcut = {
            keys,
            description
        };

        if (typeof actionOrHandler === 'function') {
            shortcut.handler = actionOrHandler;
        } else {
            shortcut.action = actionOrHandler;
        }

        this.shortcuts.set(keys, shortcut);
    }

    /**
     * Unregister a keyboard shortcut
     * @param {string} keys - Key combination
     * @returns {boolean} True if shortcut was removed
     */
    unregisterShortcut(keys) {
        return this.shortcuts.delete(keys);
    }

    /**
     * Set handler for a shortcut action
     * @param {string} action - Action name
     * @param {Function} handler - Handler function
     */
    setActionHandler(action, handler) {
        this.shortcuts.forEach((shortcut, keys) => {
            if (shortcut.action === action) {
                shortcut.handler = handler;
            }
        });
    }

    /**
     * Enable keyboard shortcuts
     */
    enable() {
        this.enabled = true;
    }

    /**
     * Disable keyboard shortcuts
     */
    disable() {
        this.enabled = false;
    }

    /**
     * Check if shortcuts are enabled
     * @returns {boolean} True if enabled
     */
    isEnabled() {
        return this.enabled;
    }

    /**
     * Get all registered shortcuts
     * @returns {Array} Array of shortcut configurations
     */
    getAllShortcuts() {
        return Array.from(this.shortcuts.entries()).map(([keys, shortcut]) => ({
            keys,
            ...shortcut
        }));
    }

    /**
     * Get shortcuts by category
     * @param {string} category - Category name
     * @returns {Array} Array of shortcuts in category
     */
    getShortcutsByCategory(category) {
        const categoryMap = {
            'clipboard': ['copy', 'paste', 'cut'],
            'selection': ['selectAll', 'deselect', 'deleteSelected'],
            'view': ['zoomIn', 'zoomOut', 'zoomReset'],
            'tools': ['selectTool', 'panTool', 'rectangleTool', 'circleTool', 'diamondTool'],
            'file': ['save', 'export'],
            'history': ['undo', 'redo'],
            'movement': ['moveUp', 'moveDown', 'moveLeft', 'moveRight', 'moveUpLarge', 'moveDownLarge', 'moveLeftLarge', 'moveRightLarge']
        };

        const actions = categoryMap[category] || [];
        return this.getAllShortcuts().filter(s => actions.includes(s.action));
    }

    /**
     * Get current modifier state
     * @returns {Object} Modifier state
     */
    getModifierState() {
        return { ...this.modifierState };
    }

    /**
     * Check if a modifier is pressed
     * @param {string} modifier - Modifier name ('ctrl', 'shift', 'alt', 'meta')
     * @returns {boolean} True if modifier is pressed
     */
    isModifierPressed(modifier) {
        return this.modifierState[modifier.toLowerCase()] || false;
    }

    /**
     * Generate help text for shortcuts
     * @returns {string} HTML help text
     */
    generateHelpText() {
        const categories = ['clipboard', 'selection', 'view', 'tools', 'file', 'history', 'movement'];
        let html = '<div class="keyboard-shortcuts-help">';

        categories.forEach(category => {
            const shortcuts = this.getShortcutsByCategory(category);
            if (shortcuts.length > 0) {
                html += `<div class="shortcut-category">`;
                html += `<h4>${category.charAt(0).toUpperCase() + category.slice(1)}</h4>`;
                html += '<ul>';
                shortcuts.forEach(s => {
                    html += `<li><kbd>${s.keys}</kbd> - ${s.description}</li>`;
                });
                html += '</ul></div>';
            }
        });

        html += '</div>';
        return html;
    }
}

// Export for use in other modules
window.KeyboardHandler = KeyboardHandler;
