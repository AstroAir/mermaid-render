// WebSocket client for Mermaid Interactive Builder
// Handles real-time collaboration and synchronization

class WebSocketClient {
    constructor() {
        this.ws = null;
        this.sessionId = null;
        this.clientId = this.generateClientId();
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.messageQueue = [];
        this.eventHandlers = new Map();

        this.initializeConnection();
        this.setupEventHandlers();
    }

    generateClientId() {
        return 'client_' + Math.random().toString(36).substr(2, 9);
    }

    initializeConnection() {
        // Get session ID from URL or generate one
        const urlParams = new URLSearchParams(window.location.search);
        this.sessionId = urlParams.get('session') || this.generateSessionId();

        this.connect();
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    connect() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/${this.sessionId}`;

            this.ws = new WebSocket(wsUrl);
            this.setupWebSocketHandlers();

            console.log('Connecting to WebSocket:', wsUrl);
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.handleConnectionError();
        }
    }

    setupWebSocketHandlers() {
        this.ws.onopen = (event) => {
            console.log('WebSocket connected');
            this.isConnected = true;
            this.reconnectAttempts = 0;

            // Process queued messages
            this.processMessageQueue();

            // Notify connection status
            this.emit('connected', { sessionId: this.sessionId, clientId: this.clientId });
            this.updateConnectionStatus(true);
        };

        this.ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.handleMessage(message);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };

        this.ws.onclose = (event) => {
            console.log('WebSocket disconnected:', event.code, event.reason);
            this.isConnected = false;
            this.updateConnectionStatus(false);

            if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
                this.scheduleReconnect();
            }

            this.emit('disconnected', { code: event.code, reason: event.reason });
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.handleConnectionError();
        };
    }

    handleMessage(message) {
        const { type } = message;

        switch (type) {
            case 'state_sync':
                this.handleStateSync(message);
                break;
            case 'element_updated':
                this.handleElementUpdate(message);
                break;
            case 'connection_updated':
                this.handleConnectionUpdate(message);
                break;
            case 'client_update':
                this.handleClientUpdate(message);
                break;
            case 'cursor_update':
                this.handleCursorUpdate(message);
                break;
            case 'selection_update':
                this.handleSelectionUpdate(message);
                break;
            case 'chat_message':
                this.handleChatMessage(message);
                break;
            case 'error':
                this.handleError(message);
                break;
            default:
                console.warn('Unknown message type:', type, message);
        }

        // Emit generic message event
        this.emit('message', message);
    }

    handleStateSync(message) {
        console.log('Received state sync:', message);

        // Update diagram builder with synchronized state
        if (window.diagramBuilder) {
            window.diagramBuilder.loadFromState(message);
        }

        // Update client count
        this.updateClientCount(message.client_count);

        this.emit('state_sync', message);
    }

    handleElementUpdate(message) {
        console.log('Element updated:', message);

        // Update local diagram builder
        if (window.diagramBuilder) {
            window.diagramBuilder.updateElementFromRemote(message.element_id, message.updates);
        }

        this.emit('element_update', message);
    }

    handleConnectionUpdate(message) {
        console.log('Connection updated:', message);

        // Update local diagram builder
        if (window.diagramBuilder) {
            window.diagramBuilder.updateConnectionFromRemote(message.connection_id, message.updates);
        }

        this.emit('connection_update', message);
    }

    handleClientUpdate(message) {
        console.log('Client update:', message);
        this.updateClientCount(message.client_count);
        this.emit('client_update', message);
    }

    handleCursorUpdate(message) {
        // Only handle cursors from other clients
        if (message.client_id !== this.clientId) {
            this.showRemoteCursor(message.client_id, message.position);
        }

        this.emit('cursor_update', message);
    }

    handleSelectionUpdate(message) {
        // Only handle selections from other clients
        if (message.client_id !== this.clientId) {
            this.showRemoteSelection(message.client_id, message.selected_elements);
        }

        this.emit('selection_update', message);
    }

    handleChatMessage(message) {
        console.log('Chat message:', message);
        this.displayChatMessage(message);
        this.emit('chat_message', message);
    }

    handleError(message) {
        console.error('Server error:', message);
        this.showErrorNotification(message.message);
        this.emit('error', message);
    }

    // Send methods
    sendElementUpdate(elementId, updates) {
        this.send({
            type: 'element_update',
            element_id: elementId,
            updates: updates,
            client_id: this.clientId
        });
    }

    sendConnectionUpdate(connectionId, updates) {
        this.send({
            type: 'connection_update',
            connection_id: connectionId,
            updates: updates,
            client_id: this.clientId
        });
    }

    sendCursorUpdate(position) {
        this.send({
            type: 'cursor_update',
            position: position,
            client_id: this.clientId
        });
    }

    sendSelectionUpdate(selectedElements) {
        this.send({
            type: 'selection_update',
            selected_elements: selectedElements,
            client_id: this.clientId
        });
    }

    sendChatMessage(message, username = 'Anonymous') {
        this.send({
            type: 'chat_message',
            message: message,
            username: username,
            client_id: this.clientId
        });
    }

    send(message) {
        if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            // Queue message for later
            this.messageQueue.push(message);
            console.warn('WebSocket not connected, message queued:', message);
        }
    }

    processMessageQueue() {
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            this.send(message);
        }
    }

    scheduleReconnect() {
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

        console.log(`Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);

