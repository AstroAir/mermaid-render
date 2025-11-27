/**
 * Canvas Manager - Handles canvas zoom, pan, and transformations
 * @module canvas/CanvasManager
 */

class CanvasManager {
    /**
     * Create a CanvasManager instance
     * @param {SVGElement} canvas - The SVG canvas element
     * @param {SVGGElement} canvasGroup - The canvas group element for transformations
     */
    constructor(canvas, canvasGroup) {
        this.canvas = canvas;
        this.canvasGroup = canvasGroup;
        this.zoom = 1;
        this.pan = { x: 0, y: 0 };
        this.minZoom = 0.1;
        this.maxZoom = 5;
        this.zoomStep = 1.2;

        this._initializeEventListeners();
    }

    /**
     * Initialize canvas event listeners
     * @private
     */
    _initializeEventListeners() {
        // Zoom controls
        const zoomInBtn = document.getElementById('zoom-in');
        const zoomOutBtn = document.getElementById('zoom-out');
        const zoomFitBtn = document.getElementById('zoom-fit');

        if (zoomInBtn) {
            zoomInBtn.addEventListener('click', () => this.zoomIn());
        }
        if (zoomOutBtn) {
            zoomOutBtn.addEventListener('click', () => this.zoomOut());
        }
        if (zoomFitBtn) {
            zoomFitBtn.addEventListener('click', () => this.zoomFit());
        }

        // Mouse wheel zoom
        this.canvas.addEventListener('wheel', this._onWheel.bind(this));
    }

    /**
     * Handle mouse wheel event for zooming
     * @param {WheelEvent} e - The wheel event
     * @private
     */
    _onWheel(e) {
        e.preventDefault();
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        const newZoom = Math.max(this.minZoom, Math.min(this.maxZoom, this.zoom * delta));

        // Zoom towards mouse position
        this.pan.x = x - (x - this.pan.x) * (newZoom / this.zoom);
        this.pan.y = y - (y - this.pan.y) * (newZoom / this.zoom);
        this.zoom = newZoom;

        this.updateTransform();
        this.updateZoomDisplay();
    }

    /**
     * Apply current transform to canvas group
     */
    updateTransform() {
        this.canvasGroup.setAttribute('transform',
            `translate(${this.pan.x}, ${this.pan.y}) scale(${this.zoom})`);
    }

    /**
     * Update zoom level display
     */
    updateZoomDisplay() {
        const zoomLevelEl = document.getElementById('zoom-level');
        if (zoomLevelEl) {
            zoomLevelEl.textContent = `${Math.round(this.zoom * 100)}%`;
        }
    }

    /**
     * Zoom in by zoom step
     */
    zoomIn() {
        this.zoom = Math.min(this.maxZoom, this.zoom * this.zoomStep);
        this.updateTransform();
        this.updateZoomDisplay();
    }

    /**
     * Zoom out by zoom step
     */
    zoomOut() {
        this.zoom = Math.max(this.minZoom, this.zoom / this.zoomStep);
        this.updateTransform();
        this.updateZoomDisplay();
    }

    /**
     * Reset zoom and pan to fit all elements
     */
    zoomFit() {
        this.zoom = 1;
        this.pan = { x: 0, y: 0 };
        this.updateTransform();
        this.updateZoomDisplay();
    }

    /**
     * Set zoom level directly
     * @param {number} level - The zoom level (0.1 to 5)
     */
    setZoom(level) {
        this.zoom = Math.max(this.minZoom, Math.min(this.maxZoom, level));
        this.updateTransform();
        this.updateZoomDisplay();
    }

    /**
     * Set pan position directly
     * @param {number} x - X position
     * @param {number} y - Y position
     */
    setPan(x, y) {
        this.pan = { x, y };
        this.updateTransform();
    }

    /**
     * Pan the canvas by delta values
     * @param {number} dx - Delta X
     * @param {number} dy - Delta Y
     */
    panBy(dx, dy) {
        this.pan.x += dx * this.zoom;
        this.pan.y += dy * this.zoom;
        this.updateTransform();
    }

    /**
     * Convert screen coordinates to canvas coordinates
     * @param {number} screenX - Screen X coordinate
     * @param {number} screenY - Screen Y coordinate
     * @returns {{x: number, y: number}} Canvas coordinates
     */
    screenToCanvas(screenX, screenY) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: (screenX - rect.left - this.pan.x) / this.zoom,
            y: (screenY - rect.top - this.pan.y) / this.zoom
        };
    }

    /**
     * Convert canvas coordinates to screen coordinates
     * @param {number} canvasX - Canvas X coordinate
     * @param {number} canvasY - Canvas Y coordinate
     * @returns {{x: number, y: number}} Screen coordinates
     */
    canvasToScreen(canvasX, canvasY) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: canvasX * this.zoom + this.pan.x + rect.left,
            y: canvasY * this.zoom + this.pan.y + rect.top
        };
    }

    /**
     * Get current zoom level
     * @returns {number} Current zoom level
     */
    getZoom() {
        return this.zoom;
    }

    /**
     * Get current pan position
     * @returns {{x: number, y: number}} Current pan position
     */
    getPan() {
        return { ...this.pan };
    }

    /**
     * Update canvas cursor based on current mode
     * @param {string} mode - The current tool mode
     */
    updateCursor(mode) {
        this.canvas.className = 'diagram-canvas';
        switch (mode) {
            case 'select':
                this.canvas.classList.add('select-mode');
                break;
            case 'pan':
                this.canvas.classList.add('pan-mode');
                break;
            default:
                // Drawing mode - use default crosshair
                break;
        }
    }

    /**
     * Set grabbing cursor during pan drag
     * @param {boolean} isGrabbing - Whether currently grabbing
     */
    setGrabbingCursor(isGrabbing) {
        this.canvas.style.cursor = isGrabbing ? 'grabbing' : 'grab';
    }
}

// Export for use in other modules
window.CanvasManager = CanvasManager;
