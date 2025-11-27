/**
 * Code Validator - Validates Mermaid diagram code
 * @module code/CodeValidator
 */

class CodeValidator {
    /**
     * Create a CodeValidator instance
     */
    constructor() {
        this.validationResultsContainer = document.getElementById('validation-results');
        this.lastValidationResult = null;
    }

    /**
     * Validate Mermaid code
     * @param {string} code - The Mermaid code to validate
     * @returns {Object} Validation result with status and issues
     */
    validate(code) {
        const result = {
            valid: true,
            errors: [],
            warnings: [],
            suggestions: []
        };

        if (!code || code.trim() === '') {
            result.valid = false;
            result.errors.push({
                type: 'error',
                message: 'Code is empty',
                line: 0
            });
            this.lastValidationResult = result;
            return result;
        }

        const lines = code.split('\n');

        // Check for diagram type declaration
        const firstLine = lines[0].trim().toLowerCase();
        if (!this._isValidDiagramType(firstLine)) {
            result.warnings.push({
                type: 'warning',
                message: 'Missing or invalid diagram type declaration',
                line: 1
            });
        }

        // Validate syntax based on diagram type
        const diagramType = this._detectDiagramType(firstLine);
        switch (diagramType) {
            case 'flowchart':
                this._validateFlowchart(lines, result);
                break;
            case 'sequence':
                this._validateSequence(lines, result);
                break;
            case 'class':
                this._validateClass(lines, result);
                break;
            default:
                this._validateGeneric(lines, result);
        }

        // Check for common issues
        this._checkCommonIssues(code, result);

        // Update valid status based on errors
        result.valid = result.errors.length === 0;
        this.lastValidationResult = result;

        return result;
    }

    /**
     * Check if first line is a valid diagram type
     * @param {string} line - First line of code
     * @returns {boolean} True if valid diagram type
     * @private
     */
    _isValidDiagramType(line) {
        const validTypes = [
            'flowchart', 'graph', 'sequencediagram', 'classdiagram',
            'statediagram', 'statediagram-v2', 'erdiagram', 'journey',
            'gantt', 'pie', 'gitgraph', 'mindmap', 'timeline',
            'quadrantchart', 'sankey', 'xychart'
        ];

        return validTypes.some(type => line.startsWith(type));
    }

    /**
     * Detect diagram type from first line
     * @param {string} line - First line of code
     * @returns {string} Detected diagram type
     * @private
     */
    _detectDiagramType(line) {
        if (line.startsWith('flowchart') || line.startsWith('graph')) {
            return 'flowchart';
        } else if (line.startsWith('sequencediagram')) {
            return 'sequence';
        } else if (line.startsWith('classdiagram')) {
            return 'class';
        } else if (line.startsWith('statediagram')) {
            return 'state';
        } else if (line.startsWith('erdiagram')) {
            return 'er';
        }
        return 'unknown';
    }

