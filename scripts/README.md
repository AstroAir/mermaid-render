# Scripts Directory

This directory contains development, deployment, and maintenance scripts for the Mermaid Render project. All scripts are designed to be cross-platform and work on Windows, macOS, and Linux.

## 📋 Script Overview

### Core Development Scripts

#### `dev.py` - Main Development Tool
The primary development utility that provides a unified interface for common development tasks.

```bash
# Setup development environment
python scripts/dev.py setup

# Run tests with coverage
python scripts/dev.py test

# Run all quality checks
python scripts/dev.py all

# Format code
python scripts/dev.py format

# Build package
python scripts/dev.py build
```

**Available Commands:**
- `setup` - Set up development environment
- `test` - Run tests with coverage
- `lint` - Run linting checks
- `format` - Format code with black and ruff
- `type-check` - Run type checking with mypy
- `security` - Run security checks
- `build` - Build the package
- `clean` - Clean build artifacts
- `docs` - Build documentation
- `all` - Run all quality checks
- `pre-commit` - Run pre-commit hooks
- `benchmark` - Run performance benchmarks
- `docker` - Docker operations (build, run, test)

#### `setup-dev.py` - Environment Setup
Cross-platform development environment setup script.

```bash
# Basic setup
python scripts/setup-dev.py

# Verbose setup with detailed output
python scripts/setup-dev.py --verbose

# Skip pre-commit hooks installation
python scripts/setup-dev.py --no-precommit

# Use UV package manager if available
python scripts/setup-dev.py --use-uv
```

**Features:**
- Virtual environment creation and management
- Dependency installation with UV or pip
- Pre-commit hooks setup
- IDE configuration
- Cross-platform compatibility

#### `setup-dev.bat` - Windows Wrapper
Windows batch file that provides native Windows experience while using the Python setup script.

```cmd
# Run from Windows Command Prompt or PowerShell
scripts\setup-dev.bat
```

### Quality Assurance Scripts

#### `qa-check.py` - Comprehensive QA
Runs comprehensive quality assurance checks including formatting, linting, type checking, security scans, and tests.

```bash
# Run all QA checks
python scripts/qa-check.py

# Run specific check types
python scripts/qa-check.py --checks lint,test,security

# Generate detailed report
python scripts/qa-check.py --report
```

#### `quality_checker.py` - Alternative QA Tool
Alternative quality checker with different focus areas and reporting capabilities.

```bash
# Run quality checks
python scripts/quality_checker.py

# Check specific files
python scripts/quality_checker.py --files src/module.py

# Generate JSON report
python scripts/quality_checker.py --output json
```

### Performance and Benchmarking

#### `benchmark.py` - Performance Benchmarking
Comprehensive performance testing and benchmarking tool.

```bash
# Run all benchmarks
python scripts/benchmark.py

# Run specific benchmark suite
python scripts/benchmark.py --suite rendering

# Compare with previous results
python scripts/benchmark.py --compare benchmark_results_123456.json

# Enable profiling
python scripts/benchmark.py --profile --memory
```

**Benchmark Suites:**
- `import` - Package import performance
- `basic` - Basic operations benchmarking
- `rendering` - Diagram rendering performance
- `caching` - Cache performance testing
- `all` - Complete benchmark suite

### Infrastructure and Deployment

#### `docker-manager.py` - Docker Operations
Comprehensive Docker management for development, testing, and deployment.

```bash
# Build Docker images
python scripts/docker-manager.py build --target production

# Run development container
python scripts/docker-manager.py run --target development

# Run tests in container
python scripts/docker-manager.py test

# Deploy to production
python scripts/docker-manager.py deploy --registry your-registry.com

# Clean Docker resources
python scripts/docker-manager.py clean --all
```

**Commands:**
- `build` - Build Docker images
- `run` - Run containers
- `test` - Run tests in containers
- `deploy` - Deploy to production
- `clean` - Clean up Docker resources
- `logs` - View container logs
- `shell` - Open shell in container
- `compose` - Docker Compose operations
- `status` - Show container status

#### `deploy.py` - Deployment Automation
Automates deployment to different environments with comprehensive checks.

```bash
# Deploy to staging
python scripts/deploy.py staging

# Deploy to production with version
python scripts/deploy.py production --version 1.2.3

# Dry run deployment
python scripts/deploy.py staging --dry-run

# Force deployment (skip checks)
python scripts/deploy.py production --force
```

**Environments:**
- `staging` - Deploy to staging environment
- `production` - Deploy to production environment
- `dev` - Deploy development build
- `docker` - Deploy using Docker

#### `db-migrate.py` - Database Management
Database schema migrations and data management.

