/**
 * Event Emitter - Simple event emitter for pub/sub pattern
 * @module websocket/EventEmitter
 */

class EventEmitter {
    /**
     * Create an EventEmitter instance
     */
    constructor() {
        this.events = new Map();
        this.onceEvents = new Map();
    }

    /**
     * Register an event handler
     * @param {string} event - Event name
     * @param {Function} handler - Handler function
     * @returns {EventEmitter} This instance for chaining
     */
    on(event, handler) {
        if (!this.events.has(event)) {
            this.events.set(event, []);
        }
        this.events.get(event).push(handler);
        return this;
    }

    /**
     * Register a one-time event handler
     * @param {string} event - Event name
     * @param {Function} handler - Handler function
     * @returns {EventEmitter} This instance for chaining
     */
    once(event, handler) {
        if (!this.onceEvents.has(event)) {
            this.onceEvents.set(event, []);
        }
        this.onceEvents.get(event).push(handler);
        return this;
    }

    /**
     * Remove an event handler
     * @param {string} event - Event name
     * @param {Function} [handler] - Handler function (removes all if not provided)
     * @returns {EventEmitter} This instance for chaining
     */
    off(event, handler) {
        if (!handler) {
            // Remove all handlers for this event
            this.events.delete(event);
            this.onceEvents.delete(event);
        } else {
            // Remove specific handler
            if (this.events.has(event)) {
                const handlers = this.events.get(event);
                const index = handlers.indexOf(handler);
                if (index > -1) {
                    handlers.splice(index, 1);
                }
            }
            if (this.onceEvents.has(event)) {
                const handlers = this.onceEvents.get(event);
                const index = handlers.indexOf(handler);
                if (index > -1) {
                    handlers.splice(index, 1);
                }
            }
        }
        return this;
    }

    /**
     * Emit an event
     * @param {string} event - Event name
     * @param {*} [data] - Event data
     * @returns {boolean} True if event had listeners
     */
    emit(event, data) {
        let hasListeners = false;

        // Call regular handlers
        if (this.events.has(event)) {
            const handlers = this.events.get(event);
            handlers.forEach(handler => {
                try {
                    handler(data);
                    hasListeners = true;
                } catch (error) {
                    console.error(`Error in event handler for "${event}":`, error);
                }
            });
        }

        // Call and remove once handlers
        if (this.onceEvents.has(event)) {
            const handlers = this.onceEvents.get(event);
            handlers.forEach(handler => {
                try {
                    handler(data);
                    hasListeners = true;
                } catch (error) {
                    console.error(`Error in once event handler for "${event}":`, error);
                }
            });
            this.onceEvents.delete(event);
        }

        return hasListeners;
    }

    /**
     * Get all registered events
     * @returns {Array} Array of event names
     */
    eventNames() {
        const names = new Set([
            ...this.events.keys(),
            ...this.onceEvents.keys()
        ]);
        return Array.from(names);
    }

    /**
     * Get listener count for an event
     * @param {string} event - Event name
     * @returns {number} Listener count
     */
    listenerCount(event) {
        let count = 0;
        if (this.events.has(event)) {
            count += this.events.get(event).length;
        }
        if (this.onceEvents.has(event)) {
            count += this.onceEvents.get(event).length;
        }
        return count;
    }

    /**
     * Get all listeners for an event
     * @param {string} event - Event name
     * @returns {Array} Array of handler functions
     */
    listeners(event) {
        const handlers = [];
        if (this.events.has(event)) {
            handlers.push(...this.events.get(event));
        }
        if (this.onceEvents.has(event)) {
            handlers.push(...this.onceEvents.get(event));
        }
        return handlers;
    }

    /**
     * Remove all event handlers
     * @returns {EventEmitter} This instance for chaining
     */
    removeAllListeners() {
        this.events.clear();
        this.onceEvents.clear();
        return this;
    }

    /**
     * Check if event has listeners
     * @param {string} event - Event name
     * @returns {boolean} True if has listeners
     */
    hasListeners(event) {
        return this.listenerCount(event) > 0;
    }

    /**
     * Prepend a handler to be called first
     * @param {string} event - Event name
     * @param {Function} handler - Handler function
     * @returns {EventEmitter} This instance for chaining
     */
    prependListener(event, handler) {
        if (!this.events.has(event)) {
            this.events.set(event, []);
        }
        this.events.get(event).unshift(handler);
        return this;
    }

    /**
     * Prepend a one-time handler to be called first
     * @param {string} event - Event name
     * @param {Function} handler - Handler function
     * @returns {EventEmitter} This instance for chaining
     */
    prependOnceListener(event, handler) {
        if (!this.onceEvents.has(event)) {
            this.onceEvents.set(event, []);
        }
        this.onceEvents.get(event).unshift(handler);
        return this;
    }
}

// Export for use in other modules
window.EventEmitter = EventEmitter;
