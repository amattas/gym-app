# Observability Requirements

This document defines logging, monitoring, alerting, and tracing requirements.

---

## Logging

### Log Levels

| Level | Use Case |
|-------|----------|
| ERROR | Unhandled exceptions, failed operations |
| WARN | Recoverable issues, deprecation notices |
| INFO | Business events, key operations |
| DEBUG | Detailed debugging (not in prod) |

### Structured Logging

```json
{
  "timestamp": "2026-01-20T10:30:00Z",
  "level": "INFO",
  "message": "Workout completed",
  "service": "api",
  "request_id": "req_abc123",
  "user_id": "uuid",
  "gym_id": "uuid",
  "duration_ms": 150
}
```

### Required Fields

| Field | Description |
|-------|-------------|
| timestamp | ISO 8601 UTC |
| level | Log level |
| message | Human-readable message |
| service | Service name |
| request_id | Request correlation ID |

### Sensitive Data

**Never log**:
- Passwords
- API tokens
- Credit card numbers
- Full SSN

**Mask partially**:
- Email (j***@example.com)
- Phone (***-***-1234)

---

## Metrics

### Application Metrics

| Metric | Type | Labels |
|--------|------|--------|
| http_requests_total | Counter | method, path, status |
| http_request_duration_seconds | Histogram | method, path |
| active_users | Gauge | gym_id |
| background_jobs_total | Counter | queue, status |

### Business Metrics

| Metric | Type |
|--------|------|
| workouts_completed | Counter |
| check_ins_total | Counter |
| active_memberships | Gauge |
| revenue_collected | Counter |

### Infrastructure Metrics

| Metric | Source |
|--------|--------|
| CPU utilization | Cloud provider |
| Memory usage | Cloud provider |
| Database connections | PostgreSQL |
| Cache hit rate | Redis |

---

## Alerting

### Alert Severity

| Severity | Response | Examples |
|----------|----------|----------|
| Critical | Page immediately | Service down, data breach |
| High | Page during hours | High error rate, degraded service |
| Medium | Ticket | Elevated latency, disk usage |
| Low | Review weekly | Informational |

### Alert Rules

| Alert | Condition | Severity |
|-------|-----------|----------|
| API Down | No successful requests for 5 min | Critical |
| High Error Rate | 5xx rate > 5% for 5 min | High |
| High Latency | p99 > 2s for 10 min | Medium |
| Database CPU | > 90% for 10 min | High |
| Disk Space | > 80% used | Medium |

### Alert Channels

| Channel | Use Case |
|---------|----------|
| PagerDuty/Opsgenie | Critical alerts |
| Slack | High/Medium alerts |
| Email | Daily digest |

---

## Distributed Tracing

### Trace Context

- Propagate trace ID across services
- Include in all logs
- Pass to third-party services

### Span Attributes

| Attribute | Description |
|-----------|-------------|
| service.name | Service identifier |
| http.method | HTTP method |
| http.url | Request URL |
| http.status_code | Response status |
| db.statement | SQL query (sanitized) |

### Sampling

| Environment | Sampling Rate |
|-------------|---------------|
| Development | 100% |
| Staging | 100% |
| Production | 10% (or adaptive) |

---

## Dashboards

### Required Dashboards

#### Service Health
- Request rate
- Error rate
- Latency (p50, p95, p99)
- Active users

#### Infrastructure
- CPU, memory, disk
- Database connections
- Cache hit rate
- Queue depth

#### Business
- Daily active users
- Workouts completed
- Check-ins
- New signups

---

## Error Tracking

### Requirements

- Capture stack traces
- Group similar errors
- Track error frequency
- Link to user context

### Tools

- Sentry, Bugsnag, or similar
- Integrate with alerting
- Source map support for frontend

---

## Health Checks

### Endpoints

```http
GET /health          # Basic health
GET /health/ready    # Readiness (includes dependencies)
GET /health/live     # Liveness (basic process check)
```

### Checks

| Check | Endpoint |
|-------|----------|
| Application running | /health/live |
| Database connected | /health/ready |
| Redis connected | /health/ready |
| Migrations current | /health/ready |

---

## Log Retention

| Log Type | Retention |
|----------|-----------|
| Application logs | 90 days |
| Security logs | 1 year |
| Audit logs | 7 years |
| Metrics | 13 months |
| Traces | 30 days |
