# Non-Functional Requirements

This document outlines the non-functional requirements for the gym management platform, including performance, security, compliance, accessibility, and operational requirements.

---

## Table of Contents

1. [Performance Requirements](#1-performance-requirements)
2. [Security Requirements](#2-security-requirements)
3. [Reliability & Infrastructure](#3-reliability--infrastructure)
4. [Compliance & Privacy](#4-compliance--privacy)
5. [Accessibility](#5-accessibility)
6. [Media & Storage](#6-media--storage)
7. [Third-Party Integrations](#7-third-party-integrations)
8. [Operational Algorithms](#8-operational-algorithms)

---

## 1. Performance Requirements

### 1.1 API Latency Targets

Performance targets are categorized by operation type based on user expectations and criticality.

#### Real-time Operations (User Waiting, Critical Path)

Operations where users are actively waiting and delays are immediately noticeable.

**Operations**:
- Authentication (login, token refresh)
- Workout logging (start workout, log set, complete exercise)
- Scheduling (check availability, book session)
- Check-in operations

**Targets**:
- **p95**: < 200ms
- **p99**: < 500ms

#### Dashboard/Reporting Operations (Acceptable Delay)

Operations where users expect some delay but need results within a reasonable timeframe.

**Operations**:
- Analytics queries
- Trainer dashboards
- Client progress reports
- Workout history

**Targets**:
- **p95**: < 1s
- **p99**: < 2s

#### Background Operations (Async, No User Waiting)

Operations that run asynchronously with no immediate user feedback required.

**Operations**:
- AI summary generation
- Usage metering rollups
- Email/push notifications

**Targets**:
- **Best effort**, no strict SLA

### 1.2 Usage Metering Performance

**Requirements**:
- Async/event-based counting (does not impact request latency)
- Rollup calculations run on schedule (nightly/hourly)
- Metrics calculated without blocking user-facing operations

---

## 2. Security Requirements

### 2.1 Authentication & Authorization

#### Role-Based Access Control (RBAC)

- **Roles**: Admin, Trainer, Front Desk, Client
- **Multi-role support**: Users can have multiple roles (e.g., Trainer + Front Desk)
- **Object-level authorization**: Trainer can only access assigned clients unless admin
- **Front Desk permissions**: Check-in operations, view schedules, monitor occupancy (read-only)

#### Custom Domain Security (Enterprise Feature)

**Domain Ownership Verification**:
- DNS verification mandatory before any domain can be used
- Verification tokens cryptographically random (32 bytes, hex-encoded)
- Verifications expire after 72 hours
- Maximum 10 retry attempts before marking as failed
- Domain uniqueness enforced at database level (one domain per gym)

**DNS Security**:
- Query multiple DNS resolvers (Google 8.8.8.8, Cloudflare 1.1.1.1, AWS Route53)
- Consensus-based validation (majority agreement required)
- Respect DNS TTL values for caching
- Optional DNSSEC validation for enhanced security

**Email Domain Security**:
- SPF record validation (must include Resend servers)
- DKIM signature verification (public key validation)
- DMARC policy validation
- Block free email domains (gmail.com, yahoo.com, etc.) for deliverability

**Login Domain Security**:
- CNAME record validation
- TXT record verification for ownership proof
- Automatic SSL certificate provisioning via Let's Encrypt
- SSL certificate renewal 30 days before expiration
- SSL certificates stored securely with restricted access

**Authorization**:
- Only gym admins can configure/modify custom domains
- Multi-factor authentication required for domain configuration changes
- Audit logging for all domain configuration changes
- Immediate cache invalidation on domain status changes

#### Password Security

**Storage**:
- **Algorithm**: Argon2id only
- **Parameters**: 64 MB memory, 3 iterations, 4 threads
- **Salting**: Cryptographically secure random salt (128-bit minimum), unique per password, automatically handled by Argon2id
- **Versioning**: Track hash algorithm version for future migrations (transparent upgrade on login)

**Requirements**:
- Minimum 12 characters
- Must include: uppercase + lowercase + number + special character
- Breach check via Have I Been Pwned API

**Password Reset**:
- Secure token-based reset (256-bit random, SHA-256 hashed)
- 1-hour expiration
- Single-use tokens
- Rate limiting: Max 3 reset requests per email per hour

#### Multi-Factor Authentication (MFA)

**Requirements by Role**:
- **Admin/Trainer**: Required after 7-day grace period
- **Client**: Optional

**Supported Methods**:
- **TOTP** (preferred): Time-based One-Time Password (e.g., Google Authenticator)
- **Email** (fallback): Email-based verification codes
- **Passkey-only** (most secure): WebAuthn/FIDO2 without password
- **NOT supported**: SMS (insecure, SIM swap attacks)

**Backup Codes**:
- Single-use backup codes for MFA recovery
- Regeneration capability

#### Passkeys (WebAuthn/FIDO2)

**Features**:
- Passwordless authentication support
- Passkey-only mode (users can delete password)
- Multiple passkey registration per user
- Device naming/management
- Platform authenticator support (biometrics)

#### OAuth2 Implementation

**Grant Types Supported**:
- `password`: Resource owner password credentials
- `authorization_code`: With PKCE (required for all code flows)
- `refresh_token`: Refresh access tokens
- `client_credentials`: Server-to-server

**Token Management**:
- **Access tokens**: 1 hour lifetime
- **Refresh tokens**: 30 days lifetime
- **Storage**: Never store plaintext, use SHA-256 hash
- **PKCE**: Required for all authorization code flows (mobile/SPA security)

**Scopes**:
- Fine-grained permissions (gym:read, clients:read, workouts:write, mcp:trainer, etc.)
- Scope-based access control for third-party integrations

**OAuth2 Clients**:
- Gym admins can create OAuth2 clients for third-party integrations
- Trainers can ONLY authorize MCP (not create general OAuth2 clients)
- Client secret regeneration capability

### 2.2 Data Security

**Payment Data**:
- Never store raw card data
- Use Stripe-hosted UI (e.g., Checkout/Payment Element)
- Webhook verification for all payment events

**Audit Logging**:
- Audit log for all critical changes
- 7-year retention for compliance/legal
- Archive after 1 year to cold storage
- Store member numbers only (not full PII)

**Media Privacy**:
- Strict access control for progress photos
- Consider per-photo encryption at rest
- Signed URLs for photo access

### 2.3 Platform Security Controls

This section defines baseline security controls that apply across the entire platform.

#### 2.3.1 Transport Layer Security (TLS)

**TLS Requirements**:
- **Minimum Version**: TLS 1.2 (TLS 1.3 preferred)
- **Certificate Authority**: Let's Encrypt (automated via Digital Ocean App Platform or certbot)
- **Certificate Renewal**: Automated renewal 30 days before expiration
- **HSTS Header**: `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`

**Cipher Suites** (ordered by preference):
- TLS 1.3: `TLS_AES_256_GCM_SHA384`, `TLS_AES_128_GCM_SHA256`
- TLS 1.2: `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384`, `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256`

**Deprecated/Insecure** (must be disabled):
- SSL 2.0, SSL 3.0, TLS 1.0, TLS 1.1
- RC4, DES, 3DES ciphers
- Export-grade ciphers
- Anonymous ciphers

**HTTP to HTTPS Redirect**:
- All HTTP requests automatically redirected to HTTPS (301 Permanent Redirect)
- No sensitive data transmitted over HTTP

#### 2.3.2 Encryption at Rest

**Database Encryption**:
- **PostgreSQL**: Transparent Data Encryption (TDE) using Digital Ocean Managed Databases encryption
- **MongoDB**: Encryption at rest enabled by default (MongoDB Atlas or Digital Ocean Managed MongoDB)
- **Encryption Keys**: Managed encryption with automatic key rotation
- **Key Management**: Separate keys per environment (dev, staging, production)

**Object Storage Encryption**:
- **Digital Ocean Spaces**: Server-side encryption (AES-256)
- **Encryption**: AES-256 by default
- **Progress Photos**: Encrypted at rest, consider additional per-object encryption for high-sensitivity gyms
- **Signed PDFs**: Encrypted at rest

**Backup Encryption**:
- All backups encrypted with AES-256
- Encryption keys separate from data keys
- Backups stored with cross-region replication (Digital Ocean backup regions)

**Local Storage** (Mobile Apps):
- iOS: Use Keychain for sensitive data (tokens, keys)
- Android: Use EncryptedSharedPreferences and Keystore
- Database: SQLCipher or equivalent for local database encryption

#### 2.3.3 Secrets Management

**Secrets Storage**:
- **Production**: HashiCorp Vault or encrypted environment variables (Digital Ocean App Platform)
- **Development**: Environment variables (never committed to git)
- **CI/CD**: GitHub Secrets or equivalent

**Secret Types**:
- Database connection strings
- API keys (Stripe, DocuSign, third-party services)
- OAuth2 client secrets
- JWT signing keys
- Encryption keys

**Secret Rotation**:
- **Automated rotation**: Database passwords every 90 days
- **Manual rotation**: API keys and OAuth2 secrets on-demand
- **Rotation procedures**: Documented runbooks for emergency rotation

**Access Control**:
- Secrets accessible only by authorized services (Digital Ocean App Platform secrets or Kubernetes secrets)
- No secrets in application logs or error messages
- Secrets never returned in API responses

#### 2.3.4 Log Redaction & PII Protection

**PII Redaction Rules**:

Never log sensitive information:
- Passwords, password hashes, or password reset tokens
- Credit card numbers, CVV codes, or full payment details
- Social Security Numbers (SSN) or government IDs
- OAuth2 access tokens or refresh tokens
- Email addresses (log only in audit logs, redacted in application logs)
- Phone numbers
- Date of birth (log only in audit logs)

**Redaction Strategy**:
- Automatic redaction using log filters
- Replace sensitive data with `[REDACTED]` or masked values
- Examples:
  - Email: `j***@example.com` (show first char + domain)
  - Phone: `+1 (***) ***-1234` (show last 4 digits)
  - Card: `**** **** **** 1234` (show last 4 digits)

**Audit Logs** (exception to redaction):
- Audit logs may contain member numbers and pseudonymous identifiers
- Never contain passwords, tokens, or payment data
- Encrypted at rest, access restricted to compliance team

**Log Access Control**:
- Production logs accessible only to on-call engineers and security team
- Audit trail for all log access
- Logs exported to SIEM for security monitoring

#### 2.3.5 API Security

**Rate Limiting** (See [API_SPECIFICATIONS.md Section 20](API_SPECIFICATIONS.md#20-rate-limiting)):
- Per-user and per-IP rate limits
- Prevents brute-force attacks and DoS
- Rate limit headers in all responses

**CORS (Cross-Origin Resource Sharing)**:
- Restrict allowed origins to known domains
- **Platform domains** (default):
  - Production: `https://app.gym.example.com`, `https://admin.gym.example.com`
  - Development: `http://localhost:3000`, `http://localhost:5173`
- **Custom login domains** (dynamic, per-gym):
  - Gyms with verified custom login domains (e.g., `https://app.powerliftgym.com`) are automatically added to CORS whitelist
  - Only verified domains (status='verified') are allowed
  - Unverified/failed domains are rejected
- **CORS Origin Validation Logic**:
  1. Check if origin matches platform default domains (`app.gym.example.com` OR `admin.gym.example.com`)
  2. If not, query `gym` table for matching `custom_login_domain` where `custom_login_status='verified'`
  3. If match found, allow origin
  4. Otherwise, reject request (403 Forbidden)
- **Caching**: Cache verified custom domains in Redis with 5-minute TTL (key: `cors:allowed_origins`)
- **Never allow** `*` wildcard in production

**CSRF Protection**:
- CSRF tokens required for all state-changing operations
- SameSite cookie attribute: `SameSite=Strict` or `SameSite=Lax`
- Not required for Bearer token authentication (API-only clients)

**Security Headers**:
```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

#### 2.3.6 Input Validation & Output Encoding

**Input Validation**:
- Validate all user input on server side (never trust client)
- Whitelist validation (allow known-good patterns)
- Reject unexpected input (fail closed)
- Validate data types, lengths, formats, ranges

**SQL Injection Prevention**:
- Use parameterized queries (prepared statements) ONLY
- Never concatenate user input into SQL queries
- ORM frameworks (Prisma, TypeORM, etc.) preferred

**XSS Prevention**:
- Encode all user-generated content before rendering in HTML
- Use framework-provided encoding (React auto-escapes by default)
- Sanitize rich text input (Markdown, HTML) using trusted libraries
- Avoid unsafe HTML injection methods

**Command Injection Prevention**:
- Never pass user input to shell commands
- Use language libraries instead of shell commands where possible
- If shell commands required, validate input rigorously

#### 2.3.7 Dependency Management & Vulnerability Scanning

**Dependency Scanning**:
- **Tool**: Dependabot (GitHub), Snyk, or npm audit
- **Frequency**: Automated scans on every PR
- **Policy**: Block PRs with critical or high-severity vulnerabilities
- **Updates**: Automated PRs for dependency updates weekly

**Container Scanning**:
- **Tool**: Trivy or Snyk Container
- **Frequency**: Scan all images before deployment
- **Policy**: Block deployment of images with critical vulnerabilities

**SAST (Static Application Security Testing)**:
- **Tool**: CodeQL, SonarQube, or Semgrep
- **Frequency**: On every PR
- **Coverage**: Detect common vulnerabilities (injection, XSS, hardcoded secrets)

**DAST (Dynamic Application Security Testing)**:
- **Tool**: OWASP ZAP or Burp Suite
- **Frequency**: Weekly automated scans against staging environment
- **Scope**: Test for OWASP Top 10 vulnerabilities

**Penetration Testing**:
- **Frequency**: Annual third-party penetration test
- **Scope**: Full application (web, mobile, API)
- **Report**: Remediation plan within 30 days for high/critical findings

#### 2.3.8 Secure Development Practices

**Code Review Requirements**:
- All code changes require at least 1 approval
- Security-sensitive changes require 2 approvals + security team review
- Security checklist for all PRs

**Security Training**:
- Annual OWASP Top 10 training for all engineers
- Secure coding guidelines documented and enforced
- Threat modeling for new features

**Secrets in Code**:
- Pre-commit hooks to prevent committing secrets
- Automated secret scanning (GitHub Secret Scanning, TruffleHog)
- Emergency secret rotation procedures documented

**Third-Party Code**:
- Security review before integrating new dependencies
- Prefer well-maintained libraries with active security support
- Document all third-party integrations and their security implications

---

## 3. Reliability & Infrastructure

### 3.1 Offline-First Strategy

#### Mobile Apps (iOS/Android): Full Offline Capability

**Requirements**:
- Local database for all critical operations
- Sync in background when connection available
- Works without internet for 30 days of cached data

**Offline-Capable Operations**:
- Add/edit clients and prospects
- Check in clients (workout start)
- Log workout data (sets, reps, measurements)
- Complete workouts
- View schedules (cached last 30 days)
- View programs (cached)
- View client profiles + recent history (cached last 30 days)
- Upload progress photos (queued for upload)

**Note**: E-signature agreements are Post-MVP and will require online connectivity when implemented.

#### Web App: Online-Only

**Rationale**: Admins typically work from office/stable environments

**Requirements**:
- Requires stable internet connection
- No offline data caching
- Clear error messaging when connection lost

### 3.2 Online-Only Operations (All Platforms)

**Operations Requiring Server Connection**:
- Admin functions (gym settings, user management, bulk operations)
- Creating/editing programs
- Reports and analytics
- Payment/billing operations
- Real-time busyness calculations (requires live data)

### 3.3 Sync Strategy

**Background Sync**:
- Sync on connection resume
- Optimistic UI: Show changes immediately, sync in background
- Cache duration: Last 30 days of historical data locally

**Conflict Resolution**:
- If two trainers log same workout offline → log both (edge case, alert admin)
- Last-write-wins for most data types
- Server reconciliation for critical conflicts

### 3.4 Availability & Uptime Targets

**Service Level Objectives (SLOs)**:

| Service Component | Target Availability | Measurement Window | Max Downtime/Month |
|-------------------|---------------------|--------------------|--------------------|
| API (production) | 99.9% | Monthly | 43.2 minutes |
| Web App (production) | 99.9% | Monthly | 43.2 minutes |
| Mobile Apps (online features) | 99.5% | Monthly | 3.6 hours |
| Documentation Site | 99.0% | Monthly | 7.2 hours |

**Exclusions** (not counted against SLO):
- Scheduled maintenance windows (announced 7 days in advance)
- Client-side network issues
- Third-party service outages (Stripe, DocuSign, etc.)
- Force majeure events (cloud provider region outages, DDoS attacks, etc.)

**Measurement**:
- Monitored via synthetic checks every 60 seconds from multiple geographic locations
- Uptime calculated as: `(total_time - downtime) / total_time * 100%`
- Downtime defined as: Any period where service returns 5xx errors or times out for >1 minute

### 3.5 Backup Strategy & Data Protection

**Database Backups (PostgreSQL)**:
- **Frequency**: Continuous WAL archiving + daily full backups
- **Retention**:
  - Daily backups: 30 days
  - Weekly backups: 90 days
  - Monthly backups: 1 year
- **Storage**: Encrypted backups stored in secondary Digital Ocean region
- **Validation**: Weekly automated restore tests to staging environment
- **Encryption**: AES-256 encryption at rest

**NoSQL Backups (MongoDB)**:
- **Frequency**: Continuous backups (point-in-time recovery via MongoDB Atlas or managed service)
- **Retention**: 35 days point-in-time recovery window
- **Storage**: Cross-region replication for disaster recovery

**Object Storage Backups (Digital Ocean Spaces)**:
- **Versioning**: Enabled for all objects (progress photos, signed PDFs)
- **Retention**: Indefinite (matches data retention policy)
- **Replication**: Cross-region replication to secondary region
- **Deletion protection**: Soft delete with 30-day recovery window

**Backup Testing**:
- Monthly: Restore random subset of data to staging environment
- Quarterly: Full disaster recovery drill (restore entire system)
- Document restore procedures and maintain runbooks

### 3.6 Recovery Objectives

**Recovery Point Objective (RPO)**: Maximum acceptable data loss

| Data Type | RPO Target | Rationale |
|-----------|------------|-----------|
| Workout data, measurements, PRs | < 5 minutes | Continuous WAL archiving |
| User accounts, memberships | < 5 minutes | Continuous WAL archiving |
| Progress photos | < 1 hour | Asynchronous replication |
| Analytics rollups | < 24 hours | Can be recalculated from source data |

**Recovery Time Objective (RTO)**: Maximum acceptable downtime

| Incident Type | RTO Target | Recovery Procedure |
|---------------|------------|--------------------|
| Single server failure | < 5 minutes | Auto-failover to standby |
| Database failure | < 15 minutes | Automated failover to replica |
| Complete region failure | < 4 hours | Manual failover to DR region |
| Data corruption | < 8 hours | Restore from backup + replay WAL |

**Disaster Recovery Plan**:
- Primary region: Digital Ocean NYC3 (New York)
- DR region: Digital Ocean SFO3 (San Francisco)
- Regular DR drills quarterly
- Documented runbooks for all failure scenarios

### 3.7 Monitoring & Observability

**Infrastructure Monitoring**:
- **Tool**: Prometheus + Grafana (Kubernetes clusters)
- **Metrics Collected**:
  - CPU, memory, disk usage per pod
  - Network traffic and error rates
  - Pod restart counts and crash loops
  - Horizontal pod autoscaler status

**Application Performance Monitoring (APM)**:
- **Tool**: DataDog or New Relic (TBD)
- **Metrics Collected**:
  - API endpoint latency (p50, p95, p99)
  - Request throughput (requests/sec)
  - Error rate by endpoint
  - Database query performance
  - External API call latency (Stripe, DocuSign, etc.)

**Real User Monitoring (RUM)**:
- **Tool**: DataDog RUM or similar
- **Metrics**:
  - Page load times
  - JavaScript errors
  - User session recordings (privacy-safe)
  - Conversion funnel analytics

**Log Aggregation**:
- **Tool**: Digital Ocean Monitoring + Fluent Bit (or Loki for self-hosted)
- **Log Levels**: ERROR, WARN, INFO, DEBUG
- **Retention**: 90 days hot storage, 1 year cold storage (exported to Spaces)
- **Log Types**:
  - Application logs (errors, warnings, critical events)
  - Access logs (API requests, response codes, latency)
  - Audit logs (authentication, authorization, data access)
  - Security logs (failed login attempts, permission denials)

**Distributed Tracing**:
- **Tool**: Jaeger or OpenTelemetry
- **Purpose**: Trace requests across microservices and external dependencies
- **Sampling**: 10% of requests in production, 100% for errors

**Alerting**:
- **Critical Alerts** (page on-call engineer immediately):
  - API error rate > 5% for 5 minutes
  - API latency p99 > 2 seconds for 5 minutes
  - Database replica lag > 60 seconds
  - Disk usage > 85%
  - SSL certificate expiring within 7 days
- **Warning Alerts** (notify team, no immediate action):
  - API error rate > 2% for 10 minutes
  - Memory usage > 80%
  - Backup failure
- **Notification Channels**: PagerDuty, Slack, email

### 3.8 Incident Response

**Incident Severity Levels**:

| Severity | Definition | Response Time | Example |
|----------|-----------|---------------|---------|
| **P0 - Critical** | Complete service outage | < 15 minutes | API down, cannot authenticate |
| **P1 - High** | Major feature unavailable | < 1 hour | Cannot start workouts, payments failing |
| **P2 - Medium** | Minor feature degraded | < 4 hours | Progress photos not uploading |
| **P3 - Low** | Cosmetic issue, no impact | < 2 business days | UI alignment issue |

**Incident Response Process**:

1. **Detection**: Automated monitoring alerts or user report
2. **Triage**: On-call engineer assesses severity, pages additional team members if P0/P1
3. **Investigation**: Use logs, metrics, and tracing to identify root cause
4. **Mitigation**: Apply temporary fix to restore service
5. **Communication**: Update status page, notify affected customers (P0/P1)
6. **Resolution**: Apply permanent fix, deploy to production
7. **Post-Mortem**: Document incident, root cause, and preventive measures (P0/P1 required)

**Communication**:
- **Status Page**: Public status page showing system health (statuspage.io or similar)
- **Customer Notifications**:
  - P0: Email + in-app banner within 30 minutes
  - P1: In-app banner within 2 hours
  - P2/P3: No proactive notification unless widespread
- **Post-Incident Communication**: RCA (Root Cause Analysis) shared with affected customers (P0/P1)

**On-Call Rotation**:
- 24/7 on-call coverage for production systems
- Weekly rotation
- Primary + secondary on-call engineers
- Escalation path documented

### 3.9 Kubernetes Deployment Strategy

#### 3.9.1 Architecture Overview

**Primary Platform**: Digital Ocean Kubernetes (DOKS) for MVP and early growth
**Migration Path**: Azure Kubernetes Service (AKS) if platform scales and requires enhanced security features

**Note**: The infrastructure examples below reference AWS/EKS for illustration. These will be adapted to Digital Ocean equivalents during implementation. Digital Ocean provides managed Kubernetes (DOKS), managed databases (PostgreSQL, Redis), container registry, Spaces (object storage), and monitoring services that map to the AWS services shown below.

The gym platform deploys to **Digital Ocean Kubernetes (DOKS)** with the following architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Digital Ocean Cloud                           │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    DOKS Cluster(s)                          │ │
│  │                                                             │ │
│  │  Namespaces:                                                │ │
│  │  ├── staging        (staging environment)                  │ │
│  │  ├── production     (production environment)               │ │
│  │  └── monitoring     (Prometheus, Grafana)                  │ │
│  │                                                             │ │
│  │  Components per namespace:                                  │ │
│  │  ├── gym-api        (Deployment, Service, HPA)            │ │
│  │  ├── postgresql     (StatefulSet)                          │ │
│  │  ├── redis          (Deployment for caching/sessions)      │ │
│  │  └── nginx-ingress  (Ingress Controller)                   │ │
│  │                                                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      Supporting Services                    │ │
│  │  ├── Container Registry (Docker image registry)            │ │
│  │  ├── Managed PostgreSQL (production DB)                    │ │
│  │  ├── MongoDB Atlas (production NoSQL)                      │ │
│  │  ├── Managed Redis (production cache)                      │ │
│  │  ├── Spaces (object storage for progress photos)           │ │
│  │  ├── Monitoring + Logs (logs and metrics)                  │ │
│  │  ├── App Platform Secrets (secrets management)             │ │
│  │  └── Load Balancer (via Ingress)                           │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.9.2 Cluster Configuration

**Development/Staging Cluster** (`gym-staging-cluster`):
- **Region**: NYC3 (New York)
- **Node Pool**: 2-4 nodes (Basic droplets, 2 vCPU / 4 GB RAM)
- **Kubernetes Version**: 1.28+
- **Namespaces**: `staging`, `monitoring`

**Production Cluster** (`gym-production-cluster`):
- **Region**: NYC3 (New York)
- **Node Pools**:
  - API nodes: 3-10 nodes (General Purpose, 4 vCPU / 8 GB RAM)
  - Database nodes (if self-hosting): 3 nodes (Memory-Optimized) with taints for StatefulSets
- **Kubernetes Version**: 1.28+
- **Namespaces**: `production`, `monitoring`
- **High Availability**: Multi-node deployment across availability zones

**Note**: The examples below use AWS eksctl commands for reference. Digital Ocean Kubernetes can be created via:
- Digital Ocean web console
- doctl CLI: `doctl kubernetes cluster create`
- Terraform Digital Ocean provider

#### 3.9.3 Database Strategy

**PostgreSQL (SQL Database)**:
- **Staging**: PostgreSQL in K8s (StatefulSet)
- **Production**: Managed PostgreSQL (Digital Ocean Managed Databases)
- **Configuration**:
  - Engine: PostgreSQL 15
  - Instance: Scaled appropriately (production), basic tier (staging)
  - High Availability: Yes (production)
  - Backups: Automated daily backups, 7-day retention
  - Encryption: At rest and in transit

**Migration Strategy**:
```bash
# Migrations run via init container in gym-api deployment
initContainers:
- name: migrate
  image: gym-api:latest
  command: ['npm', 'run', 'migrate']
  env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: gym-api-secrets
        key: database-url
```

**MongoDB (NoSQL Database)**:
- **Staging**: MongoDB in K8s (StatefulSet)
- **Production**: MongoDB Atlas or Digital Ocean Managed MongoDB
- **Configuration**:
  - Cluster: Scaled appropriately (production), basic tier (staging)
  - Region: NYC3 (aligned with DOKS)
  - Backups: Continuous (point-in-time recovery)
  - Network: VPC Peering with DOKS VPC

**Redis (Cache & Sessions)**:
- **Staging**: Redis in K8s (Deployment)
- **Production**: Digital Ocean Managed Redis
- **Configuration**:
  - Node type: Scaled appropriately
  - Cluster mode: Enabled (for high availability)
  - Backups: Daily snapshots

#### 3.9.4 Deployment Strategies

**Rolling Update (Default)**:

For staging deployments:
```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

**Blue/Green Deployment (Production)**:

Two separate deployments (`gym-api-blue`, `gym-api-green`):
1. Deploy new version to green deployment
2. Run smoke tests against green
3. Switch service selector to green
4. Monitor for 5 minutes
5. Scale down blue deployment

**Canary Deployment (Alternative)**:

Using **Flagger** (progressive delivery):
- Gradual traffic shift from stable to canary version
- Automated rollback on metric degradation
- Integration with Prometheus for metric-based validation

#### 3.9.5 Cost Optimization

**Strategies**:
- Use lower-tier droplets for non-production nodes
- Scale down staging cluster during off-hours
- Right-size pod resources (avoid over-provisioning)
- Use managed services with appropriate tier sizing
- Monitor usage and adjust resources based on actual load

**Estimated Monthly Costs** (Digital Ocean):
- **Staging**:
  - DOKS cluster: Basic tier nodes
  - Managed PostgreSQL: Basic tier
  - Total: ~$150-250/month

- **Production**:
  - DOKS cluster: General Purpose nodes with autoscaling
  - Managed PostgreSQL: High availability tier
  - Managed Redis: Appropriate tier
  - Load Balancer: Digital Ocean Load Balancer
  - Total: ~$800-1,200/month (scales with usage)

#### 3.9.6 Security Best Practices

**Network Policies**:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: gym-api-network-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: gym-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 3000
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 5432  # PostgreSQL
    - protocol: TCP
      port: 27017 # MongoDB
    - protocol: TCP
      port: 6379  # Redis
```

**Pod Security Standards**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

**Image Scanning**:
- Scan all images with vulnerability scanning tools
- Fail CI if critical vulnerabilities found
- Regular security updates for base images

---

## 4. Compliance & Privacy

**Classification**: Fitness/wellness platform (NOT medical/healthcare, NOT HIPAA-covered)

**Initial market**: US-only (GDPR deferred until international expansion)

### 4.1 Data Retention Rules

#### Active Clients (`client_status = 'active'`)

- **Workouts, PRs, measurements**: Unlimited retention
- **Check-ins, schedule history**: Unlimited retention
- **Progress photos**: Keep until client deletes or requests removal
- **Health metrics**: Keep until client disconnects integration or requests removal

#### Inactive Clients (No Activity for 3+ Years)

- **Workouts, PRs, personal data**: Purge after 3 years of inactivity
- **Payment information**: Retain for 7 years (tax/legal compliance)
- **After 3 years**: Soft-delete and anonymize (see Data Anonymization)

#### Prospects (`client_status = 'prospect' | 'lost'`)

- Keep for 2 years after status change
- Then soft-delete and anonymize
- May re-engage prospects within 2-year window

#### Payment & Financial Records

- **Retention**: Minimum 7 years (legal/tax requirement)
- Applies even if client deleted
- Archive to cold storage after 1 year

#### Audit Logs

- Keep for 7 years (compliance/legal)
- Archive after 1 year to cold storage
- Store member numbers only (not full PII)

#### System Logs & Metrics

- **Operational logs**: Keep for 90 days (debugging, performance)
- **Aggregated metrics**: Keep indefinitely

### 4.2 Data Anonymization (Soft Delete)

When client requests deletion or becomes inactive:

**1. Soft Delete (Never Hard Delete)**:
- Set `client_status = 'deleted'`, `deleted = true`
- Preserve referential integrity (foreign keys remain)

**2. Anonymize PII**:
- Replace `name` → "Deleted User #{member_number}"
- Clear: email, phone, address, date_of_birth
- Clear: progress photos (delete from object storage)
- Clear: health data
- Clear: AI summaries
- Keep: `client_id`, `account_id`, member_number (for audit trail)

**3. Retain Payment Data (7 Years)**:
- Payment history stays linked to anonymized client record
- Stripe customer data retained
- Used for tax reporting, dispute resolution

**4. Anonymize Workout Data (Optional)**:
- Could clear workout notes/comments
- Keep: Exercise names, sets, reps, weights (anonymous stats)
- PRs linked to "Deleted User" for gym analytics

### 4.3 Right to Be Forgotten (User-Initiated)

#### Client Requests Deletion

1. Client submits deletion request (or primary member for sub-member)
2. System processes within 30 days
3. All data anonymized EXCEPT payment info (7-year retention)
4. Confirmation email sent
5. Audit log records request with member number only

#### Gym Admin Manual Delete

1. Only gym administrators can delete clients
2. System shows warning: "Deleting will anonymize all data. Payment history will be retained for tax purposes (7 years). This cannot be undone."
3. Admin confirms deletion
4. Same anonymization process as above
5. Payment history survives with "Deleted User #{member_number}" placeholder

### 4.4 Data Export (Data Portability)

#### Export Formats (Async Process)

- `data.json` - Complete machine-readable export
- Multiple CSV files (`workouts.csv`, `prs.csv`, `measurements.csv`, `check_ins.csv`, etc.)
- `summary.pdf` - Human-readable report with key stats, graphs, PRs
- `progress_photos/` - Folder with all photos

#### Export Contents

- Profile & account info
- All workouts (exercises, sets, reps, weights, measurements)
- PRs (personal records)
- Check-in history
- Schedule history
- Progress photos (signed URLs for download)
- Health metric samples (if connected)
- AI summaries

#### Export Process

1. Client or primary member requests export
2. System generates ZIP file asynchronously
3. Email sent when ready with signed download link (expires in 7 days)
4. **Audit trail**: Log export request with member number only (GDPR compliance)
5. Gyms can see audit log showing when export was requested (member number only, not contents)

### 4.5 Age Restrictions & COPPA Compliance

#### Under 13

- Cannot create own account (COPPA compliance)
- Must be added as sub-member by primary member (parent/guardian)
- No login credentials (User) created
- Gym/trainer manages all data
- Parent contact info required
- Parent can request data export/deletion through primary member account

#### Ages 13-17

- Can have login if primary member (parent/guardian) grants it
- Primary member controls all privacy settings
- Primary member can revoke login at any time

#### Ages 18+

- Full independent account capabilities
- Can request transfer to own account ("emancipation")
- Full control over own data export/deletion requests

### 4.6 US Compliance (CCPA)

**Applies**: Platform has California users

**Requirements Met**:
- ✅ Privacy policy disclosing data collection/use
- ✅ Right to access personal data (data export feature)
- ✅ Right to delete personal data (deletion feature with 7-year payment retention)
- ✅ "Do Not Sell My Personal Information" - Platform does not sell data (state in privacy policy)
- ✅ Age restrictions (13+ with parental consent for under 18)

**Required Legal Documents (Before Launch)**:
- Privacy Policy
- Terms of Service (for gyms and clients)
- Data Processing Agreement (for gyms as data controllers)
- Cookie Policy (if using cookies on web)
- Health data disclaimers ("Not medical advice", "Consult physician before exercise")

**Data Breach Notification**:
- Notify affected users within 30-90 days (varies by state)
- Notify state attorney general (some states)
- Document breach response procedures

### 4.7 Future: GDPR Compliance (International Expansion)

**Defer Until**: Expanding to European markets

**Will Require**:
- Explicit consent for data processing
- Data Processing Agreements with gyms
- Standard Contractual Clauses (SCCs) for EU data transfers
- Cookie consent banners
- Enhanced privacy controls
- Data breach notification (72 hours)
- Potential data residency (EU data centers)

### 4.8 Email Deliverability & CAN-SPAM Compliance

**Email Service Provider**: Resend (selected for custom domain support, deliverability, and developer experience)

#### CAN-SPAM Act Compliance

**Requirements**:
- Clear identification of sender (gym name in From field)
- Accurate subject lines (no misleading content)
- Physical postal address in footer (gym's location address)
- Unsubscribe link in all marketing emails
- Honor unsubscribe requests within 10 business days
- Monitor third-party email services for compliance

**Email Types**:
- **Transactional emails** (password reset, MFA codes, session confirmations): CAN-SPAM exempt
- **Relationship messages** (measurement reminders, workout summaries): Transactional
- **Marketing/promotional emails**: Must comply with CAN-SPAM (unsubscribe, address, sender ID)

#### Deliverability Requirements

**DNS Records** (for custom email domains):
- **SPF record**: Must include Resend's SPF directive (`include:resend.com`)
- **DKIM**: Public key validation via CNAME record
- **DMARC**: Policy validation for domain authentication
- **Verification TXT record**: Ownership verification before domain activation

**Domain Restrictions**:
- Block free email domains (gmail.com, yahoo.com, hotmail.com, etc.) for custom email domains
- Reason: Maintains platform reputation and deliverability rates
- Only allow legitimate business domains

**Bounce & Complaint Handling**:
- Monitor bounce rates via Resend webhooks
- Automatically suppress hard bounces (invalid addresses)
- Track complaint rates (spam reports)
- Suspend email sending if complaint rate > 0.1% (industry threshold)

**Email Volume Monitoring**:
- Track sending patterns per gym
- Flag unusual spikes (potential spam)
- Rate limit: Start with conservative limits, increase based on reputation

---

## 5. Accessibility

**Standard**: WCAG 2.1 Level AA compliance for all user-facing applications (web app, iOS app, Android app)

**Scope**: All functionality must be accessible to users with disabilities, including:
- Visual impairments (blindness, low vision, color blindness)
- Motor impairments (keyboard-only navigation)
- Cognitive impairments (clear language, consistent navigation)
- Hearing impairments (visual alternatives for audio content)

### 5.1 WCAG 2.1 Level AA Requirements

#### Perceivable

**Text Alternatives (1.1.1)**:
- Alt text for all images, icons, and non-text content
- Descriptive alternative text that conveys purpose and meaning

**Captions (1.2.1-1.2.5)**:
- Captions for video content (if any)
- Audio descriptions where applicable

**Adaptable (1.3.1-1.3.5)**:
- Semantic HTML markup (headings, lists, tables, forms)
- Programmatically determinable relationships
- Meaningful sequence preserved when CSS disabled
- Orientation support (portrait and landscape)
- Identify input purpose with autocomplete attributes

**Distinguishable (1.4.1-1.4.13)**:
- **Color contrast**: Minimum 4.5:1 for normal text, 3:1 for large text
- **Color not sole indicator**: Don't rely on color alone to convey information
- **Text resize**: Support up to 200% zoom without loss of functionality
- **Reflow**: Content reflows at 400% zoom (no horizontal scrolling)
- **Text spacing**: Support increased line height, letter spacing, word spacing
- **Non-text contrast**: 3:1 for UI components and graphical objects

#### Operable

**Keyboard Accessible (2.1.1-2.1.4)**:
- All functionality available via keyboard
- No keyboard traps
- Visible focus indicators (2:1 contrast minimum)
- Logical tab order

**Enough Time (2.2.1-2.2.2)**:
- No time limits, or ability to extend/disable
- Pause/stop/hide for moving content

**Seizures (2.3.1)**:
- No content flashing more than 3 times per second

**Navigable (2.4.1-2.4.7)**:
- Skip navigation links
- Descriptive page titles
- Logical focus order
- Link purpose clear from text or context
- Multiple navigation methods (menu, search, breadcrumbs)
- Descriptive headings and labels

**Input Modalities (2.5.1-2.5.4)**:
- Gesture alternatives (swipe, pinch, drag must have single-pointer alternatives)
- Pointer cancellation (up-event activation, not down-event)
- Label in name (visible label matches accessible name)
- Motion actuation alternatives (shake, tilt must have UI alternative)

#### Understandable

**Readable (3.1.1-3.1.2)**:
- Page language declared (`lang` attribute)
- Language of parts declared when switching languages

**Predictable (3.2.1-3.2.4)**:
- No unexpected context changes on focus
- No unexpected context changes on input
- Consistent navigation across pages
- Consistent identification of components

**Input Assistance (3.3.1-3.3.4)**:
- Error identification (clear error messages)
- Labels or instructions for user input
- Error suggestions provided
- Error prevention for legal/financial/data submissions (confirmation step)

#### Robust

**Compatible (4.1.1-4.1.3)**:
- Valid HTML (no parsing errors)
- Name, role, value for all UI components (ARIA when needed)
- Status messages announced to screen readers (ARIA live regions)

### 5.2 Platform-Specific Requirements

#### Web App

**Keyboard Navigation**:
- Full keyboard navigation (Tab, Shift+Tab, Enter, Space, Arrow keys)
- Logical tab order following visual flow
- Focus management for modals and dynamic content

**ARIA Implementation**:
- ARIA landmarks for main regions (banner, navigation, main, complementary, contentinfo)
- ARIA roles for custom components (dialog, menu, tab, progressbar, etc.)
- ARIA live regions for dynamic content updates

**Screen Reader Testing**:
- NVDA (Windows)
- JAWS (Windows)
- VoiceOver (macOS)

#### iOS App

**VoiceOver Support**:
- VoiceOver support for all UI elements
- Dynamic Type support (text scales with system font size)
- VoiceOver rotor for quick navigation
- Grouped elements where appropriate (reduce verbosity)
- Custom actions for complex gestures

**Accessibility Properties**:
- `accessibilityLabel`: Clear, concise labels
- `accessibilityHint`: Additional context when needed
- `accessibilityTraits`: Proper traits for all interactive elements

**Visual Accommodations**:
- Bold Text support (alternative to color indicators)
- Reduce Motion support (disable animations if enabled)
- High contrast support

#### Android App

**TalkBack Support**:
- TalkBack support for all UI elements
- Font scaling support (up to 200% system font size)
- Content descriptions on all ImageViews and ImageButtons

**Touch Target Requirements**:
- Minimum touch target size: 48x48 dp
- Adequate spacing between interactive elements

**Accessibility Features**:
- Switch Access support (external keyboard navigation)
- Reduce Motion support
- High contrast theme support

### 5.3 Testing Requirements

#### Automated Testing

**Tools**:
- axe DevTools or similar for automated WCAG scans
- Lighthouse accessibility audits (target score: 100)

**CI/CD Integration**:
- Fail builds on critical accessibility violations
- Automated regression testing for accessibility

#### Manual Testing

**Keyboard Testing**:
- Keyboard-only navigation testing (unplug mouse)
- Test all interactive elements
- Verify focus indicators and tab order

**Screen Reader Testing**:
- Web: NVDA + Firefox, VoiceOver + Safari
- iOS: VoiceOver + Safari
- Android: TalkBack + Chrome

**Visual Testing**:
- Color contrast verification with tools (Contrast Checker)
- Color Oracle for color blindness simulation
- Zoom/reflow testing at 200% and 400%

**Form Testing**:
- Forms testing with screen reader
- Verify labels, errors, required fields
- Test error recovery flows

#### User Testing

**Requirements**:
- Include users with disabilities in beta testing
- Test with actual assistive technology users
- Gather feedback on usability, not just compliance
- Iterate based on real-world feedback

### 5.4 Accessibility Statement

**Required Content**:
- Public accessibility statement page: `/accessibility`
- Contact information for accessibility feedback
- Known limitations and workarounds
- Assistive technologies supported
- WCAG 2.1 AA conformance claim
- Date of last accessibility audit

### 5.5 Continuous Improvement

**Ongoing Processes**:
- Accessibility audits every 6 months
- User feedback mechanism for accessibility issues
- Accessibility training for developers and designers
- Accessibility review in PR process (checklist)
- Regular updates to address new issues and feedback

---

## 6. Media & Storage

### 6.1 Media Storage (Progress Photos)

**Storage Architecture**:
- Use object storage + CDN for photos
- Scalable storage for high-resolution images
- Global CDN for fast access

**Upload Flow**:
- Use short-lived, scoped, signed upload URLs
- Client-side direct upload to object storage
- Minimize server load for media uploads

**Image Processing**:
- Generate thumbnails/derivatives server-side (or via storage events)
- Multiple sizes for responsive display (thumbnail, medium, full)
- Optimize for web delivery (WebP, compression)

**Privacy & Security**:
- Strict access control; consider per-photo encryption at rest
- Signed URLs for photo access with expiration
- Row-level security (clients can only access their own photos)
- Delete from storage when client requests deletion

---

## 7. Third-Party Integrations

### 7.1 Health Integrations (Apple Health / Android Health Connect)

**User Consent**:
- Explicit user consent required before any data sync
- Allow granular sharing controls (select specific metrics)
- Clear explanation of what data is shared and why

**Data Minimization**:
- Minimize data collection: only metrics necessary for coaching
- Don't request permissions for unused data types

**Sync Reliability**:
- Handle revoked permissions gracefully
- Partial data sync support (when some metrics unavailable)
- Re-sync windows for catching up after offline periods
- Background sync when app not active

**Data Provenance**:
- Retain provider/source metadata (Apple Health, Fitbit, etc.)
- Track data source for troubleshooting and accuracy
- Display source in UI for transparency

### 7.2 Agreements & E-Signature (Post-MVP)

**Status**: Post-MVP feature. Not included in initial launch. Will be added in a future release once core platform features are stable.

**Future Implementation**: Gyms will be able to upload and manage agreements (e.g., membership agreements, liability waivers, trainer contracts, platform terms).

**Integration Target**: DocuSign (or equivalent e-sign provider)

**Template Management**:
- Template-based agreements per gym and/or per location
- Versioning (agreement revisions)
- Ability to require re-sign on major changes
- Admin controls for template activation/deactivation

**Signature Tracking**:
- Track `signed_by`, `signed_at`, signer identity/email
- Store IP address (if provided by e-sign provider)
- Store envelope/document IDs from DocuSign
- Complete audit trail for compliance

**Audit Trail**:
- Audit trail export (PDF + signature certificate where available)
- Tamper-proof signature records
- Legal compliance for electronic signatures

**Access Control**:
- Clients can only view/sign their own agreements
- Trainers may view client signature status
- Admins manage templates and view all agreements

**Storage**:
- Signed PDF stored securely in object storage
- Retain envelope metadata in database
- Do not store secrets in client apps
- Use secure API keys for DocuSign integration

### 7.3 Payments (Planned for Last)

**Integration**: Stripe

**Use Cases**:
- Gym subscriptions (gyms paying the platform)
- User memberships (clients/members paying a gym)

**Implementation Timeline**:
- Payments will be implemented after core scheduling/program/workout functionality is complete
- Until payments ship, plan for a "billing disabled / free mode" feature flag
- Internal admin controls for managing payment rollout

**Security**:
- Never store raw card data
- Use Stripe-hosted UI (e.g., Checkout/Payment Element)
- Webhook verification for all payment events
- PCI compliance through Stripe (avoid PCI scope)

---

## 8. Operational Algorithms

### 8.1 Busyness Calculations & Predictive Analytics

Real-time occupancy tracking and predictive arrival algorithms for facility management.

#### Time Granularity

- **15-minute buckets** for all busyness calculations
- Provides granular view without overwhelming data volume

#### Behavioral Stats for Predictions

**Client-Level Metrics**:
- `avg_workout_duration_minutes`: Average session length per client
- `avg_schedule_variance_minutes`: Average early/late arrival (positive = late, negative = early)

**Calculation Strategy**: Seasonality-aware algorithms (see Seasonality-Aware Calculations below)

#### View 1: Self-Directed Busyness

Shows gym occupancy from members without training sessions.

**Algorithm**:
```
For each 15-min time slot:
  count = number of active GymCheckIns where:
    - check_in_type = 'self_directed'
    - checked_in_at <= slot_start
    - (checked_out_at >= slot_end OR checked_out_at IS NULL)
    - expected_checkout_at >= slot_end
```

**Use Case**: Track facility occupancy for walk-in members

#### View 2: Training Busyness

Shows expected gym occupancy from scheduled training sessions.

**Algorithm**:
```
For each 15-min time slot:
  count = number of training sessions where:
    - Session is scheduled in this time window, OR
    - Session is already checked in and overlaps this window

  For scheduled (not yet checked in):
    - Use predicted_arrival_time ± confidence_interval
    - predicted_arrival = scheduled_time + avg_schedule_variance_minutes
    - confidence_interval = 1.28 * std_dev (80% confidence)

  For already checked in:
    - Use actual checked_in_at + avg_workout_duration_minutes
```

**Use Case**: Predict training area occupancy including no-shows

#### View 3: Per-Trainer Busyness

Shows individual trainer's load.

**Algorithm**:
```
For each trainer, for each 15-min time slot:
  count = number of their scheduled/active training sessions in this slot

Trainers can view:
  - Their own schedule load
  - Likelihood each client will actually show up (based on confidence interval)
```

**Use Case**: Trainer workload management and scheduling optimization

#### Seasonality-Aware Historical Calculations

Calculate `avg_workout_duration_minutes` and `avg_schedule_variance_minutes` using:

**New Clients** (<90 days tenure):
- Use last 90 days of data
- Short history, focus on recent behavior

**Regular Clients** (90-365 days tenure):
- Use last 180 days of data
- Established patterns, broader historical view

**Long-Term Clients** (>365 days tenure):
- Year-over-year comparison for same time period
- Example: For January 2026, use data from January 2025, January 2024, etc.
- Accounts for seasonal patterns (New Year's rush, summer dropoff, etc.)

#### Fallback Durations

When calculating expected checkout times, use this priority:

1. Client's `avg_workout_duration_minutes` (preferred)
2. Plan's `session_duration_minutes` if no history
3. Global default (60 minutes) if neither exists

### 8.2 Analytics & Reporting Calculations

Pre-calculated analytics for performance optimization and reporting.

#### WorkoutAnalytics Calculation (Async, After Workout Completion)

**Trigger**: When `POST /workouts/{id}/complete` called

**Calculation Job** (background worker):

1. **Query Data**:
   - Query all WorkoutExercises + WorkoutSets for this workout

2. **Calculate Volume Metrics**:
   - Sum all weight lifted (normalize to lbs for consistency)
   - Count total reps (sum of `actual_reps` across all sets)
   - Count total sets

3. **Calculate Completion Metrics**:
   - Count exercises where `status = 'complete'`
   - Count exercises where `status = 'skipped'`
   - Calculate `completion_rate` = completed / total

4. **Calculate Performance Metrics**:
   - Query PRs: check if any new PRs set this workout
   - Count `prs_achieved_count`
   - Optional: Calculate intensity score (avg weight as % of PR)

5. **Calculate Duration**:
   - `duration_minutes = (ended_at - started_at) / 60`

6. **Persist Results**:
   - Create WorkoutAnalytics record with all calculated metrics
   - Update client's `avg_workout_duration_minutes` (rolling average)

**Real-Time Preview** (During Workout, Not Persisted):
- As trainer logs sets, UI shows live calculations:
  - Current total weight lifted
  - Current total reps
  - Estimated workout duration
- Displayed in UI but not saved until workout complete

#### GymAnalytics Calculation (Nightly Rollup)

**Trigger**: Nightly job at 2 AM gym local time (using `Gym.timezone` field, e.g., "America/New_York")

**Daily Rollup**:

Calculate previous day metrics:

- **Revenue**: Sum payments from `ClientMembership.stripe_metadata.last_payment_at` where date = yesterday
- **Clients**: Count clients where `client_status IN ('active', 'trial')`
- **New clients**: Count clients where `created_at` between yesterday start/end
- **Churned clients**: Count ClientMemberships where `status = 'canceled'` AND `canceled_at` = yesterday
- **Workouts**: Count workouts where `ended_at` between yesterday start/end
- **Check-ins**: Count GymCheckIns where `checked_in_at` = yesterday
- **Active trainers**: Count trainers with at least 1 workout yesterday

Create GymAnalytics record with `period_type = 'day'`

**Weekly Rollup**:
- Run on Mondays
- Aggregate last 7 days of daily rollups
- Calculate weekly averages and totals

**Monthly Rollup**:
- Run on 1st of month
- Aggregate last 30 days
- Calculate retention rate: `(clients_end - churned) / clients_start * 100`

**Quarterly/Yearly Rollups**:
- Same pattern, larger time windows
- Long-term trend analysis

**Admin Dashboard Queries**:

Pre-calculated rollups enable fast queries without expensive aggregations:

- "Revenue this month": `SELECT total_revenue FROM GymAnalytics WHERE period_type = 'month' AND period_start = first_of_month`
- "Client growth": Query monthly rollups, chart `new_clients - churned_clients`
- Historical data: Archive to cold storage after 1 year

---

## Appendix: Testing & Quality Assurance

### Performance Testing

**Load Testing**:
- Simulate peak concurrent users
- Verify latency targets under load
- Identify bottlenecks and optimization opportunities

**Stress Testing**:
- Test beyond expected capacity
- Verify graceful degradation
- Test recovery after overload

### Security Testing

**Penetration Testing**:
- Annual third-party penetration testing
- Test authentication and authorization
- Verify data access controls

**Vulnerability Scanning**:
- Automated dependency scanning
- Regular security updates
- CVE monitoring and patching

### Compliance Audits

**Privacy Compliance**:
- Regular privacy audits
- Data retention verification
- Right to be forgotten testing

**Accessibility Audits**:
- Semi-annual WCAG compliance audits
- User testing with assistive technology users
- Continuous improvement based on findings

---

## Document Version History

- **Version 1.0** (2026-01-19): Initial comprehensive non-functional requirements document


## Appendix: Merged from REQUIREMENTS.md (legacy)

### 4. Non-Functional Requirements

### 4.1 Media Storage (Progress Photos)

- Use object storage + CDN for photos
- Upload flow should use short-lived, scoped, signed upload URLs
- Generate thumbnails/derivatives server-side (or via storage events)
- Privacy: strict access control; consider per-photo encryption at rest

### 4.2 Health Integrations (Apple Health / Android)

- Explicit user consent required; allow granular sharing controls
- Minimize data collection: only metrics necessary for coaching
- Sync reliability: handle revoked permissions, partial data, and re-sync windows
- Data provenance: retain provider/source metadata

### 4.3 Agreements & E-Signature (Before Payments)

Gyms can upload and manage agreements (e.g., membership agreements, liability waivers, trainer contracts, platform terms).

**Integration target**: DocuSign (or equivalent e-sign provider)

**Requirements**:
- Template-based agreements per gym and/or per location
- Versioning (agreement revisions) and ability to require re-sign on major changes
- Signature tracking: `signed_by`, `signed_at`, signer identity/email, IP address (if provided), envelope/document IDs
- Audit trail export (PDF + signature certificate where available)
- Access rules: clients can only view/sign their own; trainers may view client signature status; admins manage templates
- Storage: signed PDF stored securely; retain envelope metadata; do not store secrets in client apps

### 4.4 Payments (Planned for Last)

The system will support Stripe for:
- Gym subscriptions (gyms paying the platform)
- User memberships (clients/members paying a gym)

Payments will be implemented after core scheduling/program/workout functionality is complete.

Until payments ship, plan for a "billing disabled / free mode" feature flag and internal admin controls.

### 4.5 Security

- Role-based access control (Admin/Trainer/FrontDesk/Client)
- Users can have multiple roles
- Object-level authorization (trainer can only access assigned clients unless admin)
- Audit log for critical changes
- Payments: never store raw card data; use Stripe-hosted UI (e.g., Checkout/Payment Element) and webhook verification

### 4.6 Reliability + Performance

**API latency targets**:

*Real-time operations* (user waiting, critical path):
- Authentication (login, token refresh)
- Workout logging (start workout, log set, complete exercise)
- Scheduling (check availability, book session)
- Check-in operations
- **Target**: p95 < 200ms, p99 < 500ms

*Dashboard/reporting operations* (acceptable delay):
- Analytics queries
- Trainer dashboards
- Client progress reports
- Workout history
- **Target**: p95 < 1s, p99 < 2s

*Background operations* (async, no user waiting):
- AI summary generation
- Usage metering rollups
- Email/push notifications
- **Target**: Best effort, no strict SLA

**Offline-first strategy**:

*Mobile apps* (iOS/Android): **Full offline capability**
- Local database for all critical operations
- Sync in background when connection available
- Works without internet for 30 days of cached data

*Web app*: **Online-only**
- Requires stable internet connection
- Admins typically work from office/stable environments

**Offline-capable operations** (mobile only):
- Add/edit clients and prospects
- Sign existing e-signature agreements (queued for server signature)
- Check in clients (workout start)
- Log workout data (sets, reps, measurements)
- Complete workouts
- View schedules (cached last 30 days)
- View programs (cached)
- View client profiles + recent history (cached last 30 days)
- Upload progress photos (queued for upload)

**Online-only operations** (all platforms):
- Admin functions (gym settings, user management, bulk operations)
- Creating/editing programs
- Reports and analytics
- Payment/billing operations
- Real-time busyness calculations (requires live data)

**Sync strategy**:
- Background sync on connection resume
- Conflict resolution: If two trainers log same workout offline → log both (edge case, alert admin)
- Optimistic UI: Show changes immediately, sync in background
- Cache duration: Last 30 days of historical data locally

**Usage metering**:
- Async/event-based counting (does not impact request latency)
- Rollup calculations run on schedule (nightly/hourly)

### 4.7 Data Retention & Privacy

**Initial market**: US-only (GDPR deferred until international expansion)

**Classification**: Fitness/wellness platform (NOT medical/healthcare, NOT HIPAA-covered)

#### Data Retention Rules

**Active clients** (`client_status = 'active'`):
- Workouts, PRs, measurements: **Unlimited retention**
- Check-ins, schedule history: **Unlimited retention**
- Progress photos: Keep until client deletes or requests removal
- Health metrics: Keep until client disconnects integration or requests removal

**Inactive clients** (no activity for 3+ years):
- Workouts, PRs, personal data: **Purge after 3 years of inactivity**
- Payment information: **Retain for 7 years** (tax/legal compliance)
- After 3 years: Soft-delete and anonymize (see below)

**Prospects** (`client_status = 'prospect' | 'lost'`):
- Keep for **2 years** after status change
- Then soft-delete and anonymize
- May re-engage prospects within 2-year window

**Payment & financial records**:
- **Retain for 7 years minimum** (legal/tax requirement)
- Applies even if client deleted
- Archive to cold storage after 1 year

**Audit logs**:
- Keep for **7 years** (compliance/legal)
- Archive after 1 year to cold storage
- Store member numbers only (not full PII)

**System logs & metrics**:
- Keep for **90 days** (debugging, performance)
- Aggregated metrics: Keep indefinitely

#### Data Anonymization (Soft Delete)

When client requests deletion or becomes inactive:

1. **Soft delete** (never hard delete):
   - Set `client_status = 'deleted'`, `deleted = true`
   - Preserve referential integrity (foreign keys remain)

2. **Anonymize PII**:
   - Replace `name` → "Deleted User #{member_number}"
   - Clear: email, phone, address, date_of_birth
   - Clear: progress photos (delete from object storage)
   - Clear: health data
   - Clear: AI summaries
   - Keep: `client_id`, `account_id`, member_number (for audit trail)

3. **Retain payment data** (7 years):
   - Payment history stays linked to anonymized client record
   - Stripe customer data retained
   - Used for tax reporting, dispute resolution

4. **Anonymize workout data** (optional):
   - Could clear workout notes/comments
   - Keep: Exercise names, sets, reps, weights (anonymous stats)
   - PRs linked to "Deleted User" for gym analytics

#### Right to Be Forgotten (User-Initiated)

**Client requests deletion**:
1. Client submits deletion request (or primary member for sub-member)
2. System processes within 30 days
3. All data anonymized EXCEPT payment info (7-year retention)
4. Confirmation email sent
5. Audit log records request with member number only

**Gym admin manual delete**:
1. Only gym administrators can delete clients
2. System shows warning: "Deleting will anonymize all data. Payment history will be retained for tax purposes (7 years). This cannot be undone."
3. Admin confirms deletion
4. Same anonymization process as above
5. Payment history survives with "Deleted User #{member_number}" placeholder

#### Data Export (Data Portability)

**Export formats** (async process):
- `data.json` - Complete machine-readable export
- Multiple CSV files (`workouts.csv`, `prs.csv`, `measurements.csv`, `check_ins.csv`, etc.)
- `summary.pdf` - Human-readable report with key stats, graphs, PRs
- `progress_photos/` - Folder with all photos

**Export contents**:
- Profile & account info
- All workouts (exercises, sets, reps, weights, measurements)
- PRs (personal records)
- Check-in history
- Schedule history
- Progress photos (signed URLs for download)
- Health metric samples (if connected)
- AI summaries

**Export process**:
1. Client or primary member requests export
2. System generates ZIP file asynchronously
3. Email sent when ready with signed download link (expires in 7 days)
4. **Audit trail**: Log export request with member number only (GDPR compliance)

**Gym visibility**: Gyms can see audit log showing when export was requested (member number only, not contents)

#### Age Restrictions & COPPA Compliance

**Under 13**:
- Cannot create own account (COPPA compliance)
- Must be added as sub-member by primary member (parent/guardian)
- No login credentials (User) created
- Gym/trainer manages all data
- Parent contact info required
- Parent can request data export/deletion through primary member account

**Ages 13-17**:
- Can have login if primary member (parent/guardian) grants it
- Primary member controls all privacy settings
- Primary member can revoke login at any time

**Ages 18+**:
- Full independent account capabilities
- Can request transfer to own account ("emancipation")
- Full control over own data export/deletion requests

#### US Compliance (CCPA)

**Applies**: Platform has California users

**Requirements met**:
- ✅ Privacy policy disclosing data collection/use
- ✅ Right to access personal data (data export feature)
- ✅ Right to delete personal data (deletion feature with 7-year payment retention)
- ✅ "Do Not Sell My Personal Information" - Platform does not sell data (state in privacy policy)
- ✅ Age restrictions (13+ with parental consent for under 18)

**Required legal documents** (before launch):
- Privacy Policy
- Terms of Service (for gyms and clients)
- Data Processing Agreement (for gyms as data controllers)
- Cookie Policy (if using cookies on web)
- Health data disclaimers ("Not medical advice", "Consult physician before exercise")

**Data breach notification**:
- Notify affected users within 30-90 days (varies by state)
- Notify state attorney general (some states)
- Document breach response procedures

#### Future: GDPR Compliance (International Expansion)

**Defer until**: Expanding to European markets

**Will require**:
- Explicit consent for data processing
- Data Processing Agreements with gyms
- Standard Contractual Clauses (SCCs) for EU data transfers
- Cookie consent banners
- Enhanced privacy controls
- Data breach notification (72 hours)
- Potential data residency (EU data centers)

### 4.8 Accessibility (WCAG Compliance)

**Standard**: WCAG 2.1 Level AA compliance for all user-facing applications (web app, iOS app, Android app)

**Scope**: All functionality must be accessible to users with disabilities, including:
- Visual impairments (blindness, low vision, color blindness)
- Motor impairments (keyboard-only navigation)
- Cognitive impairments (clear language, consistent navigation)
- Hearing impairments (visual alternatives for audio content)

#### WCAG 2.1 Level AA Requirements

**Perceivable**:
- **Text alternatives** (1.1.1): Alt text for all images, icons, and non-text content
- **Captions** (1.2.1-1.2.5): Captions for video content (if any)
- **Adaptable** (1.3.1-1.3.5):
  - Semantic HTML markup (headings, lists, tables, forms)
  - Programmatically determinable relationships
  - Meaningful sequence preserved when CSS disabled
  - Orientation support (portrait and landscape)
  - Identify input purpose with autocomplete attributes
- **Distinguishable** (1.4.1-1.4.13):
  - **Color contrast**: Minimum 4.5:1 for normal text, 3:1 for large text
  - **Color not sole indicator**: Don't rely on color alone to convey information
  - **Text resize**: Support up to 200% zoom without loss of functionality
  - **Reflow**: Content reflows at 400% zoom (no horizontal scrolling)
  - **Text spacing**: Support increased line height, letter spacing, word spacing
  - **Non-text contrast**: 3:1 for UI components and graphical objects

**Operable**:
- **Keyboard accessible** (2.1.1-2.1.4):
  - All functionality available via keyboard
  - No keyboard traps
  - Visible focus indicators (2:1 contrast minimum)
  - Logical tab order
- **Enough time** (2.2.1-2.2.2):
  - No time limits, or ability to extend/disable
  - Pause/stop/hide for moving content
- **Seizures** (2.3.1): No content flashing more than 3 times per second
- **Navigable** (2.4.1-2.4.7):
  - Skip navigation links
  - Descriptive page titles
  - Logical focus order
  - Link purpose clear from text or context
  - Multiple navigation methods (menu, search, breadcrumbs)
  - Descriptive headings and labels
- **Input modalities** (2.5.1-2.5.4):
  - Gesture alternatives (swipe, pinch, drag must have single-pointer alternatives)
  - Pointer cancellation (up-event activation, not down-event)
  - Label in name (visible label matches accessible name)
  - Motion actuation alternatives (shake, tilt must have UI alternative)

**Understandable**:
- **Readable** (3.1.1-3.1.2):
  - Page language declared (`lang` attribute)
  - Language of parts declared when switching languages
- **Predictable** (3.2.1-3.2.4):
  - No unexpected context changes on focus
  - No unexpected context changes on input
  - Consistent navigation across pages
  - Consistent identification of components
- **Input assistance** (3.3.1-3.3.4):
  - Error identification (clear error messages)
  - Labels or instructions for user input
  - Error suggestions provided
  - Error prevention for legal/financial/data submissions (confirmation step)

**Robust**:
- **Compatible** (4.1.1-4.1.3):
  - Valid HTML (no parsing errors)
  - Name, role, value for all UI components (ARIA when needed)
  - Status messages announced to screen readers (ARIA live regions)

#### Platform-Specific Requirements

**Web App**:
- Full keyboard navigation (Tab, Shift+Tab, Enter, Space, Arrow keys)
- ARIA landmarks for main regions (banner, navigation, main, complementary, contentinfo)
- ARIA roles for custom components (dialog, menu, tab, progressbar, etc.)
- Focus management for modals and dynamic content
- Screen reader testing with NVDA (Windows), JAWS (Windows), VoiceOver (macOS)

**iOS App**:
- VoiceOver support for all UI elements
- Dynamic Type support (text scales with system font size)
- VoiceOver rotor for quick navigation
- Grouped elements where appropriate (reduce verbosity)
- Custom actions for complex gestures
- `accessibilityLabel`, `accessibilityHint`, `accessibilityTraits` on all interactive elements
- Bold Text support (alternative to color indicators)
- Reduce Motion support (disable animations if enabled)

**Android App**:
- TalkBack support for all UI elements
- Font scaling support (up to 200% system font size)
- Content descriptions on all ImageViews and ImageButtons
- Touch target size: minimum 48x48 dp
- Switch Access support (external keyboard navigation)
- Reduce Motion support

#### Testing Requirements

**Automated testing**:
- Use axe DevTools or similar for automated WCAG scans
- CI/CD integration: Fail builds on critical accessibility violations
- Lighthouse accessibility audits (target score: 100)

**Manual testing**:
- Keyboard-only navigation testing (unplug mouse)
- Screen reader testing:
  - Web: NVDA + Firefox, VoiceOver + Safari
  - iOS: VoiceOver + Safari
  - Android: TalkBack + Chrome
- Color contrast verification with tools (Contrast Checker, Color Oracle for color blindness simulation)
- Zoom/reflow testing at 200% and 400%
- Forms testing with screen reader (labels, errors, required fields)

**User testing**:
- Include users with disabilities in beta testing
- Test with actual assistive technology users
- Gather feedback on usability, not just compliance

#### Accessibility Statement

**Required**:
- Public accessibility statement page: `/accessibility`
- Contact information for accessibility feedback
- Known limitations and workarounds
- Assistive technologies supported
- WCAG 2.1 AA conformance claim

**Continuous improvement**:
- Accessibility audits every 6 months
- User feedback mechanism for accessibility issues
- Accessibility training for developers and designers
- Accessibility review in PR process (checklist)

---
