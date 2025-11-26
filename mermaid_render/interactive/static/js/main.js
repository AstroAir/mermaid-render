// Main JavaScript for Mermaid Interactive Builder

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Add click handlers for diagram type cards
    const diagramCards = document.querySelectorAll('.diagram-type-card');
    diagramCards.forEach(card => {
        card.addEventListener('click', function() {
            // Add visual feedback
            card.style.transform = 'scale(0.95)';
            setTimeout(() => {
                card.style.transform = '';
            }, 150);
        });
    });

    // Add smooth scrolling for navigation
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.getAttribute('href').startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Add intersection observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.diagram-type-card, .feature-item');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for quick navigation
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            showQuickNavigation();
        }
    });
}

function showQuickNavigation() {
    // Create a simple quick navigation modal
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Quick Navigation</h3>
                <button class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <div class="quick-nav-options">
                    <a href="/builder/flowchart" class="quick-nav-item">
                        <span class="nav-icon">📊</span>
                        <span class="nav-text">Flowchart Builder</span>
                    </a>
                    <a href="/builder/sequence" class="quick-nav-item">
                        <span class="nav-icon">🔄</span>
                        <span class="nav-text">Sequence Diagram</span>
                    </a>
                    <a href="/builder/class" class="quick-nav-item">
                        <span class="nav-icon">🏗️</span>
                        <span class="nav-text">Class Diagram</span>
                    </a>
                    <a href="/api/docs" class="quick-nav-item">
                        <span class="nav-icon">📚</span>
                        <span class="nav-text">API Documentation</span>
                    </a>
                </div>
            </div>
        </div>
    `;

    // Add styles for quick navigation
    const style = document.createElement('style');
    style.textContent = `
        .quick-nav-options {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        .quick-nav-item {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            text-decoration: none;
            color: #333;
            transition: all 0.2s;
        }
        .quick-nav-item:hover {
            background: #f8f9fa;
            border-color: #667eea;
            transform: translateX(5px);
        }
        .nav-icon {
            font-size: 1.5rem;
        }
        .nav-text {
            font-weight: 500;
        }
    `;
    document.head.appendChild(style);

    document.body.appendChild(modal);

    // Add event listeners
    const closeBtn = modal.querySelector('.modal-close');
    closeBtn.addEventListener('click', () => {
        modal.remove();
        style.remove();
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
            style.remove();
        }
    });

    // Focus first item
    const firstItem = modal.querySelector('.quick-nav-item');
    if (firstItem) {
        firstItem.focus();
    }

    // Add keyboard navigation
    const items = modal.querySelectorAll('.quick-nav-item');
    let currentIndex = 0;

    modal.addEventListener('keydown', (e) => {
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                currentIndex = (currentIndex + 1) % items.length;
                items[currentIndex].focus();
                break;
            case 'ArrowUp':
                e.preventDefault();
                currentIndex = (currentIndex - 1 + items.length) % items.length;
                items[currentIndex].focus();
                break;
            case 'Enter':
                e.preventDefault();
                items[currentIndex].click();
                break;
            case 'Escape':
                modal.remove();
                style.remove();
                break;
        }
    });
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 6px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        animation: slideInRight 0.3s ease;
    `;

    // Set background color based on type
    const colors = {
        info: '#17a2b8',
        success: '#28a745',
        warning: '#ffc107',
        error: '#dc3545'
    };
    notification.style.backgroundColor = colors[type] || colors.info;

    document.body.appendChild(notification);

    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Add CSS animations
const animationStyles = document.createElement('style');
animationStyles.textContent = `
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
`;
document.head.appendChild(animationStyles);

// Export utility functions for use in other scripts
window.MermaidInteractive = {
    showNotification,
    showQuickNavigation
};
