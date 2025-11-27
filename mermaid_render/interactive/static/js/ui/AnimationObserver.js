/**
 * Animation Observer - Handles scroll-based animations using Intersection Observer
 * @module ui/AnimationObserver
 */

class AnimationObserver {
    /**
     * Create an AnimationObserver instance
     * @param {Object} [options] - Observer options
     * @param {number} [options.threshold=0.1] - Intersection threshold
     * @param {string} [options.rootMargin='0px 0px -50px 0px'] - Root margin
     */
    constructor(options = {}) {
        this.threshold = options.threshold || 0.1;
        this.rootMargin = options.rootMargin || '0px 0px -50px 0px';
        this.observer = null;
        this.observedElements = new Set();
        this.animationClasses = new Map();

        this._createObserver();
    }

    /**
     * Create intersection observer
     * @private
     */
    _createObserver() {
        const observerOptions = {
            threshold: this.threshold,
            rootMargin: this.rootMargin
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this._animateIn(entry.target);
                }
            });
        }, observerOptions);
    }

    /**
     * Animate element in
     * @param {HTMLElement} element - Element to animate
     * @private
     */
    _animateIn(element) {
        // Get custom animation class if set
        const animationClass = this.animationClasses.get(element);

        if (animationClass) {
            element.classList.add(animationClass);
        } else {
            // Default animation
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }

        // Optionally unobserve after animation
        if (element.dataset.animateOnce !== 'false') {
            this.unobserve(element);
        }
    }

    /**
     * Observe an element for animation
     * @param {HTMLElement|string} element - Element or selector
     * @param {Object} [options] - Animation options
     * @param {string} [options.animationClass] - CSS class to add on intersection
     * @param {string} [options.initialStyle] - Initial inline styles
     * @param {boolean} [options.animateOnce=true] - Only animate once
     */
    observe(element, options = {}) {
        const el = typeof element === 'string' ? document.querySelector(element) : element;
        if (!el) return;

        const {
            animationClass = null,
            initialStyle = 'opacity: 0; transform: translateY(20px); transition: opacity 0.6s ease, transform 0.6s ease;',
            animateOnce = true
        } = options;

        // Set initial styles
        if (initialStyle) {
            el.style.cssText += initialStyle;
        }

        // Store animation class if provided
        if (animationClass) {
            this.animationClasses.set(el, animationClass);
        }

        // Set animate once flag
        el.dataset.animateOnce = animateOnce.toString();

        // Start observing
        this.observer.observe(el);
        this.observedElements.add(el);
    }

    /**
     * Observe multiple elements
     * @param {string} selector - CSS selector
     * @param {Object} [options] - Animation options
     */
    observeAll(selector, options = {}) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            this.observe(el, options);
        });
    }

    /**
     * Stop observing an element
     * @param {HTMLElement} element - Element to unobserve
     */
    unobserve(element) {
        if (this.observer && element) {
            this.observer.unobserve(element);
            this.observedElements.delete(element);
            this.animationClasses.delete(element);
        }
    }

    /**
     * Stop observing all elements
     */
    unobserveAll() {
        this.observedElements.forEach(el => {
            this.observer.unobserve(el);
        });
        this.observedElements.clear();
        this.animationClasses.clear();
    }

    /**
     * Disconnect observer
     */
    disconnect() {
        if (this.observer) {
            this.observer.disconnect();
            this.observedElements.clear();
            this.animationClasses.clear();
        }
    }

    /**
     * Set up default animations for common elements
     */
    setupDefaultAnimations() {
        // Animate diagram type cards
        this.observeAll('.diagram-type-card', {
            initialStyle: 'opacity: 0; transform: translateY(20px); transition: opacity 0.6s ease, transform 0.6s ease;'
        });

        // Animate feature items
        this.observeAll('.feature-item', {
            initialStyle: 'opacity: 0; transform: translateY(20px); transition: opacity 0.6s ease, transform 0.6s ease;'
        });

        // Animate sections
        this.observeAll('.animate-on-scroll', {
            initialStyle: 'opacity: 0; transform: translateY(30px); transition: opacity 0.8s ease, transform 0.8s ease;'
        });
    }

    /**
     * Add staggered animation to a group of elements
     * @param {string} selector - CSS selector
     * @param {number} [staggerDelay=100] - Delay between each element in ms
     */
    observeStaggered(selector, staggerDelay = 100) {
        const elements = document.querySelectorAll(selector);
        elements.forEach((el, index) => {
            const delay = index * staggerDelay;
            this.observe(el, {
                initialStyle: `opacity: 0; transform: translateY(20px); transition: opacity 0.6s ease ${delay}ms, transform 0.6s ease ${delay}ms;`
            });
        });
    }

    /**
     * Create fade-in animation
     * @param {HTMLElement|string} element - Element or selector
     * @param {number} [duration=600] - Duration in ms
     */
    fadeIn(element, duration = 600) {
        this.observe(element, {
            initialStyle: `opacity: 0; transition: opacity ${duration}ms ease;`
        });
    }

    /**
     * Create slide-up animation
     * @param {HTMLElement|string} element - Element or selector
     * @param {number} [distance=20] - Distance in px
     * @param {number} [duration=600] - Duration in ms
     */
    slideUp(element, distance = 20, duration = 600) {
        this.observe(element, {
            initialStyle: `opacity: 0; transform: translateY(${distance}px); transition: opacity ${duration}ms ease, transform ${duration}ms ease;`
        });
    }

    /**
     * Create slide-in-left animation
     * @param {HTMLElement|string} element - Element or selector
     * @param {number} [distance=30] - Distance in px
     * @param {number} [duration=600] - Duration in ms
     */
    slideInLeft(element, distance = 30, duration = 600) {
        this.observe(element, {
            initialStyle: `opacity: 0; transform: translateX(-${distance}px); transition: opacity ${duration}ms ease, transform ${duration}ms ease;`
        });
    }

    /**
     * Create slide-in-right animation
     * @param {HTMLElement|string} element - Element or selector
     * @param {number} [distance=30] - Distance in px
     * @param {number} [duration=600] - Duration in ms
     */
    slideInRight(element, distance = 30, duration = 600) {
        this.observe(element, {
            initialStyle: `opacity: 0; transform: translateX(${distance}px); transition: opacity ${duration}ms ease, transform ${duration}ms ease;`
        });
    }

    /**
     * Create scale-up animation
     * @param {HTMLElement|string} element - Element or selector
     * @param {number} [startScale=0.9] - Starting scale
     * @param {number} [duration=600] - Duration in ms
     */
    scaleUp(element, startScale = 0.9, duration = 600) {
        this.observe(element, {
            initialStyle: `opacity: 0; transform: scale(${startScale}); transition: opacity ${duration}ms ease, transform ${duration}ms ease;`
        });
    }

    /**
     * Get count of observed elements
     * @returns {number} Count
     */
    getObservedCount() {
        return this.observedElements.size;
    }

    /**
     * Check if element is being observed
     * @param {HTMLElement} element - Element to check
     * @returns {boolean} True if observed
     */
    isObserving(element) {
        return this.observedElements.has(element);
    }
}

// Export for use in other modules
window.AnimationObserver = AnimationObserver;