    /**
     * Validate flowchart syntax
     * @param {Array} lines - Code lines
     * @param {Object} result - Validation result object
     * @private
     */
    _validateFlowchart(lines, result) {
        const nodePattern = /^[A-Za-z0-9_]+(\[.*?\]|\(.*?\)|\{.*?\}|\(\(.*?\)\)|{{.*?}})?/;
        const connectionPattern = /^[A-Za-z0-9_]+\s*(-->|---|-\.-|==>|~~~|--o|--x)/;

        for (let i = 1; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line || line.startsWith('%') || line.startsWith('%%')) {
                continue;
            }

            // Check for unclosed brackets
            if (this._hasUnclosedBrackets(line)) {
                result.errors.push({
                    type: 'error',
                    message: 'Unclosed brackets detected',
                    line: i + 1
                });
            }

            // Check for valid node or connection
            if (!nodePattern.test(line) && !connectionPattern.test(line) && !line.startsWith('subgraph') && line !== 'end') {
                result.warnings.push({
                    type: 'warning',
                    message: `Potentially invalid syntax: "${line.substring(0, 30)}..."`,
                    line: i + 1
                });
            }
        }
    }

    /**
     * Validate sequence diagram syntax
     * @param {Array} lines - Code lines
     * @param {Object} result - Validation result object
     * @private
     */
    _validateSequence(lines, result) {
        const participantPattern = /^participant\s+\w+/i;
        const messagePattern = /^\w+\s*(->>|-->>|->|-->)\s*\w+/;

        for (let i = 1; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line || line.startsWith('%') || line.startsWith('%%')) {
                continue;
            }

            // Check for valid participant or message
            if (!participantPattern.test(line) && !messagePattern.test(line) &&
                !line.startsWith('note') && !line.startsWith('loop') &&
                !line.startsWith('alt') && !line.startsWith('opt') &&
                !line.startsWith('par') && !line.startsWith('rect') &&
                line !== 'end' && !line.startsWith('activate') &&
                !line.startsWith('deactivate') && !line.startsWith('title')) {
                result.warnings.push({
                    type: 'warning',
                    message: `Potentially invalid syntax: "${line.substring(0, 30)}..."`,
                    line: i + 1
                });
            }
        }
    }

    /**
     * Validate class diagram syntax
     * @param {Array} lines - Code lines
     * @param {Object} result - Validation result object
     * @private
     */
    _validateClass(lines, result) {
        let inClass = false;
        let braceCount = 0;

        for (let i = 1; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line || line.startsWith('%') || line.startsWith('%%')) {
                continue;
            }

            // Track class blocks
            if (line.includes('{')) {
                braceCount++;
                inClass = true;
            }
            if (line.includes('}')) {
                braceCount--;
                if (braceCount === 0) {
                    inClass = false;
                }
            }
        }

        if (braceCount !== 0) {
            result.errors.push({
                type: 'error',
                message: 'Unmatched braces in class definitions',
                line: 0
            });
        }
    }

    /**
     * Validate generic diagram syntax
     * @param {Array} lines - Code lines
     * @param {Object} result - Validation result object
     * @private
     */
    _validateGeneric(lines, result) {
        for (let i = 1; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line || line.startsWith('%') || line.startsWith('%%')) {
                continue;
            }

            // Check for unclosed brackets
            if (this._hasUnclosedBrackets(line)) {
                result.errors.push({
                    type: 'error',
                    message: 'Unclosed brackets detected',
                    line: i + 1
                });
            }
        }
    }

    /**
     * Check for common issues in code
     * @param {string} code - Full code string
     * @param {Object} result - Validation result object
     * @private
     */
    _checkCommonIssues(code, result) {
        // Check for very long lines
        const lines = code.split('\n');
        lines.forEach((line, index) => {
            if (line.length > 200) {
                result.suggestions.push({
                    type: 'suggestion',
                    message: 'Consider breaking up long lines for readability',
                    line: index + 1
                });
            }
        });

        // Check for duplicate node IDs (basic check)
        const nodeIds = new Set();
        const nodePattern = /^([A-Za-z0-9_]+)[\[\(\{]/;
        lines.forEach((line, index) => {
            const match = line.trim().match(nodePattern);
            if (match) {
                const nodeId = match[1];
                if (nodeIds.has(nodeId)) {
                    result.warnings.push({
                        type: 'warning',
                        message: `Duplicate node ID "${nodeId}" detected`,
                        line: index + 1
                    });
                }
                nodeIds.add(nodeId);
            }
        });

        // Check for empty labels
        if (code.includes('[]') || code.includes('()') || code.includes('{}')) {
            result.suggestions.push({
                type: 'suggestion',
                message: 'Consider adding labels to empty nodes',
                line: 0
            });
        }
    }

    /**
     * Check if line has unclosed brackets
     * @param {string} line - Line to check
     * @returns {boolean} True if unclosed brackets found
     * @private
     */
    _hasUnclosedBrackets(line) {
        const brackets = {
            '[': ']',
            '(': ')',
            '{': '}'
        };

        const stack = [];
        for (const char of line) {
            if (brackets[char]) {
                stack.push(brackets[char]);
            } else if (Object.values(brackets).includes(char)) {
                if (stack.length === 0 || stack.pop() !== char) {
                    return true;
                }
            }
        }

        return stack.length > 0;
    }

    /**
     * Display validation results in the UI
     * @param {Object} [result] - Validation result (uses last result if not provided)
     */
    displayResults(result = null) {
        const validationResult = result || this.lastValidationResult;
        if (!this.validationResultsContainer || !validationResult) return;

        let html = '';

        // Status indicator
        if (validationResult.valid) {
            html += `
                <div class="validation-status valid">
                    <span class="status-icon">✅</span>
                    <span class="status-text">Diagram is valid</span>
                </div>
            `;
        } else {
            html += `
                <div class="validation-status invalid">
                    <span class="status-icon">❌</span>
                    <span class="status-text">Diagram has errors</span>
                </div>
            `;
        }

        // Issues list
        const allIssues = [
            ...validationResult.errors,
            ...validationResult.warnings,
            ...validationResult.suggestions
        ];

        if (allIssues.length > 0) {
            html += '<div class="validation-issues">';
            allIssues.forEach(issue => {
                const lineInfo = issue.line > 0 ? ` (line ${issue.line})` : '';
                html += `
                    <div class="validation-issue ${issue.type}">
                        <span class="issue-type">${this._getIssueIcon(issue.type)}</span>
                        <span class="issue-message">${issue.message}${lineInfo}</span>
                    </div>
                `;
            });
            html += '</div>';
        }

        this.validationResultsContainer.innerHTML = html;
    }

    /**
     * Get icon for issue type
     * @param {string} type - Issue type
     * @returns {string} Icon string
     * @private
     */
    _getIssueIcon(type) {
        switch (type) {
            case 'error':
                return '🔴';
            case 'warning':
                return '🟡';
            case 'suggestion':
                return '💡';
            default:
                return 'ℹ️';
        }
    }

    /**
     * Validate and display results
     * @param {string} code - Code to validate
     * @returns {Object} Validation result
     */
    validateAndDisplay(code) {
        const result = this.validate(code);
        this.displayResults(result);
        return result;
    }

    /**
     * Get last validation result
     * @returns {Object|null} Last validation result
     */
    getLastResult() {
        return this.lastValidationResult;
    }

    /**
     * Check if last validation was successful
     * @returns {boolean} True if valid
     */
    isValid() {
        return this.lastValidationResult ? this.lastValidationResult.valid : false;
    }

    /**
     * Get error count from last validation
     * @returns {number} Number of errors
     */
    getErrorCount() {
        return this.lastValidationResult ? this.lastValidationResult.errors.length : 0;
    }

    /**
     * Get warning count from last validation
     * @returns {number} Number of warnings
     */
    getWarningCount() {
        return this.lastValidationResult ? this.lastValidationResult.warnings.length : 0;
    }
}

// Export for use in other modules
window.CodeValidator = CodeValidator;
