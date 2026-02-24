# Technical Glossary

This document defines technical terms used throughout the specifications.

---

## Authentication & Security

| Term | Definition |
|------|------------|
| **Argon2id** | Password hashing algorithm (memory-hard, side-channel resistant) |
| **PKCE** | Proof Key for Code Exchange - OAuth2 extension for public clients |
| **TOTP** | Time-based One-Time Password (RFC 6238) |
| **WebAuthn** | Web Authentication API for passwordless auth (FIDO2) |
| **Passkey** | FIDO2 credential for passwordless authentication |
| **MFA** | Multi-Factor Authentication |
| **JWT** | JSON Web Token for access tokens |
| **RBAC** | Role-Based Access Control |

---

## Database & Storage

| Term | Definition |
|------|------------|
| **OLTP** | Online Transaction Processing - real-time transactional data |
| **JSONB** | PostgreSQL binary JSON format with indexing support |
| **Partitioning** | Splitting large tables by time/key for performance |
| **Soft Delete** | Mark records as deleted without physical removal |
| **Idempotency Key** | Unique key to prevent duplicate operations |

---

## Caching & Performance

| Term | Definition |
|------|------------|
| **Cache-Aside** | Pattern where app checks cache before database |
| **TTL** | Time To Live - cache expiration duration |
| **CDN** | Content Delivery Network for static assets |
| **Signed URL** | Time-limited URL with authentication signature |

---

## API & Integration

| Term | Definition |
|------|------------|
| **OAuth2** | Authorization framework for API access |
| **REST** | Representational State Transfer API style |
| **GraphQL** | Query language for APIs (Phase 3) |
| **Webhook** | HTTP callback for event notifications |
| **CORS** | Cross-Origin Resource Sharing |

---

## Data Formats

| Term | Definition |
|------|------------|
| **UUID** | Universally Unique Identifier (128-bit) |
| **ISO 8601** | Date/time format (e.g., 2024-01-15T10:30:00Z) |
| **IANA Timezone** | Standard timezone identifiers (e.g., America/New_York) |
| **Decimal** | Exact numeric type for money/measurements |

---

## Architecture Patterns

| Term | Definition |
|------|------------|
| **Multi-tenant** | Single instance serving multiple organizations |
| **Event Sourcing** | Store state changes as sequence of events |
| **Outbox Pattern** | Reliable event publishing with database transactions |
| **CQRS** | Command Query Responsibility Segregation |

---

## Mobile & Sync

| Term | Definition |
|------|------------|
| **Offline-First** | App works without network, syncs when online |
| **Push Notification** | Server-initiated message to mobile device |
| **Deep Link** | URL that opens specific app screen |
| **Keychain/Keystore** | Secure credential storage on iOS/Android |
