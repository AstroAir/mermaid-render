# Security Policy

## Supported Versions

We actively support the following versions of Mermaid Render with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in Mermaid Render, please report it responsibly.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by emailing:
**[security@mermaid-render.dev](mailto:security@mermaid-render.dev)**

### What to Include

When reporting a vulnerability, please include:

1. **Description**: A clear description of the vulnerability
2. **Impact**: Potential impact and attack scenarios
3. **Reproduction**: Step-by-step instructions to reproduce the issue
4. **Environment**: Affected versions, operating systems, Python versions
5. **Proof of Concept**: Code or screenshots demonstrating the vulnerability (if applicable)
6. **Suggested Fix**: If you have ideas for how to fix the issue

### Response Timeline

- **Initial Response**: Within 48 hours of receiving your report
- **Assessment**: Within 5 business days, we'll provide an initial assessment
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days
- **Disclosure**: Coordinated disclosure after the fix is available

### Security Update Process

1. **Verification**: We verify and reproduce the reported vulnerability
2. **Assessment**: We assess the severity and impact
3. **Fix Development**: We develop and test a fix
4. **Release**: We release a security update
5. **Disclosure**: We publish a security advisory

## Security Best Practices

### For Users

When using Mermaid Render in your applications:

1. **Keep Updated**: Always use the latest version with security patches
2. **Validate Input**: Validate and sanitize user-provided diagram code
3. **Limit Permissions**: Run with minimal required permissions
4. **Network Security**: Use HTTPS for external rendering services
5. **Environment Variables**: Secure API keys and configuration secrets
6. **Dependency Scanning**: Regularly scan dependencies for vulnerabilities

### Input Validation

```python
from mermaid_render import validate_mermaid_syntax, ValidationError

# Always validate user input
def safe_render(user_diagram_code):
    try:
        result = validate_mermaid_syntax(user_diagram_code)
        if not result.is_valid:
            raise ValidationError(f"Invalid diagram: {result.errors}")

        # Proceed with rendering only if validation passes
        return render_diagram(user_diagram_code)
    except ValidationError as e:
        # Handle validation errors safely
        log_security_event(f"Invalid diagram input: {e}")
        return None
```

### Configuration Security

```python
import os
from mermaid_render import MermaidConfig

# Use environment variables for sensitive configuration
config = MermaidConfig(
    api_key=os.getenv('MERMAID_API_KEY'),  # Never hardcode API keys
    server_url=os.getenv('MERMAID_SERVER_URL', 'https://mermaid.ink'),
    timeout=int(os.getenv('MERMAID_TIMEOUT', '30'))
)
```

## Known Security Considerations

### External Dependencies

Mermaid Render relies on external services and libraries:

1. **mermaid.ink**: Default rendering service (can be configured)
2. **Third-party APIs**: AI features may use external APIs
3. **Dependencies**: Regular dependency updates for security patches

### Data Privacy

- **Diagram Content**: Diagrams may be sent to external rendering services
- **Caching**: Cached content should be secured appropriately
- **Logs**: Avoid logging sensitive diagram content

### Network Security

- **HTTPS**: Always use HTTPS for external communications
- **Timeouts**: Configure appropriate timeouts to prevent DoS
- **Rate Limiting**: Implement rate limiting for public-facing applications

## Security Features

### Built-in Protections

1. **Input Validation**: Comprehensive syntax validation
2. **Error Handling**: Secure error messages without information disclosure
3. **Timeout Protection**: Configurable timeouts for external requests
4. **Type Safety**: Strong typing to prevent injection attacks

### Configuration Options

```python
# Security-focused configuration
config = MermaidConfig(
    validate_syntax=True,           # Always validate input
    timeout=30,                     # Prevent hanging requests
    max_diagram_size=1024*1024,     # Limit diagram size
    allow_external_urls=False,      # Disable external URL loading
    sanitize_output=True            # Sanitize output content
)
```

## Vulnerability Disclosure Policy

### Coordinated Disclosure

We follow responsible disclosure practices:

1. **Private Reporting**: Initial report through secure channels
2. **Collaboration**: Work with researchers to understand and fix issues
3. **Testing**: Thorough testing of fixes before release
4. **Public Disclosure**: Coordinated public disclosure after fixes are available
5. **Credit**: Appropriate credit to security researchers

### Hall of Fame

We maintain a security hall of fame to recognize researchers who help improve our security:

*No security reports have been received yet.*

## Contact

For security-related questions or concerns:

- **Security Team**: [security@mermaid-render.dev](mailto:security@mermaid-render.dev)
- **General Contact**: [contact@mermaid-render.dev](mailto:contact@mermaid-render.dev)
- **GitHub Security**: Use GitHub's private vulnerability reporting feature

## Legal

This security policy is subject to our terms of service and privacy policy. By reporting vulnerabilities, you agree to:

1. Not publicly disclose the vulnerability until we've had a chance to address it
2. Not access or modify data that doesn't belong to you
3. Act in good faith and avoid privacy violations or service disruption
4. Provide reasonable time for us to address the issue before disclosure

Thank you for helping keep Mermaid Render secure! 🔒
