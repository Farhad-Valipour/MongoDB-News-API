# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of MongoDB News API seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please DO NOT

- **DO NOT** open a public GitHub issue for security vulnerabilities
- **DO NOT** publicly disclose the vulnerability before it has been addressed
- **DO NOT** exploit the vulnerability for malicious purposes

### Please DO

**Report security vulnerabilities to:** [security@example.com](mailto:security@example.com)

Include the following information:

1. **Type of vulnerability** (e.g., SQL injection, XSS, authentication bypass)
2. **Full paths** of source file(s) related to the vulnerability
3. **Step-by-step instructions** to reproduce the issue
4. **Proof-of-concept or exploit code** (if possible)
5. **Impact** of the vulnerability
6. **Suggested fix** (if you have one)

## What to Expect

### Response Timeline

- **Initial Response**: Within 24-48 hours
- **Assessment**: Within 1 week
- **Fix Development**: Depends on severity (1-4 weeks)
- **Public Disclosure**: After fix is released

### Assessment Process

1. We will acknowledge receipt of your vulnerability report
2. We will assess the vulnerability and its impact
3. We will develop and test a fix
4. We will release the fix in a new version
5. We will publicly disclose the vulnerability (with credit to you, if desired)

### Severity Levels

| Level | Description | Response Time |
|-------|-------------|---------------|
| **Critical** | Allows remote code execution or data breach | 24 hours |
| **High** | Allows privilege escalation or data exposure | 1 week |
| **Medium** | Allows denial of service or information disclosure | 2 weeks |
| **Low** | Minor security issues with minimal impact | 4 weeks |

## Security Best Practices

### For Users

1. **Keep dependencies updated**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

2. **Use strong API keys**
   - At least 32 characters
   - Random and unique
   - Rotate regularly

3. **Enable HTTPS**
   - Use reverse proxy (nginx, Apache)
   - Configure SSL certificates
   - Enable HSTS

4. **Limit rate limits**
   ```env
   RATE_LIMIT_PER_HOUR=1000
   ```

5. **Use environment variables**
   - Never commit `.env` files
   - Use secrets management in production

6. **Monitor logs**
   - Enable request logging
   - Monitor for suspicious activity
   - Set up alerts

### For Developers

1. **Input Validation**
   - Use Pydantic models for all inputs
   - Validate query parameters
   - Sanitize user inputs

2. **Authentication**
   - Never store API keys in code
   - Use secure token generation
   - Implement token expiration

3. **Database Security**
   - Use parameterized queries
   - Enable MongoDB authentication
   - Limit database user permissions
   - Enable encryption at rest

4. **Dependencies**
   - Regularly update dependencies
   - Use `pip-audit` to check for vulnerabilities
   ```bash
   pip install pip-audit
   pip-audit
   ```

5. **CORS Configuration**
   - Restrict origins in production
   - Don't use `*` in production
   ```python
   CORS_ORIGINS=https://yourdomain.com
   ```

6. **Error Handling**
   - Don't expose stack traces in production
   - Use generic error messages
   - Log detailed errors internally

## Known Security Considerations

### API Key Authentication

- API keys are passed in headers or query parameters
- Consider implementing JWT tokens for enhanced security
- API keys should be rotated regularly

### Rate Limiting

- Current: 1000 requests/hour per API key
- Implemented in-memory (resets on restart)
- Consider Redis for persistent rate limiting in production

### Data Exposure

- News content may contain sensitive information
- Implement data classification
- Consider content filtering

### MongoDB Security

- Ensure MongoDB authentication is enabled
- Use connection string encryption
- Implement network segmentation
- Enable audit logging

## Security Updates

Security updates will be released as patch versions (e.g., 1.0.1, 1.0.2).

Subscribe to:
- GitHub Security Advisories
- GitHub Releases
- Project mailing list (coming soon)

## Bug Bounty Program

We currently do not have a bug bounty program. However, we deeply appreciate security researchers who responsibly disclose vulnerabilities and will acknowledge your contribution in:

- Security advisories
- Release notes
- CONTRIBUTORS.md file

## Compliance

This project aims to comply with:

- OWASP Top 10 security risks
- CWE/SANS Top 25 Most Dangerous Software Errors
- General security best practices

## Security Contacts

- **Security Team**: [security@example.com](mailto:security@example.com)
- **PGP Key**: Available upon request
- **Response Time**: 24-48 hours

## Additional Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [MongoDB Security Checklist](https://docs.mongodb.com/manual/administration/security-checklist/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

**Last Updated**: 2025-11-21

Thank you for helping keep MongoDB News API secure! 🔒
