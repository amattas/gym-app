# Technical Specifications

**CONFIDENTIAL**: This document contains proprietary technical implementation details. Access restricted to authorized development team members only.

---

## Table of Contents

1. [Data Layer Architecture](#1-data-layer-architecture)
2. [Domain Entities](#2-domain-entities)
3. [Authentication & Authorization](#3-authentication--authorization)
4. [Program Progression](#4-program-progression)
5. [PR Tracking](#5-pr-tracking)
6. [Security Requirements](#6-security-requirements)
7. [Technical Implementation Decisions](#7-technical-implementation-decisions)
8. [Technical Glossary](#8-technical-glossary)
9. [Architecture Decision Records (ADRs)](#9-architecture-decision-records-adrs)
10. [Repository Structure](#10-repository-structure)

---

## 1. Data Layer Architecture

### 1.1 Storage Strategy (Hybrid: PostgreSQL + MongoDB + Redis)

The system uses a hybrid storage approach with three complementary data stores, each optimized for specific access patterns and requirements.

#### PostgreSQL (System of Record for OLTP)

Use **PostgreSQL** as the authoritative system of record for all transactional, relational data:

- **User & Auth**: users, roles, sessions, MFA credentials, OAuth2 clients/tokens
- **Organizational Hierarchy**: gyms, locations, accounts, clients, trainers
- **Membership & Billing**: client memberships (with snapshotted plan limits), plan assignments
- **Scheduling & Check-ins**: schedule bookings, check-in events, trainer availability
- **Training Data**: programs, program days, exercises, workouts, sets, measurements
- **Audit & Compliance**: audit logs, change tracking, event history
- **Agreements**: metadata and status (binary content in object storage)

**Rationale**: PostgreSQL provides ACID guarantees, foreign key constraints, complex joins, and transactional integrity required for business-critical operations. All user-facing operations that require immediate consistency must read from and write to PostgreSQL.

#### MongoDB (Document/Time-Series Data)

Use **MongoDB** narrowly for document-shaped and time-series data that benefits from schema flexibility:

- **Gym Configuration**: `GymPlanLimits` documents (feature flags, plan limits, per-gym overrides)
- **Usage Metering**: `UsageMetricRollup` time-series collections (API calls, AI calls, billing rollups)
- **Trainer Availability**: Optional document-based availability schedules (if not normalized in PostgreSQL)
- **Analytics Aggregates**: Pre-computed time-windowed rollups for dashboards

**Rationale**: MongoDB provides schema flexibility for rapidly evolving configuration and better performance for time-series data. However, **no business workflow should require atomically consistent operations across both PostgreSQL and MongoDB**. Use event-driven patterns (outbox pattern) for eventual consistency when syncing data between stores.

**Important Design Constraints**:
- If `PlanTemplate` is stored in MongoDB, snapshot critical enforcement fields (visit entitlements, expiration rules) into PostgreSQL's `ClientMembership` table at assignment time. This ensures check-in and entitlement validation never depend on MongoDB availability.
- Prefer **MongoDB Atlas** over DocumentDB to avoid compatibility issues with time-series collections, TTL indexes, and change streams.
- MongoDB is never the authoritative source for data that requires transactional guarantees or complex joins.

#### Redis (Ephemeral Performance & Coordination Layer)

Use **Redis** as a cache-aside and coordination layer for performance optimization and rate limiting:

- **Cache-Aside Reads**: GymPlanLimits lookups, PlanTemplate data, trainer availability, "today's schedule", dashboard widgets
  - Keys should include relevant IDs: `gym:{gym_id}:plan_limits`, `trainer:{trainer_id}:availability`
  - Set appropriate TTLs based on data volatility (e.g., 5-15 minutes for plan limits, 1-5 minutes for schedules)
- **Derived Aggregates**: Busyness time-slot calculations (15-min granularity), client analytics summaries, dashboard metrics
  - Short TTLs (1-5 minutes) with easy recompute from PostgreSQL
- **Rate Limiting**: Login attempts, password resets, API throttles (per-user, per-gym)
- **Idempotency Keys**: 24-hour TTL for deduplication (optional; can persist in PostgreSQL if cache loss tolerance is low)
- **Distributed Locks**: Short-lived locks for scheduling/booking to prevent double-booking (but correctness guaranteed by PostgreSQL constraints)

**Rationale**: Redis accelerates read-heavy operations and provides coordination primitives without adding a third "source of truth." The system **must remain fully functional if Redis is flushed or restarted**—all data can be reconstructed from PostgreSQL/MongoDB.

**Design Assumption**: Redis is ephemeral. All cached data has a source of truth in PostgreSQL or MongoDB. Cache misses trigger recomputation and cache population, not failures.

#### Binary Storage

Store large binaries (photos, signed PDFs) in object storage; store references/metadata in PostgreSQL.

**Implementation**: Use object storage (S3/similar) with CDN for serving. Store only URLs and metadata in the database.

### 1.2 Database Responsibilities

**OLTP Schema**:
- Transactional operations with immediate consistency requirements
- User-facing read/write operations
- Real-time data access for mobile and web apps

**Event/Audit Tables**:
- History tracking for compliance
- Audit logging for security
- Change tracking for business analytics

**Derived Aggregates**:
- Pre-calculated metrics for dashboard performance
- Busyness calculations (15-minute granularity)
- Adherence tracking
- PR rollups

---

## 2. Domain Entities

### 2.1 Gym (PostgreSQL)

**Purpose**: Top-level organization entity representing a gym business.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal

class Gym(BaseModel):
    gym_id: UUID = Field(..., description="Primary key")
    name: str = Field(..., description="Required")
    logo_url: Optional[str] = Field(None, description="Optional, CDN URL")
    primary_color: Optional[str] = Field(None, description='Hex color code, e.g., "#FF5733"')
    accent_color: Optional[str] = Field(None, description='Hex color code, e.g., "#33C1FF"')

    # Timezone & Scheduling
    timezone: str = Field(..., description='IANA timezone, e.g., "America/New_York", required for scheduling nightly jobs')

    # Measurement & Progress Settings
    measurement_reminders_enabled: bool = Field(default=False)
    measurement_reminder_frequency_days: Optional[int] = Field(None, description="e.g., 30 for monthly")
    allow_peer_comparison: bool = Field(default=False)
    progress_photo_required_for_measurements: bool = Field(default=False)

    # Calendar & Integration Settings
    hide_client_names_in_calendar: bool = Field(default=False, description="gym-wide default (can be overridden per-trainer)")

    # Custom Email Domain Configuration (Enterprise feature)
    custom_email_domain: Optional[str] = Field(None, description='e.g., "powerliftgym.com"')
    custom_email_sender_name: Optional[str] = Field(None, description='e.g., "PowerLift Gym"')
    custom_email_from_address: Optional[str] = Field(None, description='e.g., "notifications@powerliftgym.com"')
    custom_email_reply_to: Optional[str] = Field(None, description='e.g., "support@powerliftgym.com"')
    custom_email_status: Literal['not_configured', 'pending_verification', 'verified', 'failed'] = Field(default='not_configured')
    custom_email_verified_at: Optional[datetime] = None

    # Custom Login Domain Configuration (Enterprise feature)
    custom_login_domain: Optional[str] = Field(None, description='e.g., "app.powerliftgym.com"')
    custom_login_status: Literal['not_configured', 'pending_verification', 'verified', 'failed'] = Field(default='not_configured')
    custom_login_verified_at: Optional[datetime] = None

    # Email Service Provider Metadata
    resend_domain_id: Optional[str] = Field(None, description="Resend domain ID")
    ssl_certificate_path: Optional[str] = Field(None, description="Let's Encrypt certificate path")
    ssl_expires_at: Optional[datetime] = None

    # Usage metrics (derived, for billing)
    usage_clients_count: int = Field(..., description="Derived")
    usage_locations_count: int = Field(..., description="Derived")
    usage_trainers_count: int = Field(..., description="Derived")
    usage_api_calls_count: int = Field(..., description="Derived, time-windowed")
    usage_ai_api_calls_count: int = Field(..., description="Derived, time-windowed")
```

**Relationships**:
- Gym has many Locations
- Gym has many Trainers
- Gym has many UsageMetricRollups
- Gym has one GymPlanLimits (NoSQL)

**Branding**:
- Logo and colors used for white-label experience in mobile and web apps
- Each gym can have custom branding

**Custom Domains** (Enterprise feature):
- Gyms can configure custom email domains for sending emails from their own domain
- Gyms can configure custom login domains for white-label branded login experience
- Both features require DNS verification before activation
- Email domains integrated with Resend email service provider
- Login domains provisioned with automated SSL certificates (Let's Encrypt)

**CORS Integration for Custom Login Domains**:

When a gym configures a custom login domain (e.g., `app.powerliftgym.com`), the API must dynamically allow CORS requests from that domain.

**Implementation**:
```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json

# CORS middleware configuration
async def get_verified_custom_login_domains() -> List[str]:
    """Get verified custom login domains with Redis caching."""
    # Check Redis cache first
    cached = await redis.get('cors:allowed_origins')
    if cached:
        return json.loads(cached)

    # Query database for verified custom login domains
    query = {
        'custom_login_status': 'verified',
        'custom_login_domain': {'$ne': None}
    }
    gyms = await db.gyms.find(query).to_list(None)
    domains = [f"https://{gym.custom_login_domain}" for gym in gyms]

    # Cache for 5 minutes
    await redis.setex('cors:allowed_origins', 300, json.dumps(domains))

    return domains

async def get_allowed_origins() -> List[str]:
    """Get all allowed origins including platform defaults and custom domains."""
    allowed_origins = [
        'https://app.gym.example.com',        # Platform default
        'https://admin.gym.example.com',      # Platform default
    ]
    custom_domains = await get_verified_custom_login_domains()
    allowed_origins.extend(custom_domains)
    return allowed_origins

# CORS middleware setup
app = FastAPI()

@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    """Custom CORS middleware for dynamic origin validation."""
    origin = request.headers.get("origin")
    allowed_origins = await get_allowed_origins()

    response = await call_next(request)

    if origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"

    return response
```

**Cache Invalidation**:
- When a gym's `custom_login_status` changes to `'verified'`: invalidate cache
- When a gym's `custom_login_domain` is removed: invalidate cache
- Cache TTL: 5 minutes (balance between performance and consistency)

---

### 2.1.1 DomainVerification (PostgreSQL)

**Purpose**: Tracks DNS verification records for custom email and login domains.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class DNSRecord(BaseModel):
    record_type: Literal['TXT', 'CNAME']
    host: str  # e.g., "_gymapp-verify.powerliftgym.com"
    value: str  # e.g., "gymapp-verify=abc123..."

class DomainVerification(BaseModel):
    domain_verification_id: UUID
    gym_id: UUID
    domain_type: Literal['email', 'login']
    domain: str  # Domain being verified (e.g., "powerliftgym.com")

    # Verification challenge
    verification_token: str  # Random 64-char hex token (cryptographically secure)
    expected_dns_record: DNSRecord

    # Status tracking
    status: Literal['pending', 'verified', 'failed']
    last_checked_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    failed_reason: Optional[str] = None  # Human-readable error message
    retry_count: int = Field(default=0)  # Max: 10

    # Lifecycle
    created_at: datetime
    expires_at: datetime  # 72 hours from creation
```

**Relationships**:
- BelongsTo Gym (via gym_id)

**Indexes**:
- Primary key: domain_verification_id
- Unique index: (gym_id, domain_type) WHERE status IN ('pending', 'verified')
- Index on expires_at for auto-cleanup jobs
- Index on (gym_id, domain_type, status) for lookups

**Business Rules**:
- Only one active verification per (gym_id, domain_type) pair
- Verification tokens generated using crypto.randomBytes(32).toString('hex')
- Verifications expire after 72 hours
- Max 10 retry attempts before marking as failed
- Expired verifications auto-deleted by background job

---

### 2.1.2 EmailDomainSPFRecord (PostgreSQL)

**Purpose**: Tracks SPF/DKIM/DMARC validation status for custom email domains.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class EmailDomainSPFRecord(BaseModel):
    spf_record_id: UUID
    gym_id: UUID
    domain: str

    # SPF validation
    required_spf_include: str
    current_spf_record: Optional[str] = None
    is_valid: bool
    validation_errors: Optional[List[str]] = None

    # DKIM validation
    dkim_status: Literal['not_configured', 'pending', 'verified']
    dkim_cname_host: Optional[str] = None
    dkim_cname_value: Optional[str] = None

    # DMARC validation
    dmarc_status: Literal['not_configured', 'pending', 'verified']

    # Tracking
    last_checked_at: Optional[datetime] = None
    created_at: datetime```

**Relationships**:
- BelongsTo Gym (via gym_id)

**Indexes**:
- Primary key: spf_record_id
- Unique index: (gym_id, domain)
- Index on gym_id for lookups

**Business Rules**:
- One SPF record per email domain per gym
- Validation checks performed on-demand via API and nightly background job
- SPF record must include Resend's SPF include directive
- DKIM and DMARC records validated against Resend-provided values

---

### 2.1.3 EmailTemplate (PostgreSQL)

**Purpose**: Stores email templates for system-wide and gym-specific emails. Uses Jinja2 templating.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class EmailTemplate(BaseModel):
    email_template_id: UUID
    template_key: str
    gym_id: Optional[UUID] = None

    # Template content
    subject: str
    body_html: str
    body_text: Optional[str] = None

    # Template metadata
    template_type: Literal['system', 'gym_override']
    category: Literal['transactional', 'operational', 'marketing']
    description: Optional[str] = None
    required_variables: List[str]

    # Version control
    version: int
    is_active: bool

    # Audit
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime```

**Relationships**:
- BelongsTo Gym (via gym_id, optional for system templates)
- BelongsTo User (via created_by, for gym overrides)

**Indexes**:
- Primary key: email_template_id
- Unique index: (template_key) WHERE gym_id IS NULL (system templates)
- Unique index: (template_key, gym_id) WHERE gym_id IS NOT NULL (gym overrides)
- Index on (gym_id, is_active) for gym override lookups
- Index on template_key for fast resolution

**Business Rules**:
- **System templates**: `gym_id = NULL`, `template_type = 'system'`, `is_active = true` (always)
  - Platform administrator only can create/modify
  - Cannot be deleted or deactivated (critical infrastructure)
  - Always exist and are always active
  - Required for core platform functionality (password resets, MFA, etc.)
- **Gym override templates**: `gym_id = <uuid>`, `template_type = 'gym_override'`
  - Initially NOT implemented (future feature)
  - Gym admins can override system templates
  - Can be deactivated or deleted (falls back to system template)
  - When active gym template exists, use it; otherwise fall back to system template
- **Required system templates** (must always exist):
  - `password_reset` - Password reset email with token link
  - `password_changed` - Confirmation email after password change
  - `welcome_email` - New user signup welcome email
  - `email_verification` - Email address verification link
  - `mfa_code` - MFA verification code email
  - `mfa_enabled` - Confirmation email when MFA is enabled
  - `mfa_disabled` - Confirmation email when MFA is disabled
  - `membership_reminder` - Measurement reminder email to trainers
  - `session_scheduled` - Training session scheduled confirmation
  - `session_canceled` - Training session canceled notification
  - `goal_achieved` - Congratulations email when goal is achieved

**Template Resolution Logic**:
```python
function resolveEmailTemplate(template_key: string, gym_id?-> UUID)-> EmailTemplate {
  if (gym_id) {
    # Check for gym override (future feature)
    gymTemplate = await EmailTemplate.findOne({
      template_key,
      gym_id,
      is_active: True
    })
    if (gymTemplate) return gymTemplate
  }

    # Fall back to system template
  systemTemplate = await EmailTemplate.findOne({
    template_key,
    gym_id: None,
    is_active: True
  })

  if (!systemTemplate) {
    throw new Error(`Required system template "${template_key}" not found`)
  }

  return systemTemplate
}
```

**Jinja2 Variables** (common across templates):
- `gym_name` - Name of gym (from Gym entity)
- `gym_logo_url` - Logo URL for email header
- `gym_primary_color` - Primary brand color
- `gym_accent_color` - Accent brand color
- `user_name` - Recipient's name
- `user_email` - Recipient's email
- `platform_support_email` - Platform support email address

**Template-specific Variables**:
- `password_reset`: `reset_token`, `reset_url`, `expires_in_hours`
- `mfa_code`: `mfa_code`, `expires_in_minutes`
- `email_verification`: `verification_token`, `verification_url`
- `session_scheduled`: `trainer_name`, `client_name`, `scheduled_start`, `location_name`
- `goal_achieved`: `goal_type`, `goal_description`, `achieved_value`, `target_value`

---

### 2.2 UsageMetricRollup (MongoDB)

**Purpose**: Time-windowed rollups for gym usage metering (billing later; track now).

**Storage**: MongoDB time-series collection, keyed by `gym_id + window`. Optionally mirror subset into PostgreSQL for reporting joins.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class UsageMetricRollup(BaseModel):
    usage_rollup_id: UUID
    gym_id: UUID
    window_start: datetime
    window_end: datetime
    clients_count: int
    locations_count: int
    trainers_count: int
    api_calls_count: int
    ai_api_calls_count: int
    computed_at: datetime```

**Implementation Notes**:
- Store in MongoDB time-series collection for efficient time-windowed queries
- Counts computed nightly/hourly, optionally cached in Redis for dashboard access
- Source-of-truth for raw events: PostgreSQL audit logs (append-only)
- MongoDB rollups derived from PostgreSQL event logs via background jobs
- Use MongoDB TTL indexes to automatically expire old rollups (e.g., keep 13 months for annual comparisons)

---

### 2.3 GymPlanLimits (MongoDB)

**Purpose**: Gym-level plan/limits/config document for platform billing and gym capabilities.

**Storage**: MongoDB document per gym (one document per `gym_id`).

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class GymPlanLimits(BaseModel):
    gym_id: UUID
    platform_plan_id: str
    effective_at: datetime

    limits: Dict[str, Any]
    max_locations: Optional[int] = None
    max_trainers: Optional[int] = None
    max_clients: Optional[int] = None
    api_calls_per_month: Optional[int] = None
    ai_api_calls_per_month: Optional[int] = None

    features: Dict[str, Any]
    self_scheduling_enabled: bool
    progress_photos_enabled: bool
    health_integrations_enabled: bool
    esign_enabled: bool
    custom_domains_enabled: bool
    custom_email_domain_enabled: bool
    custom_login_domain_enabled: bool

    overrides: Optional[Dict[str, Any]] = None
    updated_by: UUID
    updated_at: datetime```

**Rationale**: Flexible schema allows rapid iteration on billing plans without schema migrations.

**Implementation Notes**:
- MongoDB provides schema flexibility for adding new limits/features without altering table structure
- Heavily cached in Redis (TTL: 5-15 minutes, key: `gym:{gym_id}:plan_limits`)
- Read-heavy access pattern (every entitlement check); cache-aside strategy reduces MongoDB load
- Use MongoDB change streams to invalidate Redis cache when limits are updated

---

### 2.4 PlanTemplate (MongoDB)

**Purpose**: A gym's sellable membership plan definition (what clients buy). Drives module enablement, visit entitlements, and payment structure.

**Storage**: MongoDB for versioning and flexibility.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class PlanTemplate(BaseModel):
    plan_template_id: UUID
    gym_id: UUID
    location_id: Optional[UUID] = None
    name: str
    description: str
    plan_type: str
    status: Literal['active', 'inactive']
    version: int
    effective_at: datetime

    visit_entitlement: Dict[str, Any]
    type: Literal['per_week', 'per_month', 'per_plan_duration', 'unlimited']
    count: Optional[int] = None
    rollover_enabled: bool

    plan_duration: Dict[str, Any]
    type: Literal['month', 'year', 'until_used']
    value: Optional[int] = None
    until_used_expiration_days: Optional[int] = None

    payment_config: Dict[str, Any]
    frequency: Literal['one_time', 'monthly', 'annually']
    amount: Decimal
    currency: str
    stripe_price_id: Optional[str] = None
    processing_fee_handling: Literal['gym_absorbs', 'pass_to_client']
    processing_fee_config: Optional[Dict[str, Any]] = None
    fee_type: Literal['percentage', 'flat', 'percentage_plus_flat']
    percentage: Optional[Decimal] = None
    flat_amount: Optional[Decimal] = None

    modules_enabled: Dict[str, Any]
    programming: bool
    progress_photos: bool
    health_integrations: bool
    self_scheduling: bool

    limits: Dict[str, Any]
    max_active_programs: Optional[int] = None
    session_duration_minutes: Optional[int] = None

    # Add-on plan configuration (for family discounts)
    is_addon: bool
    requires_primary_plan_type: Optional[str] = None
    addon_discount_percentage: Optional[Decimal] = None```

**Plan Type Design**:
- `plan_type` is a **string** (not enum) to allow gym-specific custom types
- **Canonical types** (recommended): `'gym_access'`, `'personal_training'`, `'group_classes'`
- **Custom types** (examples): `'hybrid_training'`, `'nutrition_coaching'`, `'specialty_class'`
- **Constraint**: Client can only have ONE active membership per `plan_type` (enforced by unique index on `(client_id, plan_type)` where `status = 'active'`)
- **Validation**: Frontend should suggest canonical types, but allow custom values
- **Naming Convention**: Use lowercase with underscores (e.g., `'specialty_class'`, not `'SpecialtyClass'`)

**Location Scoping**:
- `location_id = null`: Plan applies to all locations in the gym (gym-wide)
- `location_id = UUID`: Plan applies only to the specific location
- Use cases:
  - Gym-wide: "Monthly Unlimited Gym Access" (all locations)
  - Location-specific: "Downtown Personal Training" (downtown location only)
- When querying plans, filter by `location_id` or show gym-wide plans (`location_id IS NULL`)
- Clients can have memberships from different locations simultaneously

**Add-on Plan Rules**:
- Addon plans require primary member with base plan
- If primary cancels base plan → all linked addon plans cancel
- Addon discount applied to `payment_config.amount`

**Example Plans**:

```json
// 10-Pack Personal Training (Session Pack) - Location-specific
{
  "name": "Downtown 10-Pack Training",
  "location_id": "downtown-location-uuid",
  "plan_type": "personal_training",
  "visit_entitlement": { "type": "per_plan_duration", "count": 10 },
  "plan_duration": { "type": "until_used", "until_used_expiration_days": 180 },
  "payment_config": { "frequency": "one_time", "amount": 500.00 }
}

// Monthly Unlimited Gym Access - Gym-wide (all locations)
{
  "name": "Unlimited Access - All Locations",
  "location_id": null,
  "plan_type": "gym_access",
  "visit_entitlement": { "type": "unlimited", "count": null },
  "plan_duration": { "type": "month", "value": 1 },
  "payment_config": { "frequency": "monthly", "amount": 199.00 }
}

// Family Member Training Add-On (50% discount) - Gym-wide
{
  "name": "Family Member Training Add-On",
  "location_id": null,
  "plan_type": "personal_training",
  "is_addon": true,
  "requires_primary_plan_type": "personal_training",
  "addon_discount_percentage": 50,
  "payment_config": { "frequency": "monthly", "amount": 75.00 }
}
```

**Implementation Notes**:
- **MongoDB Storage**: Plan templates stored in MongoDB for schema flexibility and versioning. Allows rapid iteration on plan structures without schema migrations.
- **Caching**: PlanTemplate lookups are read-heavy (displayed in signup flows, plan selection). Cache in Redis with TTL: 5-15 minutes, key pattern: `plan_template:{plan_template_id}` or `gym:{gym_id}:plans`.
- **Snapshotting Strategy**: When a client is assigned a plan, critical enforcement fields (`visit_entitlement`, `plan_duration`, `plan_type`) are **snapshotted into PostgreSQL's `ClientMembership` table** at assignment time. This ensures:
  - Check-in and entitlement validation never depend on MongoDB availability
  - PostgreSQL is the authoritative source for "what this client is entitled to do right now"
  - Plan template updates do not retroactively affect existing memberships (immutability)
- **Versioning**: Use `version` field to track plan changes over time. New versions are new documents; existing memberships reference the version they were assigned.

---

### 2.5 Account (PostgreSQL)

**Purpose**: Billing and access management entity. Represents household, individual, or corporate account.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class Account(BaseModel):
    account_id: UUID
    gym_id: UUID
    account_type: Literal['individual', 'family', 'corporate']
    billing_email: str
    billing_address: Address
    stripe_customer_id: Optional[str] = None
    created_at: datetime
    deleted: bool

class Address(BaseModel):
    street1: str
    street2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str```

**Relationships**:
- Account belongs to Gym
- Account has many Clients (members)
- Account can have multiple primary Clients
- Account has consolidated billing

**Account Types**:
- `individual`: Single-person account
- `family`: Multi-member household account
- `corporate`: B2B corporate wellness (future feature)

**Tenant Scoping**:
- All accounts are scoped to a specific gym via `gym_id`
- Accounts cannot span multiple gyms
- When querying accounts, always filter by `gym_id` for security

---

### 2.6 Location (PostgreSQL)

**Purpose**: Physical gym location.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class Location(BaseModel):
    location_id: UUID
    gym_id: UUID
    name: Optional[str] = None
    picture_url: Optional[str] = None
    address: Address
    capacity: Optional[int] = None
    timezone: Optional[str] = None```

**Relationships**:
- Location belongs to Gym
- Location has many GymCheckIns
- Location has many Schedules

---

### 2.7 User (PostgreSQL)

**Purpose**: Authentication entity. Represents login credentials for a Client, Trainer, or Platform Admin.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class User(BaseModel):
    user_id: UUID
    client_id: Optional[UUID] = None
    trainer_id: Optional[UUID] = None
    email: str
    password_hash: Optional[str] = None
    password_hash_version: int
    roles: List[Role]
    login_enabled: bool
    created_by_user_id: Optional[UUID] = None
    created_at: datetime
    last_login_at: Optional[datetime] = None

    # Multi-Factor Authentication
    mfa_enabled: bool
    mfa_method: Literal['totp', 'email', 'passkey_only']
    totp_secret: Optional[str] = None
    totp_backup_codes: Optional[List[str]] = None
    mfa_enforced_at: Optional[datetime] = None
```

**User-to-Entity Mapping**:
- **Clients**: User has `client_id` set, `roles` includes `'client'`
- **Trainers**: User has `trainer_id` set, `roles` includes `'trainer'` (and optionally `'admin'`, `'front_desk'`)
- **Platform Admins**: User has `client_id = null` and `trainer_id = null`, `roles = ['platform_admin']`
- **Multi-Role Users**: A trainer can also be a client (has both `trainer_id` and `client_id` set)

**Role Hierarchy**:
- `platform_admin`: Platform operator role. Access to all gyms, can create/delete gyms, manage platform plans and limits. NOT tied to any specific gym or client.
- `admin`: Gym administrator. Manages gym settings, locations, trainers, clients, programs, billing. Scoped to specific gym.
- `trainer`: Manages assigned clients, creates programs, records workouts. Scoped to specific gym.
- `front_desk`: Check-in operations, view schedules, monitor occupancy. Read-only access. Scoped to specific gym.
- `client`: Member with login access. Can view own data, log workouts if enabled.

**Platform Admin**:
- Platform admins are NOT associated with a Client entity
- User record has `client_id = null` for platform admins
- Platform admins have role `['platform_admin']` only
- Platform admins cannot also have gym-specific roles
- Created manually via database seed or admin tool (not through signup flow)

**Password Requirements** (if using password auth):
- Minimum 12 characters
- Must contain: uppercase, lowercase, number, special character
- Cannot contain user's email or name
- Cannot be in common password breach list (Have I Been Pwned API check)
- Password hash algorithm: **Argon2id only**

**Argon2id Parameters** (version 1):
- Memory cost: 64 MB minimum
- Time cost: 3 iterations minimum
- Parallelism: 4 threads
- Output length: 32 bytes
- Salt: 128-bit minimum, cryptographically secure random, unique per password
- Salt stored with hash (Argon2id includes salt in output)

**Hash Migration Strategy**:
```python
# On successful login
if (user.password_hash_version < CURRENT_VERSION) {
    # Rehash password with current algorithm
  newHash = await argon2id.hash(password, {
    memoryCost: 64 * 1024,  # 64 MB
    timeCost: 3,
    parallelism: 4
  })

  await updateUser({
    password_hash: newHash,
    password_hash_version-> CURRENT_VERSION
  })
}
```

**MFA Requirements**:
- Required for all admin and trainer roles (7-day grace period after account creation)
- Optional for client roles
- SMS MFA is NOT supported (insecure, SIM swap attacks)
- Passkey-only authentication is most secure (no additional MFA needed)

**Constraints**:
- One Client can have at most ONE User
- Email must be unique across all Users
- MFA required for admin/trainer/platform_admin roles
- Platform admins must have `client_id = null` and `roles = ['platform_admin']`
- Gym users (admin/trainer/front_desk/client) must have non-null `client_id`

**Relationships**:
- User may belong to one Client (one-to-one) OR be a platform admin (client_id = null)
- User has many UserPasskeys
- User has many OAuth2AccessTokens

---

### 2.7.1 UserPasskey (PostgreSQL)

**Purpose**: WebAuthn/FIDO2 passkey credentials for passwordless authentication.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class UserPasskey(BaseModel):
    passkey_id: UUID
    user_id: UUID
    credential_id: str
    public_key: str
    counter: bigint
    device_name: str
    device_type: Literal['platform', 'cross_platform']
    aaguid: str
    transports: List[str]
    created_at: datetime
    last_used_at: Optional[datetime] = None```

**Device Types**:
- `platform`: Built-in authenticator (TouchID, FaceID, Windows Hello)
- `cross_platform`: External security key (YubiKey, Titan Key)

**Passkey-only Authentication**:
- If `user.password_hash IS NULL` and user has passkeys: passkey-only mode
- No password required, passkey acts as both factor 1 and MFA
- Recommended for high-security accounts (admins, trainers)

**Constraints**:
- `credential_id` must be unique globally (WebAuthn requirement)
- User can have multiple passkeys for redundancy

---

### 2.7.2 OAuth2Client (PostgreSQL)

**Purpose**: OAuth2 client applications registered by **gym administrators only** for third-party integrations.

**Important**: This is for gym-level integrations only. MCP (trainer AI assistant) uses separate authorization and does NOT create OAuth2Client records.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class OAuth2Client(BaseModel):
    client_id: UUID
    client_secret: str
    gym_id: UUID
    created_by_user_id: UUID
    name: str
    description: Optional[str] = None
    redirect_uris: List[str]
    grant_types: List[GrantType]
    scopes_allowed: List[str]
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None
```

**Available OAuth2 Scopes** (gym-level integrations):
- `gym:read` - Read gym settings, locations
- `clients:read` - Read client profiles
- `clients:write` - Create/update clients
- `workouts:read` - Read workout data
- `workouts:write` - Log workouts
- `schedule:read` - Read schedules
- `schedule:write` - Book/cancel sessions
- `measurements:read` - Read measurements
- `measurements:write` - Record measurements
- `analytics:read` - Read analytics/reports

**Note**: The `mcp:trainer` scope is NOT available for OAuth2Client.

**Access Control**:
- Only gym admins can create OAuth2 clients
- Trainers CANNOT create OAuth2 clients
- OAuth2 clients are gym-scoped (not user-scoped)

---

### 2.7.3 OAuth2AccessToken (PostgreSQL)

**Purpose**: Issued OAuth2 access tokens for API access.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class OAuth2AccessToken(BaseModel):
    token_id: UUID
    client_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    token_type: Literal['oauth_client', 'mcp', 'calendar']
    token_hash: str
    refresh_token_hash: Optional[str] = None
    scopes: List[str]
    expires_at: datetime
    refresh_token_expires_at: Optional[datetime] = None
    created_at: datetime
    revoked_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None```

**Token Types**:
- `oauth_client`: Regular OAuth2 tokens from OAuth2Client (gym admin integrations)
- `mcp`: MCP tokens for trainer AI assistant access (no OAuth2Client, user-scoped)
- `calendar`: Calendar feed tokens for trainer .ics export (long-lived, read-only)

**Token Lifecycle**:
- Access tokens: short-lived (1 hour)
- Refresh tokens: long-lived (30 days)
- Users/admins can revoke tokens at any time
- Tokens automatically revoked if user disabled or client deactivated

**Token Storage Security**:
```python
# Never store plaintext tokens
tokenHash = await sha256(accessToken)
await db.tokens.create({
  token_hash: tokenHash,
    # ... other fields
})

# Verification
incomingTokenHash = await sha256(incomingToken)
token = await db.tokens.findOne({ token_hash: incomingTokenHash })
```

---

### 2.7.4 OAuth2AuthorizationCode (PostgreSQL)

**Purpose**: Temporary authorization codes for OAuth2 authorization code flow.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class OAuth2AuthorizationCode(BaseModel):
    code_id: UUID
    code_hash: str
    client_id: UUID
    user_id: UUID
    redirect_uri: str
    scopes: List[str]
    code_challenge: str
    code_challenge_method: Literal['S256', 'plain']
    expires_at: datetime
    used_at: Optional[datetime] = None```

**PKCE Requirement**:
- All authorization code flows MUST use PKCE (RFC 7636)
- Prevents authorization code interception attacks
- Mobile apps and SPAs: public clients, must use PKCE

---

### 2.7.5 PasswordResetToken (PostgreSQL)

**Purpose**: Temporary tokens for password reset workflow.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class PasswordResetToken(BaseModel):
    token_id: UUID
    user_id: UUID
    token_hash: str
    expires_at: datetime
    created_at: datetime
    used_at: Optional[datetime] = None
    ip_address: Optional[str] = None```

**Security Requirements**:
- Tokens are 256-bit cryptographically secure random
- Never store plaintext tokens (SHA-256 hash only)
- Tokens expire after 1 hour
- Tokens are single-use (marked as used after consumption)
- Rate limiting: Max 3 reset requests per email per hour

**Cleanup**:
- Expired/used tokens can be purged after 7 days (keep for audit trail)

---

### 2.8 Trainer (PostgreSQL)

**Purpose**: Trainer entity. Represents a staff member who conducts training sessions.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class Trainer(BaseModel):
    trainer_id: UUID
    user_id: Optional[UUID] = None
    gym_id: UUID
    primary_location_id: UUID

    # Personal Information
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None

    # Employment
    hire_date: datetime
    status: Literal['invited', 'active', 'inactive']
    employment_type: Optional[Literal['full_time', 'part_time', 'contractor']] = None

    # Calendar privacy settings (per-trainer override)
    calendar_settings: Optional[Dict[str, Any]] = None
    hide_client_names: Optional[bool] = None

    created_at: datetime
    created_by_user_id: Optional[UUID] = None```

**Trainer Status Lifecycle**:
- `invited`: Trainer record created, invitation email sent, awaiting account setup
- `active`: User account linked, trainer can log in and work
- `inactive`: Deactivated/terminated, cannot log in

**Calendar Privacy Precedence**:
1. If `Trainer.calendar_settings.hide_client_names` is explicitly set (true/false), use that value
2. Otherwise, fall back to `Gym.hide_client_names_in_calendar` (gym-wide default)

**Relationships**:
- Trainer belongs to Gym (through Location and direct gym_id)
- Trainer may have one User (login credentials)
- Trainer has one TrainerAvailability (NoSQL)
- Trainer has many TrainerExceptions
- Trainer has many Schedules
- Trainer has many assigned Clients

---

### 2.8.1 TrainerAvailability (NoSQL)

**Purpose**: Trainer's recurring weekly schedule, stored as flexible JSON document.

**Storage**: One document per trainer_id in NoSQL.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class TrainerAvailability(BaseModel):
    trainer_id: UUID
    recurring: List[AvailabilityWindow]
    updated_at: datetime

class AvailabilityWindow(BaseModel):
    day_of_week: int
    location_id: UUID
    start_time: str
    end_time: str```

**Example**:
```json
{
  "trainer_id": "uuid",
  "recurring": [
    {
      "day_of_week": 1,
      "location_id": "location-a-uuid",
      "start_time": "07:00",
      "end_time": "12:00"
    },
    {
      "day_of_week": 2,
      "location_id": "location-b-uuid",
      "start_time": "15:00",
      "end_time": "21:00"
    }
  ],
  "updated_at": "2026-01-19T10:00:00Z"
}
```

**Rationale**: NoSQL allows flexible multi-location schedules without complex SQL schema.

---

### 2.8.2 TrainerException (PostgreSQL)

**Purpose**: One-off exceptions to trainer's recurring schedule (vacation, holidays, sick days).

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class TrainerException(BaseModel):
    trainer_exception_id: UUID
    trainer_id: UUID
    exception_date: datetime
    exception_type: Literal['unavailable', 'available']
    reason: Optional[str] = None
    created_at: datetime
    created_by_user_id: UUID```

**Purpose**: Allows tracking of PTO/vacation for reporting purposes.

---

### 2.9 Client (PostgreSQL)

**Purpose**: Represents an individual member/person within an Account.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class Client(BaseModel):
    client_id: UUID
    account_id: UUID
    member_role: Literal['primary', 'member']
    client_status: ClientStatus

    # Personal Information
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: datetime
    relationship_to_primary: Optional[str] = None

    # Gym Association
    member_number: str
    primary_location_id: UUID
    primary_trainer_id: Optional[UUID] = None
    qr_code: str

    deleted: bool
    created_at: datetime

    # Behavioral stats (derived)
    avg_workout_duration_minutes: int
    avg_schedule_variance_minutes: int

    # AI Summary (lazy-loaded, cached on client)
    ai_summary_latest: Optional[str] = None
    ai_summary_updated_at: Optional[datetime] = None
    ai_summary_is_stale: bool
```

**Account Member Roles**:
- `primary`: Can manage account, add/remove members, control billing, grant logins
- `member`: Standard member, managed by primary(ies)

**Age-Based Access Rules**:
- **Under 13**: Cannot have login (User), gym/trainer manages all data
- **13-17**: Can have login if primary member grants it
- **18+**: Can have login, can request to transfer to own account ("emancipation")

**Relationships**:
- Client belongs to Account
- Client may have one User (login)
- Client has many ClientMemberships
- Client has many GymCheckIns
- Client has many ProgressPhotos
- Client has many HealthMetricSamples
- Client has many Workouts
- Client has many PRs

**Constraints**:
- `member_number`: Unique per gym, auto-generated on client creation (e.g., "GYM001-0042")
  - Format: `{gym_prefix}-{sequential_number}`
  - Used for audit trails and anonymized references after deletion
  - Never changes, even after emancipation or account transfers
  - Preserved in audit logs when PII is anonymized

---

### 2.10 GymCheckIn (PostgreSQL)

**Purpose**: Tracks client check-ins and check-outs for gym occupancy and attendance tracking.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class GymCheckIn(BaseModel):
    check_in_id: UUID
    client_id: UUID
    location_id: UUID
    schedule_id: Optional[UUID] = None
    check_in_method: Literal['qr_scan', 'manual_name', 'mobile_app']
    checked_in_by_user_id: UUID
    checked_in_at: datetime
    checked_out_at: Optional[datetime] = None
    expected_checkout_at: datetime
    check_in_type: Literal['self_directed', 'training_session']```

**Behavior**:
- **Self-directed check-ins**: No schedule required, assume 60-minute duration
- **Training session check-ins**: May have schedule, use client's `avg_workout_duration_minutes`
- **Check-out**: For MVP, assume duration and don't track explicit check-outs
- **Alert on inactive membership**: When checking in, alert front desk if no active membership

---

### 2.11 ClientMembership (PostgreSQL)

**Purpose**: Active or historical membership linking client to plan template.

**Storage**: PostgreSQL. Critical enforcement fields from PlanTemplate (MongoDB) are snapshotted here at assignment time to ensure check-in and entitlement validation never depend on MongoDB availability.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class ClientMembership(BaseModel):
    client_membership_id: UUID
    client_id: UUID
    plan_template_id: UUID
    plan_type: str
    status: Literal['active', 'paused', 'expired', 'canceled']

    # Add-on plan linkage
    base_membership_id: Optional[UUID] = None
    is_addon: bool

    # Dates
    started_at: datetime
    expires_at: Optional[datetime] = None

    # Pause information
    pause_info: Optional[Dict[str, Any]] = None
    paused_at: datetime
    paused_by_user_id: UUID
    pause_reason: Optional[str] = None
    days_paused_total: int

    # Visit entitlement tracking
    visit_entitlement: Dict[str, Any]
    current_period_start: datetime
    current_period_end: datetime
    visits_allowed_this_period: Optional[int] = None
    visits_used_this_period: int
    total_visits_remaining: Optional[int] = None

    # Cancellation information
    cancellation_info: Optional[Dict[str, Any]] = None
    canceled_at: datetime
    canceled_by_user_id: UUID
    cancellation_reason: Optional[str] = None
    cancels_at_period_end: bool

    # Stripe metadata
    stripe_metadata: Optional[Dict[str, Any]] = None
    stripe_subscription_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    last_payment_at: datetime
    last_payment_amount: Decimal
    last_processing_fee: Decimal```

**Constraints**:
- Unique constraint on (`client_id`, `plan_type`) where `status = 'active'`
- A client can only have one active membership per plan_type

**Valid Combinations**:
- ✅ "Monthly Gym Access" (`gym_access`) + "10-Pack Training" (`personal_training`)
- ✅ "Annual Gym Access" (`gym_access`) + "8 Group Classes/Month" (`group_classes`)
- ❌ "Monthly Unlimited Training" (`personal_training`) + "10-Pack Training" (`personal_training`)

**Cross-Database Snapshotting**:
- When a client is assigned a `PlanTemplate` (from MongoDB), critical enforcement fields are **snapshotted** into this PostgreSQL record:
  - `plan_type`: Copied from `PlanTemplate.plan_type`
  - `visit_entitlement`: Copied from `PlanTemplate.visit_entitlement` (type, count, rollover rules)
  - `expires_at`: Computed from `PlanTemplate.plan_duration` + `started_at`
- **Rationale**: Check-in validation, entitlement checks, and visit tracking must work even if MongoDB is unavailable. PostgreSQL is the source of truth for "what this client is entitled to do right now."
- If the `PlanTemplate` in MongoDB is updated after assignment, existing `ClientMembership` records are **not** retroactively updated (immutability principle). New assignments use the latest plan version.

**Behavior**:
- **Add-on Cascading Cancellation**: When a base membership is canceled (where `is_addon = false`), all linked add-on memberships (where `base_membership_id` references the canceled membership) must also be canceled automatically
  - Set `status = 'canceled'` for all dependent add-ons
  - Record cascading cancellation in `cancellation_info.cancellation_reason` (e.g., "Base membership canceled")
- **Add-on Validation**: When assigning an add-on plan (from PlanTemplate where `is_addon = true`):
  - Verify that the client has an active base membership matching `PlanTemplate.requires_primary_plan_type`
  - Set `base_membership_id` to reference the active base membership
  - Apply `addon_discount_percentage` to calculate discounted pricing

---

### 2.12 ProgressPhoto (PostgreSQL)

**Purpose**: Client progress photos over time.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class ProgressPhoto(BaseModel):
    progress_photo_id: UUID
    client_id: UUID
    captured_at: datetime
    uploaded_at: datetime
    photo_url: str
    visibility: Literal['client_only', 'trainer', 'gym_admin']
    notes: Optional[str] = None
    tags_json: Optional[List[str]] = None```

**Constraints**:
- Enforce access control by visibility + trainer assignment
- Store derivatives/thumbnails for fast browsing

---

### 2.13 HealthConnection (PostgreSQL)

**Purpose**: Tracks health data integration connections.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class HealthConnection(BaseModel):
    health_connection_id: UUID
    client_id: UUID
    provider: Literal['apple_health', 'google_fit', 'health_connect']
    status: Literal['connected', 'disconnected', 'error']
    connected_at: datetime
    disconnected_at: Optional[datetime] = None
    scopes_granted_json: List[str]
    last_sync_at: Optional[datetime] = None```

---

### 2.14 HealthMetricSample (PostgreSQL)

**Purpose**: Health data samples synced from health platforms.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class HealthMetricSample(BaseModel):
    health_metric_sample_id: UUID
    client_id: UUID
    provider: Literal['apple_health', 'google_fit', 'health_connect']
    metric_type: str
    start_at: datetime
    end_at: Optional[datetime] = None
    value: Decimal
    unit: str
    source_device: Optional[str] = None
    ingested_at: datetime```

**Constraints**:
- Idempotency key for imports to avoid duplicates (provider_sample_id or hash of timestamp+value+type)

---

### 2.15 Program (PostgreSQL)

**Purpose**: A reusable set of program days assignable to clients.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class Program(BaseModel):
    program_id: UUID
    gym_id: UUID
    name: str
    description: str
    created_by_trainer_id: UUID
    created_at: datetime
    is_template: bool```

**Relationships**:
- Program belongs to Gym
- Program has many ProgramDays
- Program can be assigned to multiple Clients via ClientProgram

**Tenant Scoping**:
- All programs are scoped to a specific gym via `gym_id`
- Programs cannot be shared across gyms
- When querying programs, always filter by `gym_id` for security
- Trainers can only create/modify programs within their gym

---

### 2.16 ProgramDay (PostgreSQL)

**Purpose**: A workout template within a program - contains a list of exercises to be performed in a single training session. Linked list behavior for automatic progression through the program.

**Terminology Note**: In Business Requirements, this entity is referred to as a "Workout" (the template). In the Technical Specification, it's called "ProgramDay" (to distinguish from the Workout entity which represents an actual training session instance).

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class ProgramDay(BaseModel):
    program_day_id: UUID
    program_id: UUID
    name: str
    next_program_day_id: UUID```

**Constraints**:
- Last day must point to first day (circular progression)
- Validate no broken links; optionally validate exactly one cycle

**Relationships**:
- ProgramDay belongs to Program (one program contains many workout templates)
- ProgramDay has many ProgramDayExercises (the exercises to perform in this workout)

---

### 2.17 ProgramDayExercise (PostgreSQL)

**Purpose**: An exercise definition within a program day, with program-specific configurations.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class ProgramDayExercise(BaseModel):
    program_day_exercise_id: UUID
    program_day_id: UUID
    exercise_id: UUID
    order_index: int
    default_sets: int
    default_reps: Union[int, str]
    tempo: Optional[str] = None
    weight_progression_rule: Optional[Dict[str, Any]] = None
    strategy: Literal['add_from_average', 'add_from_pr', 'add_from_last_amrap', 'manual']
    increment_amount: Decimal
    increment_unit: str
    notes: Optional[str] = None```

---

### 2.18 ClientProgram (PostgreSQL)

**Purpose**: Tracks program assignment and progression for a client. Represents the link between a client and an active program, maintaining their current position in the program cycle.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class ClientProgram(BaseModel):
    client_program_id: UUID
    client_id: UUID
    program_id: UUID
    current_program_day_id: UUID
    status: Literal['active', 'paused', 'completed', 'abandoned']
    assigned_at: datetime
    assigned_by_trainer_id: UUID
    completed_at: Optional[datetime] = None
    abandoned_at: Optional[datetime] = None
    notes: Optional[str] = None```

**Relationships**:
- ClientProgram belongs to Client
- ClientProgram belongs to Program
- ClientProgram references current ProgramDay for progression tracking

**Business Rules**:
- A client can have multiple active programs simultaneously
- When workout completes with a program, the `current_program_day_id` advances to next day
- ProgramDay uses circular linked list (last day points to first day)

---

### 2.19 Exercise (PostgreSQL)

**Purpose**: Exercise definition.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class Exercise(BaseModel):
    exercise_id: UUID
    name: str
    exercise_type_id: UUID
    image_url: Optional[str] = None
    defaults: Dict[str, Any]
    default_sets: int
    default_reps_per_set: int
    default_measurements: List[str]```

---

### 2.19 ExerciseType (PostgreSQL)

**Purpose**: Exercise type definition with allowed measurements and PR direction.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class ExerciseType(BaseModel):
    exercise_type_id: UUID
    name: str
    measurements_allowed: List[MeasurementType]
    pr_direction: Literal['maximize', 'minimize']
```

**PR Direction Examples**:
- `minimize`: Sprint times, rowing for time, running for time
- `maximize`: Max weight lifted, max distance, max hold time, max reps

---

### 2.20 Workout (PostgreSQL)

**Purpose**: An actual training session instance. Records a specific client's visit to the gym and the exercises they performed.

**Relationship to Programs**: Each Workout executes one ProgramDay (workout template) from a Program. The client advances through the program's workout templates with each completed session.

**Relationship to Visits**: Each Workout is tied to a specific gym visit (GymCheckIn). The check-in may have been for a scheduled session (with schedule_id) or a walk-in.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class Workout(BaseModel):
    workout_id: UUID
    check_in_id: Optional[UUID] = None
    client_id: UUID
    trainer_id: Optional[UUID] = None
    location_id: UUID
    program_id: Optional[UUID] = None
    program_day_id: Optional[UUID] = None
    started_at: datetime
    ended_at: Optional[datetime] = None```

**Behavior**:
- When started, exercises from the ProgramDay template become WorkoutExercises with status incomplete
- Each completed Workout advances the client's position in their active Program to the next ProgramDay
- The Workout inherits location_id, client_id, and trainer_id from the associated GymCheckIn (if provided)
- **AI Summary Staleness**: When a Workout is completed (status changes to complete), set `ai_summary_is_stale = true` on the associated Client

---

### 2.21 WorkoutExercise (PostgreSQL)

**Purpose**: Exercise instance within a workout.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class WorkoutExercise(BaseModel):
    workout_exercise_id: UUID
    workout_id: UUID
    exercise_id: UUID
    status: Literal['incomplete', 'complete', 'skipped']
    order_index: int```

**Relationships**:
- WorkoutExercise has many WorkoutSets

---

### 2.22 WorkoutSet (PostgreSQL)

**Purpose**: Individual set within a workout exercise.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class WorkoutSet(BaseModel):
    workout_set_id: UUID
    workout_exercise_id: UUID
    set_index: int
    planned_reps: Optional[int] = None
    actual_reps: Optional[int] = None
    is_amrap: bool
    notes: Optional[str] = None```

**Relationships**:
- WorkoutSet has many WorkoutSetMeasurements

---

### 2.23 WorkoutExerciseGroup (PostgreSQL)

**Purpose**: Optional grouping of workout exercises to support supersets/circuits.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class WorkoutExerciseGroup(BaseModel):
    workout_exercise_group_id: UUID
    workout_id: UUID
    name: Optional[str] = None
    order_index: int```

**Relationships**:
- Group has many WorkoutExercises (add `workout_exercise_group_id` FK on WorkoutExercise)

---

### 2.24 WorkoutSetMeasurement (PostgreSQL)

**Purpose**: Measurements for a workout set (weight, time, distance, etc.).

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class WorkoutSetMeasurement(BaseModel):
    measurement_id: UUID
    workout_set_id: UUID
    type: Literal['weight', 'time', 'distance', 'rpe']
    value: Union[Decimal, str]
    unit: str```

---

### 2.25 Schedule (PostgreSQL)

**Purpose**: A tentative plan of visits with capacity/busyness computed at 15-min granularity.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class Schedule(BaseModel):
    schedule_id: UUID
    client_id: UUID
    location_id: UUID
    trainer_id: Optional[UUID] = None
    scheduled_start: datetime
    scheduled_end: datetime
    status: Literal['tentative', 'confirmed', 'canceled', 'no_show', 'completed']```

**Rules**:
- Admin can enable/disable self-scheduling
- Busyness computed every 15 minutes using active scheduled sessions + expected duration

---

### 2.26 GymMeasurementType (PostgreSQL)

**Purpose**: Gym-configurable measurement types (standard + custom).

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class GymMeasurementType(BaseModel):
    measurement_type_id: UUID
    gym_id: Optional[UUID] = None
    name: str
    category: Literal['body_composition', 'circumference', 'vitals', 'performance', 'custom']
    default_unit: str
    is_standard: bool
    is_active: bool
    sort_order: int```

**Standard Measurement Types** (system-seeded, `is_standard = true`, `gym_id = null`):

*Body Composition*:
- Body Weight, Body Fat %, Muscle Mass %, BMI

*Circumference*:
- Bicep Left, Bicep Right, Chest, Waist, Hips, Thigh Left, Thigh Right, Calf Left, Calf Right, Neck

*Vitals*:
- Blood Pressure Systolic, Blood Pressure Diastolic, Resting Heart Rate

*Performance*:
- VO2 Max, 1-Mile Run Time, Vertical Jump Height

**Constraints**:
- Standard types shared across all gyms
- Custom types (`gym_id != null`) only visible to that gym

---

### 2.27 ClientMeasurement (PostgreSQL)

**Purpose**: Manually-recorded body measurements taken by trainer.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class ClientMeasurement(BaseModel):
    measurement_id: UUID
    client_id: UUID
    measurement_type_id: UUID
    recorded_by_user_id: UUID
    recorded_at: datetime
    value: Decimal
    unit: str
    notes: Optional[str] = None
    progress_photo_id: Optional[UUID] = None```

**Permissions**:
- Trainers can add measurements for assigned clients
- Clients can view their own measurements (read-only)
- Clients CANNOT edit or delete trainer-entered measurements

**Behavior**:
- **AI Summary Staleness**: When a new measurement is created, set `ai_summary_is_stale = true` on the associated Client

---

### 2.28 ClientGoal (PostgreSQL)

**Purpose**: Client goals for measurements, exercise PRs, or workout frequency.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class ClientGoal(BaseModel):
    goal_id: UUID
    client_id: UUID
    created_by_user_id: UUID
    goal_type: Literal['measurement', 'exercise_pr', 'workout_frequency', 'custom']
    status: Literal['active', 'achieved', 'abandoned', 'expired']

    # Goal targets
    target_measurement_type_id: Optional[UUID] = None
    target_exercise_id: Optional[UUID] = None
    target_value: Decimal
    target_unit: str
    target_date: Optional[datetime] = None

    # Progress tracking (auto-updated)
    baseline_value: Decimal
    current_value: Optional[Decimal] = None
    progress_percentage: Decimal

    # Timestamps
    created_at: datetime
    achieved_at: Optional[datetime] = None

    # Metadata
    notes: Optional[str] = None
    visibility: Literal['client_only', 'trainer', 'public']```

**Auto-Update Triggers**:
- When new ClientMeasurement recorded → update matching goals
- When new PR achieved → update exercise PR goals
- When goal achieved → set `status = 'achieved'`, notify client + trainer

---

### 2.29 WorkoutAnalytics (PostgreSQL)

**Purpose**: Pre-calculated workout session metrics for fast dashboard queries.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class WorkoutAnalytics(BaseModel):
    analytics_id: UUID
    workout_id: UUID
    client_id: UUID
    computed_at: datetime

    # Volume & Intensity Metrics
    total_weight_lifted_lbs: Decimal
    total_reps: int
    total_sets: int
    duration_minutes: int

    # Completion Metrics
    exercises_completed: int
    exercises_skipped: int
    completion_rate: Decimal

    # Performance Metrics
    prs_achieved_count: int
    volume_by_muscle_group: Optional[JSON] = None
    intensity_score: Optional[Decimal] = None```

**Calculation Timing**:
- **Async** (after workout completion via background job)
- Triggered when `POST /workouts/{id}/complete` called

---

### 2.30 GymAnalytics (NoSQL - Time-Series)

**Purpose**: Admin dashboard metrics for gym business reporting.

**Storage**: NoSQL time-series database for fast queries.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class GymAnalytics(BaseModel):
    analytics_id: UUID
    gym_id: UUID
    period_start: datetime
    period_end: datetime
    period_type: Literal['day', 'week', 'month', 'quarter', 'year']
    computed_at: datetime

    # Revenue Metrics
    revenue_metrics: Dict[str, Any]
    total_revenue: Decimal
    new_revenue: Decimal
    recurring_revenue: Decimal
    churned_revenue: Decimal
    avg_revenue_per_client: Decimal

    # Client Metrics
    client_metrics: Dict[str, Any]
    total_clients: int
    active_clients: int
    new_clients: int
    churned_clients: int
    client_retention_rate: Decimal
    prospects_count: int

    # Engagement Metrics
    engagement_metrics: Dict[str, Any]
    total_workouts: int
    total_check_ins: int
    avg_workouts_per_client: Decimal
    avg_session_duration_minutes: Decimal
    workout_completion_rate: Decimal

    # Trainer Metrics
    trainer_metrics: Dict[str, Any]
    total_trainers: int
    active_trainers: int
    avg_clients_per_trainer: Decimal
    trainer_utilization_rate: Decimal```

**Calculation Timing**:
- Nightly rollup jobs calculate previous day, week, month
- Historical data archived after 1 year to cold storage

---

### 2.31 MeasurementReminder (PostgreSQL)

**Purpose**: Optional reminders for trainers to take client measurements on a schedule.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class MeasurementReminder(BaseModel):
    reminder_id: UUID
    client_id: UUID
    measurement_type_id: UUID
    last_measured_at: Optional[datetime] = None
    next_reminder_at: datetime
    frequency_days: int
    reminder_sent_at: Optional[datetime] = None
    is_snoozed: bool
    snoozed_until: Optional[datetime] = None```

**Behavior**:
- Nightly job checks all clients at gyms with `measurement_reminders_enabled = true`
- If `(today - last_measured_at) > frequency_days`: create notification
- When measurement recorded: update `last_measured_at`, clear reminder

---

### 2.32 DomainVerification (PostgreSQL)

**Purpose**: Track DNS verification records for custom domain ownership validation.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class DomainVerification(BaseModel):
    domain_verification_id: UUID
    gym_id: UUID
    domain_type: Literal['email', 'login']
    domain: str

    # Verification challenge
    verification_token: str
    expected_dns_record: Dict[str, Any]
    record_type: Literal['TXT', 'CNAME']
    host: str
    value: str

    # Status tracking
    status: Literal['pending', 'verified', 'failed']
    last_checked_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    failed_reason: Optional[str] = None
    retry_count: int

    # Lifecycle
    created_at: datetime
    expires_at: datetime```

**Constraints**:
- Only one active verification per `(gym_id, domain_type)` pair
- Auto-delete expired verifications (expires_at < NOW())
- Unique index on `(gym_id, domain_type)` WHERE status = 'pending'

**Relationships**:
- DomainVerification belongs to Gym

---

### 2.33 EmailDomainSPFRecord (PostgreSQL)

**Purpose**: Track SPF/DKIM/DMARC validation for email domains.

**Fields**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class EmailDomainSPFRecord(BaseModel):
    spf_record_id: UUID
    gym_id: UUID
    domain: str

    # SPF validation
    required_spf_include: str
    current_spf_record: Optional[str] = None
    is_valid: bool
    validation_errors: Optional[List[str]] = None

    # DKIM validation
    dkim_status: Literal['not_configured', 'pending', 'verified']
    dkim_cname_host: Optional[str] = None
    dkim_cname_value: Optional[str] = None

    # DMARC validation
    dmarc_status: Literal['not_configured', 'pending', 'verified']

    last_checked_at: Optional[datetime] = None
    created_at: datetime```

**Constraints**:
- One record per `(gym_id, domain)` pair
- Unique index on `(gym_id, domain)`

**Relationships**:
- EmailDomainSPFRecord belongs to Gym

---

## 3. Authentication & Authorization

### 3.1 OAuth2 Overview

All API authentication uses **OAuth2 2.0** standard with the following grant types:
- ⚠️ **Password (Resource Owner Password Credentials)** - **DEPRECATED in OAuth 2.1**
  - **Security Warning**: This grant type is less secure than authorization_code + PKCE
  - **Recommendation**: Use authorization_code + PKCE for all mobile and web apps
  - **Justification if used**: Only for first-party trusted clients (our own web/mobile apps)
  - **Migration Plan**: Transition to authorization_code + PKCE by Q2 2026
- Authorization Code (with PKCE required) - **PREFERRED**
- Refresh Token
- Client Credentials (server-to-server)

### 3.2 User Registration Workflow

```python
# Step 1-> User provides email and password
POST /auth/register
{
  email: "user@example.com",
  password: "SecureP@ssw0rd123"
}

# Step 2-> System validates password
- Check length >= 12 characters
- Check complexity (uppercase, lowercase, number, special char)
- Check against Have I Been Pwned API (breach database)

# Step 3-> Hash password with Argon2id
hash = await argon2id.hash(password, {
  memoryCost: 64 * 1024,  # 64 MB
  timeCost: 3,
  parallelism: 4,
  saltLength: 16          # 128-bit salt
})

#/ Step 4-> Create User record
# MFA defaults based on role (see NON_FUNCTIONAL_REQUIREMENTS.md:108)
role = determineRoleFromRegistration() # 'client', 'trainer', 'admin', etc.
mfaEnabled = ['admin', 'trainer', 'platform_admin'].includes(role) # Required for admin/trainer, optional for client
mfaEnforcedAt = mfaEnabled ? new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) : None # 7-day grace period for admin/trainer

await db.users.create({
  email,
  password_hash: hash,
  password_hash_version: 1,
  mfa_enabled: mfaEnabled,  # True for admin/trainer, False for client
  mfa_enforced_at: mfaEnforcedAt,  # 7 days for admin/trainer, None for client
  roles: [role]
})

# Step 5-> Send email verification link
await sendEmail({
  to: email,
  subject: "Verify your email",
  link: `https:#app.gymapp.com/verify-email?token=${verificationToken}`
})
```

### 3.3 Password Login Flow

```python
# Step 1-> User submits credentials
POST /auth/login
{
  email: "user@example.com",
  password: "SecureP@ssw0rd123"
}

# Step 2-> Verify password
user = await db.users.findOne({ email })
valid = await argon2id.verify(user.password_hash, password)

# Step 3-> Hash migration check
if (valid && user.password_hash_version < CURRENT_VERSION) {
  newHash = await argon2id.hash(password, currentParams)
  await db.users.update(user.id, {
    password_hash: newHash,
    password_hash_version-> CURRENT_VERSION
  })
}

# Step 4-> MFA check
if (user.mfa_enabled) {
  if (user.mfa_method === 'totp') {
    # Prompt for TOTP code
    return { requires_mfa: True, method: 'totp' }
  } else if (user.mfa_method === 'email') {
    # Send email code
    code = generateSecureRandomDigits(6)
    await sendEmailMFACode(user.email, code)
    return { requires_mfa: True, method: 'email' }
  }
}

# Step 5-> Generate OAuth2 tokens
accessToken = jwt.sign(
  { sub: user.id, roles: user.roles },
  SECRET,
  { expiresIn: '1h' }
)

refreshToken = generateSecureRandomToken()
await db.oauth2_access_tokens.create({
  user_id: user.id,
  token_type: 'oauth_client',
  token_hash: await sha256(accessToken),
  refresh_token_hash: await sha256(refreshToken),
  scopes: ['profile', 'workouts:read', 'workouts:write'],
  expires_at: new Date(Date.now() + 60 * 60 * 1000),  # 1 hour
  refresh_token_expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)  # 30 days
})

# Step 6-> Return tokens
return {
  access_token: accessToken,
  refresh_token: refreshToken,
  token_type: 'Bearer',
  expires_in: 3600
}
```

### 3.4 Passkey Registration Workflow

```python
# Step 1-> User navigates to "Add Passkey"
POST /auth/passkeys/register/challenge
Response: {
  challenge: "base64-encoded-random-challenge",
  rp: { id: "gymapp.com", name: "Gym App" },
  user: { id: user.id, name: user.email, displayName: user.name }
}

# Step 2-> Client calls navigator.credentials.create()
credential = await navigator.credentials.create({
  publicKey: {
    challenge: base64ToArrayBuffer(challenge),
    rp: { id: "gymapp.com", name: "Gym App" },
    user: { id: userId, name: email, displayName: name },
    pubKeyCredParams: [{ alg: -7, type: "public-key" }],
    authenticatorSelection: {
      authenticatorAttachment: "platform",  # or "cross-platform"
      userVerification: "required"
    }
  }
})

# Step 3-> User provides friendly device name
POST /auth/passkeys/register/verify
{
  credential_id: credential.id,
  public_key: credential.response.publicKey,
  attestation_object: credential.response.attestationObject,
  device_name: "iPhone 15"
}

# Step 4-> Server verifies and stores
await db.user_passkeys.create({
  user_id: user.id,
  credential_id: credential.id,
  public_key: extractPublicKey(attestationObject),
  counter: 0,
  device_name: "iPhone 15",
  device_type: "platform",
  aaguid: extractAAGUID(attestationObject),
  transports: ["internal"]
})

# Step 5-> Optional-> Enable passkey-only mode
if (user.wantsPasskeyOnly) {
  await db.users.update(user.id, { password_hash: None })
}
```

### 3.5 Passkey Login Flow

```python
# Step 1-> User clicks "Use Passkey"
POST /auth/login/passkey/challenge
Response: {
  challenge: "base64-encoded-random-challenge",
  allowCredentials: [
    { id: passkey.credential_id, type: "public-key", transports: ["internal"] }
  ]
}

# Step 2-> Client calls navigator.credentials.get()
assertion = await navigator.credentials.get({
  publicKey: {
    challenge: base64ToArrayBuffer(challenge),
    allowCredentials: response.allowCredentials
  }
})

# Step 3-> Verify signature
POST /auth/login/passkey/verify
{
  credential_id: assertion.id,
  authenticator_data: assertion.response.authenticatorData,
  signature: assertion.response.signature,
  client_data_json: assertion.response.clientDataJSON
}

# Step 4-> Server verifies signature
passkey = await db.user_passkeys.findOne({ credential_id: assertion.id })
valid = await verifySignature(
  passkey.public_key,
  assertion.signature,
  authenticatorData,
  clientDataJSON
)

# Step 5-> Check counter (replay protection)
if (assertion.counter <= passkey.counter) {
  throw new Error("Replay attack detected")
}

# Step 6-> Generate OAuth2 tokens (no MFA needed)
tokens = generateOAuth2Tokens(passkey.user_id)

# Step 7-> Update passkey
await db.user_passkeys.update(passkey.id, {
  counter: assertion.counter,
  last_used_at: new Date()
})

return tokens
```

### 3.6 Password Reset Workflow

**Step 1: Request Reset**

```python
POST /auth/password/forgot
{
  email: "user@example.com"
}

# Generate secure token
resetToken = generateSecureRandomToken(256)  # 256-bit
tokenHash = await sha256(resetToken)

# Store token
await db.password_reset_tokens.create({
  user_id: user.id,
  token_hash: tokenHash,
  expires_at: new Date(Date.now() + 60 * 60 * 1000),  # 1 hour
  created_at: new Date(),
  ip_address: req.ip
})

# Send email
await sendEmail({
  to: email,
  subject: "Password Reset",
  link: `https:#app.gymapp.com/reset-password?token=${resetToken}`
})

# Always show same message (prevent email enumeration)
return { message: "If that email exists, we've sent a reset link." }
```

**Step 2: Reset Password**

```python
POST /auth/password/reset
{
  token: "reset-token-from-email",
  new_password: "NewSecureP@ssw0rd123"
}

# Hash submitted token
tokenHash = await sha256(token)

# Verify token
resetToken = await db.password_reset_tokens.findOne({ token_hash: tokenHash })
if (!resetToken || resetToken.expires_at < new Date() || resetToken.used_at) {
  throw new Error("Invalid or expired reset link")
}

# Validate new password
validatePasswordRequirements(new_password)
await checkPasswordBreach(new_password)

# Hash new password
passwordHash = await argon2id.hash(new_password, {
  memoryCost: 64 * 1024,
  timeCost: 3,
  parallelism: 4
})

# Update user
await db.users.update(resetToken.user_id, {
  password_hash: passwordHash,
  password_hash_version: 1
})

# Mark token as used
await db.password_reset_tokens.update(resetToken.id, {
  used_at: new Date()
})

# Invalidate all existing sessions
await db.oauth2_access_tokens.update(
  { user_id: resetToken.user_id },
  { revoked_at: new Date() }
)

# Send confirmation email
await sendEmail({
  to: user.email,
  subject: "Password Changed",
  text: "Your password was successfully changed."
})
```

**Security Considerations**:
- Rate limiting: Max 3 reset requests per email per hour
- Tokens are single-use only
- Tokens expire after 1 hour
- Never store plaintext tokens (SHA-256 hash only)
- Invalidate all sessions on password reset

### 3.7 MFA Setup Workflow (TOTP)

```python
# Step 1-> Generate TOTP secret
POST /auth/mfa/totp/setup

secret = generateSecureRandomBase32(32)  # 32-byte random
qrCodeUri = `otpauth:#totp/GymApp:${user.email}?secret=${secret}&issuer=GymApp`

# Return QR code for scanning
return {
  secret: secret,
  qr_code_uri: qrCodeUri,
  qr_code_image: generateQRCode(qrCodeUri)
}

# Step 2-> User scans with authenticator app and enters code
POST /auth/mfa/totp/verify-setup
{
  code: "123456"
}

# Verify TOTP code
valid = verifyTOTP(secret, code)
if (!valid) {
  throw new Error("Invalid code")
}

# Step 3-> Enable MFA
backupCodes = generateBackupCodes(10)  # 10 one-time codes

await db.users.update(user.id, {
  mfa_enabled: True,
  mfa_method: 'totp',
  totp_secret: await encrypt(secret),
  totp_backup_codes: await encrypt(JSON.stringify(backupCodes))
})

# Return backup codes (display once, user must save)
return {
  backup_codes: backupCodes,
  message: "Save these codes in a secure location"
}
```

### 3.8 OAuth2 Authorization Code Flow (PKCE)

**Step 1: Authorization Request**

```python
GET /oauth/authorize?
  client_id=uuid&
  redirect_uri=https:#app.example.com/callback&
  scope=clients:read+workouts:read&
  code_challenge=base64url-encoded-challenge&
  code_challenge_method=S256&
  state=random-state

# User logs in (if not already logged in)
# System displays consent screen
```

**Step 2: Authorization Code Issuance**

```python
# User approves
POST /oauth/authorize
{
  client_id: "uuid",
  scopes: ["clients:read", "workouts:read"]
}

# Generate authorization code
authCode = generateSecureRandomToken(256)
codeHash = await sha256(authCode)

await db.oauth2_authorization_codes.create({
  code_hash: codeHash,
  client_id: client_id,
  user_id: user.id,
  redirect_uri: redirect_uri,
  scopes: scopes,
  code_challenge: code_challenge,
  code_challenge_method: 'S256',
  expires_at: new Date(Date.now() + 10 * 60 * 1000)  # 10 minutes
})

# Redirect with code
redirect(`${redirect_uri}?code=${authCode}&state=${state}`)
```

**Step 3: Token Exchange**

```python
POST /oauth/token
{
  grant_type: "authorization_code",
  code: "auth-code-from-step-2",
  code_verifier: "pkce-verifier",
  client_id: "uuid",
  client_secret: "secret",
  redirect_uri: "https:#app.example.com/callback"
}

# Verify code
codeHash = await sha256(code)
authCode = await db.oauth2_authorization_codes.findOne({ code_hash: codeHash })

# Validate
if (!authCode || authCode.expires_at < new Date() || authCode.used_at) {
  throw new Error("Invalid authorization code")
}

# Verify PKCE
expectedChallenge = base64url(sha256(code_verifier))
if (expectedChallenge !== authCode.code_challenge) {
  throw new Error("PKCE verification failed")
}

# Mark code as used
await db.oauth2_authorization_codes.update(authCode.id, {
  used_at: new Date()
})

# Generate tokens
accessToken = jwt.sign(
  { sub: authCode.user_id, scopes: authCode.scopes },
  SECRET,
  { expiresIn: '1h' }
)

refreshToken = generateSecureRandomToken()

await db.oauth2_access_tokens.create({
  client_id: authCode.client_id,
  user_id: authCode.user_id,
  token_type: 'oauth_client',
  token_hash: await sha256(accessToken),
  refresh_token_hash: await sha256(refreshToken),
  scopes: authCode.scopes,
  expires_at: new Date(Date.now() + 60 * 60 * 1000),
  refresh_token_expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
})

return {
  access_token: accessToken,
  refresh_token: refreshToken,
  token_type: 'Bearer',
  expires_in: 3600,
  scope: authCode.scopes.join(' ')
}
```

### 3.9 OAuth2 Client Registration (Gym Admin Only)

```python
# Only gym admins can create OAuth2 clients
POST /oauth/clients
{
  name: "Custom CRM Integration",
  description: "Sync client data to our CRM",
  redirect_uris: ["https:#crm.example.com/oauth/callback"],
  grant_types: ["authorization_code", "refresh_token"],
  scopes_allowed: ["clients:read", "clients:write"]
}

# Verify admin role
if (!user.roles.includes('admin')) {
  throw new Error("Forbidden-> Only gym admins can create OAuth2 clients")
}

# Generate client credentials
clientId = generateUUID()
clientSecret = generateSecureRandomToken(256)
clientSecretHash = await argon2id.hash(clientSecret, hashParams)

await db.oauth2_clients.create({
  client_id: clientId,
  client_secret: clientSecretHash,
  gym_id: user.gym_id,
  created_by_user_id: user.id,
  name: name,
  redirect_uris: redirect_uris,
  grant_types: grant_types,
  scopes_allowed: scopes_allowed,
  is_active: True
})

# Return client credentials (show secret ONCE)
return {
  client_id: clientId,
  client_secret: clientSecret,  # Only time this is shown in plaintext
  message: "Save the client secret securely. It will not be shown again."
}
```

### 3.10 MCP Integration for Trainers

**Important Distinctions**:
- MCP is **trainer-specific OAuth2 authorization** for AI assistant access
- Trainers can ONLY authorize MCP (cannot create general OAuth2 clients)
- Only gym admins can create OAuth2 clients for third-party integrations
- MCP tokens are user-scoped (trainer's data only), not gym-scoped

**Authorization Flow**:

```python
# Step 1-> Trainer initiates MCP authorization
POST /trainers/{trainer_id}/mcp/authorize

# Generate OAuth2 authorization request
authUrl = `/oauth/authorize?
  client_id=internal-mcp-client&
  scope=mcp:trainer&
  redirect_uri=https:#api.gymapp.com/trainers/${trainer_id}/mcp/callback&
  state=${generateState()}`

return { authorization_url: authUrl }

# Step 2-> Trainer approves consent screen
# Shows: "Claude/AI Assistant requests access to: clients:read, workouts:read, schedule:read, measurements:read"

# Step 3-> System creates MCP token
await db.oauth2_access_tokens.create({
  client_id: None,  # No OAuth2Client for MCP
  user_id: trainer.user_id,
  token_type: 'mcp',
  scopes: ['mcp:trainer'],
  expires_at: new Date(Date.now() + 60 * 60 * 1000),  # 1 hour
  refresh_token_expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)  # 30 days
})

# Step 4-> AI assistant uses token for API calls
# All queries automatically filtered to trainer's assigned clients only
```

**MCP Scope Restrictions**:
- `mcp:trainer` grants read-only access to:
  - Trainer's own schedule
  - Trainer's assigned clients only
  - Those clients' workouts, measurements, goals, progress
- Cannot read other trainers' data (row-level security)
- Cannot write/modify any data (read-only for AI safety)
- Cannot access gym admin functions or settings

**Token Management**:

```python
# Revoke MCP access
DELETE /trainers/{trainer_id}/mcp/revoke

await db.oauth2_access_tokens.update(
  { user_id: trainer.user_id, token_type: 'mcp' },
  { revoked_at: new Date() }
)
```

### 3.11 Token Management

**Refresh Token Flow**:

```python
POST /oauth/token
{
  grant_type: "refresh_token",
  refresh_token: "refresh-token"
}

# Hash and verify refresh token
refreshTokenHash = await sha256(refresh_token)
tokenRecord = await db.oauth2_access_tokens.findOne({ refresh_token_hash: refreshTokenHash })

# Validate
if (!tokenRecord || tokenRecord.refresh_token_expires_at < new Date() || tokenRecord.revoked_at) {
  throw new Error("Invalid refresh token")
}

# Generate new access token
newAccessToken = jwt.sign(
  { sub: tokenRecord.user_id, scopes: tokenRecord.scopes },
  SECRET,
  { expiresIn: '1h' }
)

# Optionally rotate refresh token (recommended for mobile)
newRefreshToken = generateSecureRandomToken()

await db.oauth2_access_tokens.update(tokenRecord.id, {
  token_hash: await sha256(newAccessToken),
  refresh_token_hash: await sha256(newRefreshToken),
  expires_at: new Date(Date.now() + 60 * 60 * 1000),
  refresh_token_expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
})

return {
  access_token: newAccessToken,
  refresh_token: newRefreshToken,
  token_type: 'Bearer',
  expires_in: 3600
}
```

**Token Revocation**:

```python
# Revoke specific token
DELETE /auth/sessions/{token_id}

await db.oauth2_access_tokens.update(token_id, {
  revoked_at: new Date()
})

# Revoke all sessions except current
DELETE /auth/sessions/all

await db.oauth2_access_tokens.update(
  { user_id: user.id, token_id: { $ne: current_token_id } },
  { revoked_at: new Date() }
)
```

### 3.12 Staff Onboarding Workflow

**Overview**: Staff (trainers, admins, front desk) are onboarded using an invitation flow. Admins create staff records, send invitation emails, and staff complete account setup.

**Trainer Invitation Flow**:

```python
# Step 1-> Admin creates trainer record via API
POST /gyms/{gym_id}/trainers
{
  first_name: "John",
  last_name: "Smith",
  email: "john.smith@example.com",
  phone: "+1-555-0123",
  primary_location_id: "location-uuid",
  hire_date: "2026-01-19",
  employment_type: "full_time",
  roles: ["trainer", "admin"],
  send_invitation: True  # Default: True
}

# Step 2-> System creates Trainer record
await db.trainers.create({
  trainer_id: generateUUID(),
  gym_id: gym_id,
  first_name: "John",
  last_name: "Smith",
  email: "john.smith@example.com",
  phone: "+1-555-0123",
  primary_location_id: location_id,
  hire_date: new Date("2026-01-19"),
  employment_type: "full_time",
  status: "invited",  # Pending account setup
  user_id: None,      # Will be linked after setup
  created_at: new Date(),
  created_by_user_id: admin_user_id
})

# Step 3-> Generate invitation token (7-day expiration)
invitationToken = generateSecureRandomToken()
await db.trainer_invitations.create({
  trainer_id: trainer_id,
  token_hash: await sha256(invitationToken),
  expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),  # 7 days
  created_at: new Date()
})

# Step 4-> Send invitation email
setupLink = `https:#app.gymapp.com/setup-account?token=${invitationToken}`
await sendEmail({
  to: "john.smith@example.com",
  template: "trainer_invitation",
  variables: {
    first_name: "John",
    gym_name: gym.name,
    setup_link: setupLink,
    expires_in_days: 7,
    inviting_admin_name: admin.first_name + " " + admin.last_name
  }
})

# Step 5-> Trainer clicks link and completes account setup
GET /setup-account?token={invitationToken}
# Verify token, show setup form

POST /auth/setup-account
{
  token: invitationToken,
  password: "SecureP@ssw0rd123",
  mfa_method: "totp"  # or "email"
}

# Step 6-> System creates User and links to Trainer
passwordHash = await argon2id.hash(password, { memoryCost: 64 * 1024, timeCost: 3, parallelism: 4 })

user = await db.users.create({
  email: trainer.email,  # Must match Trainer.email
  password_hash: passwordHash,
  password_hash_version: 1,
  trainer_id: trainer.trainer_id,
  roles: ["trainer", "admin"],  # From trainer creation request
  mfa_enabled: True,     # Required for staff
  mfa_method: mfa_method,
  mfa_enforced_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),  # 7-day grace period
  created_at: new Date(),
  created_by_user_id: admin_user_id
})

# Step 7-> Link User to Trainer and activate
await db.trainers.update(trainer.trainer_id, {
  user_id: user.user_id,
  status: "active"
})

# Step 8-> Mark invitation as used
await db.trainer_invitations.update(invitation.id, {
  used_at: new Date(),
  used_by_user_id: user.user_id
})

# Step 9-> Send welcome email
await sendEmail({
  to: trainer.email,
  template: "trainer_welcome",
  variables: {
    first_name: trainer.first_name,
    gym_name: gym.name,
    login_url: "https:#app.gymapp.com/login"
  }
})
```

**Invitation Expiration and Resend**:

```python
# Resend invitation if trainer hasn't completed setup
POST /trainers/{trainer_id}/resend-invitation

# Verify trainer status is still 'invited'
if (trainer.status !== 'invited') {
  throw new Error("Trainer has already completed setup")
}

# Revoke old invitation
await db.trainer_invitations.update(
  { trainer_id: trainer_id },
  { revoked_at: new Date() }
)

# Create new invitation with fresh 7-day expiration
newToken = generateSecureRandomToken()
await db.trainer_invitations.create({
  trainer_id: trainer_id,
  token_hash: await sha256(newToken),
  expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
  created_at: new Date()
})

# Send new invitation email
await sendEmail({
  to: trainer.email,
  template: "trainer_invitation_reminder",
  variables: {
    first_name: trainer.first_name,
    setup_link: `https:#app.gymapp.com/setup-account?token=${newToken}`,
    expires_in_days: 7
  }
})
```

**Client Login Grant Workflow** (optional, for clients who want app access):

```python
# Admin/trainer grants login access to existing client
POST /clients/{client_id}/grant-login
{
  send_invitation: True  # Default: True
}

# System creates User linked to Client
user = await db.users.create({
  email: client.email,  # Must have email set
  client_id: client.client_id,
  roles: ["client"],
  mfa_enabled: False,  # Optional for clients
  login_enabled: True,
  created_by_user_id: trainer_user_id,
  created_at: new Date()
})

# Send invitation to set password
if (send_invitation) {
  invitationToken = generateSecureRandomToken()
  await db.client_invitations.create({
    client_id: client_id,
    user_id: user.user_id,
    token_hash: await sha256(invitationToken),
    expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
  })

  await sendEmail({
    to: client.email,
    template: "client_login_invitation",
    variables: {
      first_name: client.first_name,
      setup_link: `https:#app.gymapp.com/setup-account?token=${invitationToken}`
    }
  })
}
```

**Key Security Considerations**:
- Invitation tokens are cryptographically secure random 256-bit values
- Tokens are stored as SHA-256 hashes (never plaintext)
- Tokens expire after 7 days
- Used/expired tokens are preserved for audit trail
- Staff users (trainer/admin) require MFA with 7-day grace period
- Email addresses must be unique across all Users
- Trainer.email must match User.email upon linkage

---

## 4. Program Progression

### 4.1 Core Concepts

- A **Program** is a set of multiple **ProgramDays** (workouts) designed by a trainer
- Programs are separate from Plans (payment), but Plans can enable/disable the programming module
- Clients may have multiple active Programs simultaneously

### 4.2 Visit Assignment (Multi-Program Support)

```python
# On check-in / workout start
POST /workouts/start
{
  client_id: "uuid",
  location_id: "uuid",
  trainer_id: "uuid",
  program_id?: "uuid",        # Optional: single program to use for this workout
  program_day_id?: "uuid",    # Optional: specific day override
  started_at: "2026-01-19T10:00:00Z"
}

# System assigns exercises from the specified program or client's active program
client = await db.clients.findOne(client_id)

# Determine which program to use
programDayId = program_day_id
if (!programDayId && program_id) {
    # Get the client's current progress in this program
  clientProgram = await db.client_programs.findOne({
    client_id: client_id,
    program_id: program_id,
    status: 'active'
  })
  if (clientProgram) {
    programDayId = clientProgram.current_program_day_id
  }
}

if (programDayId) {
    # Get all exercises for this day
  exercises = await db.program_day_exercises.find({
    program_day_id: programDayId
  }).orderBy('order_index')

    # Add exercises to workout
  for (exercise of exercises) {
    await db.workout_exercises.create({
      workout_id: workout.id,
      exercise_id: exercise.exercise_id,
      status: 'incomplete',
      order_index: exercise.order_index
    })
  }
}
```

### 4.3 Advancement

```python
# After visit completion
POST /workouts/{id}/complete

# If workout used a program, advance to next program day
workout = await db.workouts.findOne(workout_id)
if (workout.program_id) {
  clientProgram = await db.client_programs.findOne({
    client_id: workout.client_id,
    program_id: workout.program_id,
    status: 'active'
  })

  if (clientProgram) {
    # Get current program day
    currentDay = await db.program_days.findOne(clientProgram.current_program_day_id)

    # Advance to next program day (circular linked list)
    await db.client_programs.update(clientProgram.id, {
      current_program_day_id: currentDay.next_program_day_id
    })
  }
}
```

**Notes**:
- Final day loops back to beginning (circular linked list)
- Trainer can remove/change program at any time
- Client can skip individual programs for a visit

---

## 5. PR Tracking

### 5.1 PR Uniqueness Key

PRs are uniquely identified by:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class PRKey(BaseModel):
    client_id: UUID
    exercise_id: UUID
    measurement_type: Literal['weight', 'time', 'distance', 'reps']
    rep_scheme: str```

**Rep scheme is required** - 1RM, 5RM, 10RM are tracked separately.

### 5.2 PR Direction

For time/distance exercises, PR direction is determined by `ExerciseType.pr_direction`:

```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class ExerciseType(BaseModel):
    pr_direction: Literal['minimize', 'maximize']```

**Examples**:
- `minimize`: Lower is better
  - 400m sprint time
  - 2000m row time
  - Mile run time
- `maximize`: Higher is better
  - Max distance in 10 minutes
  - Plank hold time
  - Max weight lifted

### 5.3 PR Detection

```python
# When workout set completed
async def checkForPR():
  exercise = await db.exercises.findOne(workout_set.exercise_id)
  exerciseType = await db.exercise_types.findOne(exercise.exercise_type_id)

    # Get measurement value from set
  measurement = await db.workout_set_measurements.findOne({
    workout_set_id: workout_set.id,
    type: 'weight'  # or 'time', 'distance', etc.
  })

    # Calculate rep scheme (e.g., "5RM" if actual_reps = 5)
  repScheme = `${workout_set.actual_reps}RM`

    # Query existing PR
  existingPR = await db.prs.findOne({
    client_id: client_id,
    exercise_id: exercise.id,
    measurement_type: measurement.type,
    rep_scheme: repScheme
  })

    # Check if new PR
  isNewPR = False
  if (!existingPR) {
    isNewPR = True
  } else {
    if (exerciseType.pr_direction === 'maximize') {
      isNewPR = measurement.value > existingPR.value
    } else {
      isNewPR = measurement.value < existingPR.value
    }
  }

    # Create or update PR
  if (isNewPR) {
    await db.prs.upsert({
      client_id: client_id,
      exercise_id: exercise.id,
      measurement_type: measurement.type,
      rep_scheme: repScheme,
      value: measurement.value,
      unit: measurement.unit,
      achieved_at: new Date(),
      workout_set_id: workout_set.id
    })

    # Update goal progress if applicable
    await updateGoalProgress(client_id, exercise.id, measurement.value)

    # Send notification
    await notifyPRAchieved(client_id, exercise.name, repScheme, measurement.value)
  }
}
```

---

## 6. Security Requirements

### 6.1 Role-Based Access Control (RBAC)

**Roles**:
- `admin`: Gym administrator
- `trainer`: Trainer at gym
- `front_desk`: Front desk staff
- `client`: Regular client

**Multi-Role Support**:
- Users can have multiple roles (e.g., `["trainer", "front_desk"]`)
- Permissions are union of all roles

**Permission Matrix**:

| Resource | Admin | Trainer | Front Desk | Client |
|----------|-------|---------|------------|--------|
| Gym settings | Write | - | - | - |
| Users/roles | Write | - | - | - |
| Client profiles | Write | Read (assigned) | Read (all) | Read (self) |
| Programs | Write | Write | - | Read (assigned) |
| Workouts | Write | Write (assigned) | - | Read (self) |
| Check-in | Write | Write | Write | - |
| Schedule | Write | Write | Read | Read (self) |
| Measurements | Write | Write (assigned) | - | Read (self) |
| Reports | Read | Read (assigned) | - | - |

### 6.2 Object-Level Authorization

**Row-Level Security**:

```python
# Trainers can only access assigned clients
async def getClient():
  client = await db.clients.findOne({
    client_id: client_id,
    primary_trainer_id: trainer_id  # Filter by assignment
  })

  if (!client) {
    throw new Error("Forbidden-> Not your assigned client")
  }

  return client
}

# Clients can only access own data
async def getWorkouts():
    # Verify user owns this client
  if (user.client_id !== client_id && !user.roles.includes('admin')) {
    throw new Error("Forbidden-> Cannot access other client's data")
  }

  return db.workouts.find({ client_id: client_id })
}
```

### 6.3 Audit Logging

**Critical events to log**:
- User login/logout
- Password changes
- MFA enable/disable
- OAuth2 client creation/deletion
- Token issuance/revocation
- Client data export/deletion
- Membership creation/cancellation
- Payment events

**Audit Log Structure**:

```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class AuditLog(BaseModel):
    event_id: UUID
    event_type: str
    user_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    gym_id: UUID
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    details: JSON```

**Retention**: Keep audit logs for 7 years (compliance).

### 6.4 Payment Security

**Never store raw card data**:
- Use Stripe-hosted UI (Checkout/Payment Element)
- Store only Stripe IDs (customer_id, subscription_id, payment_intent_id)
- All payment processing happens on Stripe servers

**Webhook Verification**:

```python
# Verify Stripe webhook signatures
import Stripe from 'stripe'

async def handleStripeWebhook():
  sig = req.headers['stripe-signature']
  webhookSecret = process.env.STRIPE_WEBHOOK_SECRET

  event
  try {
    event = Stripe.webhooks.constructEvent(
      req.body,
      sig,
      webhookSecret
    )
  } catch (err) {
    throw new Error('Webhook signature verification failed')
  }

    # Process event
  switch (event.type) {
    case 'payment_intent.succeeded':
      await handlePaymentSuccess(event.data.object)
      break
    case 'customer.subscription.deleted':
      await handleSubscriptionCanceled(event.data.object)
      break
  }
}
```

---

## 7. Technical Implementation Decisions

### 7.1 Password Storage

**Decision**: Use **Argon2id only** for password hashing.

**Rationale**:
- Memory-hard algorithm resistant to GPU/ASIC attacks
- Industry best practice as of 2024+
- Winner of Password Hashing Competition (PHC)

**Implementation**:
```python
import argon2 from 'argon2'

hash = await argon2.hash(password, {
  type: argon2.argon2id,
  memoryCost: 64 * 1024,  # 64 MB
  timeCost: 3,
  parallelism: 4,
  saltLength: 16          # 128-bit salt
})
```

**Hash Versioning**:
- Track algorithm version in `password_hash_version` field
- Allows transparent migration to stronger algorithms over time
- On successful login: check version, rehash if outdated

### 7.2 MFA Methods

**Decision**: Support TOTP, email, and passkey-only. **Do NOT support SMS**.

**Rationale**:
- **TOTP**: Industry standard, secure, works offline
- **Email**: Acceptable fallback, better than nothing
- **Passkey-only**: Most secure (FIDO2 certified, phishing-resistant)
- **SMS**: Vulnerable to SIM swap attacks, NOT recommended by security experts

### 7.3 OAuth2 Access Control

**Decision**: Separate OAuth2 client creation (admin-only) from MCP authorization (trainer-only).

**Rationale**:
- Prevents trainers from creating malicious OAuth2 clients
- MCP is read-only, user-scoped (safe for trainers)
- General OAuth2 clients can have write access, gym-scoped (requires admin approval)

**Implementation**:
```python
# Admin creates OAuth2 client
if (!user.roles.includes('admin')) {
  throw new Error("Forbidden-> Only admins can create OAuth2 clients")
}

# Trainer authorizes MCP
if (!user.roles.includes('trainer')) {
  throw new Error("Forbidden-> MCP is for trainers only")
}
```

### 7.4 Data Storage Strategy

**Decision**: Hybrid PostgreSQL + MongoDB + Redis.

**Rationale**:
- **PostgreSQL**: System of record for OLTP; strong referential integrity, ACID guarantees, complex joins
- **MongoDB**: Document/time-series data; schema flexibility, time-series collections, change streams
- **Redis**: Ephemeral caching and coordination; performance optimization without creating a third source of truth
- **Object Storage**: Cost-effective for large binaries (photos, PDFs)

**Technology Selection**:
- **PostgreSQL**: Authoritative database for all transactional data
- **MongoDB Atlas**: Preferred over DocumentDB for full MongoDB feature compatibility (time-series collections, TTL indexes, change streams)
- **Redis**: Cache-aside layer; system must function correctly if Redis is unavailable or flushed
- **S3 + CloudFront**: Object storage with CDN for binary assets

**Data Mapping**:
| Data Type | Storage | Rationale |
|-----------|---------|-----------|
| Users, Auth, Sessions | PostgreSQL | Transactional, ACID required |
| Gyms, Locations, Clients, Trainers | PostgreSQL | Relational hierarchy, FK constraints |
| Memberships, Check-ins, Bookings | PostgreSQL | Business-critical OLTP, immediate consistency |
| Programs, Workouts, Sets, Measurements | PostgreSQL | Relational, complex queries, audit history |
| Audit Logs, Change Tracking | PostgreSQL | Compliance, immutability, joins with operational data |
| Gym Plan Limits, Feature Flags | MongoDB | Flexible schema, rapid iteration, versioned config |
| Usage Metering Rollups | MongoDB | Time-series collections, high write volume |
| Trainer Availability (optional) | MongoDB | Document-based schedules (alternative: PostgreSQL normalized) |
| Gym Analytics Aggregates | MongoDB | Time-windowed rollups, change streams |
| Plan Limits Cache | Redis (TTL: 5-15 min) | Read-heavy, cache-aside from MongoDB |
| Schedule Cache ("today") | Redis (TTL: 1-5 min) | Reduce PostgreSQL read load |
| Busyness Time-Slots | Redis (TTL: 1-5 min) | Derived aggregate, recomputed on miss |
| Rate Limiting Counters | Redis | Login attempts, API throttles, abuse prevention |
| Idempotency Keys | Redis (TTL: 24h) or PostgreSQL | Deduplication; PostgreSQL if cache loss intolerance |
| Distributed Locks | Redis (short-lived) | Scheduling coordination (PostgreSQL enforces correctness) |
| Progress Photos, Signed PDFs | S3 + CloudFront | Large binaries, CDN delivery, metadata in PostgreSQL |

**Cross-Database Consistency**:
- **No atomic transactions across PostgreSQL and MongoDB**. If a workflow requires strong consistency, keep it entirely in PostgreSQL.
- Use **outbox pattern** for eventual consistency: write to PostgreSQL, publish events asynchronously to update MongoDB.
- **Snapshot critical fields**: If `PlanTemplate` lives in MongoDB, snapshot visit entitlements and expiration rules into PostgreSQL's `ClientMembership` at assignment time. Check-in/entitlement validation must never depend on MongoDB availability.

**Redis Design Assumptions**:
- Redis can be flushed or restarted at any time—the system must remain fully functional.
- All cached data has a source of truth in PostgreSQL or MongoDB.
- Cache misses trigger recomputation and repopulation, not failures.
- Rate limiting and idempotency key loss is acceptable (temporary degradation, not data corruption).

### 7.5 API Latency Targets

**Decision**: Define formal SLAs for different operation types.

**Real-time operations** (p95 < 200ms, p99 < 500ms):
- Authentication (login, token refresh)
- Workout logging (start workout, log set, complete exercise)
- Scheduling (check availability, book session)
- Check-in operations

**Dashboard/reporting** (p95 < 1s, p99 < 2s):
- Analytics queries
- Trainer dashboards
- Client progress reports
- Workout history

**Background operations** (best effort, no SLA):
- AI summary generation
- Usage metering rollups
- Email/push notifications

**Rationale**:
- Real-time ops are user-facing, blocking critical workflows
- Dashboard ops tolerate slight delay for complex queries
- Background ops can be async without impacting UX

### 7.6 Offline-First Strategy

**Decision**: Full offline capability for mobile apps, online-only for web app.

**Rationale**:
- Mobile users (trainers on gym floor) may have spotty internet
- Web users (admins) typically on stable connections
- Offline-first improves UX and reliability for critical operations

**Offline-Capable Operations** (mobile only):
- Add/edit clients and prospects
- Sign existing e-signature agreements (queued for server signature)
- Check in clients (workout start)
- Log workout data (sets, reps, measurements)
- Complete workouts
- View schedules (cached last 30 days)
- View programs (cached)
- View client profiles + recent history (cached last 30 days)
- Upload progress photos (queued for upload)

**Online-Only Operations** (all platforms):
- Admin functions
- Creating/editing programs
- Reports and analytics
- Payment/billing operations

**Sync Strategy**:
```python
# Background sync on connection resume
addEventListener('online', async () => {
  pendingOps = await localDB.pendingOperations.findAll()

  for (op of pendingOps) {
    try {
      await syncOperation(op)
      await localDB.pendingOperations.delete(op.id)
    } catch (error) {
      # Retry later
      console.error('Sync failed:', error)
    }
  }
})

# Conflict resolution
async def syncOperation():
  result = await api.post(op.endpoint, op.data)

  if (result.conflict) {
    # Two trainers logged same workout offline
    # Log both, alert admin
    await logConflict(op, result.existing)
  }
}
```

**Idempotency & Conflict Resolution**:

For offline-first operations to work reliably, the system must handle:
1. Network retries (same operation sent multiple times)
2. Concurrent modifications (multiple trainers editing same data offline)
3. Optimistic concurrency control (version conflicts)

#### Idempotency Keys

**Implementation** (see [API_SPECIFICATIONS.md:244](API_SPECIFICATIONS.md#28-idempotency)):

All state-changing operations include an idempotency key generated on the client:

```python
# Mobile app generates idempotency key before offline operation
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class PendingOperation(BaseModel):
    id: UUID
    idempotency_key: UUID
    endpoint: str
    method: Literal['POST', 'PUT', 'PATCH', 'DELETE']
    data: Any
    created_at: datetime
    retry_count: int

# Example: Start workout offline
async function startWorkout(clientId: UUID, trainerId: UUID) {
  const idempotencyKey = uuidv4();  // Generate once, reuse on retries

  const operation: PendingOperation = {
    id: uuidv4(),
    idempotency_key: idempotencyKey,
    endpoint: '
    method: 'POST',
    data: Dict[str, Any]
    client_id: clientId,
    trainer_id: trainerId,
    started_at: new Date().toISOString()
    },
    created_at: new Date(),
    retry_count: 0

    # Store in local pending operations queue
  await localDB.pendingOperations.insert(operation);

    # Optimistic UI: Show workout started immediately
  return { workout_id: operation.id, status: 'pending_sync' };

# Sync operation sends idempotency key
async function syncPendingOperation(op: PendingOperation) {
  try {
    const response = await api.post(op.endpoint, op.data, {
    headers: Dict[str, Any]
        'X-Idempotency-Key': op.idempotency_key,
        'Content-Type': 'application/json'
    });

    # Server responds with 200 OK if idempotency key already processed
    # Server responds with 201 Created if first time
    return response;
  } catch (error) {
    op.retry_count++;
    if (op.retry_count < 5) {
      # Exponential backoff: 2^retry_count seconds
      await sleep(Math.pow(2, op.retry_count) * 1000);
      return syncPendingOperation(op);
    throw error;```

**Server-side idempotency handling**:

```python
# Server stores idempotency keys for 24 hours
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class IdempotencyRecord(BaseModel):
    idempotency_key: UUID
    request_hash: str
    response_status: int
    response_body: Any
    created_at: datetime
    expires_at: datetime

async function handleIdempotentRequest(req: Request) {
  const idempotencyKey = req.headers['x-idempotency-key'];

  if (!idempotencyKey) {
    # Idempotency key required for POST/PUT/PATCH/DELETE
    throw new Error('X-Idempotency-Key header required');

    # Check if key already processed
  const existing = await db.idempotency_records.findOne({
    idempotency_key: idempotencyKey,
    expires_at: Dict[str, Any]
  });

  if (existing) {
    # Return cached response
    return {
    status: existing.response_status,
    body: existing.response_body,
    headers: Dict[str, Any]
        'X-Idempotent-Replay': 'true'

    # Process request normally
  const response = await processRequest(req);

    # Store idempotency record
  await db.idempotency_records.create({
    idempotency_key: idempotencyKey,
    request_hash: sha256(JSON.stringify(req.body)),
    response_status: response.status,
    response_body: response.body,
    created_at: new Date(),
    expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000)
  });

  return response;```

#### Conflict Resolution Strategies

**Last-Write-Wins (LWW)** - For most entity updates:

```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class Entity(BaseModel):
    id: UUID
    updated_at: datetime
    updated_by: UUID
    version: int

# Client sends current version with update
async function updateClient(clientId: UUID, updates: Partial<Client>, currentVersion: number) {
  const result = await db.clients.updateOne({
    client_id: clientId,
    version: currentVersion = Field(None, description="Optimistic lock")
  }, {
    $set: {
      ...updates,
    updated_at: new Date(),
    updated_by: currentUser.id
    },
    $inc: { version: 1 }
  });

  if (result.matchedCount === 0) {
    # Version conflict: another update happened since client read this record
    throw new ConflictError('Record has been modified by another user');

  return result;```

**Merge Strategy** - For workout sets (additive, non-conflicting):

```python
# Two trainers can log different sets for same workout offline
# Server merges both when syncing
async def syncWorkoutSets():
  existingSets = await db.workout_sets.find({ workout_id: workoutId })

    # Merge-> Keep all unique sets (by set_index + exercise_id)
  mergedSets = [...existingSets]

  for (newSet of newSets) {
    exists = mergedSets.find(s =>
      s.exercise_id === newSet.exercise_id &&
      s.set_index === newSet.set_index
    )

    if (!exists) {
      mergedSets.push(newSet)
    } else if (newSet.updated_at > exists.updated_at) {
      # Replace with newer version
      Object.assign(exists, newSet)
    }
  }

  return mergedSets
}
```

**Manual Resolution** - For critical conflicts:

```python
# If two trainers complete the same workout offline
# Flag for manual admin review
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any

class ConflictLog(BaseModel):
    conflict_id: UUID
    entity_type: str
    entity_id: UUID
    operation1: PendingOperation
    operation2: PendingOperation
    status: Literal['pending_review', 'resolved', 'ignored']
    resolved_by: Optional[UUID] = None
    resolved_at: Optional[datetime] = None

async function detectConflict(op: PendingOperation) {
  if (op.endpoint.includes('/workouts') && op.method === 'POST') {
    # Check if another offline operation already completed this workout
    const existingOp = await db.pending_operations.findOne({
    endpoint: op.endpoint,
      'data.client_id': op.data.client_id,
      'data.started_at': { $near: op.data.started_at, $within: 60 * 1000 } // Within 1 minute
    });

    if (existingOp) {
      # Log conflict for admin review
      await db.conflict_logs.create({
    conflict_id: uuidv4(),
    entity_type: 'workout',
    entity_id: op.data.workout_id,
    operation1: existingOp,
    operation2: op,
    status: 'pending_review'
      });

      # Notify admins
      await notifyAdmins({
    type: 'conflict_detected',
    message: 'Two trainers logged workout for same client at same time',
    conflict_id: conflict.conflict_id
      });```

#### Sync Queue Priority

Operations synced in priority order:

1. **High Priority** (sync immediately when online):
   - Workout completion
   - Client check-in
   - Measurements and PRs

2. **Medium Priority** (sync within 5 minutes):
   - Client profile updates
   - Progress photo uploads

3. **Low Priority** (sync within 30 minutes):
   - Analytics events
   - Audit logs

```python
async def processSyncQueue():
  pending = await localDB.pendingOperations.findAll({
    orderBy: [
      { priority: 'desc' },
      { created_at: 'asc' }
    ]
  })

  for (op of pending) {
    await syncPendingOperation(op)
  }
}
```

### 7.7 Busyness Calculations

**Decision**: Three separate busyness views with 15-minute granularity.

**Views**:
1. **Self-Directed Busyness**: Gym occupancy from members without training
2. **Training Busyness**: Expected occupancy from scheduled training sessions
3. **Per-Trainer Busyness**: Individual trainer load

**Rationale**:
- Different use cases require different views
- Self-directed helps with general gym capacity planning
- Training busyness helps with trainer scheduling
- Per-trainer helps with workload balancing

**Implementation**:
```python
# View 1-> Self-Directed Busyness
async def getSelfDirectedBusyness():
  slots = generate15MinuteSlots(date)

  for (slot of slots) {
    count = await db.gym_check_ins.count({
      location_id: location_id,
      check_in_type: 'self_directed',
      checked_in_at: { $lte: slot.start },
      expected_checkout_at: { $gte: slot.end }
    })

    slot.occupancy = count
  }

  return slots
}

# View 2-> Training Busyness (with predictive analytics)
async def getTrainingBusyness():
  slots = generate15MinuteSlots(date)

  for (slot of slots) {
    # Count already checked-in sessions
    checkedIn = await db.gym_check_ins.count({
      location_id: location_id,
      check_in_type: 'training_session',
      checked_in_at: { $lte: slot.start },
      expected_checkout_at: { $gte: slot.end }
    })

    # Count scheduled (not yet checked in)
    scheduled = await db.schedules.find({
      location_id: location_id,
      scheduled_start: { $lte: slot.end },
      scheduled_end: { $gte: slot.start },
      status: { $in: ['tentative', 'confirmed'] }
    })

    # Predict arrivals
    predictedCount = 0
    for (session of scheduled) {
      client = await db.clients.findOne(session.client_id)
      predictedArrival = session.scheduled_start + client.avg_schedule_variance_minutes
      confidence = calculateConfidence(client.schedule_history)

      if (predictedArrival >= slot.start && predictedArrival <= slot.end) {
        predictedCount += confidence  # Weighted by confidence
      }
    }

    slot.occupancy = checkedIn + predictedCount
  }

  return slots
}
```

### 7.8 Seasonality-Aware Analytics

**Decision**: Use different lookback periods based on client tenure.

**Algorithm**:
- **New clients** (<90 days): Last 90 days of data
- **Regular clients** (90-365 days): Last 180 days of data
- **Long-term clients** (>365 days): Year-over-year comparison for same time period

**Rationale**:
- Accounts for seasonal patterns (New Year's rush, summer dropoff)
- More accurate predictions for long-term members
- Sufficient data for new members without overfitting

**Implementation**:
```python
async def calculateAvgWorkoutDuration():
  client = await db.clients.findOne(client_id)
  tenureDays = (Date.now() - client.created_at) / (1000 * 60 * 60 * 24)

  workouts
  if (tenureDays < 90) {
    # New client: last 90 days
    workouts = await db.workouts.find({
      client_id: client_id,
      started_at: { $gte: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000) }
    })
  } else if (tenureDays < 365) {
    # Regular client: last 180 days
    workouts = await db.workouts.find({
      client_id: client_id,
      started_at: { $gte: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000) }
    })
  } else {
    # Long-term client: year-over-year for current month
    currentMonth = new Date().getMonth()
    workouts = await db.workouts.find({
      client_id: client_id,
      $where: `this.started_at.getMonth() === ${currentMonth}`
    })
  }

  avgDuration = workouts.reduce((sum, w) => sum + (w.ended_at - w.started_at), 0) / workouts.length
  return avgDuration / (1000 * 60)  # Convert to minutes
}
```

### 7.9 Web App UI Framework

**Decision**: Use D3.js for data visualizations and Tailwind CSS for styling and UI components.

**Rationale**:
- **D3.js** provides powerful, flexible data visualizations for analytics dashboards
- **Tailwind CSS** enables rapid UI development with utility-first approach and maintains consistency
- Both technologies support highly interactive, responsive user interfaces matching mobile app experience
- Tailwind UI (premium templates license available) accelerates professional component development

**Technology Stack**:
- **Data Visualization**: D3.js v7+ for charts, graphs, and interactive data displays
- **CSS Framework**: Tailwind CSS v3+ with utility classes
- **Component Library**: Tailwind UI (premium templates with license)
- **Animations**: Tailwind transitions + Framer Motion for smooth interactions
- **Real-time Updates**: WebSocket or Server-Sent Events for live data

**Key Visualization Requirements**:

**Admin Dashboard**:
- Attendance trends over time (line/area charts)
- Revenue analytics (bar charts, trend lines)
- Trainer utilization heat maps
- Gym capacity/busyness visualizations (real-time)
- Client acquisition funnel (conversion charts)

**Trainer Dashboard**:
- Client progress tracking (multi-line charts)
- PR progression graphs (scatter plots, trend lines)
- Adherence/attendance rates (gauge charts)
- Workout volume comparisons (stacked bar charts)
- Client engagement scores (radial charts)

**Client Portal** (optional):
- Personal progress charts (line/area charts)
- PR history visualization (timeline)
- Body composition tracking (area charts)
- Goal progress indicators (progress bars, gauge charts)

**Implementation Example**:
```python
# D3.js progress chart with Tailwind styling
import * as d3 from 'd3'

def renderProgressChart():
  svg = d3.select(container)
    .append('svg')
    .attr('class', 'w-full h-64 rounded-lg shadow-lg')
    .attr('viewBox', '0 0 800 400')

  xScale = d3.scaleTime()
    .domain(d3.extent(data, d => d.date))
    .range([50, 750])

  yScale = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.value)])
    .range([350, 50])

  line = d3.line<ProgressData>()
    .x(d => xScale(d.date))
    .y(d => yScale(d.value))
    .curve(d3.curveMonotoneX)

  svg.append('path')
    .datum(data)
    .attr('class', 'stroke-indigo-600 fill-none stroke-2')
    .attr('d', line)

    # Tailwind-styled tooltip
  svg.selectAll('circle')
    .data(data)
    .enter()
    .append('circle')
    .attr('class', 'fill-indigo-500 hover:fill-indigo-700 cursor-pointer transition-colors')
    .attr('cx', d => xScale(d.date))
    .attr('cy', d => yScale(d.value))
    .attr('r', 5)
}
```

**Component Patterns**:
```tsx
// Tailwind UI component example (dashboard card)
<div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
  <h3 className="text-lg font-semibold text-gray-900 mb-4">
    Client Progress
  </h3>
  <div id="progress-chart" className="w-full h-64">
    {/* D3 chart rendered here */}
  </div>
  <div className="mt-4 flex items-center justify-between">
    <span className="text-sm text-gray-500">Last 30 days</span>
    <button className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors">
      View Details
    </button>
  </div>
</div>
```

**Performance Considerations**:
- Use D3's `transition()` API for smooth animations (matching 60fps target)
- Implement virtualization for large datasets (react-virtualized or similar)
- Lazy-load D3 charts on viewport intersection (Intersection Observer API)
- Cache chart SVGs with appropriate TTLs
- Use Tailwind's JIT (Just-In-Time) compiler to minimize CSS bundle size

**Accessibility**:
- Ensure all D3 visualizations have ARIA labels and descriptions
- Provide keyboard navigation for interactive charts
- Use Tailwind's focus ring utilities for visible focus states
- Include text alternatives for charts (data tables, summaries)
- Meet WCAG 2.1 Level AA contrast requirements (Tailwind color palette compliant)

---

## 8. Technical Glossary

### Authentication & Security

**Argon2id**: Memory-hard password hashing algorithm resistant to GPU/ASIC attacks. Winner of the Password Hashing Competition (PHC). Combines Argon2i (side-channel resistant) and Argon2d (GPU-resistant) modes.

**MFA (Multi-Factor Authentication)**: Requires two or more verification factors to authenticate. Factors: something you know (password), something you have (phone/security key), something you are (biometric).

**TOTP (Time-based One-Time Password)**: Algorithm for generating one-time passwords based on current time. Used by apps like Google Authenticator, Authy, 1Password.

**WebAuthn (Web Authentication)**: W3C standard for passkey/FIDO2 authentication. Enables passwordless login using biometrics or security keys.

**FIDO2**: Industry standard for phishing-resistant authentication. Combines WebAuthn (browser API) and CTAP (device protocol).

**PKCE (Proof Key for Code Exchange)**: OAuth2 security extension (RFC 7636) that prevents authorization code interception attacks. Required for mobile apps and single-page applications.

**OAuth2**: Industry-standard protocol for authorization. Allows third-party apps to access user resources without exposing passwords.

**SHA-256**: Cryptographic hash function producing 256-bit digest. Used for token hashing (NOT for password hashing).

**Salt**: Random data added to passwords before hashing to prevent rainbow table attacks. Argon2id automatically generates and stores salts.

### Data Architecture

**ACID**: Atomicity, Consistency, Isolation, Durability. Database transaction properties guaranteeing data integrity.

**OLTP (Online Transaction Processing)**: Database optimized for transactional operations with immediate consistency. Used for user-facing read/write operations.

**Time-Series Database**: Database optimized for time-stamped data. Used for metrics, logs, and analytics rollups.

**CDN (Content Delivery Network)**: Distributed network of servers for fast content delivery. Used for serving progress photos and static assets.

**Object Storage**: Scalable storage for large binaries (photos, PDFs). Examples: AWS S3, Google Cloud Storage.

**Foreign Key (FK)**: Database constraint ensuring referential integrity. Links records across tables.

**Soft Delete**: Marking records as deleted without physically removing them. Preserves data for audit trails and compliance.

**Denormalization**: Duplicating data across tables for query performance. Trade-off: faster reads, more complex writes.

### Fitness & Workout Tracking

**AMRAP (As Many Reps As Possible)**: Exercise set type where client performs maximum reps until failure.

**PR (Personal Record)**: Client's best performance on a specific exercise. Tracked per exercise + measurement type + rep scheme.

**RPE (Rate of Perceived Exertion)**: Subjective measure of exercise difficulty, typically 1-10 scale.

**1RM (One-Rep Max)**: Maximum weight client can lift for one repetition. Used for strength benchmarking.

**Tempo**: Prescribed speed for exercise phases. Format: "eccentric-pause-concentric-pause" (e.g., "3-1-1-0" = 3 seconds down, 1 second pause, 1 second up, no pause at top).

**Superset**: Performing two exercises back-to-back with no rest. Modeled using WorkoutExerciseGroup.

**Circuit**: Performing multiple exercises in sequence with minimal rest. Also modeled using WorkoutExerciseGroup.

### Program & Membership

**Plan**: What a client pays for (membership/entitlement bundle). Defines visit entitlements, payment terms, module access.

**Program**: Prescribed set of training activities (workouts). Separate from payment plans.

**Plan Type**: Category of membership plan (gym_access, personal_training, group_classes). Client can have max one active membership per type.

**Visit Entitlement**: Number of gym visits allowed per period. Types: unlimited, per_week, per_month, per_plan_duration.

**Session Pack**: One-time payment for fixed number of visits (until-used plan type). Example: "10-Pack Personal Training".

**Add-on Plan**: Discounted membership plan for family members. Requires primary member with base plan.

**Emancipation**: Transfer of sub-member to own independent account. Typically when child turns 18.

### Analytics & Reporting

**Busyness**: Gym occupancy at 15-minute granularity. Three views: self-directed, training, per-trainer.

**Rollup**: Pre-calculated aggregate metrics for fast dashboard queries. Computed nightly/hourly.

**Cold Storage**: Archived data moved to cheaper storage for infrequent access. Used for data older than 1 year.

**Seasonality**: Recurring patterns in data based on time of year. Example: New Year's gym rush, summer dropoff.

**Confidence Interval**: Statistical range indicating prediction certainty. Used for predicting client arrivals.

**Adherence**: Client's consistency in attending scheduled workouts. Metric for engagement tracking.

### Compliance & Privacy

**COPPA (Children's Online Privacy Protection Act)**: US law restricting data collection for children under 13. Requires parental consent.

**CCPA (California Consumer Privacy Act)**: California privacy law granting data access, deletion, and opt-out rights.

**GDPR (General Data Protection Regulation)**: EU privacy law with strict data protection requirements. Not applicable until international expansion.

**Right to Be Forgotten**: Legal right to request data deletion. Implemented via soft delete + anonymization.

**PII (Personally Identifiable Information)**: Data that can identify an individual (name, email, address, DOB).

**Data Anonymization**: Removing PII while preserving data for analytics. Example: "Deleted User #12345".

**Data Export**: Providing user's data in portable format (JSON, CSV, PDF). Required by CCPA and GDPR.

### Accessibility

**WCAG (Web Content Accessibility Guidelines)**: W3C standard for web accessibility. Levels: A (minimum), AA (recommended), AAA (enhanced).

**ARIA (Accessible Rich Internet Applications)**: HTML attributes for semantic markup. Helps assistive technologies understand UI.

**Screen Reader**: Software that reads screen content aloud for blind/low-vision users. Examples: VoiceOver (iOS/macOS), TalkBack (Android), NVDA/JAWS (Windows).

**VoiceOver**: Apple's built-in screen reader for iOS and macOS.

**TalkBack**: Android's built-in screen reader.

**Dynamic Type**: iOS feature for system-wide font size scaling. Improves readability for low-vision users.

**Keyboard Navigation**: Using Tab, Enter, Space, Arrow keys instead of mouse/touch. Required for motor-impaired users.

**Focus Indicator**: Visual highlight showing which element has keyboard focus. Required for WCAG compliance.

**Alt Text**: Descriptive text for images read by screen readers. Required for all non-decorative images.

**Color Contrast**: Ratio between text and background colors. WCAG AA requires 4.5:1 for normal text, 3:1 for large text.

---

## Appendix A: Database Schema Diagrams

### Core Entity Relationships

```
Account (1) ──── (M) Client (1) ──── (1) User
   │                  │
   │                  ├──── (M) ClientMembership ──── (1) PlanTemplate (NoSQL)
   │                  │
   │                  ├──── (M) Workout ──── (M) WorkoutExercise ──── (M) WorkoutSet
   │                  │                                                     │
   │                  │                                                     └──── (M) WorkoutSetMeasurement
   │                  │
   │                  ├──── (M) GymCheckIn
   │                  ├──── (M) ProgressPhoto
   │                  ├──── (M) ClientMeasurement ──── (1) GymMeasurementType
   │                  └──── (M) ClientGoal

Gym (1) ──── (M) Location
  │
  ├──── (M) Trainer ──── (1) TrainerAvailability (NoSQL)
  │                 └──── (M) TrainerException
  │
  ├──── (1) GymPlanLimits (NoSQL)
  ├──── (M) UsageMetricRollup (NoSQL)
  └──── (M) GymAnalytics (NoSQL)

Program (1) ──── (M) ProgramDay (circular linked list)
                        │
                        └──── (M) ProgramDayExercise ──── (1) Exercise ──── (1) ExerciseType

User (1) ──── (M) UserPasskey
       │
       ├──── (M) OAuth2AccessToken
       └──── (M) PasswordResetToken

OAuth2Client (1) ──── (M) OAuth2AccessToken
                 └──── (M) OAuth2AuthorizationCode
```

### Authentication Flow Diagram

```
                                 ┌─────────────┐
                                 │   Client    │
                                 └──────┬──────┘
                                        │
                         ┌──────────────┴──────────────┐
                         │                             │
                    Password Login              Passkey Login
                         │                             │
                 ┌───────▼────────┐           ┌────────▼────────┐
                 │ Verify Password│           │ WebAuthn Verify │
                 └───────┬────────┘           └────────┬────────┘
                         │                             │
                    ┌────▼────┐                        │
                    │   MFA?  │                        │
                    └────┬────┘                        │
                         │                             │
              ┌──────────┴──────────┐                  │
              │                     │                  │
          MFA Required         MFA Disabled            │
              │                     │                  │
      ┌───────▼────────┐            │                  │
      │ Verify TOTP/   │            │                  │
      │ Email Code     │            │                  │
      └───────┬────────┘            │                  │
              │                     │                  │
              └──────────┬──────────┘                  │
                         │                             │
                 ┌───────▼─────────────────────────────▼────┐
                 │    Generate OAuth2 Access Token          │
                 └───────┬──────────────────────────────────┘
                         │
                 ┌───────▼────────┐
                 │ Return Tokens  │
                 └────────────────┘
```

---

## 9. Architecture Decision Records (ADRs)

This section records key technical and business decisions made during the design of the gym management platform. Each decision follows the ADR format: context, decision, rationale, and consequences.

### 9.1 Payments & Billing

#### ADR-001: Stripe as Payment Processor

**Status**: Approved
**Date**: 2026-01-19

**Context**: Need payment processing for gym subscriptions and client memberships.

**Decision**: Use Stripe as the payment processor, implemented last in the development roadmap.

**Rationale**:
- Industry-standard payment platform with comprehensive API
- Reduces PCI compliance scope by keeping sensitive payment data in Stripe
- Supports both subscriptions and one-time payments
- Strong webhook support for event-driven architecture

**Consequences**:
- Positive: Reduces security and compliance burden
- Positive: Accelerates development with pre-built payment UI components
- Negative: Vendor lock-in to Stripe ecosystem
- Negative: Stripe fees (2.9% + $0.30 per transaction)

#### ADR-002: Gym as Merchant of Record

**Status**: Approved
**Date**: 2026-01-19

**Context**: Determine who collects payments from clients (platform vs. gyms).

**Decision**: Gyms are merchant of record for client memberships via Stripe Connect.

**Rationale**:
- Simplifies platform accounting (no revenue pass-through)
- Gyms maintain direct relationship with clients
- Avoids platform liability for gym-specific services
- Gyms responsible for their own sales tax reporting

**Consequences**:
- Positive: Platform avoids complex accounting and tax reporting for gym revenue
- Positive: Gyms have full control over pricing and refunds
- Negative: Platform-side tax reporting remains TBD
- Negative: Each gym requires individual Stripe Connect onboarding

#### ADR-003: Processing Fee Configuration

**Status**: Approved
**Date**: 2026-01-19

**Context**: Stripe charges processing fees (2.9% + $0.30). Gyms may want flexibility in handling these fees.

**Decision**: Allow gyms to configure fee handling:
- `gym_absorbs`: Gym pays all Stripe processing fees (default)
- `pass_to_client`: Fees added to client invoice (configurable percentage/flat/both)

**Rationale**:
- Gives gyms flexibility in pricing strategy
- Standard practice in many SaaS platforms
- Simple to implement with Stripe's fee calculation tools

**Consequences**:
- Positive: Gyms can choose cost structure
- Negative: Adds complexity to invoice calculations
- Negative: Passing fees to clients may impact conversion rates

### 9.2 Plan & Program Architecture

#### ADR-004: Plan vs Program Separation

**Status**: Approved
**Date**: 2026-01-19

**Context**: Need clear separation between what clients pay for vs. what trainers prescribe.

**Decision**:
- **Plan** = what a client pays for (membership/entitlement bundle)
- **Program** = prescribed set of training activities
- Plans control module access (e.g., programming, health integration, progress photos)
- Clients can have multiple active Programs (subject to Plan entitlements)

**Rationale**:
- Clear separation of concerns (billing vs. training)
- Allows flexible program assignments without affecting billing
- Plans can gate features (e.g., "Basic" plan doesn't include progress photos)

**Consequences**:
- Positive: Clean architecture boundary
- Positive: Easy to add new features gated by plan tier
- Negative: Requires careful entitlement checking on all feature access

#### ADR-005: One Membership Per Plan Type

**Status**: Approved
**Date**: 2026-01-19

**Context**: Prevent conflicting memberships (e.g., two overlapping "Personal Training" plans).

**Decision**: Clients can only have ONE active membership per `plan_type` (e.g., `gym_access`, `personal_training`, `group_classes`).

**Valid combinations**:
- "Monthly Gym Access" + "10-Pack Training" (different types)

**Invalid combinations**:
- "Monthly Training" + "10-Pack Training" (same type)

**Rationale**:
- Prevents conflicts in visit entitlement tracking
- Simplifies business logic for check-ins
- Clear to gyms and clients

**Consequences**:
- Positive: Eliminates ambiguity in membership status
- Negative: Clients must cancel one membership before purchasing another of the same type

#### ADR-016: Extensible Plan Types

**Status**: Approved
**Date**: 2026-01-19

**Context**: Need to decide whether `plan_type` should be a fixed enum or an extensible string value.

**Decision**: Use extensible **string** type for `plan_type` rather than fixed TypeScript enum.

**Canonical types** (recommended):
- `'gym_access'`: General gym membership
- `'personal_training'`: One-on-one training sessions
- `'group_classes'`: Group fitness classes

**Custom types** (examples):
- `'hybrid_training'`: Mix of personal and group sessions
- `'nutrition_coaching'`: Nutrition-focused programs
- `'specialty_class'`: Specialty programs (e.g., powerlifting, Olympic lifting)

**Rationale**:
- Gyms have diverse business models beyond the three canonical types
- Hard-coding types in an enum requires code changes to support new types
- String type with documented conventions provides flexibility while maintaining clarity
- Unique constraint on `(client_id, plan_type)` still prevents conflicting memberships
- Frontend can suggest canonical types while allowing custom values

**Implementation**:
- Naming convention: lowercase with underscores (e.g., `'specialty_class'`)
- Validation: Frontend suggests canonical types, allows free-text entry
- Database: Unique partial index on `(client_id, plan_type)` where `status = 'active'`
- API documentation lists canonical types with "(recommended)" label

**Consequences**:
- Positive: Gyms can model their specific offerings without waiting for platform updates
- Positive: No schema migrations needed to add new plan types
- Negative: No compile-time type safety for plan_type values
- Negative: Risk of inconsistent naming (e.g., "gym_access" vs "GymAccess" vs "gym-access")
- Mitigation: Frontend validation suggests canonical types, enforces naming convention

### 9.3 Data Model & Storage

#### ADR-006: Hybrid SQL + NoSQL Storage

**Status**: Approved
**Date**: 2026-01-19

**Context**: Different data types have different access patterns and requirements.

**Decision**: Use hybrid storage strategy:
- **SQL** (PostgreSQL): Relational data (gyms, clients, programs, workouts)
- **NoSQL** (MongoDB/DynamoDB): Configuration, metering, trainer availability
- **Object Storage** (S3/Azure Blob): Photos, PDFs

**Rationale**:
- SQL provides ACID guarantees for transactional data
- NoSQL offers flexibility for evolving schemas (feature flags, metering)
- Object storage optimized for binary data

**Consequences**:
- Positive: Optimal performance for each data type
- Negative: More complex infrastructure
- Negative: Need to manage consistency across storage systems

#### ADR-007: Soft Delete with Anonymization

**Status**: Approved
**Date**: 2026-01-19

**Context**: Comply with "Right to Be Forgotten" while maintaining audit trails and payment history.

**Decision**: Implement soft delete with PII anonymization:
- Set `client_status = 'deleted'`, `deleted = true`
- Replace PII with "Deleted User #{member_number}"
- Keep payment history for 7 years (tax/legal requirement)
- Never hard delete records

**Rationale**:
- Maintains referential integrity
- Complies with GDPR/CCPA data deletion requirements
- Preserves audit trail and financial records
- Protects against accidental data loss

**Consequences**:
- Positive: Compliance with privacy regulations
- Positive: Preserves business records
- Negative: Deleted records still consume storage
- Negative: Queries must filter out `deleted = true` records

### 9.4 Authentication & Security

#### ADR-008: OAuth2 with Multiple Grant Types

**Status**: Approved (with deprecation notice)
**Date**: 2026-01-19

**Context**: Need flexible authentication for web, mobile, and third-party integrations.

**Decision**: Support multiple OAuth2 2.0 grant types:
- ⚠️ **Password grant** (DEPRECATED in OAuth 2.1) - for first-party clients only
- **Authorization code + PKCE** (PREFERRED) - for web and mobile apps
- **Refresh token** - for token renewal
- **Client credentials** - for server-to-server

**Migration Plan**: Transition to authorization_code + PKCE by Q2 2026.

**Rationale**:
- OAuth2 is industry standard
- Password grant provides simple auth for MVP (first-party apps only)
- Authorization code + PKCE more secure for production
- Client credentials enables third-party integrations

**Consequences**:
- Positive: Standards-compliant authentication
- Negative: Password grant is deprecated and less secure
- Action Required: Migrate to authorization_code + PKCE

#### ADR-009: Argon2id for Password Hashing

**Status**: Approved
**Date**: 2026-01-19

**Context**: Need secure password storage resistant to brute-force attacks.

**Decision**: Use Argon2id with parameters:
- 64 MB memory
- 3 iterations
- 4 threads
- 128-bit random salt (automatic)

**Rationale**:
- Winner of Password Hashing Competition (2015)
- Memory-hard algorithm resists GPU/ASIC attacks
- Recommended by OWASP
- Auto-handles salting

**Consequences**:
- Positive: State-of-the-art password security
- Negative: Higher CPU/memory usage than bcrypt (acceptable trade-off)

#### ADR-010: Role-Based MFA Requirements

**Status**: Approved
**Date**: 2026-01-19

**Context**: Balance security with user experience.

**Decision**: MFA requirements by role:
- **Admin/Trainer**: Required after 7-day grace period
- **Client**: Optional (user choice)

**Supported Methods**: TOTP (preferred), Email (fallback), Passkey-only (most secure)
**NOT Supported**: SMS (insecure due to SIM swap attacks)

**Rationale**:
- Admin/trainers have access to sensitive client data
- Clients typically lower-value targets
- 7-day grace period allows setup without blocking access
- SMS MFA vulnerable to attacks

**Consequences**:
- Positive: Strong security for privileged accounts
- Positive: Flexible security for clients
- Negative: Some users may resist MFA setup

### 9.5 Offline-First Strategy

#### ADR-011: Offline-First Mobile, Online-Only Web

**Status**: Approved
**Date**: 2026-01-19

**Context**: Trainers on gym floor may have unreliable connectivity; admins typically on stable connections.

**Decision**:
- **Mobile apps** (iOS/Android): Full offline capability
- **Web app**: Online-only

**Offline-Capable Operations** (mobile only):
- Check-in clients, log workouts, add/edit clients
- View cached schedules, programs, client history (last 30 days)

**Online-Only Operations** (all platforms):
- Admin functions, program creation, reports, billing

**Rationale**:
- Critical operations (workout logging) must work offline
- Improves UX and reliability on gym floor
- Web users (admins) on stable connections don't need offline mode
- Reduces complexity of web app

**Consequences**:
- Positive: Reliable mobile experience
- Positive: Trainers never blocked by connectivity
- Negative: Complex sync logic required
- Negative: Potential for conflicts

#### ADR-012: Idempotency Keys for Offline Sync

**Status**: Approved
**Date**: 2026-01-19

**Context**: Offline operations may be retried multiple times when syncing.

**Decision**: Require idempotency keys (UUIDv4) for all state-changing operations (POST/PUT/PATCH/DELETE).

**Server stores idempotency records for 24 hours**:
- Key + request hash + response
- Duplicate requests return cached response

**Rationale**:
- Prevents duplicate operations from network retries
- Standard pattern for distributed systems
- Crucial for offline-first architecture

**Consequences**:
- Positive: Reliable sync without duplicates
- Negative: Additional storage for idempotency records
- Negative: Clients must generate and track keys

### 9.6 Compliance & Privacy

#### ADR-013: US-Only Launch, GDPR Deferred

**Status**: Approved
**Date**: 2026-01-19

**Context**: Compliance requirements vary by region.

**Decision**: Launch US-only, comply with CCPA/COPPA. Defer GDPR compliance until international expansion.

**CCPA Compliance**:
- Privacy policy, data export, right to deletion
- "Do Not Sell" (platform does not sell data)

**COPPA Compliance**:
- <13: Must be sub-members (no independent accounts)
- 13-17: Login with parental consent
- 18+: Full independent accounts

**Rationale**:
- Simplifies initial launch
- CCPA requirements mostly met by existing features
- GDPR requires additional infrastructure (EU data residency, DPAs, etc.)

**Consequences**:
- Positive: Faster time to market
- Negative: Cannot serve EU customers initially
- Action Required: Implement GDPR before international expansion

#### ADR-014: 3-Year Data Retention for Inactive Clients

**Status**: Approved
**Date**: 2026-01-19

**Context**: Balance data retention for analytics vs. privacy obligations.

**Decision**: Retain workout/client data for:
- **Active clients**: Unlimited
- **Inactive clients** (3+ years no activity): Purge and anonymize
- **Payment data**: 7 years (tax/legal requirement)

**Rationale**:
- 3 years allows clients to return without losing history
- Meets privacy best practices
- Payment retention required by tax law

**Consequences**:
- Positive: Balances utility and privacy
- Negative: Automated purge process required
- Action Required: Implement scheduled anonymization job

### 9.7 Accessibility

#### ADR-015: WCAG 2.1 Level AA Compliance

**Status**: Approved
**Date**: 2026-01-19

**Context**: Ensure platform accessible to users with disabilities.

**Decision**: Achieve WCAG 2.1 Level AA compliance for all user-facing applications (web, iOS, Android).

**Key Requirements**:
- Color contrast: 4.5:1 (normal text), 3:1 (large text)
- Full keyboard navigation
- Screen reader support (VoiceOver, TalkBack, NVDA/JAWS)
- Text scaling up to 200%

**Testing**:
- Automated: axe DevTools, Lighthouse (target 100 score)
- Manual: Keyboard-only, screen reader testing
- User testing with actual assistive technology users

**Rationale**:
- Legal requirement (ADA compliance)
- Expands addressable market
- Right thing to do

**Consequences**:
- Positive: Accessible to all users
- Positive: Improved UX for everyone
- Negative: Additional development and testing effort
- Action Required: Accessibility training for team

### 9.8 Technical Implementation

#### ADR-017: Custom OAuth Implementation

**Status**: Approved
**Date**: 2026-01-19

**Context**: Need authentication system for web and mobile applications.

**Decision**: Implement custom OAuth2 server using well-known, battle-tested libraries rather than third-party authentication services.

**Rationale**:
- Full control over authentication flow and user data
- No vendor lock-in to Auth0, Firebase, or similar services
- Lower long-term costs (no per-user fees)
- Flexibility to customize authentication requirements
- Can leverage existing OAuth2 libraries (e.g., oauth2-server, passport, etc.)

**Consequences**:
- Positive: Complete control over authentication architecture
- Positive: No monthly SaaS fees based on user count
- Positive: Can customize flows for specific requirements
- Negative: More initial development effort
- Negative: Responsibility for security updates and maintenance
- Action Required: Select and implement OAuth2 library for chosen backend framework

#### ADR-018: Exercise Library Seeding Strategy

**Status**: Approved
**Date**: 2026-01-19

**Context**: Need to provide initial exercise library while allowing gym customization.

**Decision**: Seed database with comprehensive library of well-known exercises. Allow gyms to add custom exercises specific to their facility or methodology.

**Seeded Library Includes**:
- Standard compound movements (squat, bench, deadlift, etc.)
- Isolation exercises (bicep curl, tricep extension, etc.)
- Cardio activities (running, cycling, rowing, etc.)
- Bodyweight exercises (push-up, pull-up, plank, etc.)
- Exercise metadata (muscle groups, equipment, difficulty level)

**Custom Exercise Features**:
- Gyms can create facility-specific exercises
- Custom exercises scoped to gym (not visible to other gyms)
- Same data model as seeded exercises
- Can mark custom exercises as "private" (trainer-only)

**Rationale**:
- Immediate value for new gyms (don't start with empty library)
- Reduces friction in onboarding process
- Standardized exercise names improve cross-gym analytics
- Flexibility for specialized training methodologies
- Maintains data quality while allowing customization

**Consequences**:
- Positive: New gyms can start using platform immediately
- Positive: Consistent exercise naming across platform
- Positive: Supports specialized gyms (CrossFit, powerlifting, etc.)
- Negative: Need to maintain and update seeded exercise library
- Action Required: Curate initial exercise library with proper metadata

#### ADR-019: Digital Ocean Spaces for Media Storage

**Status**: Approved
**Date**: 2026-01-19

**Context**: Need object storage for progress photos, exercise images, and documents.

**Decision**: Use Digital Ocean Spaces for all media storage.

**Rationale**:
- Consistent with Digital Ocean hosting decision
- S3-compatible API (easy migration if needed)
- Competitive pricing ($5/mo for 250GB + 1TB transfer)
- CDN integration included
- Simple infrastructure management (single provider)

**Implementation**:
- Use signed URLs for secure direct uploads from mobile apps
- 30-day expiration on signed URLs
- Organize by: `{gym_id}/{client_id}/{media_type}/{timestamp}_{uuid}.{ext}`
- Enable CDN for fast global delivery
- Lifecycle policies for old media cleanup

**Consequences**:
- Positive: Cost-effective for initial deployment
- Positive: S3-compatible API allows future migration
- Positive: Built-in CDN reduces latency
- Negative: Vendor coupling to Digital Ocean ecosystem
- Mitigation: S3-compatible API ensures portability

### 9.9 Mobile Architecture

#### ADR-020: Native Mobile SDKs

**Status**: Approved
**Date**: 2026-01-19

**Context**: Need to choose mobile development framework for iOS and Android apps.

**Decision**: Build separate native applications using Swift (iOS) and Kotlin (Android).

**Rationale**:
- **Entitlements access required**: Need deep integration with HealthKit (iOS) and Health Connect (Android)
- **Performance**: Native apps provide best performance for offline-first architecture
- **Platform features**: Full access to latest iOS/Android features without framework lag
- **User experience**: Native UI components provide best platform-specific UX
- **App Store compliance**: Easier to meet App Store and Play Store requirements

**Consequences**:
- Positive: Full access to platform entitlements (HealthKit, Health Connect)
- Positive: Best performance and user experience
- Positive: Access to latest platform features immediately
- Negative: Two separate codebases to maintain
- Negative: Higher development effort than cross-platform
- Mitigation: Share API client logic, documentation, and testing strategies

#### ADR-021: Native Push Notification Providers

**Status**: Approved
**Date**: 2026-01-19

**Context**: Need push notification infrastructure for session reminders and updates.

**Decision**: Use native push notification providers:
- **iOS**: Apple Push Notification Service (APNs) directly
- **Android**: Firebase Cloud Messaging (FCM)

**Rationale**:
- No additional third-party service fees (OneSignal, Pusher, etc.)
- Direct integration provides best reliability
- Lower complexity (no vendor abstraction layer)
- APNs and FCM are free for standard usage
- Native apps already integrate easily with these services

**Implementation**:
- Backend sends to both APNs and FCM based on device registration
- Store device tokens in `device_tokens` table with platform identifier
- Handle token refresh and expiration
- Support notification preferences per user

**Consequences**:
- Positive: No monthly push notification service fees
- Positive: Direct control over notification delivery
- Positive: Best reliability and performance
- Negative: Need to implement backend logic for both APNs and FCM
- Negative: More complex backend implementation than unified service
- Action Required: Implement APNs and FCM backend integration

#### ADR-022: Anthropic AI Provider with Provider Abstraction

**Status**: Approved
**Date**: 2026-01-19

**Context**: Need AI provider for workout summaries and future intelligent features.

**Decision**: Use Anthropic Claude as primary AI provider with abstraction layer to support provider switching.

**Architecture**:
- Abstract AI service interface in backend
- Initial implementation uses Anthropic Claude API
- Configuration allows switching to OpenAI, Google, or other providers
- Prompt templates versioned separately from provider implementation

**Rationale**:
- Anthropic Claude excels at structured analysis and summaries
- Provider abstraction prevents vendor lock-in
- Can switch based on cost, performance, or feature requirements
- Can A/B test different providers
- Future-proof for emerging AI providers

**Consequences**:
- Positive: Flexibility to switch providers based on needs
- Positive: Can optimize costs by choosing best provider per use case
- Positive: Not locked into single AI vendor
- Negative: Abstraction layer adds initial development complexity
- Negative: Need to maintain compatibility layer
- Action Required: Design AI service abstraction interface

#### ADR-023: Custom REST Batch Sync Protocol

**Status**: Approved
**Date**: 2026-01-19

**Context**: Need efficient sync protocol for offline-first mobile apps.

**Decision**: Implement custom RESTful batch sync protocol leveraging existing idempotency infrastructure (ADR-012).

**Architecture**:
- **Upload changes**: `POST /api/v1/sync/batch` with array of offline operations
- **Download updates**: `GET /api/v1/{resource}?since={timestamp}` for delta queries
- **Conflict resolution**: Last-write-wins using `updated_at` timestamps
- **Idempotency**: Reuse existing UUIDv4 keys to prevent duplicate operations
- **Change tracking**: All entities include `updated_at` timestamp for sync

**Sync Flow**:
1. Mobile app tracks offline changes in local queue
2. On connectivity, upload all changes via batch endpoint
3. Server processes with idempotency protection
4. Download updates for each entity type since last sync
5. Merge changes locally (server wins on conflicts)

**Rationale**:
- Builds on existing RESTful API and idempotency foundation
- Native mobile SDKs work well with REST (URLSession, Retrofit)
- Simpler than GraphQL subscriptions or CRDTs for MVP
- Batch operations reduce network round-trips
- Last-write-wins is simple and predictable for users
- Allows incremental complexity (GraphQL in Phase 3)

**Consequences**:
- Positive: Leverages existing API infrastructure
- Positive: Simple conflict resolution (predictable for users)
- Positive: Efficient batching reduces mobile data usage
- Negative: Last-write-wins can lose data in rare concurrent edit scenarios
- Mitigation: Show "last synced" timestamp to users
- Future Enhancement: GraphQL in Phase 3 for flexible querying

---

## 10. Repository Structure

The platform uses a **polyrepo architecture** with 8 separate repositories providing independent release cycles, clear ownership boundaries, and faster CI/CD pipelines.

### 10.1 Repository Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         gym-docs                                 │
│  (Source of truth: requirements, specs, API docs)               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ references
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         gym-api                                  │
│  (Backend: API server, database, business logic)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ generates OpenAPI spec
                              ▼
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
          ┌──────────────────┐  ┌──────────────────┐
          │  gym-sdk-python  │  │  gym-sdk-kotlin  │
          └──────────────────┘  └──────────────────┘
                    │                   │
                    │                   │
                    ▼                   ▼
          ┌──────────────────┐  ┌──────────────────┐
          │   gym-app-web    │  │  gym-app-android │
          └──────────────────┘  └──────────────────┘

                    ┌──────────────────┐
                    │  gym-sdk-swift   │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   gym-app-ios    │
                    └──────────────────┘
```

### 10.2 Repository List

| # | Repository Name | Purpose | Primary Language | Visibility |
|---|----------------|---------|------------------|------------|
| 1 | `gym-docs` | Documentation & specifications | Markdown | Private |
| 2 | `gym-api` | Backend API server & data model | Python + FastAPI | Private |
| 3 | `gym-sdk-python` | Python SDK for API | Python | Private (Public later) |
| 4 | `gym-sdk-kotlin` | Kotlin SDK for Android | Kotlin | Private (Public later) |
| 5 | `gym-sdk-swift` | Swift SDK for iOS | Swift | Private (Public later) |
| 6 | `gym-app-web` | Web application (admin/trainer) | Next.js + TailwindCSS + d3.js | Private |
| 7 | `gym-app-android` | Android mobile app (client/trainer) | Kotlin | Private |
| 8 | `gym-app-ios` | iOS mobile app (client/trainer) | Swift | Private |

### 10.3 Branching Strategy

#### Branch Types

| Branch Type | Naming Convention | Purpose | Protected? |
|-------------|-------------------|---------|------------|
| Main | `main` | Production-ready code | ✅ Yes |
| Development | `develop` (optional) | Integration branch for next release | ✅ Yes |
| Feature | `feature/<ticket-id>-<description>` | New features | No |
| Bugfix | `bugfix/<ticket-id>-<description>` | Bug fixes | No |
| Hotfix | `hotfix/<ticket-id>-<description>` | Emergency production fixes | No |
| Release | `release/v<version>` | Release preparation | ✅ Yes |

#### Commit Message Convention

Use **Conventional Commits** format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Add or update tests
- `chore`: Build process, dependencies, tooling
- `ci`: CI/CD changes

**Examples**:
```
feat(workouts): add workout analytics dashboard
fix(auth): resolve OAuth2 token refresh race condition
docs(api): update authentication guide with passkey examples
chore(deps): upgrade React to 18.3.0
```

### 10.4 Version Management

All repositories follow **Semantic Versioning 2.0.0**:

```
MAJOR.MINOR.PATCH

Example: v1.2.3
```

**Version Bump Rules**:
- **MAJOR**: Breaking API changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

#### Versioning Strategy by Repo

| Repo | Versioning Strategy | Example Tags |
|------|---------------------|--------------|
| gym-api | Semantic versioning | v1.0.0, v1.1.0, v2.0.0 |
| gym-sdk-* | Match API version + SDK patch | v1.0.0, v1.0.1 (SDK bug fix) |
| gym-app-* | Independent semantic versioning | v1.0.0, v1.5.0, v2.0.0 |
| gym-docs | Date-based or semantic | v2024.01.15 or v1.0.0 |

---

**End of Technical Specifications**

This document should be updated as technical decisions are made and implementation details are finalized. All developers must review this specification before beginning work on authentication, data models, or API endpoints.
