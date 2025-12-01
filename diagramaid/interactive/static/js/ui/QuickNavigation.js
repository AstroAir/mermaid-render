/**
 * Quick Navigation - Provides quick navigation modal functionality
 * @module ui/QuickNavigation
 */

class QuickNavigation {
    /**
     * Create a QuickNavigation instance
     */
    constructor() {
        this.modal = null;
        this.styleElement = null;
        this.currentIndex = 0;
        this.items = [];

        this._initializeKeyboardShortcut();
    }

    /**
     * Initialize keyboard shortcut
     * @private
     */
    _initializeKeyboardShortcut() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K for quick navigation
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.show();
            }
        });
    }

    /**
     * Show quick navigation modal
     */
    show() {
        if (this.modal) {
            this.hide();
            return;
        }

        this._createModal();
        this._addStyles();
        this._setupEventListeners();
        this._focusFirstItem();
    }

    /**
     * Hide quick navigation modal
     */
    hide() {
        if (this.modal) {
            this.modal.remove();
            this.modal = null;
        }
        if (this.styleElement) {
            this.styleElement.remove();
            this.styleElement = null;
        }
        this.currentIndex = 0;
    }

    /**
     * Create modal element
     * @private
     */
    _createModal() {
        this.modal = document.createElement('div');
        this.modal.className = 'modal show quick-nav-modal';
        this.modal.innerHTML = `
            <div class="modal-content quick-nav-content">
                <div class="modal-header">
                    <h3>Quick Navigation</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="quick-nav-search">
                        <input type="text" id="quick-nav-search" placeholder="Search..." autocomplete="off">
                    </div>
                    <div class="quick-nav-options" id="quick-nav-options">
                        ${this._generateNavigationItems()}
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(this.modal);
        this.items = this.modal.querySelectorAll('.quick-nav-item');
    }

    /**
     * Generate navigation items HTML
     * @returns {string} HTML string
     * @private
     */
    _generateNavigationItems() {
        const navItems = [
            { href: '/builder/flowchart', icon: '📊', text: 'Flowchart Builder' },
            { href: '/builder/sequence', icon: '🔄', text: 'Sequence Diagram' },
            { href: '/builder/class', icon: '🏗️', text: 'Class Diagram' },
            { href: '/builder/state', icon: '🔀', text: 'State Diagram' },
            { href: '/api/docs', icon: '📚', text: 'API Documentation' },
            { href: '/', icon: '🏠', text: 'Home' }
        ];

        return navItems.map((item, index) => `
            <a href="${item.href}" class="quick-nav-item" data-index="${index}">
                <span class="nav-icon">${item.icon}</span>
                <span class="nav-text">${item.text}</span>
            </a>
        `).join('');
    }

    /**
     * Add styles for quick navigation
     * @private
     */
    _addStyles() {
        this.styleElement = document.createElement('style');
        this.styleElement.textContent = `
            .quick-nav-modal .modal-content {
                max-width: 400px;
            }
            .quick-nav-search {
                margin-bottom: 1rem;
            }
            .quick-nav-search input {
                width: 100%;
                padding: 0.75rem;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 1rem;
            }
            .quick-nav-search input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            .quick-nav-options {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
                max-height: 300px;
                overflow-y: auto;
            }
            .quick-nav-item {
                display: flex;
                align-items: center;
                gap: 1rem;
                padding: 1rem;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                text-decoration: none;
                color: #333;
                transition: all 0.2s;
            }
            .quick-nav-item:hover,
            .quick-nav-item.focused {
                background: #f8f9fa;
                border-color: #667eea;
                transform: translateX(5px);
            }
            .quick-nav-item.focused {
                background: #667eea;
                color: white;
            }
            .quick-nav-item.focused .nav-text {
                color: white;
            }
            .nav-icon {
                font-size: 1.5rem;
            }
            .nav-text {
                font-weight: 500;
            }
            .quick-nav-item.hidden {
                display: none;
            }
        `;
        document.head.appendChild(this.styleElement);
    }

    /**
     * Setup event listeners
     * @private
     */
    _setupEventListeners() {
        // Close button
        const closeBtn = this.modal.querySelector('.modal-close');
        closeBtn.addEventListener('click', () => this.hide());

        // Click outside to close
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.hide();
            }
        });

        // Search input
        const searchInput = this.modal.querySelector('#quick-nav-search');
        searchInput.addEventListener('input', (e) => {
            this._filterItems(e.target.value);
        });

        // Keyboard navigation
        this.modal.addEventListener('keydown', (e) => {
            this._handleKeydown(e);
        });

        // Focus search input
        searchInput.focus();
    }

    /**
     * Handle keydown events
     * @param {KeyboardEvent} e - Keyboard event
     * @private
     */
    _handleKeydown(e) {
        const visibleItems = Array.from(this.items).filter(item => !item.classList.contains('hidden'));

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this._moveFocus(1, visibleItems);
                break;
            case 'ArrowUp':
                e.preventDefault();
                this._moveFocus(-1, visibleItems);
                break;
            case 'Enter':
                e.preventDefault();
                const focusedItem = visibleItems[this.currentIndex];
                if (focusedItem) {
                    focusedItem.click();
                }
                break;
            case 'Escape':
                this.hide();
                break;
        }
    }

    /**
     * Move focus to next/previous item
     * @param {number} direction - Direction (1 or -1)
     * @param {Array} visibleItems - Array of visible items
     * @private
     */
    _moveFocus(direction, visibleItems) {
        // Remove focus from current item
        visibleItems.forEach(item => item.classList.remove('focused'));

        // Calculate new index
        this.currentIndex = (this.currentIndex + direction + visibleItems.length) % visibleItems.length;

        // Add focus to new item
        if (visibleItems[this.currentIndex]) {
            visibleItems[this.currentIndex].classList.add('focused');
            visibleItems[this.currentIndex].scrollIntoView({ block: 'nearest' });
        }
    }

    /**
     * Focus first item
     * @private
     */
    _focusFirstItem() {
        this.currentIndex = 0;
        if (this.items.length > 0) {
            this.items[0].classList.add('focused');
        }
    }

    /**
     * Filter items based on search query
     * @param {string} query - Search query
     * @private
     */
    _filterItems(query) {
        const lowerQuery = query.toLowerCase();

        this.items.forEach(item => {
            const text = item.querySelector('.nav-text').textContent.toLowerCase();
            if (text.includes(lowerQuery)) {
                item.classList.remove('hidden');
            } else {
                item.classList.add('hidden');
            }
        });

        // Reset focus to first visible item
        this.currentIndex = 0;
        const visibleItems = Array.from(this.items).filter(item => !item.classList.contains('hidden'));
        this.items.forEach(item => item.classList.remove('focused'));
        if (visibleItems.length > 0) {
            visibleItems[0].classList.add('focused');
        }
    }

    /**
     * Add custom navigation item
     * @param {Object} item - Navigation item
     * @param {string} item.href - Link URL
     * @param {string} item.icon - Icon (emoji or HTML)
     * @param {string} item.text - Display text
     */
    addItem(item) {
        const optionsContainer = document.getElementById('quick-nav-options');
        if (!optionsContainer) return;

        const itemElement = document.createElement('a');
        itemElement.href = item.href;
        itemElement.className = 'quick-nav-item';
        itemElement.innerHTML = `
            <span class="nav-icon">${item.icon}</span>
            <span class="nav-text">${item.text}</span>
        `;

        optionsContainer.appendChild(itemElement);
        this.items = this.modal.querySelectorAll('.quick-nav-item');
    }

    /**
     * Check if modal is visible
     * @returns {boolean} True if visible
     */
    isVisible() {
        return this.modal !== null;
    }

    /**
     * Toggle modal visibility
     */
    toggle() {
        if (this.isVisible()) {
            this.hide();
        } else {
            this.show();
        }
    }
}

// Export for use in other modules
window.QuickNavigation = QuickNavigation;
