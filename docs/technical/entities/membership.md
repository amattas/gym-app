# Membership Entities

All entities stored in PostgreSQL.

---

## PlanTemplate

**Purpose**: A gym's sellable membership plan definition.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `plan_template_id` | UUID | Primary key |
| `gym_id` | UUID | FK to Gym |
| `name` | string | Plan name |
| `description` | text? | Plan description |
| `plan_type` | enum | 'gym_access', 'personal_training', 'group_classes' |
| `status` | enum | 'active', 'inactive' |

### Visit Entitlement (JSONB)

```json
{
  "type": "per_week",      // per_week, per_month, per_plan_duration, unlimited
  "count": 3,              // null for unlimited
  "rollover_enabled": false
}
```

### Plan Duration (JSONB)

```json
{
  "type": "month",           // month, year, until_used
  "value": 1,                // e.g., 12 for 12 months
  "until_used_expiration_days": 180  // optional expiration for until_used
}
```

### Payment Configuration (JSONB)

```json
{
  "frequency": "monthly",     // one_time, monthly, annually
  "amount": 150.00,
  "currency": "USD",
  "stripe_price_id": "price_xxx",
  "processing_fee_handling": "gym_absorbs",  // or pass_to_client
  "processing_fee_config": {
    "fee_type": "percentage_plus_flat",
    "percentage": 2.9,
    "flat_amount": 0.30
  }
}
```

### Modules Enabled (JSONB)

```json
{
  "programming": true,
  "progress_photos": true,
  "health_integrations": false,
  "self_scheduling": false
}
```

### Add-on Configuration

| Field | Type | Description |
|-------|------|-------------|
| `is_addon` | bool | Is this an add-on plan? |
| `requires_primary_plan_type` | string? | Required base plan type |
| `addon_discount_percentage` | decimal? | Discount percentage |

---

## ClientMembership

**Purpose**: Active or historical membership linking client to plan.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `client_membership_id` | UUID | Primary key |
| `client_id` | UUID | FK to Client |
| `plan_template_id` | UUID | FK to PlanTemplate |
| `plan_type` | string | Denormalized for fast queries |
| `status` | enum | 'active', 'paused', 'expired', 'canceled' |
| `started_at` | datetime | When membership started |
| `expires_at` | datetime? | When membership expires |

### Pause Information (JSONB)

```json
{
  "paused_at": "2024-01-15T00:00:00Z",
  "paused_by_user_id": "uuid",
  "pause_reason": "Vacation",
  "days_paused_total": 14
}
```

### Visit Entitlement Tracking (JSONB)

```json
{
  "current_period_start": "2024-01-01T00:00:00Z",
  "current_period_end": "2024-01-31T23:59:59Z",
  "visits_allowed_this_period": 12,
  "visits_used_this_period": 5,
  "total_visits_remaining": null  // for until_used plans only
}
```

### Cancellation Information (JSONB)

```json
{
  "canceled_at": "2024-01-20T00:00:00Z",
  "canceled_by_user_id": "uuid",
  "cancellation_reason": "Moving",
  "cancels_at_period_end": true
}
```

### Stripe Metadata (JSONB)

```json
{
  "stripe_subscription_id": "sub_xxx",
  "stripe_payment_intent_id": null,
  "last_payment_at": "2024-01-01T00:00:00Z",
  "last_payment_amount": 150.00,
  "last_processing_fee": 0.00
}
```

### Constraints

- Unique: (`client_id`, `plan_type`) WHERE `status = 'active'`
- Client can only have one active membership per plan_type

---

## GymPlanLimits

**Purpose**: Gym-level plan limits and feature flags.

### Storage Options

**Option 1**: JSONB column on Gym table
**Option 2**: Separate table with gym_id FK

### Structure

```json
{
  "gym_id": "uuid",
  "platform_plan_id": "pro",
  "effective_at": "2024-01-01T00:00:00Z",
  "limits": {
    "max_locations": 5,
    "max_trainers": 20,
    "max_clients": 500,
    "api_calls_per_month": 100000,
    "ai_api_calls_per_month": 1000
  },
  "features": {
    "self_scheduling_enabled": true,
    "progress_photos_enabled": true,
    "health_integrations_enabled": true,
    "esign_enabled": false,
    "custom_domains_enabled": false
  },
  "overrides": {}
}
```

### Caching

- Cache in Redis with 5-15 minute TTL
- Key: `gym:{gym_id}:plan_limits`
- Invalidate on plan changes
