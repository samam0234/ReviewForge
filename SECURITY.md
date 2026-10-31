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
- **Set `JWT_SECRET` in production.** The fallback value in `backend/src/main/resources/application.yml` is public and for local development only.
- Keep the Flask AI server (5000) and Gradio demo (7860) on an internal network; only the Spring Boot API is meant to be public.

## Uploaded Images

- Review photos are validated at every layer (browser, Spring Boot, Flask): JPEG/PNG/WEBP only, 5MB per file, 6MB per request, 40M pixels max, and the actual file format is checked with Pillow (not just the extension or `Content-Type`).
- Images are analyzed in memory and **never stored**; only the analysis result (score, label, signal reasons, width/height) is saved to MongoDB.
- EXIF metadata is read only to derive signals (editing software, presence of camera make/model); the raw metadata is not stored or returned.

See also: [`Docs/web_management/261101_public_release_checklist.md`](./Docs/web_management/261101_public_release_checklist.md)

## Responsible Disclosure

Thank you for helping keep ReviewForge and its users safe.
