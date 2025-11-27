/**
 * WebSocket Connection - Handles WebSocket connection management and reconnection
 * @module websocket/WebSocketConnection
 */

class WebSocketConnection extends EventEmitter {
    /**
     * Create a WebSocketConnection instance
     * @param {Object} [options] - Connection options
     * @param {number} [options.maxReconnectAttempts=5] - Maximum reconnection attempts
     * @param {number} [options.reconnectDelay=1000] - Initial reconnect delay in ms
     * @param {number} [options.maxReconnectDelay=30000] - Maximum reconnect delay in ms
     */
    constructor(options = {}) {
        super();

        this.ws = null;
        this.url = null;
        this.isConnected = false;
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = options.maxReconnectAttempts || 5;
        this.reconnectDelay = options.reconnectDelay || 1000;
        this.maxReconnectDelay = options.maxReconnectDelay || 30000;
        this.messageQueue = [];
        this.reconnectTimer = null;
    }

    /**
     * Connect to WebSocket server
     * @param {string} url - WebSocket URL
     * @returns {Promise<void>}
     */
    connect(url) {
        return new Promise((resolve, reject) => {
            if (this.isConnected || this.isConnecting) {
                resolve();
                return;
            }

            this.url = url;
            this.isConnecting = true;

            try {
                this.ws = new WebSocket(url);
                this._setupEventHandlers(resolve, reject);
            } catch (error) {
                this.isConnecting = false;
                reject(error);
            }
        });
    }

    /**
     * Setup WebSocket event handlers
     * @param {Function} resolve - Promise resolve
     * @param {Function} reject - Promise reject
     * @private
     */
    _setupEventHandlers(resolve, reject) {
        this.ws.onopen = (event) => {
            this.isConnected = true;
            this.isConnecting = false;
            this.reconnectAttempts = 0;

            // Process queued messages
            this._processMessageQueue();

            this.emit('open', event);
            resolve();
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.emit('message', data);
            } catch (error) {
                // If not JSON, emit raw data
                this.emit('message', event.data);
            }
        };

        this.ws.onclose = (event) => {
            const wasConnected = this.isConnected;
            this.isConnected = false;
            this.isConnecting = false;

            this.emit('close', {
                code: event.code,
                reason: event.reason,
                wasClean: event.wasClean
            });

            // Attempt reconnection if not clean close
            if (wasConnected && !event.wasClean) {
                this._scheduleReconnect();
            }
        };

        this.ws.onerror = (error) => {
            this.isConnecting = false;
            this.emit('error', error);

            if (!this.isConnected) {
                reject(error);
            }
        };
    }

    /**
     * Disconnect from WebSocket server
     * @param {number} [code=1000] - Close code
     * @param {string} [reason='Client disconnecting'] - Close reason
     */
    disconnect(code = 1000, reason = 'Client disconnecting') {
        this._cancelReconnect();

        if (this.ws) {
            this.ws.close(code, reason);
            this.ws = null;
        }

        this.isConnected = false;
        this.isConnecting = false;
    }

    /**
     * Send data through WebSocket
     * @param {*} data - Data to send (will be JSON stringified if object)
     * @returns {boolean} True if sent, false if queued
     */
    send(data) {
        const message = typeof data === 'object' ? JSON.stringify(data) : data;

        if (this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(message);
            return true;
        } else {
            // Queue message for later
            this.messageQueue.push(message);
            return false;
        }
    }

    /**
     * Process queued messages
     * @private
     */
    _processMessageQueue() {
        while (this.messageQueue.length > 0 && this.isConnected) {
            const message = this.messageQueue.shift();
            this.ws.send(message);
        }
    }

    /**
     * Schedule reconnection attempt
     * @private
     */
    _scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            this.emit('reconnect_failed', {
                attempts: this.reconnectAttempts
            });
            return;
        }

        this.reconnectAttempts++;

        // Calculate delay with exponential backoff
        const delay = Math.min(
            this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
            this.maxReconnectDelay
        );

        this.emit('reconnecting', {
            attempt: this.reconnectAttempts,
            delay: delay
        });

        this.reconnectTimer = setTimeout(() => {
            this._attemptReconnect();
        }, delay);
    }

    /**
     * Attempt to reconnect
     * @private
     */
    async _attemptReconnect() {
        if (!this.url || this.isConnected || this.isConnecting) {
            return;
        }

        try {
            await this.connect(this.url);
            this.emit('reconnected', {
                attempts: this.reconnectAttempts
            });
        } catch (error) {
            // Will trigger another reconnect attempt via onclose
        }
    }

    /**
     * Cancel scheduled reconnection
     * @private
     */
    _cancelReconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
    }

    /**
     * Get connection state
     * @returns {string} Connection state
     */
    getState() {
        if (!this.ws) return 'CLOSED';

        switch (this.ws.readyState) {
            case WebSocket.CONNECTING:
                return 'CONNECTING';
            case WebSocket.OPEN:
                return 'OPEN';
            case WebSocket.CLOSING:
                return 'CLOSING';
            case WebSocket.CLOSED:
                return 'CLOSED';
            default:
                return 'UNKNOWN';
        }
    }

    /**
     * Check if connected
     * @returns {boolean} True if connected
     */
    isOpen() {
        return this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN;
    }

    /**
     * Get queued message count
     * @returns {number} Queue length
     */
    getQueueLength() {
        return this.messageQueue.length;
    }

    /**
     * Clear message queue
     */
    clearQueue() {
        this.messageQueue = [];
    }

    /**
     * Reset reconnection attempts
     */
    resetReconnectAttempts() {
        this.reconnectAttempts = 0;
    }

    /**
     * Get connection info
     * @returns {Object} Connection info
     */
    getInfo() {
        return {
            url: this.url,
            state: this.getState(),
            isConnected: this.isConnected,
            isConnecting: this.isConnecting,
            reconnectAttempts: this.reconnectAttempts,
            queueLength: this.messageQueue.length
        };
    }
}

// Export for use in other modules
window.WebSocketConnection = WebSocketConnection;
