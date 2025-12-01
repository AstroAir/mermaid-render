/**
 * Message Handler - Handles WebSocket message processing and dispatching
 * @module websocket/MessageHandler
 */

class MessageHandler extends EventEmitter {
    /**
     * Create a MessageHandler instance
     */
    constructor() {
        super();

        this.handlers = new Map();
        this._registerDefaultHandlers();
    }

    /**
     * Register default message handlers
     * @private
     */
    _registerDefaultHandlers() {
        // State synchronization
        this.registerHandler('state_sync', (message) => {
            this.emit('state_sync', message);
        });

        // Element updates
        this.registerHandler('element_updated', (message) => {
            this.emit('element_updated', {
                elementId: message.element_id,
                updates: message.updates,
                timestamp: message.timestamp
            });
        });

        // Connection updates
        this.registerHandler('connection_updated', (message) => {
            this.emit('connection_updated', {
                connectionId: message.connection_id,
                updates: message.updates,
                timestamp: message.timestamp
            });
        });

        // Client updates
        this.registerHandler('client_update', (message) => {
            this.emit('client_update', {
                clientCount: message.client_count
            });
        });

        // Cursor updates
        this.registerHandler('cursor_update', (message) => {
            this.emit('cursor_update', {
                clientId: message.client_id,
                position: message.position,
                timestamp: message.timestamp
            });
        });

        // Selection updates
        this.registerHandler('selection_update', (message) => {
            this.emit('selection_update', {
                clientId: message.client_id,
                selectedElements: message.selected_elements,
                timestamp: message.timestamp
            });
        });

        // Chat messages
        this.registerHandler('chat_message', (message) => {
            this.emit('chat_message', {
                clientId: message.client_id,
                username: message.username,
                message: message.message,
                timestamp: message.timestamp
            });
        });

        // Error messages
        this.registerHandler('error', (message) => {
            this.emit('error', {
                message: message.message,
                originalMessage: message.original_message
            });
        });

        // Ping/Pong for keepalive
        this.registerHandler('ping', (message) => {
            this.emit('pong_required', message);
        });

        this.registerHandler('pong', (message) => {
            this.emit('pong_received', message);
        });
    }

    /**
     * Register a message handler
     * @param {string} type - Message type
     * @param {Function} handler - Handler function
     */
    registerHandler(type, handler) {
        this.handlers.set(type, handler);
    }

    /**
     * Unregister a message handler
     * @param {string} type - Message type
     * @returns {boolean} True if handler was removed
     */
    unregisterHandler(type) {
        return this.handlers.delete(type);
    }

    /**
     * Handle incoming message
     * @param {Object} message - Message object
     * @returns {boolean} True if message was handled
     */
    handle(message) {
        if (!message || typeof message !== 'object') {
            console.warn('Invalid message received:', message);
            return false;
        }

        const type = message.type;
        if (!type) {
            console.warn('Message missing type:', message);
            return false;
        }

        const handler = this.handlers.get(type);
        if (handler) {
            try {
                handler(message);
                return true;
            } catch (error) {
                console.error(`Error handling message type "${type}":`, error);
                this.emit('handler_error', { type, error, message });
                return false;
            }
        } else {
            console.warn('Unknown message type:', type, message);
            this.emit('unknown_message', message);
            return false;
        }
    }

    /**
     * Create outgoing message
     * @param {string} type - Message type
     * @param {Object} data - Message data
     * @param {string} [clientId] - Client ID
     * @returns {Object} Formatted message
     */
    createMessage(type, data, clientId = null) {
        return {
            type,
            ...data,
            client_id: clientId,
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Create element update message
     * @param {string} elementId - Element ID
     * @param {Object} updates - Updates to apply
     * @param {string} clientId - Client ID
     * @returns {Object} Message object
     */
    createElementUpdate(elementId, updates, clientId) {
        return this.createMessage('element_update', {
            element_id: elementId,
            updates
        }, clientId);
    }

    /**
     * Create connection update message
     * @param {string} connectionId - Connection ID
     * @param {Object} updates - Updates to apply
     * @param {string} clientId - Client ID
     * @returns {Object} Message object
     */
    createConnectionUpdate(connectionId, updates, clientId) {
        return this.createMessage('connection_update', {
            connection_id: connectionId,
            updates
        }, clientId);
    }

    /**
     * Create cursor update message
     * @param {Object} position - Cursor position {x, y}
     * @param {string} clientId - Client ID
     * @returns {Object} Message object
     */
    createCursorUpdate(position, clientId) {
        return this.createMessage('cursor_update', {
            position
        }, clientId);
    }

    /**
     * Create selection update message
     * @param {Array} selectedElements - Array of selected element IDs
     * @param {string} clientId - Client ID
     * @returns {Object} Message object
     */
    createSelectionUpdate(selectedElements, clientId) {
        return this.createMessage('selection_update', {
            selected_elements: selectedElements
        }, clientId);
    }

    /**
     * Create chat message
     * @param {string} message - Chat message text
     * @param {string} username - Username
     * @param {string} clientId - Client ID
     * @returns {Object} Message object
     */
    createChatMessage(message, username, clientId) {
        return this.createMessage('chat_message', {
            message,
            username
        }, clientId);
    }

    /**
     * Get all registered handler types
     * @returns {Array} Array of handler types
     */
    getHandlerTypes() {
        return Array.from(this.handlers.keys());
    }

    /**
     * Check if handler exists for type
     * @param {string} type - Message type
     * @returns {boolean} True if handler exists
     */
    hasHandler(type) {
        return this.handlers.has(type);
    }
}

// Export for use in other modules
window.MessageHandler = MessageHandler;
