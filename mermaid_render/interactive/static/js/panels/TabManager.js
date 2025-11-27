/**
 * Tab Manager - Handles bottom panel tab switching
 * @module panels/TabManager
 */

class TabManager {
    /**
     * Create a TabManager instance
     */
    constructor() {
        this.currentTab = 'code';
        this.tabs = new Map();
        this.onTabChangeCallbacks = [];

        this._initializeTabs();
        this._initializeEventListeners();
    }

    /**
     * Initialize tabs configuration
     * @private
     */
    _initializeTabs() {
        this.tabs.set('code', {
            id: 'code',
            name: 'Code',
            paneId: 'code-tab'
        });
        this.tabs.set('preview', {
            id: 'preview',
            name: 'Preview',
            paneId: 'preview-tab'
        });
        this.tabs.set('validation', {
            id: 'validation',
            name: 'Validation',
            paneId: 'validation-tab'
        });
    }

    /**
     * Initialize event listeners for tab buttons
     * @private
     */
    _initializeEventListeners() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.dataset.tab || e.target.closest('.tab-btn')?.dataset.tab;
                if (tab) {
                    this.switchTab(tab);
                }
            });
        });
    }

    /**
     * Switch to a specific tab
     * @param {string} tabName - The tab ID to switch to
     */
    switchTab(tabName) {
        if (!this.tabs.has(tabName)) {
            console.warn(`Tab "${tabName}" not found`);
            return;
        }

        const previousTab = this.currentTab;
        this.currentTab = tabName;

        // Update tab button states
        this._updateTabButtonStates();

        // Update tab pane visibility
        this._updateTabPaneVisibility();

        // Notify callbacks
        this.onTabChangeCallbacks.forEach(callback => {
            callback(tabName, previousTab);
        });
    }

    /**
     * Update visual state of tab buttons
     * @private
     */
    _updateTabButtonStates() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        const activeBtn = document.querySelector(`[data-tab="${this.currentTab}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
    }

    /**
     * Update tab pane visibility
     * @private
     */
    _updateTabPaneVisibility() {
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });

        const tab = this.tabs.get(this.currentTab);
        if (tab) {
            const pane = document.getElementById(tab.paneId);
            if (pane) {
                pane.classList.add('active');
            }
        }
    }

    /**
     * Get the current active tab
     * @returns {string} Current tab ID
     */
    getCurrentTab() {
        return this.currentTab;
    }

    /**
     * Get tab configuration by ID
     * @param {string} tabId - The tab ID
     * @returns {Object|undefined} Tab configuration
     */
    getTab(tabId) {
        return this.tabs.get(tabId);
    }

    /**
     * Register callback for tab change events
     * @param {Function} callback - Callback function (newTab, previousTab) => void
     */
    onTabChange(callback) {
        this.onTabChangeCallbacks.push(callback);
    }

    /**
     * Remove tab change callback
     * @param {Function} callback - The callback to remove
     */
    offTabChange(callback) {
        const index = this.onTabChangeCallbacks.indexOf(callback);
        if (index > -1) {
            this.onTabChangeCallbacks.splice(index, 1);
        }
    }

    /**
     * Register a custom tab
     * @param {Object} tab - Tab configuration
     * @param {string} tab.id - Unique tab ID
     * @param {string} tab.name - Display name
     * @param {string} tab.paneId - ID of the tab pane element
     */
    registerTab(tab) {
        this.tabs.set(tab.id, tab);
    }

    /**
     * Unregister a tab
     * @param {string} tabId - The tab ID to remove
     * @returns {boolean} True if tab was removed
     */
    unregisterTab(tabId) {
        if (this.currentTab === tabId) {
            // Switch to first available tab
            const firstTab = this.tabs.keys().next().value;
            if (firstTab && firstTab !== tabId) {
                this.switchTab(firstTab);
            }
        }
        return this.tabs.delete(tabId);
    }

    /**
     * Get all registered tabs
     * @returns {Array} Array of all tabs
     */
    getAllTabs() {
        return Array.from(this.tabs.values());
    }

    /**
     * Check if a tab is currently active
     * @param {string} tabId - The tab ID to check
     * @returns {boolean} True if tab is active
     */
    isActive(tabId) {
        return this.currentTab === tabId;
    }

    /**
     * Enable or disable a tab
     * @param {string} tabId - The tab ID
     * @param {boolean} enabled - Whether to enable or disable
     */
    setTabEnabled(tabId, enabled) {
        const btn = document.querySelector(`[data-tab="${tabId}"]`);
        if (btn) {
            btn.disabled = !enabled;
            btn.classList.toggle('disabled', !enabled);
        }
    }

    /**
     * Set tab badge/notification
     * @param {string} tabId - The tab ID
     * @param {string|number|null} badge - Badge content (null to remove)
     */
    setTabBadge(tabId, badge) {
        const btn = document.querySelector(`[data-tab="${tabId}"]`);
        if (!btn) return;

        // Remove existing badge
        const existingBadge = btn.querySelector('.tab-badge');
        if (existingBadge) {
            existingBadge.remove();
        }

        // Add new badge if provided
        if (badge !== null && badge !== undefined) {
            const badgeEl = document.createElement('span');
            badgeEl.className = 'tab-badge';
            badgeEl.textContent = badge;
            btn.appendChild(badgeEl);
        }
    }
}

// Export for use in other modules
window.TabManager = TabManager;
