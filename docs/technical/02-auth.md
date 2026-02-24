# Authentication & Authorization

This document defines the authentication and authorization implementation.

---

## OAuth2 Overview

All API authentication uses **OAuth2 2.0** standard with the following grant types:

| Grant Type | Use Case | Security |
|------------|----------|----------|
| **Authorization Code + PKCE** | Web/mobile apps (preferred) | Most secure |
| **Refresh Token** | Token renewal | Standard |
| **Client Credentials** | Server-to-server | For trusted backends |
| ~~Password~~ | ~~First-party apps only~~ | **DEPRECATED** - migrate to PKCE |

---

## Authentication Flows

### 1. User Registration

```
1. User provides email + password
2. Validate password (12+ chars, complexity, breach check)
3. Hash password with Argon2id
4. Create User record (MFA enabled for admin/trainer)
5. Send email verification link
```

**MFA Defaults by Role**:
- Admin/Trainer: MFA required (7-day grace period)
- Client: MFA optional

### 2. Password Login

```
1. User submits email + password
2. Verify password hash (Argon2id)
3. Hash migration check (upgrade old hashes)
4. MFA check if enabled
5. Generate OAuth2 tokens (access + refresh)
6. Return tokens
```

**Token Lifetimes**:
- Access token: 1 hour
- Refresh token: 30 days

### 3. Passkey Registration

```
1. User navigates to "Add Passkey"
2. Server generates WebAuthn challenge
3. Client calls navigator.credentials.create()
4. User authenticates with biometric/PIN
5. Server verifies attestation, stores public key
6. Optional: Enable passkey-only mode (remove password)
```

### 4. Passkey Login

```
1. User clicks "Use Passkey"
2. Server generates challenge with allowed credentials
3. Client calls navigator.credentials.get()
4. User authenticates with biometric/PIN
5. Server verifies signature against stored public key
6. Check signature counter (replay protection)
7. Generate OAuth2 tokens (no additional MFA needed)
```

### 5. Password Reset

```
1. User requests reset (POST /auth/reset-password)
2. Generate 256-bit secure token, hash with SHA-256
3. Store hash in PasswordResetToken (1 hour expiry)
4. Send reset link via email
5. User clicks link, enters new password
6. Verify token (not expired, not used)
7. Hash new password, update User
8. Invalidate all existing sessions
9. Send confirmation email
```

**Security**:
- Same response whether email exists or not (prevent enumeration)
- Rate limit: 3 requests per email per hour
- Single-use tokens

---

## MFA Implementation

### TOTP (Time-based One-Time Password)

```
1. User enables MFA in settings
2. Generate 32-byte secret, display QR code
3. User scans with authenticator app
4. User enters current code to verify
5. Generate 10 backup codes (one-time use)
6. Store encrypted secret and codes
```

**Verification**:
- Accept codes within ±1 time period (30 seconds tolerance)
- Rate limit: 5 attempts per minute

### Email MFA (Fallback)

```
1. Generate 6-digit code
2. Send to user's email
3. Code expires in 10 minutes
4. Single-use
```

### Backup Codes

- 10 codes generated on MFA setup
- Each code is one-time use
- User notified when codes running low
- Can regenerate all codes (invalidates old)

---

## Token Security

### Access Tokens (JWT)

```json
{
  "sub": "user_id",
  "roles": ["trainer", "client"],
  "gym_id": "...",
  "iat": 1234567890,
  "exp": 1234571490
}
```

- Signed with RS256 or EdDSA
- Contains minimal claims (not sensitive data)
- Validated on every API request

### Refresh Tokens

- Opaque tokens (not JWT)
- Stored as SHA-256 hash in database
- Can be rotated on each use (optional)
- Revocable at any time

### Token Storage

| Token | Storage | Notes |
|-------|---------|-------|
| Access Token | Memory only | Never persist |
| Refresh Token | Secure storage | Keychain (iOS), Keystore (Android) |

---

## OAuth2 Scopes

### Client Scopes

| Scope | Description |
|-------|-------------|
| `profile` | Read user profile |
| `workouts:read` | Read workout history |
| `workouts:write` | Log workouts |
| `schedule:read` | View schedule |
| `schedule:write` | Book/cancel sessions |
| `measurements:read` | View measurements |
| `health:read` | View health data |

### Admin/Trainer Scopes

| Scope | Description |
|-------|-------------|
| `gym:read` | Read gym settings |
| `gym:write` | Modify gym settings |
| `clients:read` | View all clients |
| `clients:write` | Manage clients |
| `analytics:read` | View reports |

---

## Role-Based Access Control (RBAC)

### Roles

| Role | Description |
|------|-------------|
| `platform_admin` | Platform-level admin |
| `admin` | Gym administrator |
| `trainer` | Gym trainer |
| `front_desk` | Front desk staff |
| `client` | Regular member |

### Role Hierarchy

```
platform_admin
    └── admin
        ├── trainer
        └── front_desk
client (separate hierarchy)
```

### Permission Examples

| Action | Required Role |
|--------|---------------|
| Modify gym settings | admin |
| View all clients | admin, trainer |
| Log workout for client | trainer |
| View own workouts | client, trainer, admin |
| Cancel membership | admin |

---

## Session Management

### Active Sessions

- Users can view all active sessions
- Sessions identified by: device, location, last used
- Users can revoke individual sessions
- Admin can revoke all sessions for a user

### Session Invalidation

Sessions are invalidated when:
- User changes password
- User enables/disables MFA
- Admin revokes access
- Token expires naturally

---

## Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/auth/login` | 5 attempts | 15 minutes |
| `/auth/reset-password` | 3 requests | 1 hour |
| `/auth/mfa/verify` | 5 attempts | 1 minute |
| `/auth/register` | 10 requests | 1 hour |

---

## Related Documents

- [Entities - User/Auth](entities/user-auth.md) - Entity definitions
- [Security](../nfr/security.md) - Security requirements
