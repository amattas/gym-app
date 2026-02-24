# Gym Management App — API Specifications

**CONFIDENTIAL**: This document contains proprietary technical information. Access restricted to authorized team members, contractors, and partners only. Do not share publicly or with competitors.

This document defines the API endpoints, integrations, and data exchange formats for the gym management system. For business requirements, see BUSINESS_REQUIREMENTS.md. For technical implementation details, see TECHNICAL_SPECIFICATIONS.md.

---

## Document Metadata

- **Version**: 1.1.0
- **Last Updated**: 2026-01-19
- **Owner**: Engineering Team
- **Status**: Approved
- **Related Documents**:
  - [BUSINESS_REQUIREMENTS.md](BUSINESS_REQUIREMENTS.md) - Business requirements
  - [TECHNICAL_SPECIFICATIONS.md](TECHNICAL_SPECIFICATIONS.md) - Technical implementation
  - [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) - Performance, security, compliance

---

## Table of Contents

1. [API Layer Overview](#1-api-layer-overview)
2. [API Conventions](#2-api-conventions)
3. [Authentication & OAuth2](#3-authentication--oauth2)
4. [Account Management](#4-account-management)
5. [Membership & Plans](#5-membership--plans)
6. [Check-In & Occupancy](#6-check-in--occupancy)
7. [Calendar & Schedule](#7-calendar--schedule)
8. [Workouts & Programs](#8-workouts--programs)
9. [Measurements & Goals](#9-measurements--goals)
10. [Progress Photos & Media](#10-progress-photos--media)
11. [Health Integrations](#11-health-integrations)
12. [Agreements & E-Signature](#12-agreements--e-signature)
13. [Analytics & Reporting](#13-analytics--reporting)
14. [Usage & Metering](#14-usage--metering-internaladmin)
15. [Plan Limits & Feature Flags](#15-plan-limits--feature-flags-internaladmin)
16. [Data Export & Privacy](#16-data-export--privacy)
17. [Gym & Location Management](#17-gym--location-management)
18. [People Management](#18-people-management)
19. [Error Responses](#19-error-responses)
20. [Rate Limiting](#20-rate-limiting)
21. [Webhooks](#21-webhooks)

---

## 1. API Layer Overview

### 1.1 Purpose

Single source of truth for all clients (web, iOS, Android, integrations).

### 1.2 Responsibilities

- Authentication + authorization
- Domain services (program assignment, workout start/finish, schedule booking)
- Validation + business rules enforcement
- Audit logging

### 1.3 API Design Principles

- RESTful architecture with resource-based URLs
- OAuth2 2.0 for authentication
- JSON request/response format
- HTTP status codes follow standard conventions
- Rate limiting to prevent abuse
- Comprehensive error responses with error codes

---

## 2. API Conventions

This section defines the standard conventions used across all API endpoints for consistency and predictability.

### 2.1 Timestamp Format & Timezone

**Standard Format**: ISO 8601 with UTC timezone

**Examples**:
- `2026-01-19T10:30:00Z` - UTC timestamp (preferred)
- `2026-01-19T10:30:00.123Z` - With milliseconds
- `2026-01-19T05:30:00-05:00` - With timezone offset (accepted, converted to UTC server-side)

**Rules**:
- All timestamps stored in database as UTC
- API responses always return UTC timestamps with `Z` suffix
- Clients responsible for converting to local timezone for display
- Date-only fields use format: `2026-01-19` (ISO 8601 date)

**Example Response**:
```json
{
  "workout_id": "uuid",
  "started_at": "2026-01-19T10:30:00Z",
  "ended_at": "2026-01-19T11:15:00Z",
  "created_at": "2026-01-19T10:29:55.123Z"
}
```

### 2.2 API Versioning

**Strategy**: URL-based versioning

**Base URL Format**: `https://{hostname}/api/v1/`

**Current Version**: `v1`

**Important**: All API endpoints documented in this specification are prefixed with `/api/v1/`. For brevity, endpoint examples show only the resource path (e.g., `/clients/{id}`) but the full URL would be `/api/v1/clients/{id}`.

**Versioning Policy**:
- Major version increments (`v1` → `v2`) for breaking changes
- Backward-compatible changes do NOT require new version
- Old versions supported for minimum 12 months after new version release
- Deprecation notices provided 6 months in advance

**Breaking Changes** (require new version):
- Removing endpoints or fields
- Changing field types
- Changing authentication requirements
- Changing error response format

**Non-Breaking Changes** (same version):
- Adding new endpoints
- Adding new optional fields to requests
- Adding new fields to responses (clients should ignore unknown fields)
- Deprecating fields (mark in docs, keep functional)

**Example Full URLs**:
```
GET https://api.gym.example.com/api/v1/clients/{id}          # Current
GET https://api.gym.example.com/api/v2/clients/{id}          # Future breaking change
```

**Documentation Convention**: Endpoint examples in this document show paths relative to the `/api/v1/` base path for readability (e.g., `GET /clients/{id}` represents `GET /api/v1/clients/{id}`).

### 2.3 Pagination

**Standard Pagination**: Cursor-based for scalability

**Query Parameters**:
- `limit` - Number of results per page (default: 20, max: 100)
- `cursor` - Opaque pagination cursor from previous response
- `order` - Sort order: `asc` or `desc` (default: `desc` for time-based, `asc` for alphabetical)

**Response Format**:
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTIzfQ==",
    "prev_cursor": "eyJpZCI6MTAwfQ==",
    "has_more": true,
    "total_count": 1500  // Optional, expensive to calculate
  }
}
```

**Example Request**:
```
GET /api/v1/workouts?limit=50&cursor=eyJpZCI6MTIzfQ==&order=desc
```

**Implementation Notes**:
- Cursor is base64-encoded JSON containing sort key(s)
- Never expose internal IDs or implementation details in cursor
- Cursor format may change without notice (clients must treat as opaque)
- If `cursor` is omitted, returns first page

**Alternative: Offset Pagination** (for specific use cases):
- Use for small datasets or admin UIs where total count is needed
- Query params: `offset`, `limit`
- Less performant for large datasets

### 2.4 Query Parameter Formats

**Date Ranges**:
- Format: `date_range=YYYY-MM-DD,YYYY-MM-DD`
- Example: `?date_range=2026-01-01,2026-01-31`
- Both start and end dates are inclusive

**Time Ranges**:
- Format: `time_range=ISO8601,ISO8601`
- Example: `?time_range=2026-01-19T00:00:00Z,2026-01-19T23:59:59Z`

**Filters (Multiple Values)**:
- Comma-separated for OR logic
- Example: `?status=active,trial,paused`
- URL-encoded: `?status=active%2Ctrial`

**Boolean Filters**:
- Use `true` or `false` (case-insensitive)
- Example: `?is_active=true`

**Search**:
- Use `q` parameter for free-text search
- Example: `?q=john+smith`

### 2.5 Request Headers

**Required Headers**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Optional Headers**:
```
X-Request-ID: {uuid}           // Client-generated request ID for tracing
X-Idempotency-Key: {uuid}      // For idempotent operations (POST/PUT)
Accept-Language: en-US         // Preferred language for error messages
```

### 2.6 Response Headers

**Standard Headers**:
```
Content-Type: application/json; charset=utf-8
X-Request-ID: {uuid}           // Echo client's request ID or server-generated
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705668000  // Unix timestamp
```

### 2.7 HTTP Status Codes

**Success**:
- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST that creates a resource
- `202 Accepted` - Async operation accepted (background job)
- `204 No Content` - Successful DELETE or operation with no response body

**Client Errors**:
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource does not exist
- `409 Conflict` - Resource conflict (e.g., duplicate email)
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded

**Server Errors**:
- `500 Internal Server Error` - Unexpected server error
- `502 Bad Gateway` - Upstream service error
- `503 Service Unavailable` - Temporary outage or maintenance
- `504 Gateway Timeout` - Upstream service timeout

### 2.8 Idempotency

**Purpose**: Prevent duplicate operations from network retries

**Supported Methods**: POST, PUT, PATCH, DELETE

**Implementation**:
- Client sends `X-Idempotency-Key` header with unique UUID
- Server stores key + response for 24 hours
- Duplicate requests with same key return cached response
- GET requests are naturally idempotent (no key needed)

**Example**:
```
POST /api/v1/workouts/start
X-Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{
  "client_id": "...",
  "trainer_id": "...",
  "started_at": "2026-01-19T10:30:00Z"
}
```

**Response** (first request):
```
201 Created
X-Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000

{ "workout_id": "...", ... }
```

**Response** (duplicate request):
```
200 OK
X-Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
X-Idempotent-Replay: true

{ "workout_id": "...", ... }  // Same response as first request
```

**Key Guidelines**:
- Generate UUIDv4 on client side
- Use same key for retries of same logical operation
- Server responds with 200 OK (not 201) for replayed requests
- Keys expire after 24 hours

### 2.9 Field Naming Conventions

**Format**: `snake_case` for all JSON fields

**Examples**:
```json
{
  "client_id": "uuid",
  "first_name": "John",
  "created_at": "2026-01-19T10:30:00Z",
  "is_active": true
}
```

**Abbreviations** (avoid unless widely understood):
- Prefer `identifier` over `id` in field names (except primary keys)
- Use `id` suffix for foreign keys: `client_id`, `trainer_id`
- Boolean fields start with `is_`, `has_`, `can_`, `should_`

### 2.10 Error Response Format

See [Section 19: Error Responses](#19-error-responses) for complete error format specification.

---

## 3. Authentication & OAuth2

### 3.1 User Authentication

**User Registration**:
- `POST /auth/register` - Create new user account with email + password
  - Request: `{ email, password }`
  - Response: `{ user_id, email, email_verification_sent: true }`

**Email Verification**:
- `GET /auth/verify-email?token={token}` - Verify email address
  - Response: `{ verified: true, message: "Email verified successfully" }`

**Password Login**:
- `POST /auth/login` - Password login, returns OAuth2 tokens
  - Request: `{ email, password }`
  - Response: `{ access_token, refresh_token, token_type: "Bearer", expires_in: 3600, mfa_required: false }`
  - If MFA enabled: `{ mfa_required: true, mfa_method: "totp", session_id }`

**Passkey Login**:
- `POST /auth/login/passkey/challenge` - Initiate passkey login, get WebAuthn challenge
  - Request: `{ email }`
  - Response: `{ challenge, rpId, allowCredentials: [...] }`
- `POST /auth/login/passkey/verify` - Verify passkey signature, return OAuth2 tokens
  - Request: `{ email, credential: {...} }`
  - Response: `{ access_token, refresh_token, token_type: "Bearer", expires_in: 3600 }`

**Logout**:
- `POST /auth/logout` - Revoke current access token
  - Headers: `Authorization: Bearer {access_token}`
  - Response: `{ message: "Logged out successfully" }`

**Password Management**:
- `POST /auth/password/forgot` - Request password reset email
  - Request: `{ email }`
  - Response: `{ message: "If that email exists, we've sent a password reset link" }`
- `POST /auth/password/reset` - Reset password with token from email
  - Request: `{ token, new_password }`
  - Response: `{ message: "Password reset successful" }`
- `PUT /auth/password/change` - Change password (requires current password)
  - Request: `{ current_password, new_password }`
  - Response: `{ message: "Password changed successfully" }`

### 3.2 Multi-Factor Authentication (MFA)

**TOTP Setup**:
- `POST /auth/mfa/totp/setup` - Generate TOTP secret, return QR code
  - Response: `{ secret, qr_code_url, backup_codes: [...] }`
- `POST /auth/mfa/totp/verify-setup` - Verify TOTP code to complete setup
  - Request: `{ code }`
  - Response: `{ mfa_enabled: true, backup_codes: [...] }`

**TOTP Verification (during login)**:
- `POST /auth/mfa/totp/verify` - Verify TOTP code during login
  - Request: `{ session_id, code }`
  - Response: `{ access_token, refresh_token, token_type: "Bearer", expires_in: 3600 }`

**Backup Codes**:
- `GET /auth/mfa/backup-codes` - Get current backup codes
  - Response: `{ backup_codes: [...], used_codes: [...] }`
- `POST /auth/mfa/backup-codes/regenerate` - Generate new backup codes
  - Response: `{ backup_codes: [...] }`
- `POST /auth/mfa/backup-codes/verify` - Verify backup code during login
  - Request: `{ session_id, code }`
  - Response: `{ access_token, refresh_token, codes_remaining: 9 }`

**Email MFA**:
- `POST /auth/mfa/email/send` - Send email MFA code
  - Request: `{ session_id }`
  - Response: `{ message: "Code sent to email", expires_in: 600 }`
- `POST /auth/mfa/email/verify` - Verify email MFA code during login
  - Request: `{ session_id, code }`
  - Response: `{ access_token, refresh_token, token_type: "Bearer", expires_in: 3600 }`

**MFA Settings**:
- `PUT /auth/mfa/method` - Switch MFA method
  - Request: `{ method: "totp" | "email" | "passkey_only" }`
  - Response: `{ mfa_method: "totp", message: "MFA method updated" }`
- `DELETE /auth/mfa/disable` - Disable MFA (requires password + current MFA code)
  - Request: `{ password, mfa_code }`
  - Response: `{ mfa_enabled: false }`

### 3.3 Passkey Management (WebAuthn/FIDO2)

**Passkey Registration**:
- `POST /auth/passkeys/register/challenge` - Generate WebAuthn registration challenge
  - Response: `{ challenge, rp: {...}, user: {...}, pubKeyCredParams: [...] }`
- `POST /auth/passkeys/register/verify` - Verify attestation, save passkey
  - Request: `{ credential: {...}, device_name: "iPhone 15" }`
  - Response: `{ passkey_id, device_name, device_type: "platform", created_at }`

**Passkey Management**:
- `GET /auth/passkeys` - List user's registered passkeys
  - Response: `{ passkeys: [{ passkey_id, device_name, device_type, created_at, last_used_at }] }`
- `PUT /auth/passkeys/{id}` - Rename passkey device
  - Request: `{ device_name: "YubiKey 5" }`
  - Response: `{ passkey_id, device_name }`
- `DELETE /auth/passkeys/{id}` - Remove passkey
  - Response: `{ message: "Passkey removed" }`

### 3.4 OAuth2 Token Management

**Token Endpoint** (supports multiple grant types):
- `POST /oauth/token`

  **Grant type: password (Resource Owner Password Credentials)**:
  - Request: `{ grant_type: "password", email, password }`
  - Response: `{ access_token, refresh_token, token_type: "Bearer", expires_in: 3600 }`

  **Grant type: authorization_code (with PKCE)**:
  - Request: `{ grant_type: "authorization_code", code, code_verifier, redirect_uri, client_id }`
  - Response: `{ access_token, refresh_token, token_type: "Bearer", expires_in: 3600 }`

  **Grant type: refresh_token**:
  - Request: `{ grant_type: "refresh_token", refresh_token }`
  - Response: `{ access_token, refresh_token, token_type: "Bearer", expires_in: 3600 }`

  **Grant type: client_credentials (server-to-server)**:
  - Headers: `Authorization: Basic {base64(client_id:client_secret)}`
  - Request: `{ grant_type: "client_credentials", scope: "gym:read clients:read" }`
  - Response: `{ access_token, token_type: "Bearer", expires_in: 3600, scope: "gym:read clients:read" }`

**Token Management**:
- `POST /oauth/token/revoke` - Revoke access or refresh token
  - Request: `{ token, token_type_hint: "access_token" | "refresh_token" }`
  - Response: `{ message: "Token revoked" }`
- `GET /oauth/token/introspect` - Check token validity, return claims
  - Request: `{ token }`
  - Response: `{ active: true, scope: "...", client_id, user_id, exp: 1234567890 }`

### 3.5 OAuth2 Authorization Flow

**Authorization Endpoint**:
- `GET /oauth/authorize` - Display consent screen
  - Query params: `?client_id=&redirect_uri=&scope=&code_challenge=&code_challenge_method=S256&state=`
  - Response: HTML consent screen
- `POST /oauth/authorize` - User approves/denies authorization
  - Request: `{ client_id, redirect_uri, scope, code_challenge, approved: true }`
  - Response: Redirect to `{redirect_uri}?code={authorization_code}&state={state}`
- `GET /oauth/authorize/callback` - Handle redirect after authorization
  - Used by client apps to receive authorization code

### 3.6 OAuth2 Client Management (gym admin only)

- `GET /oauth/clients` - List OAuth2 clients for gym
  - Response: `{ clients: [{ client_id, name, scopes_allowed, is_active, created_at }] }`
- `POST /oauth/clients` - Create new OAuth2 client/integration
  - Request: `{ name, description, redirect_uris: [...], grant_types: [...], scopes_allowed: [...] }`
  - Response: `{ client_id, client_secret, name, ...} ` (client_secret shown ONCE)
- `GET /oauth/clients/{id}` - Get client details (excludes secret)
  - Response: `{ client_id, name, redirect_uris, grant_types, scopes_allowed, is_active }`
- `PUT /oauth/clients/{id}` - Update client
  - Request: `{ name, redirect_uris, scopes_allowed }`
  - Response: `{ client_id, name, ... }`
- `POST /oauth/clients/{id}/regenerate-secret` - Regenerate client secret
  - Response: `{ client_secret }` (shown ONCE)
- `DELETE /oauth/clients/{id}` - Deactivate OAuth2 client
  - Response: `{ message: "Client deactivated", is_active: false }`

### 3.7 Active Sessions & Token Management

- `GET /auth/sessions` - List user's active sessions/tokens
  - Response: `{ sessions: [{ token_id, token_type, created_at, last_used_at, expires_at, ip_address, user_agent }] }`
- `DELETE /auth/sessions/{token_id}` - Revoke specific session
  - Response: `{ message: "Session revoked" }`
- `DELETE /auth/sessions/all` - Revoke all sessions except current
  - Response: `{ message: "All other sessions revoked", revoked_count: 5 }`

### 3.8 MCP Integration (trainer-only, OAuth2-based)

- `POST /trainers/{id}/mcp/authorize` - Initiate OAuth2 authorization for MCP
  - Response: `{ authorization_url, state }`
- `GET /trainers/{id}/mcp/callback?code=...` - OAuth2 callback, exchange code for tokens
  - Response: `{ access_token, refresh_token, expires_in: 3600, scope: "mcp:trainer" }`
- `GET /trainers/{id}/mcp/status` - Check if MCP enabled
  - Response: `{ enabled: true, scopes: ["mcp:trainer"], created_at, last_used_at }`
- `DELETE /trainers/{id}/mcp/revoke` - Revoke MCP access tokens
  - Response: `{ message: "MCP access revoked" }`

**Important**: MCP uses OAuth2 but is separate from general OAuth2 clients. Trainers can ONLY authorize MCP, not create general OAuth2 integrations.

---

## 4. Account Management

- `POST /accounts` - Create new account (used during signup)
  - Request: `{ account_type: "individual" | "family", billing_email, billing_address: {...} }`
  - Response: `{ account_id, account_type, created_at }`

- `GET /accounts/{id}` - Get account details
  - Response: `{ account_id, account_type, billing_email, billing_address, stripe_customer_id, created_at }`

- `GET /accounts/{id}/members` - List all members in account
  - Response: `{ members: [{ client_id, member_role, name, date_of_birth, relationship_to_primary, has_login }] }`

- `POST /accounts/{id}/members` - Add sub-member to account
  - Request: `{ name, date_of_birth, relationship_to_primary: "spouse" | "child" | "parent" }`
  - Response: `{ client_id, member_role: "member", name, date_of_birth }`

- `PUT /accounts/{id}/members/{client_id}` - Update member details
  - Request: `{ name, relationship_to_primary }`
  - Response: `{ client_id, name, relationship_to_primary }`

- `POST /accounts/{id}/members/{client_id}/grant-login` - Create User for sub-member 13+
  - Request: `{ email }`
  - Response: `{ user_id, email, login_enabled: true, message: "Email sent to set password" }`

- `POST /accounts/{id}/members/{client_id}/revoke-login` - Disable login for sub-member
  - Response: `{ user_id, login_enabled: false }`

- `POST /accounts/{id}/members/{client_id}/emancipate` - Transfer sub-member to own account
  - Response: `{ new_account_id, client_id, member_role: "primary", message: "Member transferred to independent account" }`

- `DELETE /accounts/{id}/members/{client_id}` - Soft-delete member, anonymize PII
  - Response: `{ message: "Member deleted and data anonymized", client_id, deleted: true }`

---

## 5. Membership & Plans

### 5.1 Plan Templates

- `GET /gyms/{id}/plan-templates` - List available plans
  - Query params: `?location_id={uuid}` (optional: filter by location, or omit to see all including gym-wide)
  - Response: `{ plan_templates: [{ plan_template_id, name, description, plan_type, location_id, visit_entitlement, plan_duration, payment_config, status }] }`
  - Returns both location-specific plans (matching location_id) and gym-wide plans (location_id = null)

- `POST /gyms/{id}/plan-templates` - Create new plan template (admin only)
  - Request: `{ name, description, plan_type, location_id?, visit_entitlement: {...}, plan_duration: {...}, payment_config: {...}, modules_enabled: {...} }`
  - Response: `{ plan_template_id, name, location_id, ... }`
  - If `location_id` is null or omitted, plan applies to all gym locations

- `PUT /plan-templates/{id}` - Update plan template
  - Request: `{ name, description, location_id?, payment_config, ... }`
  - Response: `{ plan_template_id, name, location_id, ... }`

- `DELETE /plan-templates/{id}` - Deactivate plan template
  - Response: `{ plan_template_id, status: "inactive" }`

### 5.2 Client Memberships

- `POST /clients/{id}/memberships` - Assign plan to client
  - Request: `{ plan_template_id, started_at }`
  - Response: `{ client_membership_id, client_id, plan_template_id, status: "active", started_at, expires_at, visit_entitlement: {...} }`

- `GET /clients/{id}/memberships` - List client's memberships
  - Query params: `?status=active|paused|expired|canceled`
  - Response: `{ memberships: [{ client_membership_id, plan_name, plan_type, status, started_at, expires_at, visit_entitlement }] }`

- `GET /memberships/{id}` - Get membership details
  - Response: `{ client_membership_id, client_id, plan_template_id, status, started_at, expires_at, visit_entitlement, pause_info, cancellation_info, stripe_metadata }`

- `POST /memberships/{id}/pause` - Pause membership (admin/trainer only)
  - Request: `{ pause_reason }`
  - Response: `{ client_membership_id, status: "paused", paused_at, pause_reason }`

- `POST /memberships/{id}/unpause` - Unpause membership
  - Response: `{ client_membership_id, status: "active", days_paused_total, new_expires_at }`

- `POST /memberships/{id}/cancel` - Cancel membership (admin only)
  - Request: `{ cancellation_reason, cancels_at_period_end: true }`
  - Response: `{ client_membership_id, status: "active" | "canceled", cancels_at_period_end, expires_at }`

- `GET /memberships/{id}/visit-entitlement` - Check remaining visits
  - Response: `{ current_period_start, current_period_end, visits_allowed_this_period, visits_used_this_period, total_visits_remaining }`

---

## 6. Check-In & Occupancy

- `POST /locations/{id}/check-in` - Check in client by QR or name
  - Request: `{ client_id?, qr_code?, check_in_method: "qr_scan" | "manual_name" | "mobile_app", checked_in_by_user_id }`
  - Response: `{ check_in_id, client_id, location_id, checked_in_at, expected_checkout_at, check_in_type, membership_status: "active" | "alert_no_membership" }`

- `GET /locations/{id}/check-ins/active` - Currently checked-in clients
  - Response: `{ active_check_ins: [{ check_in_id, client_name, checked_in_at, expected_checkout_at }], count: 15 }`

- `GET /locations/{id}/busyness?date=&view=` - Busyness calculations
  - Query params: `?date=2026-01-19&view=self_directed|training|combined`
  - Response: `{ date, view, time_slots: [{ time: "09:00", count: 12, capacity: 50, percentage: 24 }] }`

- `GET /trainers/{id}/busyness?date=` - Trainer's personal schedule load
  - Response: `{ date, trainer_id, time_slots: [{ time: "09:00", scheduled_sessions: 2, predicted_arrivals: 1.8 }] }`

- `GET /clients/{id}/qr-code` - Get client's unique QR code for scanning
  - Response: `{ qr_code: "CLIENT-ABC123XYZ", qr_code_url: "data:image/png;base64,..." }`

---

## 7. Calendar & Schedule

### 7.1 Trainer Calendar Export

- `POST /trainers/{id}/calendar/token/generate` - Generate dedicated calendar access token
  - Response: `{ calendar_url, calendar_token, expires_at: null (long-lived) }`
  - **Security**: Generates a dedicated calendar token separate from OAuth access tokens
  - Calendar URL format: `GET /trainers/{id}/calendar.ics?token={calendar_token}`

- `GET /trainers/{id}/calendar.ics?token={calendar_token}` - iCalendar feed (read-only)
  - Response: iCalendar format (.ics) with scheduled training sessions
  - Updates every 15 minutes (cached)
  - **Security**: Requires dedicated calendar token, NOT OAuth access token
  - Calendar tokens are long-lived and revocable

- `POST /trainers/{id}/calendar/token/rotate` - Rotate calendar access token
  - Response: `{ calendar_url, calendar_token, previous_token_revoked: true }`
  - Use this to rotate tokens if compromised

- `DELETE /trainers/{id}/calendar/token/revoke` - Revoke calendar access token
  - Response: `{ message: "Calendar access revoked" }`

- `GET /trainers/{id}/calendar/settings` - Get calendar privacy settings
  - Response: `{ hide_client_names: false, uses_gym_default: true }`
  - **Behavior**: Returns effective setting (trainer override if set, otherwise gym default)

- `PUT /trainers/{id}/calendar/settings` - Update settings
  - Request: `{ hide_client_names: true }` OR `{ hide_client_names: null }` to reset to gym default
  - Response: `{ hide_client_names: true, uses_gym_default: false }`
  - **Precedence**: Trainer setting overrides gym default. Set to `null` to inherit gym default.

### 7.2 Client Calendar Export

- `POST /clients/{id}/calendar/token/generate` - Generate dedicated calendar access token
  - Response: `{ calendar_url, calendar_token, expires_at: null (long-lived) }`
  - **Security**: Generates a dedicated calendar token separate from OAuth access tokens
  - Calendar URL format: `GET /clients/{id}/calendar.ics?token={calendar_token}`

- `GET /clients/{id}/calendar.ics?token={calendar_token}` - iCalendar feed (read-only)
  - Response: iCalendar format (.ics) with client's scheduled training sessions
  - Updates every 15 minutes (cached)
  - **Security**: Requires dedicated calendar token, NOT OAuth access token
  - Shows only sessions for this specific client

- `POST /clients/{id}/calendar/token/rotate` - Rotate calendar access token
  - Response: `{ calendar_url, calendar_token, previous_token_revoked: true }`
  - Use this to rotate tokens if compromised

- `DELETE /clients/{id}/calendar/token/revoke` - Revoke calendar access token
  - Response: `{ message: "Calendar access revoked" }`

### 7.3 Schedule Management

- `GET /schedule?location_id=&trainer_id=&date=` - Query schedules
  - Response: `{ schedules: [{ schedule_id, client_id, client_name, location_id, trainer_id, scheduled_start, scheduled_end, status }] }`

- `POST /schedule/book` - Book training session
  - Request: `{ client_id, location_id, trainer_id, scheduled_start, scheduled_end }`
  - Response: `{ schedule_id, status: "tentative", scheduled_start, scheduled_end }`

- `PUT /schedule/{id}` - Update scheduled session
  - Request: `{ scheduled_start, scheduled_end }`
  - Response: `{ schedule_id, scheduled_start, scheduled_end }`

- `POST /schedule/{id}/cancel` - Cancel session
  - Response: `{ schedule_id, status: "canceled" }`

- `POST /schedule/{id}/confirm` - Confirm tentative session
  - Response: `{ schedule_id, status: "confirmed" }`

- `POST /schedule/{id}/mark-no-show` - Mark session as no-show (trainer/admin only)
  - Response: `{ schedule_id, status: "no_show", marked_at, marked_by_user_id }`

- `POST /schedule/{id}/mark-completed` - Mark session as completed (trainer/admin only)
  - Response: `{ schedule_id, status: "completed", completed_at, marked_by_user_id }`

---

## 8. Workouts & Programs

### 8.1 Programs

- `GET /programs?gym_id=` - List programs
  - Response: `{ programs: [{ program_id, name, description, days_count }] }`

- `POST /programs` - Create program
  - Request: `{ name, description }`
  - Response: `{ program_id, name, description }`

- `GET /programs/{id}/days` - List program days
  - Response: `{ program_days: [{ program_day_id, name, next_program_day_id, exercises_count }] }`

- `POST /programs/{id}/days` - Create program day
  - Request: `{ name, next_program_day_id }`
  - Response: `{ program_day_id, name, next_program_day_id }`

- `GET /programs/{id}/days/{day_id}/exercises` - List exercises in program day
  - Response: `{ exercises: [{ program_day_exercise_id, exercise_id, exercise_name, order_index, default_sets, default_reps, default_rest_seconds, notes }] }`

- `POST /programs/{id}/days/{day_id}/exercises` - Add exercise to program day
  - Request: `{ exercise_id, order_index?, default_sets?, default_reps?, default_rest_seconds?, notes? }`
  - Response: `{ program_day_exercise_id, exercise_id, exercise_name, order_index, default_sets, default_reps, default_rest_seconds, notes }`

- `PUT /programs/{id}/days/{day_id}/exercises/{pde_id}` - Update exercise in program day
  - Request: `{ order_index?, default_sets?, default_reps?, default_rest_seconds?, notes? }`
  - Response: `{ program_day_exercise_id, order_index, default_sets, default_reps, default_rest_seconds, notes }`

- `DELETE /programs/{id}/days/{day_id}/exercises/{pde_id}` - Remove exercise from program day
  - Response: `{ message: "Exercise removed from program day" }`

### 8.2 Client Program Assignment

- `POST /clients/{id}/programs` - Assign program to client
  - Request: `{ program_id, start_program_day_id?, notes? }`
  - Response: `{ client_program_id, client_id, program_id, current_program_day_id, status: "active", assigned_at, assigned_by_trainer_id }`

- `GET /clients/{id}/programs` - List client's program assignments
  - Query params: `?status=active|paused|completed|abandoned`
  - Response: `{ programs: [{ client_program_id, program_id, program_name, current_program_day_id, current_program_day_name, status, assigned_at, assigned_by_trainer_id }] }`

- `GET /clients/{id}/programs/{client_program_id}` - Get program assignment details
  - Response: `{ client_program_id, client_id, program_id, program_name, current_program_day_id, current_program_day_name, status, assigned_at, completed_at?, notes }`

- `PUT /clients/{id}/programs/{client_program_id}` - Update program assignment
  - Request: `{ current_program_day_id?, notes? }`
  - Response: `{ client_program_id, current_program_day_id, notes }`

- `POST /clients/{id}/programs/{client_program_id}/pause` - Pause program
  - Response: `{ client_program_id, status: "paused" }`

- `POST /clients/{id}/programs/{client_program_id}/resume` - Resume paused program
  - Response: `{ client_program_id, status: "active" }`

- `POST /clients/{id}/programs/{client_program_id}/complete` - Mark program as completed
  - Response: `{ client_program_id, status: "completed", completed_at }`

- `DELETE /clients/{id}/programs/{client_program_id}` - Remove program assignment
  - Response: `{ client_program_id, status: "abandoned", abandoned_at }`

### 8.3 Workouts

- `POST /workouts/start` - Start workout
  - Request: `{ client_id, trainer_id, location_id, check_in_id?, program_id?, program_day_id?, started_at }`
  - **check_in_id**: Optional FK to GymCheckIn (ties workout to specific visit). Recommended for tracking visit-to-workout relationship.
  - Response: `{ workout_id, check_in_id?, client_id, started_at, workout_exercises: [{ workout_exercise_id, exercise_id, exercise_name, order_index, default_sets, default_reps }] }`

- `POST /workouts/{id}/complete` - Complete workout
  - Request: `{ ended_at }`
  - Response: `{ workout_id, ended_at, duration_minutes, analytics: { total_weight_lifted_lbs, total_reps, total_sets, prs_achieved_count } }`

- `PUT /workouts/{id}/exercises/{we_id}/sets` - Update exercise sets
  - Request: `{ sets: [{ set_index, planned_reps, actual_reps, is_amrap, measurements: [{ type: "weight", value: 225, unit: "lbs" }] }] }`
  - Response: `{ workout_exercise_id, sets: [...] }`

- `GET /workouts/{id}` - Get workout details
  - Response: `{ workout_id, client_id, started_at, ended_at, workout_exercises: [...] }`

### 8.4 Exercise Catalog

- `GET /exercises?gym_id=` - List exercises available to gym
  - Query params: `?gym_id=<uuid>&category=&muscle_group=`
  - Response: `{ exercises: [{ exercise_id, name, category, muscle_group, equipment_needed, is_standard, is_custom, created_by_gym_id? }] }`
  - **Behavior**: Returns both standard platform exercises (is_standard=true) and gym-specific custom exercises (is_custom=true, created_by_gym_id matches gym)

- `GET /exercises/{id}` - Get exercise details
  - Response: `{ exercise_id, name, description?, category, muscle_group, equipment_needed, demo_video_url?, is_standard, is_custom, created_by_gym_id?, created_at }`

- `POST /exercises` - Create custom exercise (trainer/admin only)
  - Request: `{ gym_id, name, description?, category, muscle_group, equipment_needed?, demo_video_url? }`
  - Response: `{ exercise_id, name, description, category, muscle_group, equipment_needed, demo_video_url, is_standard: false, is_custom: true, created_by_gym_id, created_at }`
  - **Authorization**: Trainer or admin within the gym

- `PUT /exercises/{id}` - Update custom exercise (trainer/admin only)
  - Request: `{ name?, description?, category?, muscle_group?, equipment_needed?, demo_video_url? }`
  - Response: `{ exercise_id, name, description, category, muscle_group, equipment_needed, demo_video_url }`
  - **Authorization**: Can only update custom exercises (is_custom=true) created by the same gym. Standard exercises cannot be modified.

- `DELETE /exercises/{id}` - Delete custom exercise (admin only)
  - Response: `{ message: "Exercise deleted" }`
  - **Authorization**: Can only delete custom exercises created by the same gym. Standard exercises cannot be deleted.
  - **Behavior**: Soft-delete (archive). Exercise remains in historical workout data but is removed from exercise picker.

---

## 9. Measurements & Goals

### 9.1 Measurement Types

- `GET /gyms/{id}/measurement-types` - List all active measurement types for gym
  - Response: `{ measurement_types: [{ measurement_type_id, name, category, default_unit, is_standard, is_active, sort_order }] }`

- `POST /gyms/{id}/measurement-types` - Create custom measurement type (admin only)
  - Request: `{ name, category: "custom", default_unit }`
  - Response: `{ measurement_type_id, name, category, default_unit, is_standard: false }`

- `PUT /measurement-types/{id}` - Update custom type or deactivate standard type
  - Request: `{ name?, default_unit?, is_active? }`
  - Response: `{ measurement_type_id, name, default_unit, is_active }`

- `DELETE /measurement-types/{id}` - Soft-delete custom measurement type
  - Response: `{ message: "Measurement type deleted" }`

### 9.2 Client Measurements

- `GET /clients/{id}/measurements?type=&date_range=` - List measurements
  - Query params: `?type=body_weight&date_range=2026-01-01,2026-01-31`
  - Response: `{ measurements: [{ measurement_id, measurement_type, recorded_at, value, unit, recorded_by, notes, progress_photo_id }] }`

- `POST /clients/{id}/measurements` - Record new measurement (trainer only)
  - Request: `{ measurement_type_id, value, unit, notes?, progress_photo_id? }`
  - Response: `{ measurement_id, client_id, measurement_type, value, unit, recorded_at, goals_updated: [{ goal_id, progress_percentage, achieved }] }`

- `GET /clients/{id}/measurements/{measurement_id}` - Get single measurement
  - Response: `{ measurement_id, measurement_type, value, unit, recorded_at, recorded_by, notes, progress_photo }`

- `GET /clients/{id}/measurements/latest?types=` - Get latest measurements for specified types
  - Query params: `?types=body_weight,body_fat_percentage`
  - Response: `{ measurements: [{ measurement_type, value, unit, recorded_at }] }`

- `GET /clients/{id}/measurements/history?type=` - Time-series data for charting
  - Query params: `?type=body_weight&date_range=2025-01-01,2026-01-31`
  - Response: `{ measurement_type, data_points: [{ recorded_at, value, unit }] }`

### 9.3 Goals

- `GET /clients/{id}/goals?status=` - List client goals
  - Query params: `?status=active|achieved|abandoned`
  - Response: `{ goals: [{ goal_id, goal_type, target_value, current_value, progress_percentage, status, created_at, achieved_at }] }`

- `POST /clients/{id}/goals` - Create new goal
  - Request: `{ goal_type: "measurement" | "exercise_pr" | "workout_frequency" | "custom", target_measurement_type_id?, target_exercise_id?, target_value, target_unit, target_date?, notes? }`
  - Response: `{ goal_id, goal_type, baseline_value, target_value, current_value, progress_percentage: 0, status: "active" }`

- `GET /goals/{id}` - Get goal with current progress
  - Response: `{ goal_id, goal_type, baseline_value, current_value, target_value, progress_percentage, status, created_at, achieved_at }`

- `PUT /goals/{id}` - Update goal target or deadline
  - Request: `{ target_value?, target_date?, notes? }`
  - Response: `{ goal_id, target_value, target_date }`

- `POST /goals/{id}/abandon` - Mark goal as abandoned
  - Response: `{ goal_id, status: "abandoned" }`

- `DELETE /goals/{id}` - Soft-delete goal
  - Response: `{ message: "Goal deleted" }`

- `GET /clients/{id}/goals/progress` - Summary of all active goals
  - Response: `{ active_goals_count: 5, goals: [{ goal_id, goal_type, target_value, progress_percentage, days_remaining }] }`

### 9.4 Measurement Reminders

- `GET /trainers/{id}/reminders/due` - List clients due for measurements today
  - Response: `{ reminders: [{ reminder_id, client_id, client_name, measurement_type, last_measured_at, days_overdue }], total_count: 5 }`

- `POST /reminders/{id}/snooze` - Snooze reminder
  - Request: `{ snooze_duration_days: 3 | 7 | 14 }`
  - Response: `{ reminder_id, is_snoozed: true, snoozed_until }`

- `GET /gyms/{id}/reminders/settings` - Get gym measurement reminder settings
  - Response: `{ measurement_reminders_enabled: true, measurement_reminder_frequency_days: 30 }`

- `PUT /gyms/{id}/reminders/settings` - Update reminder settings (admin only)
  - Request: `{ measurement_reminders_enabled: true, measurement_reminder_frequency_days: 30 }`
  - Response: `{ measurement_reminders_enabled: true, measurement_reminder_frequency_days: 30 }`

---

## 10. Progress Photos & Media

### 10.1 Progress Photos

- `POST /clients/{id}/progress-photos/upload-url` - Get signed upload URL
  - Request: `{ filename, content_type: "image/jpeg" }`
  - Response: `{ upload_url, photo_id, expires_in: 3600 }`

- `POST /clients/{id}/progress-photos` - Create progress photo record
  - Request: `{ photo_id, captured_at, visibility: "client_only" | "trainer" | "gym_admin", notes?, tags?: [...] }`
  - Response: `{ progress_photo_id, client_id, photo_url, captured_at, visibility }`

- `GET /clients/{id}/progress-photos` - List progress photos
  - Query params: `?date_range=2025-01-01,2026-01-31`
  - Response: `{ photos: [{ progress_photo_id, photo_url, thumbnail_url, captured_at, uploaded_at, visibility, notes, tags }] }`

- `DELETE /clients/{id}/progress-photos/{photo_id}` - Delete progress photo
  - Response: `{ message: "Progress photo deleted" }`

---

## 11. Health Integrations

- `POST /clients/{id}/health/connect` - Initiate health integration connection
  - Request: `{ provider: "apple_health" | "google_fit" | "health_connect", scopes_requested: ["steps", "active_energy", "weight"] }`
  - Response: `{ health_connection_id, provider, status: "connected", scopes_granted: [...] }`

- `POST /clients/{id}/health/disconnect` - Disconnect health integration
  - Request: `{ provider }`
  - Response: `{ provider, status: "disconnected" }`

- `GET /clients/{id}/health/metrics?type=&range=` - Get health metrics
  - Query params: `?type=steps&range=2026-01-01,2026-01-31`
  - Response: `{ metric_type: "steps", samples: [{ start_at, end_at, value, unit, source_device }] }`

- `POST /webhooks/health` - Health provider webhook receiver (optional)
  - Request: Provider-specific webhook payload
  - Response: `{ received: true }`

---

## 12. Agreements & E-Signature (Post-MVP)

**Status**: Post-MVP feature. API endpoints below are planned for future implementation but not included in initial launch.

- `GET /agreements/templates?gym_id=` - List agreement templates
  - Response: `{ templates: [{ template_id, name, version, effective_at, requires_signature }] }`

- `POST /agreements/templates` - Create agreement template (admin only)
  - Request: `{ gym_id, name, content, version }`
  - Response: `{ template_id, name, version }`

- `POST /agreements/envelopes/create` - Create signing envelope for client
  - Request: `{ template_id, client_id, signer_email }`
  - Response: `{ envelope_id, signing_url, status: "pending" }`

- `GET /agreements/envelopes/{id}` - Get envelope status
  - Response: `{ envelope_id, status: "pending" | "signed" | "declined", signed_at?, signer_email, document_ids: [...] }`

- `POST /webhooks/esign` - DocuSign webhook receiver
  - Request: DocuSign event payload
  - Response: `{ received: true }`

---

## 13. Analytics & Reporting

### 13.1 Client Progress

- `GET /clients/{id}/analytics/workouts?date_range=` - Workout metrics over time
  - Response: `{ date_range, data_points: [{ date, total_workouts, total_volume_lbs, avg_duration_minutes }] }`

- `GET /clients/{id}/analytics/volume?date_range=` - Total weight lifted trends
  - Response: `{ date_range, data_points: [{ date, total_volume_lbs }] }`

- `GET /clients/{id}/analytics/prs?date_range=` - PRs achieved over time
  - Response: `{ date_range, prs: [{ date, exercise, measurement_type, value, unit }] }`

- `GET /clients/{id}/analytics/exercises/{exercise_id}` - Progress on specific exercise
  - Response: `{ exercise_id, exercise_name, data_points: [{ date, max_weight, max_reps, volume }] }`

- `GET /clients/{id}/analytics/summary` - High-level stats
  - Response: `{ total_workouts, total_prs, avg_volume_per_workout, current_streak_days, longest_streak_days }`

### 13.2 Peer Comparison

- `GET /clients/{id}/analytics/compare?measurement_type=` - Compare client to gym average
  - Query params: `?measurement_type=body_weight`
  - Response: `{ measurement_type, client_value: 180, gym_average: 175, percentile: 60, sample_size: 120 }`

- `GET /gyms/{id}/analytics/benchmarks` - Anonymized gym averages
  - Response: `{ benchmarks: [{ measurement_type, average_value, unit, sample_size }] }`

### 13.3 Workout Analytics

- `GET /workouts/{id}/analytics` - Get pre-calculated analytics for completed workout
  - Response: `{ workout_id, total_weight_lifted_lbs, total_reps, total_sets, duration_minutes, completion_rate, prs_achieved_count, exercises_completed, exercises_skipped }`

- `GET /workouts/{id}/analytics/preview` - Real-time preview during active workout (not persisted)
  - Response: `{ current_total_weight_lbs, current_total_reps, current_duration_minutes, exercises_remaining }`

### 13.4 Gym Admin Reporting

**Dashboard Metrics**:
- `GET /gyms/{id}/analytics/dashboard?period=day|week|month` - High-level metrics
  - Response: `{ period, total_revenue, total_clients, new_clients, churned_clients, total_workouts, active_trainers }`

- `GET /gyms/{id}/analytics/revenue?period_type=day|week|month&date_range=` - Revenue trends
  - Response: `{ date_range, data_points: [{ period_start, total_revenue, new_revenue, recurring_revenue, churned_revenue }] }`

- `GET /gyms/{id}/analytics/clients?period_type=day|week|month&date_range=` - Client growth/churn
  - Response: `{ date_range, data_points: [{ period_start, total_clients, new_clients, churned_clients, retention_rate }] }`

- `GET /gyms/{id}/analytics/engagement?period_type=day|week|month&date_range=` - Workout frequency, check-ins
  - Response: `{ date_range, data_points: [{ period_start, total_workouts, total_check_ins, avg_workouts_per_client, workout_completion_rate }] }`

- `GET /gyms/{id}/analytics/trainers?period_type=week|month&date_range=` - Trainer utilization
  - Response: `{ date_range, data_points: [{ period_start, total_trainers, active_trainers, avg_clients_per_trainer, trainer_utilization_rate }] }`

**Export**:
- `POST /gyms/{id}/analytics/export` - Request analytics export (async)
  - Request: `{ format: "csv" | "pdf", date_range, include_sections: ["revenue", "clients", "engagement"] }`
  - Response: `{ export_id, status: "processing", estimated_completion: "2026-01-19T10:30:00Z" }`

- `GET /gyms/{id}/analytics/export/{export_id}/download` - Download link
  - Response: `{ download_url, expires_at, format, size_bytes }`

**Real-time Stats**:
- `GET /gyms/{id}/analytics/realtime` - Current active clients, trainers on duty
  - Response: `{ current_active_clients: 45, trainers_on_duty: 8, today_workouts: 120, today_check_ins: 150 }`

- `GET /locations/{id}/analytics/realtime` - Per-location realtime occupancy
  - Response: `{ location_id, current_occupancy: 32, capacity: 50, percentage: 64, checked_in_clients: [...] }`

---

## 14. Usage & Metering (Internal/Admin)

- `GET /gyms/{id}/usage?range=` - Get gym usage metrics
  - Query params: `?range=2026-01-01,2026-01-31`
  - Response: `{ gym_id, date_range, clients_count, locations_count, trainers_count, api_calls_count, ai_api_calls_count }`

- `GET /gyms/{id}/usage/rollups?granularity=day|hour&range=` - Time-windowed rollups
  - Response: `{ rollups: [{ window_start, window_end, clients_count, api_calls_count, ai_api_calls_count }] }`

- `GET /admin/usage/top` - Platform-level overview (platform admin only)
  - Response: `{ top_gyms_by_clients: [...], top_gyms_by_api_calls: [...], total_platform_clients, total_platform_api_calls }`

---

## 15. Plan Limits & Feature Flags (Internal/Admin)

- `GET /gyms/{id}/plan` - Get gym's current plan/limits
  - Response: `{ gym_id, platform_plan_id, limits: { max_locations, max_trainers, max_clients, ... }, features: { self_scheduling_enabled, ... } }`

- `PUT /gyms/{id}/plan` - Update plan/limits (platform admin only)
  - Request: `{ platform_plan_id, limits: {...}, features: {...} }`
  - Response: `{ gym_id, platform_plan_id, limits, features, updated_at }`

- `GET /plans` - List platform plan templates
  - Response: `{ plans: [{ platform_plan_id, name, description, limits, features, pricing }] }`

- `PUT /plans/{id}` - Update plan template (platform admin only)
  - Request: `{ name, limits, features }`
  - Response: `{ platform_plan_id, name, limits, features }`

---

## 16. Data Export & Privacy

- `POST /clients/{id}/data-export` - Request data export (async)
  - Request: `{ formats: ["json", "csv", "pdf"], include_photos: true }`
  - Response: `{ export_id, status: "processing", estimated_completion: "2026-01-19T10:30:00Z" }`

- `GET /clients/{id}/data-export/{export_id}/status` - Check export status
  - Response: `{ export_id, status: "completed" | "processing" | "failed", created_at, completed_at?, download_expires_at? }`

- `GET /clients/{id}/data-export/{export_id}/download` - Signed download URL
  - Response: `{ download_url, expires_in: 604800 (7 days), size_bytes }`

- `POST /clients/{id}/request-deletion` - Right to be forgotten request
  - Request: `{ confirmation: true, reason? }`
  - Response: `{ deletion_request_id, status: "pending", scheduled_deletion_date }`

- `GET /clients/{id}/deletion-status` - Check deletion request status
  - Response: `{ deletion_request_id, status: "pending" | "completed", requested_at, completed_at? }`

---

## 17. Gym & Location Management

### 17.1 Gyms

- `GET /gyms` - List gyms (platform admin only)
- `POST /gyms` - Create gym (platform admin only)
- `GET /gyms/{id}` - Get gym details
- `PUT /gyms/{id}` - Update gym settings
- `DELETE /gyms/{id}` - Soft-delete gym

### 17.2 Locations

- `GET /gyms/{id}/locations` - List locations for gym
- `POST /gyms/{id}/locations` - Create location
- `GET /locations/{id}` - Get location details
- `PUT /locations/{id}` - Update location
- `DELETE /locations/{id}` - Soft-delete location

### 17.3 Custom Email Domains (Enterprise Feature)

**Authorization**: All endpoints require `admin` role for the gym.

- `GET /gyms/{gym_id}/domains/email` - Get email domain configuration
  - Response: `{ domain, sender_name, from_address, reply_to, status, verified_at }`

- `POST /gyms/{gym_id}/domains/email` - Configure custom email domain
  - Request: `{ domain, sender_name, from_address, reply_to }`
  - Response: `{ domain, status: "pending_verification", dns_records: [...], verification_expires_at }`
  - Rate limit: 5 requests per 24 hours per gym

- `PUT /gyms/{gym_id}/domains/email` - Update email domain configuration
  - Request: `{ sender_name?, from_address?, reply_to? }`
  - Response: `{ domain, sender_name, from_address, reply_to, status }`

- `DELETE /gyms/{gym_id}/domains/email` - Remove email domain configuration
  - Response: `{ message: "Email domain removed", domain }`

- `POST /gyms/{gym_id}/domains/email/verify` - Trigger DNS verification check
  - Response: `{ status: "verified" | "pending" | "failed", validation_errors?: [...] }`
  - Rate limit: 10 requests per hour per gym

- `GET /gyms/{gym_id}/domains/email/status` - Get verification status and progress
  - Response: `{ status, last_checked_at, verification_expires_at, dns_records: [...] }`
  - Rate limit: 60 requests per hour per gym

### 17.4 Custom Login Domains (Enterprise Feature)

**Authorization**: All endpoints require `admin` role for the gym.

- `GET /gyms/{gym_id}/domains/login` - Get login domain configuration
  - Response: `{ domain, status, verified_at, ssl_expires_at }`

- `POST /gyms/{gym_id}/domains/login` - Configure custom login domain
  - Request: `{ domain }`
  - Response: `{ domain, status: "pending_verification", dns_records: [...], verification_expires_at }`
  - Rate limit: 5 requests per 24 hours per gym

- `PUT /gyms/{gym_id}/domains/login` - Update login domain configuration
  - Request: `{ domain }`
  - Response: `{ domain, status }`

- `DELETE /gyms/{gym_id}/domains/login` - Remove login domain configuration
  - Response: `{ message: "Login domain removed", domain }`

- `POST /gyms/{gym_id}/domains/login/verify` - Trigger DNS and SSL verification
  - Response: `{ status: "verified" | "pending" | "failed", validation_errors?: [...], ssl_status? }`
  - Rate limit: 10 requests per hour per gym

- `GET /gyms/{gym_id}/domains/login/status` - Get verification and SSL status
  - Response: `{ status, last_checked_at, verification_expires_at, ssl_expires_at, dns_records: [...] }`
  - Rate limit: 60 requests per hour per gym

### 17.5 Email Templates

**Initial Implementation**: System templates only (platform admin). Gym overrides are future feature.

#### System Template Management (Platform Admin Only)

- `GET /api/v1/admin/email-templates` - List all system email templates
  - Response: `{ templates: [{ email_template_id, template_key, subject, category, description, version, is_active }] }`
  - Query params: `?category=transactional|operational|marketing`, `?is_active=true`

- `GET /api/v1/admin/email-templates/{template_key}` - Get system template details
  - Response: `{ email_template_id, template_key, subject, body_html, body_text, category, required_variables, version, is_active, created_at, updated_at }`

- `POST /api/v1/admin/email-templates` - Create new system template
  - Request: `{ template_key, subject, body_html, body_text?, category, description, required_variables }`
  - Response: `{ email_template_id, template_key, version: 1, is_active: true }`
  - Authorization: Platform admin only

- `PUT /api/v1/admin/email-templates/{template_key}` - Update system template
  - Request: `{ subject?, body_html?, body_text?, description?, required_variables? }`
  - Response: `{ email_template_id, template_key, version, updated_at }`
  - Note: Version increments on update
  - Authorization: Platform admin only

- `POST /api/v1/admin/email-templates/{template_key}/preview` - Preview rendered template
  - Request: `{ sample_data: { user_name: "John Doe", gym_name: "PowerLift Gym", ... } }`
  - Response: `{ rendered_subject, rendered_html, rendered_text, variables_used }`
  - Authorization: Platform admin only

#### Gym Template Overrides (Future Feature)

**Authorization**: Gym admin only for these endpoints.

- `GET /api/v1/gyms/{gym_id}/email-templates` - List gym's template overrides
  - Response: `{ templates: [{ email_template_id, template_key, subject, version, is_active }] }`

- `GET /api/v1/gyms/{gym_id}/email-templates/{template_key}` - Get gym override template
  - Response: `{ email_template_id, template_key, subject, body_html, body_text, version, created_at }`
  - Falls back to system template if no override exists

- `POST /api/v1/gyms/{gym_id}/email-templates` - Create gym template override
  - Request: `{ template_key, subject, body_html, body_text? }`
  - Response: `{ email_template_id, template_key, template_type: "gym_override", version: 1 }`
  - Must match required_variables from system template

- `PUT /api/v1/gyms/{gym_id}/email-templates/{template_key}` - Update gym override
  - Request: `{ subject?, body_html?, body_text? }`
  - Response: `{ email_template_id, template_key, version, updated_at }`

- `DELETE /api/v1/gyms/{gym_id}/email-templates/{template_key}` - Delete gym override
  - Response: `{ message: "Template override deleted, falling back to system template" }`
  - Falls back to system template after deletion

- `POST /api/v1/gyms/{gym_id}/email-templates/{template_key}/preview` - Preview gym template
  - Request: `{ sample_data: { ... } }`
  - Response: `{ rendered_subject, rendered_html, rendered_text }`

#### Template Validation

All template create/update endpoints validate:
- Jinja2 syntax correctness
- Required variables present in template body
- Subject and body not empty
- Valid category value
- Template key matches pattern: `^[a-z_]+$` (lowercase, underscores only)

**Error Response** (422 Unprocessable Entity):
```json
{
  "error": {
    "code": "TEMPLATE_VALIDATION_ERROR",
    "message": "Template validation failed",
    "details": {
      "jinja_errors": ["Unexpected end of template"],
      "missing_variables": ["reset_token"],
      "invalid_fields": ["template_key"]
    }
  }
}
```

---

## 18. People Management

### 18.1 Trainers

- `GET /gyms/{id}/trainers` - List trainers at gym
  - Query params: `?status=invited|active|inactive`
  - Response: `{ trainers: [{ trainer_id, first_name, last_name, email, phone, primary_location_id, status, hire_date, employment_type }] }`

- `POST /gyms/{id}/trainers` - Create trainer (invitation flow)
  - Request: `{ first_name, last_name, email, phone?, primary_location_id, hire_date?, employment_type?, roles?: ['trainer', 'admin'?, 'front_desk'?], send_invitation?: true }`
  - Response: `{ trainer_id, first_name, last_name, email, status: "invited", invitation_sent: true, invitation_expires_at: "2026-01-26T10:00:00Z" }`
  - **Behavior**: Creates Trainer record with status='invited'. If `send_invitation=true` (default), sends invitation email with setup link. Trainer must complete account setup within 7 days.
  - **Authorization**: Admin only

- `GET /trainers/{id}` - Get trainer details
  - Response: `{ trainer_id, first_name, last_name, email, phone, primary_location_id, gym_id, status, hire_date, employment_type, user_id, calendar_settings, created_at }`

- `PUT /trainers/{id}` - Update trainer
  - Request: `{ first_name?, last_name?, phone?, primary_location_id?, employment_type?, status? }`
  - Response: `{ trainer_id, first_name, last_name, email, phone, status }`
  - **Note**: Cannot change email directly. Status changes: invited→active (on account setup), active→inactive (on termination)

- `DELETE /trainers/{id}` - Soft-delete trainer (sets status='inactive', revokes login)
  - Response: `{ trainer_id, status: "inactive", login_enabled: false }`
  - **Behavior**: Sets Trainer.status='inactive' and User.login_enabled=false. Preserves historical data. Trainer cannot log in but remains in audit logs.

- `POST /trainers/{id}/resend-invitation` - Resend invitation email
  - Response: `{ trainer_id, invitation_sent: true, invitation_expires_at: "2026-01-26T10:00:00Z" }`
  - **Authorization**: Admin only
  - **Behavior**: Only works for trainers with status='invited'. Generates new invitation link, sends email.

**Trainer Availability**:
- `GET /trainers/{id}/availability` - Get recurring availability
- `PUT /trainers/{id}/availability` - Update recurring availability
- `GET /trainers/{id}/exceptions` - List exceptions (PTO, vacation)
- `POST /trainers/{id}/exceptions` - Create exception
- `DELETE /trainers/{id}/exceptions/{exception_id}` - Remove exception

### 18.2 Clients

- `GET /gyms/{id}/clients` - List clients at gym
  - Query params: `?status=prospect|trial|active|inactive|lost&primary_trainer_id=`
  - Response: `{ clients: [{ client_id, first_name, last_name, email, phone, member_number, client_status, primary_trainer_id, date_of_birth, created_at }] }`

- `POST /gyms/{id}/clients` - Create client
  - Request: `{ account_id?, first_name, last_name, email?, phone?, date_of_birth, primary_location_id, primary_trainer_id?, client_status?: 'prospect'|'trial'|'active', member_role?: 'primary'|'member', relationship_to_primary? }`
  - Response: `{ client_id, account_id, first_name, last_name, email, phone, member_number, client_status, qr_code, created_at }`
  - **Behavior**: Creates Client record. If `account_id` is omitted, creates a new Account. Generates unique member_number and qr_code. Does NOT create User (login) automatically.
  - **Authorization**: Admin or Trainer

- `GET /clients/{id}` - Get client details
  - Response: `{ client_id, account_id, first_name, last_name, email, phone, date_of_birth, member_number, client_status, primary_location_id, primary_trainer_id, qr_code, member_role, relationship_to_primary, avg_workout_duration_minutes, ai_summary_latest, ai_summary_updated_at, ai_summary_is_stale, created_at }`

- `PUT /clients/{id}` - Update client
  - Request: `{ first_name?, last_name?, email?, phone?, primary_location_id?, primary_trainer_id?, client_status? }`
  - Response: `{ client_id, first_name, last_name, email, phone, client_status }`

- `DELETE /clients/{id}` - Soft-delete client
  - Response: `{ client_id, deleted: true, client_status: "deleted", anonymized_at }`
  - **Behavior**: Soft-deletes client (sets deleted=true, client_status='deleted'). Anonymizes PII after retention period (see data privacy requirements). Revokes login if User exists.

- `POST /clients/{id}/grant-login` - Grant login access to client
  - Request: `{ send_invitation?: true }`
  - Response: `{ user_id, client_id, email, invitation_sent: true }`
  - **Behavior**: Creates User record linked to Client. If `send_invitation=true`, sends email with account setup link. For clients under 18, requires primary member approval.

**AI Summary**:
- `GET /clients/{id}/ai-summary` - Get AI summary (generates if stale or missing)
  - **Behavior**: Returns cached summary if fresh. If stale/missing, generates new summary using AI API and caches it on client.
  - **Authorization**: Trainer (assigned to client) or gym admin only
  - **Response**: `{ summary: "AI-generated summary text...", generated_at: "2026-01-19T10:00:00Z", is_stale: false, data_sources: { workouts_count: 15, measurements_count: 8, prs_count: 3, goals_count: 2 } }`
  - **Summary Contents**: Includes workout history & trends, measurements & body composition, PRs & strength progress, goals & progress toward goals
  - **Rate Limit**: 10 requests per client per hour (to control AI API costs)

- `POST /clients/{id}/ai-summary/refresh` - Force regenerate AI summary
  - **Behavior**: Bypasses cache, always generates fresh summary
  - **Authorization**: Trainer or gym admin only
  - **Response**: Same as GET endpoint
  - **Rate Limit**: 3 requests per client per hour

---

## 19. Error Responses

All API errors follow a standard format:

```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "details": {
      "field": "password",
      "reason": "Password does not match"
    },
    "request_id": "req_123456"
  }
}
```

### Common Error Codes

- `AUTHENTICATION_REQUIRED` - 401: Missing or invalid access token
- `PERMISSION_DENIED` - 403: User lacks required permissions
- `RESOURCE_NOT_FOUND` - 404: Requested resource does not exist
- `VALIDATION_ERROR` - 400: Request data validation failed
- `RATE_LIMIT_EXCEEDED` - 429: Too many requests
- `INTERNAL_SERVER_ERROR` - 500: Server error
- `SERVICE_UNAVAILABLE` - 503: Service temporarily unavailable

---

## 20. Rate Limiting

- **Authentication endpoints**: 10 requests per minute per IP
- **Password reset**: 3 requests per email per hour
- **Standard API endpoints**: 100 requests per minute per user
- **Analytics/reporting**: 30 requests per minute per user
- **Webhook endpoints**: 1000 requests per minute per gym
- **Custom domain configuration** (POST/PUT/DELETE): 5 requests per 24 hours per gym
- **Domain verification attempts** (POST verify): 10 requests per hour per gym
- **Domain status checks** (GET status): 60 requests per hour per gym

Rate limit headers included in all responses:
- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## 21. Webhooks

### 21.1 Webhook Events

The system can send webhooks for:
- Client check-ins
- Workout completions
- Goal achievements
- Membership changes
- Payment events (via Stripe)

Webhook payload format:
```json
{
  "event_id": "evt_123456",
  "event_type": "workout.completed",
  "created_at": "2026-01-19T10:00:00Z",
  "data": {
    "workout_id": "...",
    "client_id": "...",
    ...
  }
}
```

### 21.2 Webhook Security

- All webhooks signed with HMAC-SHA256
- Signature included in `X-Webhook-Signature` header
- Verify signature before processing
- Include timestamp to prevent replay attacks


## Appendix: Merged from REQUIREMENTS.md (legacy)

### 5. API Specification Outline

### 5.1 Media

- `POST /clients/{id}/progress-photos/upload-url`
- `POST /clients/{id}/progress-photos` (create record)
- `GET /clients/{id}/progress-photos`
- `DELETE /clients/{id}/progress-photos/{photo_id}`

### 5.2 Health Integrations

- `POST /clients/{id}/health/connect` (init connect)
- `POST /clients/{id}/health/disconnect`
- `GET /clients/{id}/health/metrics?type=&range=`
- `POST /webhooks/health` (optional, if provider supports push)

### 5.3 Agreements & E-Signature

- `GET /agreements/templates?gym_id=`
- `POST /agreements/templates` (admin)
- `POST /agreements/envelopes/create` (create envelope for client)
- `GET /agreements/envelopes/{id}` (status)
- `POST /webhooks/esign` (DocuSign webhook receiver)

### 5.4 Usage & Metering (Internal/Admin)

- `GET /gyms/{id}/usage?range=`
- `GET /gyms/{id}/usage/rollups?granularity=day|hour&range=`
- `GET /admin/usage/top` (platform-level overview)

### 5.5 Plan Limits & Feature Flags (Internal/Admin)

- `GET /gyms/{id}/plan`
- `PUT /gyms/{id}/plan` (update plan/limits doc)
- `GET /plans` (list plan templates)
- `PUT /plans/{id}` (update plan templates)

### 5.6 Account Management

- `POST /accounts` (create new account, used during signup)
- `GET /accounts/{id}` (get account details)
- `GET /accounts/{id}/members` (list all members in account)
- `POST /accounts/{id}/members` (add sub-member to account)
- `PUT /accounts/{id}/members/{client_id}` (update member details)
- `POST /accounts/{id}/members/{client_id}/grant-login` (create User for sub-member 13+)
- `POST /accounts/{id}/members/{client_id}/revoke-login` (disable login for sub-member)
- `POST /accounts/{id}/members/{client_id}/emancipate` (transfer sub-member to own account)
- `DELETE /accounts/{id}/members/{client_id}` (soft-delete member, anonymize PII)

### 5.7 Data Export & Privacy

- `POST /clients/{id}/data-export` (request data export, async)
- `GET /clients/{id}/data-export/{export_id}/status` (check export status)
- `GET /clients/{id}/data-export/{export_id}/download` (signed download URL)
- `POST /clients/{id}/request-deletion` (right to be forgotten request)
- `GET /clients/{id}/deletion-status` (check deletion request status)

### 5.8 Membership & Plans

- `GET /gyms/{id}/plan-templates` (list available plans)
- `POST /gyms/{id}/plan-templates` (create new plan template)
- `PUT /plan-templates/{id}` (update plan template)
- `DELETE /plan-templates/{id}` (deactivate plan template)
- `POST /clients/{id}/memberships` (assign plan to client)
- `GET /clients/{id}/memberships` (list client's memberships)
- `GET /memberships/{id}` (get membership details)
- `POST /memberships/{id}/pause` (pause membership)
- `POST /memberships/{id}/unpause` (unpause membership)
- `POST /memberships/{id}/cancel` (cancel membership)
- `GET /memberships/{id}/visit-entitlement` (check remaining visits)

### 5.9 Check-In & Occupancy

- `POST /locations/{id}/check-in` (check in client by QR or name)
- `GET /locations/{id}/check-ins/active` (currently checked-in clients)
- `GET /locations/{id}/busyness?date=&view=` (view: self_directed | training | combined)
- `GET /trainers/{id}/busyness?date=` (trainer's personal schedule load)
- `GET /clients/{id}/qr-code` (get client's unique QR code for scanning)

### 5.10 Authentication & OAuth2

**User Authentication**:
- `POST /auth/register` (create new user account with email + password)
- `GET /auth/verify-email?token=` (verify email address)
- `POST /auth/login` (password login, returns OAuth2 tokens)
- `POST /auth/login/passkey/challenge` (initiate passkey login, get WebAuthn challenge)
- `POST /auth/login/passkey/verify` (verify passkey signature, return OAuth2 tokens)
- `POST /auth/logout` (revoke current access token)
- `POST /auth/password/forgot` (request password reset email)
- `POST /auth/password/reset` (reset password with token from email)
- `PUT /auth/password/change` (change password, requires current password)

**Multi-Factor Authentication (MFA)**:
- `POST /auth/mfa/totp/setup` (generate TOTP secret, return QR code)
- `POST /auth/mfa/totp/verify-setup` (verify TOTP code to complete setup)
- `POST /auth/mfa/totp/verify` (verify TOTP code during login)
- `GET /auth/mfa/backup-codes` (get current backup codes)
- `POST /auth/mfa/backup-codes/regenerate` (generate new backup codes)
- `POST /auth/mfa/backup-codes/verify` (verify backup code during login)
- `POST /auth/mfa/email/send` (send email MFA code)
- `POST /auth/mfa/email/verify` (verify email MFA code during login)
- `PUT /auth/mfa/method` (switch MFA method: totp | email | passkey_only)
- `DELETE /auth/mfa/disable` (disable MFA, requires password + current MFA code)

**Passkey Management (WebAuthn/FIDO2)**:
- `POST /auth/passkeys/register/challenge` (generate WebAuthn registration challenge)
- `POST /auth/passkeys/register/verify` (verify attestation, save passkey)
- `GET /auth/passkeys` (list user's registered passkeys)
- `PUT /auth/passkeys/{id}` (rename passkey device)
- `DELETE /auth/passkeys/{id}` (remove passkey)

**OAuth2 Token Management**:
- `POST /oauth/token` (OAuth2 token endpoint, supports multiple grant types)
  - `grant_type=password` (resource owner password credentials)
  - `grant_type=authorization_code` (authorization code with PKCE)
  - `grant_type=refresh_token` (refresh access token)
  - `grant_type=client_credentials` (server-to-server)
- `POST /oauth/token/revoke` (revoke access or refresh token)
- `GET /oauth/token/introspect` (check token validity, return claims)

**OAuth2 Authorization Flow**:
- `GET /oauth/authorize` (authorization endpoint, display consent screen)
- `POST /oauth/authorize` (user approves/denies authorization request)
- `GET /oauth/authorize/callback` (handle redirect after authorization)

**OAuth2 Client Management** (gym admin only):
- `GET /oauth/clients` (list OAuth2 clients for gym)
- `POST /oauth/clients` (create new OAuth2 client/integration)
- `GET /oauth/clients/{id}` (get client details, excludes secret)
- `PUT /oauth/clients/{id}` (update client name, redirect URIs, scopes)
- `POST /oauth/clients/{id}/regenerate-secret` (regenerate client secret)
- `DELETE /oauth/clients/{id}` (deactivate OAuth2 client)

**Active Sessions & Token Management**:
- `GET /auth/sessions` (list user's active sessions/tokens)
- `DELETE /auth/sessions/{token_id}` (revoke specific session)
- `DELETE /auth/sessions/all` (revoke all sessions except current)

**MCP Integration** (trainer-only, OAuth2-based):
- `POST /trainers/{id}/mcp/authorize` (initiate OAuth2 authorization for MCP, returns authorization URL)
- `GET /trainers/{id}/mcp/callback?code=...` (OAuth2 callback, exchange code for tokens)
- `GET /trainers/{id}/mcp/status` (check if MCP enabled, return token info)
- `DELETE /trainers/{id}/mcp/revoke` (revoke MCP access tokens)

**Important**: MCP uses OAuth2 but is separate from general OAuth2 clients. Trainers can ONLY authorize MCP, not create general OAuth2 integrations.

### 5.11 Calendar & Schedule

**Trainer Calendar Export**:
- `GET /trainers/{id}/calendar.ics?token={access_token}` (iCalendar feed, read-only)
- `POST /trainers/{id}/calendar/token/generate` (generate calendar access token)
- `DELETE /trainers/{id}/calendar/token/revoke` (revoke calendar access token)
- `GET /trainers/{id}/calendar/settings` (get calendar privacy settings)
- `PUT /trainers/{id}/calendar/settings` (update settings, e.g., hide client names)

**Schedule Management**:
- `GET /schedule?location_id=&trainer_id=&date=` (query schedules)
- `POST /schedule/book` (book training session)
- `PUT /schedule/{id}` (update scheduled session)
- `POST /schedule/{id}/cancel` (cancel session)
- `POST /schedule/{id}/confirm` (confirm tentative session)

### 5.12 Gym/Location

- `GET/POST/PUT/DELETE /gyms`
- `GET/POST/PUT/DELETE /locations`

### 5.13 People

- `/trainers`
- `/clients`

### 5.14 Programs

- `/programs`
- `/programs/{id}/days`

### 5.15 Workouts

- `POST /workouts/start`
- `POST /workouts/{id}/complete`
- `PUT /workouts/{id}/exercises/{we_id}/sets`

### 5.16 Measurements & Goals

**Measurement Types**:
- `GET /gyms/{id}/measurement-types` (list all active measurement types for gym)
- `POST /gyms/{id}/measurement-types` (admin: create custom measurement type)
- `PUT /measurement-types/{id}` (admin: update custom type or deactivate standard type)
- `DELETE /measurement-types/{id}` (admin: soft-delete custom measurement type)

**Client Measurements**:
- `GET /clients/{id}/measurements?type=&date_range=` (list measurements, filterable by type and date)
- `POST /clients/{id}/measurements` (trainer: record new measurement, optionally link to progress photo)
- `GET /clients/{id}/measurements/{measurement_id}` (get single measurement with details)
- `GET /clients/{id}/measurements/latest?types=` (get latest measurements for specified types)
- `GET /clients/{id}/measurements/history?type=` (time-series data for charting)

**Goals**:
- `GET /clients/{id}/goals?status=` (list client goals, filterable by status: active | achieved | abandoned)
- `POST /clients/{id}/goals` (create new goal)
- `GET /goals/{id}` (get goal with current progress)
- `PUT /goals/{id}` (update goal target or deadline)
- `POST /goals/{id}/abandon` (mark goal as abandoned)
- `DELETE /goals/{id}` (soft-delete goal)
- `GET /clients/{id}/goals/progress` (summary of all active goals with progress percentages)

**Measurement Reminders**:
- `GET /trainers/{id}/reminders/due` (list clients due for measurements today)
- `POST /reminders/{id}/snooze` (snooze reminder for 3 days, 1 week, or 2 weeks)
- `GET /gyms/{id}/reminders/settings` (get gym measurement reminder settings)
- `PUT /gyms/{id}/reminders/settings` (admin: enable/disable reminders, set frequency)

### 5.17 Analytics & Progress Visualization

**Client Progress**:
- `GET /clients/{id}/analytics/workouts?date_range=` (workout metrics over time)
- `GET /clients/{id}/analytics/volume?date_range=` (total weight lifted trends)
- `GET /clients/{id}/analytics/prs?date_range=` (PRs achieved over time)
- `GET /clients/{id}/analytics/exercises/{exercise_id}` (progress on specific exercise)
- `GET /clients/{id}/analytics/summary` (high-level stats: total workouts, PRs, avg volume)

**Peer Comparison** (if enabled):
- `GET /clients/{id}/analytics/compare?measurement_type=` (compare client to gym average)
- `GET /gyms/{id}/analytics/benchmarks` (anonymized gym averages for measurements)

**Workout Analytics**:
- `GET /workouts/{id}/analytics` (get pre-calculated analytics for completed workout)
- `GET /workouts/{id}/analytics/preview` (real-time preview during active workout, not persisted)

### 5.18 Gym Admin Reporting

**Dashboard Metrics**:
- `GET /gyms/{id}/analytics/dashboard?period=` (high-level metrics: revenue, clients, workouts)
- `GET /gyms/{id}/analytics/revenue?period_type=day|week|month&date_range=` (revenue trends)
- `GET /gyms/{id}/analytics/clients?period_type=day|week|month&date_range=` (client growth/churn)
- `GET /gyms/{id}/analytics/engagement?period_type=day|week|month&date_range=` (workout frequency, check-ins)
- `GET /gyms/{id}/analytics/trainers?period_type=week|month&date_range=` (trainer utilization, client load)

**Export**:
- `POST /gyms/{id}/analytics/export` (request analytics export as CSV/PDF, async)
- `GET /gyms/{id}/analytics/export/{export_id}/download` (download link)

**Real-time Stats** (for admin dashboard):
- `GET /gyms/{id}/analytics/realtime` (current active clients, trainers on duty, today's workouts)
- `GET /locations/{id}/analytics/realtime` (per-location realtime occupancy)

---
