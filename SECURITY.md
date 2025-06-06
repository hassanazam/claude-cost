# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Security Features

### Privacy-First Design
- **No message content access**: Only processes usage metadata (tokens, costs, timestamps)
- **Local-only analysis**: All data processing happens on your machine
- **No data transmission**: Never sends data to external services
- **PII protection**: Designed to avoid processing any personally identifiable information

### Data Processing
- Only accesses: Token counts, model names, timestamps, usage statistics
- Never accesses: Message content, conversation text, user prompts, AI responses
- Local file processing: `~/.claude/projects/*/` conversation logs

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### For Critical Security Issues
- **Do NOT** open a public GitHub issue
- Email: [security email would go here]
- Include: Detailed description, steps to reproduce, potential impact

### For Non-Critical Issues
- Open a GitHub issue with the `security` label
- Provide clear description and reproduction steps

### Response Timeline
- **Critical vulnerabilities**: 24-48 hours initial response
- **Other security issues**: 7 days initial response
- **Security updates**: Released as soon as validated

## Security Best Practices for Users

### Installation
```bash
# Always install from official PyPI
pip install claude-cost

# Verify package integrity (optional)
pip install --force-reinstall claude-cost
```

### Usage
```bash
# CLI tool processes local files only
claude-cost metrics  # Safe - local analysis only
claude-cost predict  # Safe - local analysis only
```

### Data Security
- Tool only reads conversation logs from `~/.claude/projects/*/`
- No network connections made during analysis
- All processing happens locally on your machine
- No data is uploaded, downloaded, or transmitted

## Security Checklist

### For Contributors
- [ ] No hardcoded credentials in code
- [ ] No API keys or tokens committed
- [ ] Privacy-first design maintained
- [ ] Security scan passes (bandit)
- [ ] No access to message content
- [ ] All file access is read-only for analysis

### For Users
- [ ] Install only from official PyPI
- [ ] Keep package updated to latest version
- [ ] Review permissions if prompted
- [ ] Report any suspicious behavior

## Known Security Considerations

### File Access
- Tool requires read access to `~/.claude/projects/*/` for analysis
- This is expected behavior for conversation log analysis
- No write access needed to any sensitive directories

### Dependencies
- **Zero runtime dependencies** for core functionality
- Optional visualization dependencies available
- Regular dependency scanning via Dependabot

## Security Updates

Security updates are released as patch versions (e.g., 1.0.1) and include:
- Security vulnerability fixes
- Dependency security updates
- Privacy protection improvements

Subscribe to releases on GitHub to stay informed about security updates.

## Contact

For security-related questions or concerns:
- GitHub Issues: [Security label](https://github.com/hassanazam/claude-cost/issues?q=label%3Asecurity)
- General inquiries: GitHub Discussions

---

**Remember**: This tool is designed with privacy-first principles. It only processes usage metadata and never accesses message content or personal information.