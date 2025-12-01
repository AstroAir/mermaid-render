/**
 * Main JavaScript for Mermaid Interactive Builder
 * Refactored to use modular components
 * @module main
 */

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    // Initialize UI components
    initializeQuickNavigation();
    initializeNotifications();
    initializeAnimations();
    initializeDiagramCards();
    initializeNavigation();
}

/**
 * Initialize quick navigation
 */
function initializeQuickNavigation() {
    // Quick navigation is now handled by QuickNavigation module
    // Create instance if not on builder page
    if (!document.getElementById('diagram-canvas')) {
        window.quickNav = new QuickNavigation();
    }
}

/**
 * Initialize notification system
 */
function initializeNotifications() {
    // Notification manager is auto-initialized by Notification module
    // Just ensure it's available globally
    if (!window.notificationManager) {
        window.notificationManager = new Notification();
    }
}

/**
 * Initialize scroll animations
 */
function initializeAnimations() {
    // Use AnimationObserver for scroll-based animations
    const animationObserver = new AnimationObserver({
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    // Setup default animations
    animationObserver.setupDefaultAnimations();

    // Store reference
    window.animationObserver = animationObserver;
}

/**
 * Initialize diagram type cards
 */
function initializeDiagramCards() {
    const diagramCards = document.querySelectorAll('.diagram-type-card');
    diagramCards.forEach(card => {
        card.addEventListener('click', function() {
            // Add visual feedback
            card.style.transform = 'scale(0.95)';
            setTimeout(() => {
                card.style.transform = '';
            }, 150);
        });

        // Add keyboard support
        card.setAttribute('tabindex', '0');
        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                card.click();
            }
        });
    });
}

/**
 * Initialize smooth scrolling navigation
 */
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
}

/**
 * Legacy showNotification function for backward compatibility
 * @param {string} message - Notification message
 * @param {string} [type='info'] - Notification type
 */
function showNotification(message, type = 'info') {
    if (window.notificationManager) {
        return window.notificationManager.show(message, type);
    }

    // Fallback if notification manager not available
    console.log(`[${type}] ${message}`);
}

/**
 * Legacy showQuickNavigation function for backward compatibility
 */
function showQuickNavigation() {
    if (window.quickNav) {
        window.quickNav.show();
    } else {
        // Create temporary instance
        const quickNav = new QuickNavigation();
        quickNav.show();
    }
}

// Export utility functions for use in other scripts
window.MermaidInteractive = {
    showNotification,
    showQuickNavigation,

    // Expose module classes
    QuickNavigation: window.QuickNavigation,
    Notification: window.Notification,
    AnimationObserver: window.AnimationObserver,

    // Version info
    version: '2.0.0',
    modulesLoaded: true
};
