/**
 * WebSocket Client - Main WebSocket client for real-time collaboration
 * @module WebSocketClient
 */

class WebSocketClient {
    /**
     * Create a WebSocketClient instance
     */
    constructor() {
        this.sessionId = null;
        this.clientId = this._generateClientId();

        // Initialize sub-modules
        this.connection = new WebSocketConnection({
            maxReconnectAttempts: 5,
            reconnectDelay: 1000
        });

        this.messageHandler = new MessageHandler();
        this.cursorSync = new CursorSync({
            throttleMs: 100,
            cursorTimeout: 5000
        });

        // Remote selection tracking
        this._remoteSelections = new Map(); // clientId -> { elements: [], color: string }
        this._selectionColors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
            '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
        ];
        this._colorIndex = 0;

        // Chat panel state
        this._chatMessages = [];
        this._maxChatMessages = 100;

        // Setup handlers
        this._setupConnectionHandlers();
        this._setupMessageHandlers();
        this._setupCursorSync();

        // Initialize connection
        this._initializeConnection();
    }

    /**
     * Generate unique client ID
     * @returns {string} Client ID
     * @private
     */
    _generateClientId() {
        return 'client_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Generate session ID
     * @returns {string} Session ID
     * @private
     */
    _generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Initialize WebSocket connection
     * @private
     */
    _initializeConnection() {
        // Get session ID from URL or generate one
        const urlParams = new URLSearchParams(window.location.search);
        this.sessionId = urlParams.get('session') || this._generateSessionId();

        this._connect();
    }

    /**
     * Connect to WebSocket server
     * @private
     */
    async _connect() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/${this.sessionId}`;

            console.log('Connecting to WebSocket:', wsUrl);
            await this.connection.connect(wsUrl);
        } catch (error) {
            console.error('Failed to connect to WebSocket:', error);
        }
    }

    /**
     * Setup connection event handlers
     * @private
     */
    _setupConnectionHandlers() {
        this.connection.on('open', () => {
            console.log('WebSocket connected');
            this._updateConnectionStatus(true);
            this.emit('connected', {
                sessionId: this.sessionId,
                clientId: this.clientId
            });
        });

        this.connection.on('close', (data) => {
            console.log('WebSocket disconnected:', data.code, data.reason);
            this._updateConnectionStatus(false);
            this.emit('disconnected', data);
        });

        this.connection.on('error', (error) => {
            console.error('WebSocket error:', error);
            this._showErrorNotification('Connection error');
        });

        this.connection.on('message', (data) => {
            this.messageHandler.handle(data);
        });

        this.connection.on('reconnecting', (data) => {
            console.log(`Reconnecting attempt ${data.attempt} in ${data.delay}ms`);
            this._updateConnectionStatus(false, `Reconnecting (${data.attempt})...`);
        });

        this.connection.on('reconnected', (data) => {
            console.log('Reconnected after', data.attempts, 'attempts');
            this._updateConnectionStatus(true);

            if (window.notificationManager) {
                window.notificationManager.success('Reconnected to server');
            }
        });

        this.connection.on('reconnect_failed', (data) => {
            console.error('Failed to reconnect after', data.attempts, 'attempts');
            this._showErrorNotification('Failed to reconnect to server');
        });
    }

    /**
     * Setup message handlers
     * @private
     */
    _setupMessageHandlers() {
        // State sync
        this.messageHandler.on('state_sync', (data) => {
            console.log('Received state sync:', data);

            if (window.diagramBuilder) {
                window.diagramBuilder.loadFromState(data);
            }

            this._updateClientCount(data.client_count);
            this.emit('state_sync', data);
        });

        // Element updates
        this.messageHandler.on('element_updated', (data) => {
            console.log('Element updated:', data);

            if (window.diagramBuilder) {
                window.diagramBuilder.updateElementFromRemote(data.elementId, data.updates);
            }

            this.emit('element_update', data);
        });

        // Connection updates
        this.messageHandler.on('connection_updated', (data) => {
            console.log('Connection updated:', data);

            if (window.diagramBuilder) {
                window.diagramBuilder.updateConnectionFromRemote(data.connectionId, data.updates);
            }

            this.emit('connection_update', data);
        });

        // Client updates
        this.messageHandler.on('client_update', (data) => {
            console.log('Client update:', data);
            this._updateClientCount(data.clientCount);
            this.emit('client_update', data);
        });

        // Cursor updates
        this.messageHandler.on('cursor_update', (data) => {
            if (data.clientId !== this.clientId) {
                this.cursorSync.updateRemoteCursor(data.clientId, data.position);
            }
            this.emit('cursor_update', data);
        });

        // Selection updates
        this.messageHandler.on('selection_update', (data) => {
            if (data.clientId !== this.clientId) {
                this._showRemoteSelection(data.clientId, data.selectedElements);
            }
            this.emit('selection_update', data);
        });

        // Chat messages
        this.messageHandler.on('chat_message', (data) => {
            console.log(`Chat from ${data.username}: ${data.message}`);
            this._displayChatMessage(data);
            this.emit('chat_message', data);
        });

        // Errors
        this.messageHandler.on('error', (data) => {
            console.error('Server error:', data);
            this._showErrorNotification(data.message);
            this.emit('error', data);
        });

        // Pong required
        this.messageHandler.on('pong_required', () => {
            this.connection.send({ type: 'pong', client_id: this.clientId });
        });
    }

    /**
     * Setup cursor synchronization
     * @private
     */
    _setupCursorSync() {
        const canvas = document.getElementById('diagram-canvas');
        if (canvas) {
            this.cursorSync.initialize(this.clientId, canvas);

            this.cursorSync.onCursorUpdate((position) => {
                if (position) {
                    this.sendCursorUpdate(position);
                }
            });
        }
    }

    /**
     * Send element update
     * @param {string} elementId - Element ID
     * @param {Object} updates - Updates to send
     */
    sendElementUpdate(elementId, updates) {
        const message = this.messageHandler.createElementUpdate(elementId, updates, this.clientId);
        this.connection.send(message);
    }

    /**
     * Send connection update
     * @param {string} connectionId - Connection ID
     * @param {Object} updates - Updates to send
     */
    sendConnectionUpdate(connectionId, updates) {
        const message = this.messageHandler.createConnectionUpdate(connectionId, updates, this.clientId);
        this.connection.send(message);
    }

    /**
     * Send cursor update
     * @param {Object} position - Cursor position
     */
    sendCursorUpdate(position) {
        const message = this.messageHandler.createCursorUpdate(position, this.clientId);
        this.connection.send(message);
    }

    /**
     * Send selection update
     * @param {Array} selectedElements - Selected element IDs
     */
    sendSelectionUpdate(selectedElements) {
        const message = this.messageHandler.createSelectionUpdate(selectedElements, this.clientId);
        this.connection.send(message);
    }

    /**
     * Send chat message
     * @param {string} message - Chat message
     * @param {string} [username='Anonymous'] - Username
     */
    sendChatMessage(message, username = 'Anonymous') {
        const msg = this.messageHandler.createChatMessage(message, username, this.clientId);
        this.connection.send(msg);
    }

    /**
     * Update connection status UI
     * @param {boolean} connected - Connection status
     * @param {string} [message] - Status message
     * @private
     */
    _updateConnectionStatus(connected, message = null) {
        const statusElement = document.querySelector('.collaboration-status');
        if (statusElement) {
            if (connected) {
                statusElement.style.color = '#28a745';
                statusElement.innerHTML = '<span id="client-count">1</span> user(s) online';
            } else {
                statusElement.style.color = '#dc3545';
                statusElement.innerHTML = message || 'Disconnected - Reconnecting...';
            }
        }
    }

    /**
     * Update client count UI
     * @param {number} count - Client count
     * @private
     */
    _updateClientCount(count) {
        const clientCountElement = document.getElementById('client-count');
        if (clientCountElement) {
            clientCountElement.textContent = count;
        }
    }

    /**
     * Show remote selection
     * @param {string} clientId - Client ID
     * @param {Array} selectedElements - Selected element IDs
     * @private
     */
    _showRemoteSelection(clientId, selectedElements) {
        // Get or assign a color for this client
        let selectionInfo = this._remoteSelections.get(clientId);
        if (!selectionInfo) {
            selectionInfo = {
                elements: [],
                color: this._selectionColors[this._colorIndex % this._selectionColors.length]
            };
            this._colorIndex++;
            this._remoteSelections.set(clientId, selectionInfo);
        }

        // Clear previous selection highlights for this client
        this._clearRemoteSelectionHighlights(clientId);

        // Update selection info
        selectionInfo.elements = selectedElements || [];

        // Apply new selection highlights
        selectionInfo.elements.forEach(elementId => {
            this._highlightElement(elementId, selectionInfo.color, clientId);
        });

        // Update collaboration panel if it exists
        this._updateCollaborationPanel();
    }

    /**
     * Clear remote selection highlights for a specific client
     * @param {string} clientId - Client ID
     * @private
     */
    _clearRemoteSelectionHighlights(clientId) {
        const highlights = document.querySelectorAll(`[data-remote-selection="${clientId}"]`);
        highlights.forEach(highlight => {
            highlight.remove();
        });
    }

    /**
     * Highlight an element with remote selection indicator
     * @param {string} elementId - Element ID to highlight
     * @param {string} color - Highlight color
     * @param {string} clientId - Client ID for tracking
     * @private
     */
    _highlightElement(elementId, color, clientId) {
        const element = document.querySelector(`[data-id="${elementId}"]`);
        if (!element) return;

        // Create highlight overlay
        const highlight = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        const bbox = element.getBBox ? element.getBBox() : element.getBoundingClientRect();

        highlight.setAttribute('x', (bbox.x || 0) - 4);
        highlight.setAttribute('y', (bbox.y || 0) - 4);
        highlight.setAttribute('width', (bbox.width || 120) + 8);
        highlight.setAttribute('height', (bbox.height || 60) + 8);
        highlight.setAttribute('fill', 'none');
        highlight.setAttribute('stroke', color);
        highlight.setAttribute('stroke-width', '3');
        highlight.setAttribute('stroke-dasharray', '5,5');
        highlight.setAttribute('rx', '4');
        highlight.setAttribute('ry', '4');
        highlight.setAttribute('data-remote-selection', clientId);
        highlight.setAttribute('class', 'remote-selection-highlight');
        highlight.style.pointerEvents = 'none';
        highlight.style.animation = 'pulse-selection 1.5s ease-in-out infinite';

        // Add to canvas
        const canvasGroup = document.getElementById('canvas-group');
        if (canvasGroup) {
            canvasGroup.appendChild(highlight);
        }

        // Add client label
        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', (bbox.x || 0) - 4);
        label.setAttribute('y', (bbox.y || 0) - 8);
        label.setAttribute('fill', color);
        label.setAttribute('font-size', '10');
        label.setAttribute('font-weight', 'bold');
        label.setAttribute('data-remote-selection', clientId);
        label.textContent = clientId.substring(0, 8);
        label.style.pointerEvents = 'none';

        if (canvasGroup) {
            canvasGroup.appendChild(label);
        }
    }

    /**
     * Update collaboration panel with current remote users
     * @private
     */
    _updateCollaborationPanel() {
        const panel = document.getElementById('collaboration-users');
        if (!panel) return;

        panel.innerHTML = '';

        this._remoteSelections.forEach((info, clientId) => {
            const userItem = document.createElement('div');
            userItem.className = 'collaboration-user';
            userItem.innerHTML = `
                <span class="user-indicator" style="background-color: ${info.color}"></span>
                <span class="user-name">${clientId.substring(0, 8)}</span>
                <span class="user-selection">${info.elements.length} selected</span>
            `;
            panel.appendChild(userItem);
        });
    }

    /**
     * Display chat message
     * @param {Object} data - Chat message data
     * @private
     */
    _displayChatMessage(data) {
        // Store message
        this._chatMessages.push({
            ...data,
            timestamp: Date.now()
        });

        // Limit stored messages
        if (this._chatMessages.length > this._maxChatMessages) {
            this._chatMessages.shift();
        }

        // Get or create chat panel
        let chatPanel = document.getElementById('chat-panel');
        if (!chatPanel) {
            chatPanel = this._createChatPanel();
        }

        // Add message to chat
        const messagesContainer = chatPanel.querySelector('.chat-messages');
        if (messagesContainer) {
            const messageElement = this._createChatMessageElement(data);
            messagesContainer.appendChild(messageElement);

            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        // Show notification if chat panel is collapsed
        if (chatPanel.classList.contains('collapsed')) {
            this._showChatNotification(data);
        }
    }

    /**
     * Create chat panel element
     * @returns {HTMLElement} Chat panel element
     * @private
     */
    _createChatPanel() {
        const panel = document.createElement('div');
        panel.id = 'chat-panel';
        panel.className = 'chat-panel';
        panel.innerHTML = `
            <div class="chat-header">
                <span class="chat-title">Chat</span>
                <button class="chat-toggle" onclick="this.parentElement.parentElement.classList.toggle('collapsed')">
                    <span class="toggle-icon">−</span>
                </button>
            </div>
            <div class="chat-messages"></div>
            <div class="chat-input-container">
                <input type="text" class="chat-input" placeholder="Type a message..." />
                <button class="chat-send" onclick="window.wsClient && window.wsClient._sendChatFromInput()">
                    Send
                </button>
            </div>
        `;

        // Add enter key handler for input
        const input = panel.querySelector('.chat-input');
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this._sendChatFromInput();
                }
            });
        }

        // Add styles if not already present
        this._addChatStyles();

        // Append to body
        document.body.appendChild(panel);

        return panel;
    }

    /**
     * Create chat message element
     * @param {Object} data - Message data
     * @returns {HTMLElement} Message element
     * @private
     */
    _createChatMessageElement(data) {
        const messageEl = document.createElement('div');
        messageEl.className = 'chat-message';

        const isOwnMessage = data.clientId === this.clientId;
        if (isOwnMessage) {
            messageEl.classList.add('own-message');
        }

        const time = new Date(data.timestamp || Date.now()).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });

        messageEl.innerHTML = `
            <div class="message-header">
                <span class="message-username">${this._escapeHtml(data.username || 'Anonymous')}</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-content">${this._escapeHtml(data.message)}</div>
        `;

        return messageEl;
    }

    /**
     * Send chat message from input field
     * @private
     */
    _sendChatFromInput() {
        const input = document.querySelector('#chat-panel .chat-input');
        if (!input || !input.value.trim()) return;

        const message = input.value.trim();
        const username = localStorage.getItem('chat_username') || 'Anonymous';

        this.sendChatMessage(message, username);

        // Also display locally
        this._displayChatMessage({
            message,
            username,
            clientId: this.clientId,
            timestamp: Date.now()
        });

        input.value = '';
    }

    /**
     * Show chat notification
     * @param {Object} data - Message data
     * @private
     */
    _showChatNotification(data) {
        if (window.notificationManager) {
            window.notificationManager.info(
                `${data.username || 'Anonymous'}: ${data.message.substring(0, 50)}${data.message.length > 50 ? '...' : ''}`
            );
        }
    }

    /**
     * Add chat panel styles
     * @private
     */
    _addChatStyles() {
        if (document.getElementById('chat-panel-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'chat-panel-styles';
        styles.textContent = `
            .chat-panel {
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 300px;
                max-height: 400px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                display: flex;
                flex-direction: column;
                z-index: 1000;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            .chat-panel.collapsed {
                max-height: 40px;
                overflow: hidden;
            }
            .chat-panel.collapsed .chat-messages,
            .chat-panel.collapsed .chat-input-container {
                display: none;
            }
            .chat-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 15px;
                background: #4a90d9;
                color: white;
                border-radius: 8px 8px 0 0;
                cursor: pointer;
            }
            .chat-title {
                font-weight: 600;
            }
            .chat-toggle {
                background: none;
                border: none;
                color: white;
                font-size: 18px;
                cursor: pointer;
                padding: 0 5px;
            }
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 10px;
                max-height: 280px;
            }
            .chat-message {
                margin-bottom: 10px;
                padding: 8px 12px;
                background: #f0f0f0;
                border-radius: 8px;
            }
            .chat-message.own-message {
                background: #e3f2fd;
            }
            .message-header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 4px;
                font-size: 11px;
            }
            .message-username {
                font-weight: 600;
                color: #333;
            }
            .message-time {
                color: #888;
            }
            .message-content {
                font-size: 13px;
                color: #333;
                word-wrap: break-word;
            }
            .chat-input-container {
                display: flex;
                padding: 10px;
                border-top: 1px solid #eee;
            }
            .chat-input {
                flex: 1;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 20px;
                outline: none;
                font-size: 13px;
            }
            .chat-input:focus {
                border-color: #4a90d9;
            }
            .chat-send {
                margin-left: 8px;
                padding: 8px 16px;
                background: #4a90d9;
                color: white;
                border: none;
                border-radius: 20px;
                cursor: pointer;
                font-size: 13px;
            }
            .chat-send:hover {
                background: #357abd;
            }
            .remote-selection-highlight {
                pointer-events: none;
            }
            @keyframes pulse-selection {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            .collaboration-user {
                display: flex;
                align-items: center;
                padding: 5px 10px;
                font-size: 12px;
            }
            .user-indicator {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 8px;
            }
            .user-name {
                flex: 1;
                font-weight: 500;
            }
            .user-selection {
                color: #888;
                font-size: 11px;
            }
        `;
        document.head.appendChild(styles);
    }

    /**
     * Escape HTML special characters
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     * @private
     */
    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Show error notification
     * @param {string} message - Error message
     * @private
     */
    _showErrorNotification(message) {
        if (window.notificationManager) {
            window.notificationManager.error(message);
        } else {
            console.error('Error:', message);
        }
    }

    /**
     * Disconnect from server
     */
    disconnect() {
        this.cursorSync.destroy();
        this.connection.disconnect();
    }

    /**
     * Get session ID
     * @returns {string} Session ID
     */
    getSessionId() {
        return this.sessionId;
    }

    /**
     * Get client ID
     * @returns {string} Client ID
     */
    getClientId() {
        return this.clientId;
    }

    /**
     * Check if connected
     * @returns {boolean} Connection status
     */
    isConnected() {
        return this.connection.isOpen();
    }

    /**
     * Get connection info
     * @returns {Object} Connection info
     */
    getConnectionInfo() {
        return {
            sessionId: this.sessionId,
            clientId: this.clientId,
            ...this.connection.getInfo()
        };
    }

    // Event emitter methods (delegate to connection)
    on(event, handler) {
        this.connection.on(event, handler);
    }

    off(event, handler) {
        this.connection.off(event, handler);
    }

    emit(event, data) {
        this.connection.emit(event, data);
    }
}

// Initialize WebSocket client when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('diagram-canvas')) {
        window.wsClient = new WebSocketClient();

        // Integrate with diagram builder if it exists
        if (window.diagramBuilder) {
            window.wsClient.on('state_sync', (data) => {
                window.diagramBuilder.syncWithRemoteState(data);
            });
        }
    }
});

// Export for use in other modules
window.WebSocketClient = WebSocketClient;
