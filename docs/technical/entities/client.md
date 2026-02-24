# Account & Client Entities

All entities stored in PostgreSQL.

---

## Account

**Purpose**: Billing and access management entity. Represents a household, individual, or corporate account.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `account_id` | UUID | Primary key |
| `account_type` | enum | 'individual', 'family', 'corporate' |
| `billing_email` | string | Email for billing |
| `billing_address` | JSON | Structured address |
| `stripe_customer_id` | string? | Stripe customer ID |
| `deleted` | bool | Soft delete flag |

### Relationships

- Has many Clients (members)
- Can have multiple primary Clients
- Consolidated billing for all ClientMemberships

---

## Client

**Purpose**: Individual member/person within an Account.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `client_id` | UUID | Primary key |
| `account_id` | UUID | FK to Account |
| `member_role` | enum | 'primary' or 'member' |
| `client_status` | enum | 'prospect', 'trial', 'active', 'inactive', 'lost', 'deleted' |
| `date_of_birth` | date | Required for age-based rules |
| `relationship_to_primary` | string? | 'spouse', 'child', 'self', etc. |
| `primary_location_id` | UUID | FK to Location |
| `primary_trainer_id` | UUID? | FK to Trainer |
| `qr_code` | string | Unique code for scan check-in |
| `deleted` | bool | Soft delete flag |

### Behavioral Stats (derived)

| Field | Type | Description |
|-------|------|-------------|
| `avg_workout_duration_minutes` | float | Average session duration |
| `avg_schedule_variance_minutes` | float | Typical early/late arrival |

### AI Summary

| Field | Type | Description |
|-------|------|-------------|
| `ai_summary_latest` | text | Cached AI-generated summary |
| `ai_summary_updated_at` | datetime | When summary was generated |

### Relationships

- Belongs to Account
- May have one User (login)
- Has many ClientMemberships
- Has many GymCheckIns
- Has many ProgressPhotos
- Has many HealthMetricSamples
- Has many Workouts
- Has many ClientGoals
- Has many ClientMeasurements

---

## ProgressPhoto

**Purpose**: Client progress photos for visual tracking.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `progress_photo_id` | UUID | Primary key |
| `client_id` | UUID | FK to Client |
| `captured_at` | datetime | When photo was taken |
| `uploaded_at` | datetime | When uploaded |
| `photo_url` | string | CDN URL with signed access |
| `visibility` | enum | 'client_only', 'trainer', 'gym_admin' |
| `notes` | text? | Optional notes |
| `tags_json` | JSON? | Tags (cut, bulk, bodyweight, etc.) |

### Constraints

- Enforce access control by visibility + trainer assignment
- Store thumbnails for fast browsing

---

## HealthConnection

**Purpose**: Connection to external health data providers.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `health_connection_id` | UUID | Primary key |
| `client_id` | UUID | FK to Client |
| `provider` | enum | 'apple_health', 'google_fit', 'health_connect' |
| `status` | enum | 'connected', 'disconnected', 'error' |
| `connected_at` | datetime | When connected |
| `disconnected_at` | datetime? | When disconnected |
| `scopes_granted_json` | JSON | Which metrics permitted |
| `last_sync_at` | datetime | Last successful sync |

---

## HealthMetricSample

**Purpose**: Time-series health data imported from external providers.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `health_metric_sample_id` | UUID | Primary key |
| `client_id` | UUID | FK to Client |
| `provider` | enum | Source provider |
| `metric_type` | string | 'steps', 'active_energy', 'resting_hr', 'sleep_duration', 'weight', etc. |
| `start_at` | datetime | Sample start time |
| `end_at` | datetime? | Sample end time |
| `value` | decimal | Metric value |
| `unit` | string | Unit of measurement |
| `source_device` | string? | Device that recorded sample |
| `ingested_at` | datetime | When imported |

### Constraints

- Idempotency key for imports (provider_sample_id or hash)
- Prevents duplicate imports
