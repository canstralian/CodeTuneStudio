# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**DO NOT** open public issues for security vulnerabilities.

Please report security vulnerabilities to: [your-email@domain.com]

### Response Time
- Initial response: 48 hours
- Status update: 7 days
- Fix timeline: 30 days (depending on severity)

## Security Update Process

1. Dependabot automatically creates PRs for security updates
2. Security PRs are labeled with `security` and prioritized
3. All security updates undergo automated testing before merge
4. Critical vulnerabilities (CVSS >= 7.0) are patched within 24-48 hours

## Security Best Practices

- All API endpoints implement rate limiting
- Input validation on all user-provided data
- Parameterized queries for database operations (PostgreSQL)
- JWT tokens with short expiration times
- HTTPS enforced in production
- Environment variables for sensitive configuration
- Regular dependency audits via `pip-audit` and `npm audit`