```bash
# Initialize migration system
python scripts/db-migrate.py init

# Create new migration
python scripts/db-migrate.py create --name add_user_table

# Apply pending migrations
python scripts/db-migrate.py migrate

# Check migration status
python scripts/db-migrate.py status

# Rollback last migration
python scripts/db-migrate.py rollback
```

### Validation and CI/CD

#### `validate-package.py` - Package Validation
Validates package integrity, imports, API compatibility, and security.

```bash
# Validate package
python scripts/validate-package.py

# Validate specific aspects
python scripts/validate-package.py --checks imports,api,security

# Generate validation report
python scripts/validate-package.py --report
```

#### `version_manager.py` - Version Management
Semantic versioning and release management with changelog generation.

```bash
# Bump version
python scripts/version_manager.py bump --type minor

# Create release
python scripts/version_manager.py release --version 1.2.3

# Generate changelog
python scripts/version_manager.py changelog
```

## 🚀 Quick Start

### 1. Initial Setup
```bash
# Clone the repository
git clone <repository-url>
cd mermaid-render

# Set up development environment
python scripts/setup-dev.py --verbose

# Verify setup
python scripts/dev.py test
```

### 2. Development Workflow
```bash
# Start development
python scripts/dev.py setup

# Make changes to code...

# Run quality checks
python scripts/dev.py all

# Run specific tests
python scripts/dev.py test

# Format code
python scripts/dev.py format

# Build package
python scripts/dev.py build
```

### 3. Docker Development
```bash
# Build development image
python scripts/docker-manager.py build --target development

# Run in container
python scripts/docker-manager.py run --target development

# Run tests in container
python scripts/docker-manager.py test
```

### 4. Deployment
```bash
# Deploy to staging
python scripts/deploy.py staging --dry-run
python scripts/deploy.py staging

# Deploy to production
python scripts/deploy.py production --version 1.2.3
```

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL` - Database connection string
- `DOCKER_REGISTRY` - Docker registry URL
- `CI` - Set to "true" in CI environments
- `PYTHONPATH` - Python path (automatically managed)

### Configuration Files
- `deployment.json` - Deployment configuration
- `docker-compose.yml` - Docker Compose configuration
- `pyproject.toml` - Project configuration
- `Makefile` - Build automation

## 📊 Integration with Build Tools

### Makefile Integration
The scripts integrate with the existing Makefile:

```makefile
# Use scripts through make
make setup     # Calls scripts/setup-dev.py
make test      # Calls scripts/dev.py test
make lint      # Calls scripts/dev.py lint
make build     # Calls scripts/dev.py build
```

### CI/CD Integration
Scripts are designed for CI/CD integration:

```yaml
# GitHub Actions example
- name: Setup Development Environment
  run: python scripts/setup-dev.py --no-interactive

- name: Run Quality Checks
  run: python scripts/dev.py all

- name: Build Package
  run: python scripts/dev.py build

- name: Deploy
  run: python scripts/deploy.py staging
```

### Pre-commit Integration
Scripts work with pre-commit hooks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: quality-check
        name: Quality Check
        entry: python scripts/qa-check.py
        language: system
        pass_filenames: false
```

## 🛠️ Troubleshooting

### Common Issues

1. **Permission Errors on Windows**
   ```bash
   # Run as administrator or use:
   python scripts/setup-dev.py --user
   ```

2. **Virtual Environment Issues**
   ```bash
   # Reset virtual environment
   python scripts/dev.py clean
   python scripts/setup-dev.py --force
   ```

3. **Docker Issues**
   ```bash
   # Check Docker status
   python scripts/docker-manager.py status
   
   # Clean Docker resources
   python scripts/docker-manager.py clean --all
   ```

4. **Database Migration Issues**
   ```bash
   # Check migration status
   python scripts/db-migrate.py status
   
   # Reset database (DANGEROUS)
   python scripts/db-migrate.py reset --confirm
   ```

### Getting Help
All scripts support the `--help` flag for detailed usage information:

```bash
python scripts/dev.py --help
python scripts/docker-manager.py --help
python scripts/deploy.py --help
```

## 📈 Performance Considerations

- Scripts use UV package manager when available for faster dependency management
- Parallel execution where possible (e.g., multiple quality checks)
- Caching mechanisms for repeated operations
- Efficient Docker layer caching
- Incremental builds and testing

## 🔒 Security Features

- Security scanning with bandit and safety
- Dependency vulnerability checking
- Docker image security scanning
- Secrets detection and prevention
- Secure deployment practices

## 📝 Contributing

When adding new scripts:

1. Follow the established patterns and naming conventions
2. Include comprehensive help text and documentation
3. Ensure cross-platform compatibility
4. Add appropriate error handling and logging
5. Include tests for script functionality
6. Update this README with new script information

## 📄 License

These scripts are part of the Mermaid Render project and follow the same license terms.
