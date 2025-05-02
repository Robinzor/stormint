# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please send an email to the project maintainer. All security vulnerabilities will be promptly addressed.

### Security Considerations

1. **API Usage**
   - The project uses the SANS Internet Storm Center / DShield API
   - Rate limiting is implemented to prevent abuse
   - User-Agent identification is required for all requests

2. **Data Handling**
   - No sensitive data is stored or processed
   - All data is publicly available through the SANS API
   - Generated queries contain no confidential information

3. **Dependencies**
   - Keep all dependencies up to date
   - Monitor for security advisories
   - Report any security issues in dependencies

### Best Practices

1. **API Security**
   - Always use the latest version of the API
   - Implement proper error handling
   - Respect rate limits and retry-after headers

2. **Code Security**
   - Follow secure coding practices
   - Validate all input data
   - Use parameterized queries
   - Implement proper error handling

3. **Deployment Security**
   - Use HTTPS for all communications
   - Implement proper access controls
   - Keep the server software up to date
   - Monitor for suspicious activity

### Security Updates

Security updates will be released as needed. Users are encouraged to:
- Keep their installations up to date
- Monitor the repository for security announcements
- Report any security concerns immediately

## Contact

To report a security vulnerability, please email the project maintainer with the following information:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

All security reports will be acknowledged within 48 hours, and a more detailed response will be provided within 7 days. 