        setTimeout(() => {
            if (!this.isConnected) {
                this.connect();
            }
        }, delay);
    }

    handleConnectionError() {
        this.isConnected = false;
        this.updateConnectionStatus(false);
        this.emit('error', { message: 'Connection error' });
    }

    // UI update methods
    updateConnectionStatus(connected) {
        const statusElement = document.querySelector('.collaboration-status');
        if (statusElement) {
            if (connected) {
                statusElement.style.color = '#28a745';
                statusElement.innerHTML = '<span id="client-count">1</span> user(s) online';
            } else {
                statusElement.style.color = '#dc3545';
                statusElement.innerHTML = 'Disconnected - Reconnecting...';
            }
        }
    }

    updateClientCount(count) {
        const clientCountElement = document.getElementById('client-count');
        if (clientCountElement) {
            clientCountElement.textContent = count;
        }
    }

    showRemoteCursor(clientId, position) {
        // Implementation for showing remote user cursors
        // This would create/update cursor indicators on the canvas
        console.log(`Remote cursor from ${clientId}:`, position);
    }

    showRemoteSelection(clientId, selectedElements) {
        // Implementation for showing remote user selections
        // This would highlight elements selected by other users
        console.log(`Remote selection from ${clientId}:`, selectedElements);
    }

    displayChatMessage(message) {
        // Implementation for displaying chat messages
        // This would add messages to a chat panel if it exists
        console.log(`Chat from ${message.username}: ${message.message}`);
    }

    showErrorNotification(message) {
        if (window.MermaidInteractive && window.MermaidInteractive.showNotification) {
            window.MermaidInteractive.showNotification(message, 'error');
        } else {
            console.error('Error:', message);
        }
    }

    // Event system
    on(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event).push(handler);
    }

    off(event, handler) {
        if (this.eventHandlers.has(event)) {
            const handlers = this.eventHandlers.get(event);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }

    emit(event, data) {
        if (this.eventHandlers.has(event)) {
            this.eventHandlers.get(event).forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Error in event handler for ${event}:`, error);
                }
            });
        }
    }

    setupEventHandlers() {
        // Set up mouse tracking for cursor sharing
        let cursorThrottle = null;
        document.addEventListener('mousemove', (e) => {
            if (cursorThrottle) return;

            cursorThrottle = setTimeout(() => {
                const canvas = document.getElementById('diagram-canvas');
                if (canvas) {
                    const rect = canvas.getBoundingClientRect();
                    const position = {
                        x: e.clientX - rect.left,
                        y: e.clientY - rect.top
                    };
                    this.sendCursorUpdate(position);
                }
                cursorThrottle = null;
            }, 100); // Throttle to 10fps
        });
    }

    // Cleanup
    disconnect() {
        if (this.ws) {
            this.ws.close(1000, 'Client disconnecting');
        }
        this.isConnected = false;
    }
}

// Initialize WebSocket client when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('diagram-canvas')) {
        window.wsClient = new WebSocketClient();

        // Integrate with diagram builder if it exists
        if (window.diagramBuilder) {
            // Set up integration between WebSocket and diagram builder
            window.wsClient.on('state_sync', (data) => {
                window.diagramBuilder.syncWithRemoteState(data);
            });
        }
    }
});

// Export for use in other modules
window.WebSocketClient = WebSocketClient;
