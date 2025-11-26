#!/bin/bash
# Development environment setup script for Mermaid Render
# This script sets up a complete development environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python_version() {
    log_info "Checking Python version..."

    if ! command_exists python3; then
        log_error "Python 3 is not installed. Please install Python 3.9 or higher."
        exit 1
    fi

    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    required_version="3.9"

    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        log_error "Python $python_version is installed, but Python $required_version or higher is required."
        exit 1
    fi

    log_success "Python $python_version is installed and compatible."
}

# Setup virtual environment
setup_virtual_env() {
    log_info "Setting up virtual environment..."

    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_success "Virtual environment created."
    else
        log_info "Virtual environment already exists."
    fi

    # Activate virtual environment
    source venv/bin/activate
    log_success "Virtual environment activated."

    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip
    log_success "Pip upgraded."
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."

    # Install the package in development mode with all extras
    pip install -e ".[dev,test,cache,interactive,ai,collaboration,docs,pdf,performance,all]"
    log_success "Dependencies installed."
}

# Setup pre-commit hooks
setup_pre_commit() {
    log_info "Setting up pre-commit hooks..."

    if command_exists pre-commit; then
        pre-commit install
        pre-commit install --hook-type commit-msg
        log_success "Pre-commit hooks installed."
    else
        log_warning "pre-commit not found. Installing..."
        pip install pre-commit
        pre-commit install
        pre-commit install --hook-type commit-msg
        log_success "Pre-commit installed and hooks configured."
    fi
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."

    directories=(
        "output"
        "logs"
        "profiling"
        "docs/_build"
        ".mermaid_cache"
        "temp"
    )

    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_info "Created directory: $dir"
        fi
    done

    log_success "Directories created."
}

# Setup environment file
setup_environment() {
    log_info "Setting up environment configuration..."

    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "Environment file created from .env.example"
            log_info "Please edit .env to configure your environment."
        else
            log_warning ".env.example not found. Skipping environment setup."
        fi
    else
        log_info "Environment file already exists."
    fi
}

# Install system dependencies (optional)
install_system_dependencies() {
    log_info "Checking for system dependencies..."

    # Check for Cairo (needed for PDF export)
    if ! command_exists pkg-config || ! pkg-config --exists cairo; then
        log_warning "Cairo not found. PDF export may not work."
        log_info "To install Cairo:"
        log_info "  Ubuntu/Debian: sudo apt-get install libcairo2-dev"
        log_info "  macOS: brew install cairo"
        log_info "  Windows: Install GTK+ development libraries"
    else
        log_success "Cairo found."
    fi

    # Check for Git
    if ! command_exists git; then
        log_warning "Git not found. Version control features may not work."
    else
        log_success "Git found."
    fi
}

# Run initial tests
run_initial_tests() {
    log_info "Running initial tests to verify setup..."

    # Run a quick test
    if python -c "import mermaid_render; print('✅ Import successful')"; then
        log_success "Package import test passed."
    else
        log_error "Package import test failed."
        return 1
    fi

    # Run basic tests
    if command_exists pytest; then
        log_info "Running basic tests..."
        if pytest tests/ -x -q --tb=short; then
            log_success "Basic tests passed."
        else
            log_warning "Some tests failed. This might be expected in a fresh setup."
        fi
    else
        log_warning "pytest not found. Skipping test run."
    fi
}

# Setup IDE configuration
setup_ide_config() {
    log_info "Setting up IDE configuration..."

    # VS Code settings
    if [ ! -d ".vscode" ]; then
        mkdir -p .vscode

        cat > .vscode/settings.json << EOF
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": false,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".mypy_cache": true,
        "htmlcov": true,
        "dist": true,
        "build": true,
        "*.egg-info": true
    }
}
EOF
        log_success "VS Code settings created."
    fi
}

# Main setup function
main() {
    log_info "Starting Mermaid Render development environment setup..."
    echo

    # Change to project root
    cd "$(dirname "$0")/.."

    # Run setup steps
    check_python_version
    setup_virtual_env
    install_dependencies
    setup_pre_commit
    create_directories
    setup_environment
    install_system_dependencies
    setup_ide_config
    run_initial_tests

    echo
    log_success "Development environment setup complete!"
    echo
    log_info "Next steps:"
    log_info "1. Activate the virtual environment: source venv/bin/activate"
    log_info "2. Edit .env file to configure your environment"
    log_info "3. Run tests: make test"
    log_info "4. Start developing!"
    echo
    log_info "Available commands:"
    log_info "  make help          - Show all available commands"
    log_info "  make test          - Run tests"
    log_info "  make lint          - Run linting"
    log_info "  make format        - Format code"
    log_info "  python demo.py     - Run demo"
    echo
}

# Run main function
main "$@"
