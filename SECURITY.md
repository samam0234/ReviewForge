# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in ReviewForge, please report it responsibly.

- Do **not** open a public GitHub issue.
- Contact the maintainer privately via the project repository or email associated with the account.
- Provide a clear description, steps to reproduce, and impact assessment.

We will acknowledge receipt within 48 hours and provide an update on the resolution timeline.

## Security Practices

- Never commit API keys, MongoDB connection strings, or secrets.
- Use environment variables (`.env`, `application.yml` with externalized config).
- Validate all user inputs (Bean Validation on Spring Boot, input checks on Next.js).
- Keep dependencies updated.
- AI/ML model files and large datasets should not be committed; use Git LFS or external storage if needed.

## Responsible Disclosure

Thank you for helping keep ReviewForge and its users safe.
