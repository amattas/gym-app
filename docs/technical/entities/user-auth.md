# User & Authentication Entities

All entities stored in PostgreSQL.

---

## User

**Purpose**: Authentication entity representing login credentials for a Client.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | UUID | Primary key |
| `client_id` | UUID | FK to Client (one-to-one) |
| `email` | string | Unique, required |
| `password_hash` | string? | Argon2id hash (null if passkey-only) |
| `password_hash_version` | int | Hash algorithm version (1 = Argon2id) |
| `roles` | JSON | Array of roles (admin, trainer, front_desk, client) |
| `login_enabled` | bool | Can be revoked by primary member |
| `created_by_client_id` | UUID? | Which primary member granted login |
| `last_login_at` | datetime? | Last successful login |

### MFA Fields

| Field | Type | Description |
|-------|------|-------------|
| `mfa_enabled` | bool | Default true for admin/trainer |
| `mfa_method` | enum | 'totp', 'email', 'passkey_only' |
| `totp_secret` | string | Encrypted TOTP secret |
| `totp_backup_codes` | JSON | Encrypted backup codes (10 codes) |
| `mfa_enforced_at` | datetime? | When MFA became required |

### Password Requirements

- Minimum 12 characters
- Must contain: uppercase, lowercase, number, special character
- Cannot contain user's email or name
- Checked against Have I Been Pwned breach database

### Argon2id Parameters (version 1)

- Memory cost: 64 MB minimum
- Time cost: 3 iterations minimum
- Parallelism: 4 threads
- Output length: 32 bytes
- Salt: 128-bit minimum, auto-generated

### Constraints

- One Client can have at most one User
- Email must be unique across all Users
- MFA required for admin/trainer roles (7-day grace period)

---

## UserPasskey

**Purpose**: WebAuthn/FIDO2 passkey credentials for passwordless authentication.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `passkey_id` | UUID | Primary key |
| `user_id` | UUID | FK to User |
| `credential_id` | string | WebAuthn credential ID (unique) |
| `public_key` | text | COSE-encoded public key |
| `counter` | bigint | Signature counter for replay protection |
| `device_name` | string | User-friendly name (e.g., "iPhone 15") |
| `device_type` | enum | 'platform' or 'cross_platform' |
| `last_used_at` | datetime? | Last authentication |

### Device Types

- `platform`: Built-in (TouchID, FaceID, Windows Hello)
- `cross_platform`: External security key (YubiKey, Titan Key)

---

## OAuth2Client

**Purpose**: OAuth2 client applications registered by gym administrators.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `client_id` | UUID | OAuth2 client_id |
| `client_secret` | string | Hashed secret |
| `gym_id` | UUID | FK to Gym |
| `created_by_user_id` | UUID | Admin who created it |
| `name` | string | Client name |
| `redirect_uris` | JSON | Allowed redirect URIs |
| `grant_types` | JSON | Allowed grant types |
| `scopes_allowed` | JSON | Allowed scopes |
| `is_active` | bool | Can be revoked |

### Available Scopes

- `gym:read`, `clients:read`, `clients:write`
- `workouts:read`, `workouts:write`
- `schedule:read`, `schedule:write`
- `measurements:read`, `measurements:write`
- `analytics:read`

### Access Control

- Only gym admins can create OAuth2 clients
- Trainers cannot create OAuth2 clients

---

## OAuth2AccessToken

**Purpose**: Issued OAuth2 access tokens for API access.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `token_id` | UUID | Primary key |
| `client_id` | UUID? | FK to OAuth2Client (null for MCP tokens) |
| `user_id` | UUID? | FK to User |
| `token_type` | enum | 'oauth_client', 'mcp', 'calendar' |
| `token_hash` | string | SHA-256 hash of access token |
| `refresh_token_hash` | string? | SHA-256 hash of refresh token |
| `scopes` | JSON | Granted scopes |
| `expires_at` | datetime | Access token expiration (1 hour) |
| `refresh_token_expires_at` | datetime? | Refresh token expiration (30 days) |
| `revoked_at` | datetime? | If manually revoked |

### Security

- Never store plaintext tokens
- Store SHA-256 hash only
- Tokens auto-revoked if user disabled

---

## PasswordResetToken

**Purpose**: Temporary tokens for password reset workflow.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `token_id` | UUID | Primary key |
| `user_id` | UUID | FK to User |
| `token_hash` | string | SHA-256 hash of reset token |
| `expires_at` | datetime | 1 hour expiration |
| `used_at` | datetime? | Null until token used |
| `ip_address` | string? | IP that requested reset |

### Security Requirements

- Tokens are 256-bit cryptographically secure random
- Never store plaintext (SHA-256 hash only)
- Single-use (marked as used after consumption)
- Rate limit: Max 3 requests per email per hour
