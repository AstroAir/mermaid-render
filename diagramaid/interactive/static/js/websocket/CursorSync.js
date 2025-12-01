/**
 * Cursor Sync - Handles cursor synchronization for collaborative editing
 * @module websocket/CursorSync
 */

class CursorSync {
    /**
     * Create a CursorSync instance
     * @param {Object} [options] - Options
     * @param {number} [options.throttleMs=100] - Throttle interval in ms
     * @param {number} [options.cursorTimeout=5000] - Cursor timeout in ms
     */
    constructor(options = {}) {
        this.throttleMs = options.throttleMs || 100;
        this.cursorTimeout = options.cursorTimeout || 5000;

        this.localClientId = null;
        this.remoteCursors = new Map();
        this.cursorElements = new Map();
        this.cursorTimeouts = new Map();

        this.throttleTimer = null;
        this.lastPosition = null;

        this.onCursorUpdateCallback = null;
        this.container = null;

        this._addStyles();
    }

    /**
     * Add cursor styles
     * @private
     */
    _addStyles() {
        if (document.getElementById('cursor-sync-styles')) return;

        const style = document.createElement('style');
        style.id = 'cursor-sync-styles';
        style.textContent = `
            .remote-cursor {
                position: absolute;
                pointer-events: none;
                z-index: 1000;
                transition: transform 0.1s ease-out;
            }

            .remote-cursor-pointer {
                width: 0;
                height: 0;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-bottom: 12px solid var(--cursor-color, #667eea);
                transform: rotate(-45deg);
            }

            .remote-cursor-label {
                position: absolute;
                top: 12px;
                left: 8px;
                background: var(--cursor-color, #667eea);
                color: white;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 11px;
                font-weight: 500;
                white-space: nowrap;
            }

            .remote-cursor.fading {
                opacity: 0.5;
                transition: opacity 1s ease;
            }

            .remote-cursor.hidden {
                display: none;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Initialize cursor sync
     * @param {string} clientId - Local client ID
     * @param {HTMLElement} container - Container element for cursors
     */
    initialize(clientId, container) {
        this.localClientId = clientId;
        this.container = container;

        this._setupMouseTracking();
    }

    /**
     * Setup mouse tracking
     * @private
     */
    _setupMouseTracking() {
        if (!this.container) return;

        this.container.addEventListener('mousemove', (e) => {
            this._handleMouseMove(e);
        });

        this.container.addEventListener('mouseleave', () => {
            this._handleMouseLeave();
        });
    }

    /**
     * Handle mouse move
     * @param {MouseEvent} e - Mouse event
     * @private
     */
    _handleMouseMove(e) {
        if (this.throttleTimer) return;

        this.throttleTimer = setTimeout(() => {
            const rect = this.container.getBoundingClientRect();
            const position = {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            };

            this.lastPosition = position;

            if (this.onCursorUpdateCallback) {
                this.onCursorUpdateCallback(position);
            }

            this.throttleTimer = null;
        }, this.throttleMs);
    }

    /**
     * Handle mouse leave
     * @private
     */
    _handleMouseLeave() {
        this.lastPosition = null;

        if (this.onCursorUpdateCallback) {
            this.onCursorUpdateCallback(null);
        }
    }

    /**
     * Set cursor update callback
     * @param {Function} callback - Callback function (position) => void
     */
    onCursorUpdate(callback) {
        this.onCursorUpdateCallback = callback;
    }

    /**
     * Update remote cursor position
     * @param {string} clientId - Remote client ID
     * @param {Object} position - Cursor position {x, y}
     * @param {string} [username] - Username for label
     */
    updateRemoteCursor(clientId, position, username = null) {
        if (clientId === this.localClientId) return;

        // Clear existing timeout
        if (this.cursorTimeouts.has(clientId)) {
            clearTimeout(this.cursorTimeouts.get(clientId));
        }

        if (!position) {
            // Hide cursor
            this._hideCursor(clientId);
            return;
        }

        // Update or create cursor element
        let cursorEl = this.cursorElements.get(clientId);
        if (!cursorEl) {
            cursorEl = this._createCursorElement(clientId, username);
            this.cursorElements.set(clientId, cursorEl);
        }

        // Update position
        cursorEl.style.transform = `translate(${position.x}px, ${position.y}px)`;
        cursorEl.classList.remove('fading', 'hidden');

        // Store position
        this.remoteCursors.set(clientId, {
            position,
            username,
            lastUpdate: Date.now()
        });

        // Set timeout to fade cursor
        const timeout = setTimeout(() => {
            this._fadeCursor(clientId);
        }, this.cursorTimeout);
        this.cursorTimeouts.set(clientId, timeout);
    }

    /**
     * Create cursor element
     * @param {string} clientId - Client ID
     * @param {string} [username] - Username
     * @returns {HTMLElement} Cursor element
     * @private
     */
    _createCursorElement(clientId, username) {
        const cursor = document.createElement('div');
        cursor.className = 'remote-cursor';
        cursor.dataset.clientId = clientId;

        // Generate color from client ID
        const color = this._generateColor(clientId);
        cursor.style.setProperty('--cursor-color', color);

        cursor.innerHTML = `
            <div class="remote-cursor-pointer"></div>
            <div class="remote-cursor-label">${username || clientId.substring(0, 8)}</div>
        `;

        if (this.container) {
            this.container.appendChild(cursor);
        }

        return cursor;
    }

    /**
     * Generate color from string
     * @param {string} str - Input string
     * @returns {string} HSL color
     * @private
     */
    _generateColor(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = str.charCodeAt(i) + ((hash << 5) - hash);
        }
        const hue = hash % 360;
        return `hsl(${hue}, 70%, 50%)`;
    }

    /**
     * Fade cursor
     * @param {string} clientId - Client ID
     * @private
     */
    _fadeCursor(clientId) {
        const cursorEl = this.cursorElements.get(clientId);
        if (cursorEl) {
            cursorEl.classList.add('fading');
        }
    }

    /**
     * Hide cursor
     * @param {string} clientId - Client ID
     * @private
     */
    _hideCursor(clientId) {
        const cursorEl = this.cursorElements.get(clientId);
        if (cursorEl) {
            cursorEl.classList.add('hidden');
        }
    }

    /**
     * Remove cursor
     * @param {string} clientId - Client ID
     */
    removeCursor(clientId) {
        // Clear timeout
        if (this.cursorTimeouts.has(clientId)) {
            clearTimeout(this.cursorTimeouts.get(clientId));
            this.cursorTimeouts.delete(clientId);
        }

        // Remove element
        const cursorEl = this.cursorElements.get(clientId);
        if (cursorEl && cursorEl.parentNode) {
            cursorEl.parentNode.removeChild(cursorEl);
        }
        this.cursorElements.delete(clientId);

        // Remove data
        this.remoteCursors.delete(clientId);
    }

    /**
     * Remove all remote cursors
     */
    removeAllCursors() {
        const clientIds = Array.from(this.cursorElements.keys());
        clientIds.forEach(clientId => {
            this.removeCursor(clientId);
        });
    }

    /**
     * Get all remote cursor positions
     * @returns {Map} Map of client ID to cursor data
     */
    getRemoteCursors() {
        return new Map(this.remoteCursors);
    }

    /**
     * Get cursor count
     * @returns {number} Number of remote cursors
     */
    getCursorCount() {
        return this.remoteCursors.size;
    }

    /**
     * Update username for cursor
     * @param {string} clientId - Client ID
     * @param {string} username - New username
     */
    updateUsername(clientId, username) {
        const cursorEl = this.cursorElements.get(clientId);
        if (cursorEl) {
            const label = cursorEl.querySelector('.remote-cursor-label');
            if (label) {
                label.textContent = username;
            }
        }

        const cursorData = this.remoteCursors.get(clientId);
        if (cursorData) {
            cursorData.username = username;
        }
    }

    /**
     * Set throttle interval
     * @param {number} ms - Throttle interval in ms
     */
    setThrottle(ms) {
        this.throttleMs = ms;
    }

    /**
     * Set cursor timeout
     * @param {number} ms - Timeout in ms
     */
    setCursorTimeout(ms) {
        this.cursorTimeout = ms;
    }

    /**
     * Get last local cursor position
     * @returns {Object|null} Last position
     */
    getLastPosition() {
        return this.lastPosition;
    }

    /**
     * Cleanup
     */
    destroy() {
        this.removeAllCursors();

        if (this.throttleTimer) {
            clearTimeout(this.throttleTimer);
        }

        this.onCursorUpdateCallback = null;
    }
}

// Export for use in other modules
window.CursorSync = CursorSync;
