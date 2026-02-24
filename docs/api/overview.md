# API Overview

This document defines the API conventions and standards for the gym management system.

---

## Purpose

Single source of truth for all clients (web, iOS, Android, integrations).

## Responsibilities

- Authentication + authorization
- Domain services (program assignment, workout start/finish, schedule booking)
- Validation + business rules enforcement
- Audit logging

## Design Principles

- RESTful architecture with resource-based URLs
- OAuth2 2.0 for authentication
- JSON request/response format
- HTTP status codes follow standard conventions
- Rate limiting to prevent abuse
- Comprehensive error responses with error codes

---

## Base URL

```
Production: https://api.gymapp.com/v1
Staging:    https://api.staging.gymapp.com/v1
```

---

## Conventions

### Timestamp Format

**Standard**: ISO 8601 with UTC timezone

```json
{
  "started_at": "2026-01-19T10:30:00Z",
  "date": "2026-01-19"
}
```

**Rules**:
- All timestamps stored in UTC
- Responses always return UTC with `Z` suffix
- Clients convert to local timezone for display

### URL Structure

```
GET    /v1/{resource}           # List
POST   /v1/{resource}           # Create
GET    /v1/{resource}/{id}      # Read
PUT    /v1/{resource}/{id}      # Update (full)
PATCH  /v1/{resource}/{id}      # Update (partial)
DELETE /v1/{resource}/{id}      # Delete
```

### Pagination

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

Query params: `?page=1&per_page=20`

### Filtering

```
GET /v1/clients?status=active&trainer_id=xxx
GET /v1/workouts?started_after=2026-01-01&started_before=2026-01-31
```

### Sorting

```
GET /v1/clients?sort=name&order=asc
GET /v1/workouts?sort=started_at&order=desc
```

---

## Authentication

All endpoints (except `/auth/*`) require Bearer token:

```
Authorization: Bearer <access_token>
```

See [auth.md](auth.md) for authentication endpoints.

---

## Request Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes* | Bearer token (*except auth endpoints) |
| `Content-Type` | For POST/PUT/PATCH | `application/json` |
| `Accept` | Optional | `application/json` (default) |
| `X-Request-ID` | Optional | Client-generated request ID for tracing |
| `X-Gym-ID` | Contextual | Gym context for multi-gym users |

---

## Response Format

### Success Response

```json
{
  "data": { ... },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

### List Response

```json
{
  "data": [ ... ],
  "pagination": { ... },
  "meta": { ... }
}
```

### Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      { "field": "email", "message": "Invalid email format" }
    ]
  },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Success |
| 201 | Created - Resource created |
| 204 | No Content - Success, no body |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Auth required |
| 403 | Forbidden - No permission |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource conflict |
| 422 | Unprocessable - Business rule violation |
| 429 | Too Many Requests - Rate limited |
| 500 | Server Error - Internal error |

---

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `AUTHENTICATION_REQUIRED` | Missing or invalid token |
| `PERMISSION_DENIED` | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | Resource doesn't exist |
| `RESOURCE_CONFLICT` | Duplicate or conflict |
| `BUSINESS_RULE_VIOLATION` | Business logic error |
| `RATE_LIMITED` | Too many requests |
| `INTERNAL_ERROR` | Server error |

---

## Rate Limiting

| Endpoint Category | Limit | Window |
|-------------------|-------|--------|
| Authentication | 10 req | 1 minute |
| Read (GET) | 100 req | 1 minute |
| Write (POST/PUT/PATCH) | 30 req | 1 minute |
| Bulk operations | 5 req | 1 minute |

Response headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

---

## API Endpoints Index

| Category | File | Key Endpoints |
|----------|------|---------------|
| Authentication | [auth.md](auth.md) | `/auth/*` |
| Gyms & Locations | [gyms.md](gyms.md) | `/gyms/*`, `/locations/*` |
| Clients | [clients.md](clients.md) | `/clients/*`, `/accounts/*` |
| Memberships | [memberships.md](memberships.md) | `/memberships/*`, `/plans/*` |
| Training | [training.md](training.md) | `/programs/*`, `/workouts/*`, `/exercises/*` |
| Scheduling | [scheduling.md](scheduling.md) | `/schedules/*`, `/check-ins/*` |
| Measurements | [measurements.md](measurements.md) | `/measurements/*`, `/goals/*` |
