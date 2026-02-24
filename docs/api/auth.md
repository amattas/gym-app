# Authentication API

Authentication and authorization endpoints.

---

## Registration

### Register User

```http
POST /auth/register
```

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecureP@ssw0rd123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response** (201):
```json
{
  "data": {
    "user_id": "uuid",
    "email": "user@example.com",
    "email_verified": false
  }
}
```

### Verify Email

```http
POST /auth/verify-email
```

**Request**:
```json
{
  "token": "verification_token"
}
```

---

## Login

### Password Login

```http
POST /auth/login
```

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecureP@ssw0rd123"
}
```

**Response** (200) - Without MFA:
```json
{
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

**Response** (200) - MFA Required:
```json
{
  "data": {
    "requires_mfa": true,
    "mfa_method": "totp",
    "mfa_token": "temporary_token"
  }
}
```

### Verify MFA

```http
POST /auth/mfa/verify
```

**Request**:
```json
{
  "mfa_token": "temporary_token",
  "code": "123456"
}
```

### Passkey Login - Challenge

```http
POST /auth/login/passkey/challenge
```

**Request**:
```json
{
  "email": "user@example.com"
}
```

**Response**:
```json
{
  "data": {
    "challenge": "base64_encoded_challenge",
    "allowCredentials": [
      { "id": "credential_id", "type": "public-key" }
    ]
  }
}
```

### Passkey Login - Verify

```http
POST /auth/login/passkey/verify
```

**Request**:
```json
{
  "credential_id": "...",
  "authenticator_data": "...",
  "client_data_json": "...",
  "signature": "..."
}
```

---

## Token Management

### Refresh Token

```http
POST /auth/token/refresh
```

**Request**:
```json
{
  "refresh_token": "..."
}
```

**Response**:
```json
{
  "data": {
    "access_token": "new_token",
    "expires_in": 3600
  }
}
```

### Revoke Token

```http
POST /auth/token/revoke
```

**Request**:
```json
{
  "token": "token_to_revoke"
}
```

---

## Password Reset

### Request Reset

```http
POST /auth/password/reset
```

**Request**:
```json
{
  "email": "user@example.com"
}
```

**Response** (200) - Always same response:
```json
{
  "data": {
    "message": "If that email exists, we've sent a reset link"
  }
}
```

### Complete Reset

```http
POST /auth/password/reset/confirm
```

**Request**:
```json
{
  "token": "reset_token",
  "password": "NewSecureP@ssw0rd123"
}
```

---

## MFA Management

### Enable TOTP

```http
POST /auth/mfa/totp/enable
```

**Response**:
```json
{
  "data": {
    "secret": "base32_secret",
    "qr_code_url": "otpauth://totp/...",
    "backup_codes": ["code1", "code2", ...]
  }
}
```

### Verify TOTP Setup

```http
POST /auth/mfa/totp/verify
```

**Request**:
```json
{
  "code": "123456"
}
```

### Disable MFA

```http
POST /auth/mfa/disable
```

**Request**:
```json
{
  "password": "current_password"
}
```

---

## Passkey Management

### Register Passkey - Challenge

```http
POST /auth/passkeys/register/challenge
```

### Register Passkey - Complete

```http
POST /auth/passkeys/register/verify
```

**Request**:
```json
{
  "credential_id": "...",
  "public_key": "...",
  "attestation_object": "...",
  "device_name": "iPhone 15"
}
```

### List Passkeys

```http
GET /auth/passkeys
```

**Response**:
```json
{
  "data": [
    {
      "passkey_id": "uuid",
      "device_name": "iPhone 15",
      "device_type": "platform",
      "created_at": "...",
      "last_used_at": "..."
    }
  ]
}
```

### Delete Passkey

```http
DELETE /auth/passkeys/{passkey_id}
```

---

## Sessions

### List Active Sessions

```http
GET /auth/sessions
```

**Response**:
```json
{
  "data": [
    {
      "session_id": "uuid",
      "device": "Chrome on macOS",
      "ip_address": "192.168.1.1",
      "location": "New York, US",
      "last_active_at": "...",
      "is_current": true
    }
  ]
}
```

### Revoke Session

```http
DELETE /auth/sessions/{session_id}
```

### Revoke All Sessions

```http
DELETE /auth/sessions
```
