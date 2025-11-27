/**
 * Notification - Provides toast notification functionality
 * @module ui/Notification
 */

class Notification {
    /**
     * Create a Notification manager instance
     */
    constructor() {
        this.container = null;
        this.notifications = [];
        this.defaultDuration = 3000;
        this.maxNotifications = 5;

        this._createContainer();
        this._addStyles();
    }

    /**
     * Create notification container
     * @private
     */
    _createContainer() {
        this.container = document.createElement('div');
        this.container.className = 'notification-container';
        this.container.id = 'notification-container';
        document.body.appendChild(this.container);
    }

    /**
     * Add notification styles
     * @private
     */
    _addStyles() {
        // Check if styles already exist
        if (document.getElementById('notification-styles')) return;

        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                display: flex;
                flex-direction: column;
                gap: 10px;
                pointer-events: none;
            }

            .notification {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 16px;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                font-size: 14px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                pointer-events: auto;
                animation: slideInRight 0.3s ease;
                max-width: 350px;
                word-wrap: break-word;
            }

            .notification.removing {
                animation: slideOutRight 0.3s ease forwards;
            }

            .notification-info {
                background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
            }

            .notification-success {
                background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%);
            }

            .notification-warning {
                background: linear-gradient(135deg, #ffc107 0%, #d39e00 100%);
                color: #212529;
            }

            .notification-error {
                background: linear-gradient(135deg, #dc3545 0%, #bd2130 100%);
            }

            .notification-icon {
                font-size: 18px;
                flex-shrink: 0;
            }

            .notification-content {
                flex: 1;
            }

            .notification-title {
                font-weight: 600;
                margin-bottom: 2px;
            }

            .notification-message {
                font-weight: 400;
                opacity: 0.9;
            }

            .notification-close {
                background: none;
                border: none;
                color: inherit;
                font-size: 18px;
                cursor: pointer;
                opacity: 0.7;
                padding: 0;
                margin-left: 8px;
                flex-shrink: 0;
            }

            .notification-close:hover {
                opacity: 1;
            }

            .notification-progress {
                position: absolute;
                bottom: 0;
                left: 0;
                height: 3px;
                background: rgba(255, 255, 255, 0.5);
                border-radius: 0 0 8px 8px;
                animation: progressShrink linear forwards;
            }

            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }

            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }

            @keyframes progressShrink {
                from {
                    width: 100%;
                }
                to {
                    width: 0%;
                }
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Show a notification
     * @param {string} message - Notification message
     * @param {string} [type='info'] - Notification type ('info', 'success', 'warning', 'error')
     * @param {Object} [options] - Additional options
     * @param {string} [options.title] - Notification title
     * @param {number} [options.duration] - Duration in milliseconds
     * @param {boolean} [options.closable=true] - Whether notification can be closed
     * @param {boolean} [options.showProgress=false] - Show progress bar
     * @returns {HTMLElement} Notification element
     */
    show(message, type = 'info', options = {}) {
        const {
            title = null,
            duration = this.defaultDuration,
            closable = true,
            showProgress = false
        } = options;

        // Remove oldest notification if at max
        if (this.notifications.length >= this.maxNotifications) {
            this.remove(this.notifications[0]);
        }

        const notification = this._createNotification(message, type, title, closable, showProgress, duration);
        this.container.appendChild(notification);
        this.notifications.push(notification);

        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                this.remove(notification);
            }, duration);
        }

        return notification;
    }

    /**
     * Create notification element
     * @param {string} message - Message
     * @param {string} type - Type
     * @param {string|null} title - Title
     * @param {boolean} closable - Closable
     * @param {boolean} showProgress - Show progress
     * @param {number} duration - Duration
     * @returns {HTMLElement} Notification element
     * @private
     */
    _createNotification(message, type, title, closable, showProgress, duration) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;

        const icon = this._getIcon(type);

        let html = `
            <span class="notification-icon">${icon}</span>
            <div class="notification-content">
        `;

        if (title) {
            html += `<div class="notification-title">${this._escapeHtml(title)}</div>`;
        }

        html += `<div class="notification-message">${this._escapeHtml(message)}</div>`;
        html += '</div>';

        if (closable) {
            html += '<button class="notification-close">&times;</button>';
        }

        if (showProgress && duration > 0) {
            html += `<div class="notification-progress" style="animation-duration: ${duration}ms"></div>`;
        }

        notification.innerHTML = html;

        // Add close handler
        if (closable) {
            const closeBtn = notification.querySelector('.notification-close');
            closeBtn.addEventListener('click', () => {
                this.remove(notification);
            });
        }

        return notification;
    }

    /**
     * Get icon for notification type
     * @param {string} type - Notification type
     * @returns {string} Icon
     * @private
     */
    _getIcon(type) {
        const icons = {
            info: 'ℹ️',
            success: '✅',
            warning: '⚠️',
            error: '❌'
        };
        return icons[type] || icons.info;
    }

    /**
     * Remove a notification
     * @param {HTMLElement} notification - Notification element
     */
    remove(notification) {
        if (!notification || !notification.parentNode) return;

        notification.classList.add('removing');

        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
            const index = this.notifications.indexOf(notification);
            if (index > -1) {
                this.notifications.splice(index, 1);
            }
        }, 300);
    }

    /**
     * Remove all notifications
     */
    removeAll() {
        [...this.notifications].forEach(notification => {
            this.remove(notification);
        });
    }

    /**
     * Show info notification
     * @param {string} message - Message
     * @param {Object} [options] - Options
     * @returns {HTMLElement} Notification element
     */
    info(message, options = {}) {
        return this.show(message, 'info', options);
    }

    /**
     * Show success notification
     * @param {string} message - Message
     * @param {Object} [options] - Options
     * @returns {HTMLElement} Notification element
     */
    success(message, options = {}) {
        return this.show(message, 'success', options);
    }

    /**
     * Show warning notification
     * @param {string} message - Message
     * @param {Object} [options] - Options
     * @returns {HTMLElement} Notification element
     */
    warning(message, options = {}) {
        return this.show(message, 'warning', options);
    }

    /**
     * Show error notification
     * @param {string} message - Message
     * @param {Object} [options] - Options
     * @returns {HTMLElement} Notification element
     */
    error(message, options = {}) {
        return this.show(message, 'error', options);
    }

    /**
     * Escape HTML to prevent XSS
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
     * Set default duration
     * @param {number} duration - Duration in milliseconds
     */
    setDefaultDuration(duration) {
        this.defaultDuration = duration;
    }

    /**
     * Set max notifications
     * @param {number} max - Maximum number of notifications
     */
    setMaxNotifications(max) {
        this.maxNotifications = max;
    }

    /**
     * Get active notification count
     * @returns {number} Count
     */
    getCount() {
        return this.notifications.length;
    }
}

// Create global instance
const notificationManager = new Notification();

// Legacy function for backward compatibility
function showNotification(message, type = 'info') {
    return notificationManager.show(message, type);
}

// Export for use in other modules
window.Notification = Notification;
window.notificationManager = notificationManager;
window.showNotification = showNotification;
