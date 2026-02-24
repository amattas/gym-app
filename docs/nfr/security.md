# Security Requirements

This document defines security requirements and controls.

---

## Authentication

### Password Requirements

- Minimum 12 characters
- Must contain: uppercase, lowercase, number, special character
- Cannot contain user's email or name
- Checked against Have I Been Pwned breach database
- Hash with Argon2id only

### MFA Requirements

| Role | MFA Required | Grace Period |
|------|--------------|--------------|
| Platform Admin | Yes | None |
| Gym Admin | Yes | 7 days |
| Trainer | Yes | 7 days |
| Client | Optional | N/A |

**Supported Methods**:
- TOTP (recommended)
- Email OTP (fallback)
- Passkeys (most secure)

**NOT Supported**:
- SMS OTP (vulnerable to SIM swapping)

### Session Security

- Access tokens: 1 hour expiry
- Refresh tokens: 30 days expiry
- Tokens revoked on password change
- Concurrent session limit: 5 per user

---

## Authorization (RBAC)

### Role Hierarchy

```
platform_admin
    └── admin (gym)
        ├── trainer
        └── front_desk
client (separate)
```

### Permission Matrix

| Action | Platform Admin | Admin | Trainer | Front Desk | Client |
|--------|----------------|-------|---------|------------|--------|
| Modify gym settings | ✓ | ✓ | - | - | - |
| Manage trainers | ✓ | ✓ | - | - | - |
| Manage clients | ✓ | ✓ | ✓ | - | - |
| View all clients | ✓ | ✓ | ✓ | ✓ | - |
| Log workouts | ✓ | ✓ | ✓ | - | Own |
| Check in clients | ✓ | ✓ | ✓ | ✓ | - |
| View analytics | ✓ | ✓ | Limited | - | - |

---

## Data Protection

### Encryption at Rest

- Database: AES-256 encryption
- File storage: Server-side encryption (S3 SSE)
- Secrets: Encrypted with environment-specific keys

### Encryption in Transit

- TLS 1.2 minimum (prefer TLS 1.3)
- HTTPS required for all endpoints
- Certificate pinning for mobile apps (optional)

### Sensitive Data Handling

| Data Type | Storage | Access |
|-----------|---------|--------|
| Passwords | Hashed (Argon2id) | Never exposed |
| MFA secrets | Encrypted | Encrypted at rest |
| API tokens | Hashed (SHA-256) | Never logged |
| PII | Encrypted columns | Role-based access |
| Payment data | Stripe (PCI compliant) | Never stored locally |

---

## API Security

### Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/auth/login` | 5 | 15 minutes |
| `/auth/password/reset` | 3 | 1 hour |
| General API (GET) | 100 | 1 minute |
| General API (POST) | 30 | 1 minute |

### Input Validation

- Validate all input on server side
- Parameterized queries (prevent SQL injection)
- Output encoding (prevent XSS)
- Content-Type validation

### CORS Policy

- Allow only known origins
- No wildcard in production
- Include credentials only for first-party

---

## Audit Logging

### Events to Log

| Event | Details Captured |
|-------|------------------|
| Login success/failure | User ID, IP, timestamp, method |
| Password change | User ID, timestamp |
| Permission changes | Who, what, when |
| Data exports | User ID, data scope, timestamp |
| Admin actions | Full action details |

### Log Retention

- Security logs: 1 year minimum
- Audit logs: 7 years (compliance)
- Application logs: 90 days

### Log Security

- Logs stored in separate system
- No PII in logs (use IDs only)
- Immutable audit trail
- Access restricted to security team

---

## Infrastructure Security

### Network Security

- VPC isolation
- Private subnets for databases
- WAF for API protection
- DDoS protection

### Secret Management

- Use secrets manager (AWS Secrets Manager, Vault)
- Rotate secrets regularly
- No secrets in code or version control
- Environment-specific secrets

### Dependency Security

- Regular dependency scanning
- Automated security patches
- SBOM (Software Bill of Materials)
- Pin dependency versions

---

## Incident Response

### Severity Levels

| Level | Description | Response Time |
|-------|-------------|---------------|
| Critical | Data breach, service down | < 1 hour |
| High | Security vulnerability exploited | < 4 hours |
| Medium | Potential vulnerability | < 24 hours |
| Low | Security improvement | Next sprint |

### Response Steps

1. Detect and contain
2. Assess scope and impact
3. Notify affected parties
4. Remediate
5. Document and learn

---

## Compliance

See [compliance.md](compliance.md) for GDPR, CCPA, COPPA, and PCI requirements.
