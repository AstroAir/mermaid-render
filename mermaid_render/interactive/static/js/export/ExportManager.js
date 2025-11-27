/**
 * Export Manager - Handles diagram export functionality
 * @module export/ExportManager
 */

class ExportManager {
    /**
     * Create an ExportManager instance
     * @param {PreviewManager} [previewManager] - Preview manager instance for getting SVG
     */
    constructor(previewManager = null) {
        this.previewManager = previewManager;
        this.modal = document.getElementById('export-modal');
        this.defaultFilename = 'diagram';

        this._initializeEventListeners();
    }

    /**
     * Set preview manager reference
     * @param {PreviewManager} previewManager - Preview manager instance
     */
    setPreviewManager(previewManager) {
        this.previewManager = previewManager;
    }

    /**
     * Initialize event listeners
     * @private
     */
    _initializeEventListeners() {
        // Export button
        const exportBtn = document.getElementById('export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.showModal();
            });
        }

        // Modal close buttons
        if (this.modal) {
            this.modal.querySelectorAll('.modal-close').forEach(btn => {
                btn.addEventListener('click', () => {
                    this.hideModal();
                });
            });

            // Click outside to close
            this.modal.addEventListener('click', (e) => {
                if (e.target === this.modal) {
                    this.hideModal();
                }
            });
        }

        // Download button
        const downloadBtn = document.getElementById('export-download');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                this.exportDiagram();
            });
        }
    }

    /**
     * Show export modal
     */
    showModal() {
        if (this.modal) {
            this.modal.classList.add('show');

            // Reset filename
            const filenameInput = document.getElementById('export-filename');
            if (filenameInput) {
                filenameInput.value = this.defaultFilename;
            }
        }
    }

    /**
     * Hide export modal
     */
    hideModal() {
        if (this.modal) {
            this.modal.classList.remove('show');
        }
    }

    /**
     * Export diagram based on selected options
     */
    async exportDiagram() {
        const formatInput = document.querySelector('input[name="export-format"]:checked');
        const filenameInput = document.getElementById('export-filename');

        const format = formatInput ? formatInput.value : 'svg';
        const filename = filenameInput ? filenameInput.value || this.defaultFilename : this.defaultFilename;

        try {
            switch (format) {
                case 'svg':
                    await this.exportSvg(filename);
                    break;
                case 'png':
                    await this.exportPng(filename);
                    break;
                case 'pdf':
                    await this.exportPdf(filename);
                    break;
                case 'mermaid':
                    await this.exportMermaidCode(filename);
                    break;
                default:
                    console.warn(`Unknown export format: ${format}`);
            }

            this.hideModal();
            this._showNotification(`Exported as ${format.toUpperCase()}`, 'success');
        } catch (error) {
            console.error('Export failed:', error);
            this._showNotification(`Export failed: ${error.message}`, 'error');
        }
    }

    /**
     * Export as SVG file
     * @param {string} filename - Filename without extension
     */
    async exportSvg(filename) {
        const svgString = this._getSvgString();
        if (!svgString) {
            throw new Error('No diagram to export');
        }

        const blob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
        this._downloadBlob(blob, `${filename}.svg`);
    }

    /**
     * Export as PNG file
     * @param {string} filename - Filename without extension
     * @param {number} [scale=2] - Scale factor for PNG
     */
    async exportPng(filename, scale = 2) {
        const svgString = this._getSvgString();
        if (!svgString) {
            throw new Error('No diagram to export');
        }

        const dataUrl = await this._svgToPng(svgString, scale);
        const blob = await this._dataUrlToBlob(dataUrl);
        this._downloadBlob(blob, `${filename}.png`);
    }

    /**
     * Export as PDF file
     * @param {string} filename - Filename without extension
     */
    async exportPdf(filename) {
        // PDF export requires additional library (jsPDF)
        // For now, we'll export as SVG with PDF extension note
        const svgString = this._getSvgString();
        if (!svgString) {
            throw new Error('No diagram to export');
        }

        // Check if jsPDF is available
        if (typeof jspdf !== 'undefined' && typeof jspdf.jsPDF !== 'undefined') {
            const { jsPDF } = jspdf;
            const doc = new jsPDF();

            // Convert SVG to image and add to PDF
            const dataUrl = await this._svgToPng(svgString, 2);
            const img = new Image();
            img.src = dataUrl;

            await new Promise((resolve) => {
                img.onload = () => {
                    const imgWidth = 190; // A4 width minus margins
                    const imgHeight = (img.height * imgWidth) / img.width;
                    doc.addImage(dataUrl, 'PNG', 10, 10, imgWidth, imgHeight);
                    doc.save(`${filename}.pdf`);
                    resolve();
                };
            });
        } else {
            // Fallback: download as SVG with instructions
            console.warn('jsPDF not available, falling back to SVG export');
            this._showNotification('PDF export requires jsPDF library. Exporting as SVG instead.', 'warning');
            await this.exportSvg(filename);
        }
    }

    /**
     * Export Mermaid code as text file
     * @param {string} filename - Filename without extension
     */
    async exportMermaidCode(filename) {
        const codeEditor = document.getElementById('code-editor');
        const code = codeEditor ? codeEditor.value : '';

        if (!code) {
            throw new Error('No code to export');
        }

        const blob = new Blob([code], { type: 'text/plain;charset=utf-8' });
        this._downloadBlob(blob, `${filename}.mmd`);
    }

    /**
     * Get SVG string from preview
     * @returns {string|null} SVG string
     * @private
     */
    _getSvgString() {
        if (this.previewManager) {
            return this.previewManager.getSvgString();
        }

        // Fallback: try to get from preview container directly
        const previewContent = document.getElementById('preview-content');
        if (previewContent) {
            const svg = previewContent.querySelector('svg');
            if (svg) {
                const serializer = new XMLSerializer();
                return serializer.serializeToString(svg);
            }
        }

        return null;
    }

    /**
     * Convert SVG string to PNG data URL
     * @param {string} svgString - SVG string
     * @param {number} scale - Scale factor
     * @returns {Promise<string>} PNG data URL
     * @private
     */
    _svgToPng(svgString, scale = 2) {
        return new Promise((resolve, reject) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
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

            img.onerror = () => {
                reject(new Error('Failed to load SVG for conversion'));
            };

            const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
            img.src = URL.createObjectURL(svgBlob);
        });
    }

    /**
     * Convert data URL to Blob
     * @param {string} dataUrl - Data URL
     * @returns {Promise<Blob>} Blob
     * @private
     */
    _dataUrlToBlob(dataUrl) {
        return new Promise((resolve) => {
            const arr = dataUrl.split(',');
            const mime = arr[0].match(/:(.*?);/)[1];
            const bstr = atob(arr[1]);
            let n = bstr.length;
            const u8arr = new Uint8Array(n);
            while (n--) {
                u8arr[n] = bstr.charCodeAt(n);
            }
            resolve(new Blob([u8arr], { type: mime }));
        });
    }

    /**
     * Download blob as file
     * @param {Blob} blob - Blob to download
     * @param {string} filename - Filename
     * @private
     */
    _downloadBlob(blob, filename) {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    /**
     * Show notification
     * @param {string} message - Notification message
     * @param {string} type - Notification type
     * @private
     */
    _showNotification(message, type) {
        if (window.MermaidInteractive && window.MermaidInteractive.showNotification) {
            window.MermaidInteractive.showNotification(message, type);
        } else {
            console.log(`[${type}] ${message}`);
        }
    }

    /**
     * Set default filename
     * @param {string} filename - Default filename
     */
    setDefaultFilename(filename) {
        this.defaultFilename = filename;
    }

    /**
     * Get supported export formats
     * @returns {Array} Array of supported formats
     */
    static getSupportedFormats() {
        return [
            { id: 'svg', name: 'SVG (Vector)', extension: '.svg' },
            { id: 'png', name: 'PNG (Raster)', extension: '.png' },
            { id: 'pdf', name: 'PDF (Document)', extension: '.pdf' },
            { id: 'mermaid', name: 'Mermaid Code', extension: '.mmd' }
        ];
    }

    /**
     * Export to clipboard
     * @param {string} [format='svg'] - Format to copy ('svg' or 'code')
     */
    async copyToClipboard(format = 'svg') {
        try {
            let content;
            if (format === 'svg') {
                content = this._getSvgString();
            } else {
                const codeEditor = document.getElementById('code-editor');
                content = codeEditor ? codeEditor.value : '';
            }

            if (!content) {
                throw new Error('No content to copy');
            }

            await navigator.clipboard.writeText(content);
            this._showNotification('Copied to clipboard', 'success');
        } catch (error) {
            console.error('Copy failed:', error);
            this._showNotification('Failed to copy to clipboard', 'error');
        }
    }
}

// Export for use in other modules
window.ExportManager = ExportManager;
