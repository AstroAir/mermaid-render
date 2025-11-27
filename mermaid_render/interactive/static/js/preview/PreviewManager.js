/**
 * Preview Manager - Handles diagram preview rendering
 * @module preview/PreviewManager
 */

class PreviewManager {
    /**
     * Create a PreviewManager instance
     * @param {string} [containerId='preview-content'] - Preview container element ID
     */
    constructor(containerId = 'preview-content') {
        this.container = document.getElementById(containerId);
        this.previewFormat = 'svg';
        this.autoUpdate = true;
        this.lastCode = '';
        this.renderCount = 0;

        this._initializeEventListeners();
        this._initializeMermaid();
    }

    /**
     * Initialize Mermaid library
     * @private
     */
    _initializeMermaid() {
        if (typeof mermaid !== 'undefined') {
            mermaid.initialize({
                startOnLoad: false,
                theme: 'default',
                securityLevel: 'loose',
                flowchart: {
                    useMaxWidth: true,
                    htmlLabels: true,
                    curve: 'basis'
                },
                sequence: {
                    useMaxWidth: true,
                    diagramMarginX: 50,
                    diagramMarginY: 10
                }
            });
        }
    }

    /**
     * Initialize event listeners
     * @private
     */
    _initializeEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refresh-preview');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refresh();
            });
        }

        // Format selector
        const formatSelect = document.getElementById('preview-format');
        if (formatSelect) {
            formatSelect.addEventListener('change', (e) => {
                this.setFormat(e.target.value);
            });
        }
    }

    /**
     * Update preview with Mermaid code
     * @param {string} code - Mermaid diagram code
     * @returns {Promise<boolean>} True if render was successful
     */
    async update(code) {
        if (!this.container) {
            console.warn('Preview container not found');
            return false;
        }

        if (!code || code.trim() === '') {
            this.container.innerHTML = '<p class="preview-placeholder">Preview will appear here...</p>';
            return false;
        }

        this.lastCode = code;

        try {
            // Generate unique ID for this render
            this.renderCount++;
            const diagramId = `preview-diagram-${this.renderCount}`;

            // Use Mermaid to render the diagram
            if (typeof mermaid !== 'undefined') {
                const result = await mermaid.render(diagramId, code);
                this.container.innerHTML = result.svg;

                // Apply format-specific styling
                this._applyFormatStyling();

                return true;
            } else {
                this.container.innerHTML = `
                    <div class="preview-error">
                        <p>Mermaid library not loaded</p>
                    </div>
                `;
                return false;
            }
        } catch (error) {
            this._showError(error);
            return false;
        }
    }

    /**
     * Show error in preview container
     * @param {Error} error - The error object
     * @private
     */
    _showError(error) {
        if (!this.container) return;

        this.container.innerHTML = `
            <div class="preview-error">
                <p class="error-title">Preview Error</p>
                <p class="error-message">${this._escapeHtml(error.message)}</p>
            </div>
        `;
    }

    /**
     * Apply format-specific styling to preview
     * @private
     */
    _applyFormatStyling() {
        const svg = this.container.querySelector('svg');
        if (!svg) return;

        // Ensure SVG is responsive
        svg.style.maxWidth = '100%';
        svg.style.height = 'auto';

        if (this.previewFormat === 'png') {
            // Add background for PNG export
            svg.style.backgroundColor = '#ffffff';
        }
    }

    /**
     * Refresh preview with last code
     */
    refresh() {
        if (this.lastCode) {
            this.update(this.lastCode);
        }
    }

    /**
     * Set preview format
     * @param {string} format - Format ('svg' or 'png')
     */
    setFormat(format) {
        this.previewFormat = format;
        this._applyFormatStyling();
    }

    /**
     * Get current preview format
     * @returns {string} Current format
     */
    getFormat() {
        return this.previewFormat;
    }

    /**
     * Enable or disable auto-update
     * @param {boolean} enabled - Whether auto-update is enabled
     */
    setAutoUpdate(enabled) {
        this.autoUpdate = enabled;
    }

    /**
     * Check if auto-update is enabled
     * @returns {boolean} Auto-update status
     */
    isAutoUpdateEnabled() {
        return this.autoUpdate;
    }

    /**
     * Get the rendered SVG element
     * @returns {SVGElement|null} The SVG element
     */
    getSvgElement() {
        return this.container ? this.container.querySelector('svg') : null;
    }

    /**
     * Get SVG as string
     * @returns {string|null} SVG string
     */
    getSvgString() {
        const svg = this.getSvgElement();
        if (!svg) return null;

        const serializer = new XMLSerializer();
        return serializer.serializeToString(svg);
    }

    /**
     * Convert preview to PNG data URL
     * @param {number} [scale=2] - Scale factor for PNG
     * @returns {Promise<string|null>} PNG data URL
     */
    async toPngDataUrl(scale = 2) {
        const svg = this.getSvgElement();
        if (!svg) return null;

        return new Promise((resolve, reject) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const svgData = this.getSvgString();

            const img = new Image();
            img.onload = () => {
                canvas.width = img.width * scale;
                canvas.height = img.height * scale;

                // Fill white background
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.scale(scale, scale);
                ctx.drawImage(img, 0, 0);

                resolve(canvas.toDataURL('image/png'));
            };
            img.onerror = reject;

            const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
            img.src = URL.createObjectURL(svgBlob);
        });
    }

    /**
     * Clear preview
     */
    clear() {
        if (this.container) {
            this.container.innerHTML = '<p class="preview-placeholder">Preview will appear here...</p>';
        }
        this.lastCode = '';
    }

    /**
     * Set Mermaid theme
     * @param {string} theme - Theme name ('default', 'dark', 'forest', 'neutral')
     */
    setTheme(theme) {
        if (typeof mermaid !== 'undefined') {
            mermaid.initialize({
                theme: theme
            });
            this.refresh();
        }
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
     * Get preview container dimensions
     * @returns {{width: number, height: number}} Container dimensions
     */
    getContainerDimensions() {
        if (!this.container) return { width: 0, height: 0 };
        return {
            width: this.container.clientWidth,
            height: this.container.clientHeight
        };
    }

    /**
     * Zoom preview
     * @param {number} scale - Zoom scale (1 = 100%)
     */
    zoom(scale) {
        const svg = this.getSvgElement();
        if (svg) {
            svg.style.transform = `scale(${scale})`;
            svg.style.transformOrigin = 'top left';
        }
    }

    /**
     * Reset preview zoom
     */
    resetZoom() {
        const svg = this.getSvgElement();
        if (svg) {
            svg.style.transform = '';
            svg.style.transformOrigin = '';
        }
    }

    /**
     * Check if preview has content
     * @returns {boolean} True if preview has rendered content
     */
    hasContent() {
        return this.getSvgElement() !== null;
    }

    /**
     * Get last rendered code
     * @returns {string} Last code
     */
    getLastCode() {
        return this.lastCode;
    }
}

// Export for use in other modules
window.PreviewManager = PreviewManager;
