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
        // TODO: Implement remote selection visualization
        console.log(`Remote selection from ${clientId}:`, selectedElements);
    }

    /**
     * Display chat message
     * @param {Object} data - Chat message data
     * @private
     */
    _displayChatMessage(data) {
        // TODO: Implement chat panel
        console.log(`Chat from ${data.username}: ${data.message}`);
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
