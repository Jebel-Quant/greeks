# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

**Do NOT report security vulnerabilities through public GitHub issues.**

Instead, please use one of the following methods:

1. **GitHub Security Advisories** (Preferred)
   - Go to the [Security Advisories](https://github.com/Jebel-Quant/greeks/security/advisories) page
   - Click "New draft security advisory"
   - Fill in the details and submit

2. **Email**
   - Send details to the repository maintainers
   - Include "SECURITY" in the subject line

### What to Include

- **Description**: A clear description of the vulnerability
- **Impact**: The potential impact of the vulnerability
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Affected Versions**: Which versions are affected
- **Suggested Fix**: If you have one (optional)

### What to Expect

- **Acknowledgment**: We will acknowledge receipt within 48 hours
- **Initial Assessment**: We will provide an initial assessment within 7 days
- **Resolution Timeline**: We aim to resolve critical issues within 30 days
- **Credit**: We will credit reporters in the security advisory (unless you prefer to remain anonymous)

## Security Measures

### Code Scanning
- **CodeQL**: Automated code scanning for Python and GitHub Actions
- **Bandit**: Python security linter integrated in CI and pre-commit
- **pip-audit**: Dependency vulnerability scanning

### Supply Chain Security
- **Locked Dependencies**: `uv.lock` ensures reproducible builds
- **Renovate**: Automated dependency updates with security patches

## Acknowledgments

We thank the security researchers and community members who help keep this project secure.
