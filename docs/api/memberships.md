# Memberships & Plans API

Membership and plan management endpoints.

---

## Plan Templates

### List Plan Templates

```http
GET /gyms/{gym_id}/plan-templates
```

### Create Plan Template

```http
POST /gyms/{gym_id}/plan-templates
```

**Request**:
```json
{
  "name": "Monthly Gym Access",
  "description": "Unlimited gym access",
  "plan_type": "gym_access",
  "visit_entitlement": {
    "type": "unlimited"
  },
  "plan_duration": {
    "type": "month",
    "value": 1
  },
  "payment_config": {
    "frequency": "monthly",
    "amount": 99.00,
    "currency": "USD"
  },
  "modules_enabled": {
    "programming": true,
    "progress_photos": true
  }
}
```

### Get Plan Template

```http
GET /plan-templates/{plan_template_id}
```

### Update Plan Template

```http
PATCH /plan-templates/{plan_template_id}
```

### Deactivate Plan Template

```http
POST /plan-templates/{plan_template_id}/deactivate
```

---

## Client Memberships

### List Client Memberships

```http
GET /clients/{client_id}/memberships
```

### Assign Membership

```http
POST /clients/{client_id}/memberships
```

**Request**:
```json
{
  "plan_template_id": "uuid",
  "started_at": "2026-01-15T00:00:00Z"
}
```

### Get Membership

```http
GET /memberships/{membership_id}
```

### Get Membership Entitlements

```http
GET /memberships/{membership_id}/entitlements
```

**Response**:
```json
{
  "data": {
    "visits_allowed_this_period": 12,
    "visits_used_this_period": 5,
    "visits_remaining_this_period": 7,
    "period_ends_at": "2026-01-31T23:59:59Z",
    "total_visits_remaining": null
  }
}
```

### Pause Membership

```http
POST /memberships/{membership_id}/pause
```

**Request**:
```json
{
  "reason": "Vacation"
}
```

### Unpause Membership

```http
POST /memberships/{membership_id}/unpause
```

### Cancel Membership

```http
POST /memberships/{membership_id}/cancel
```

**Request**:
```json
{
  "reason": "Moving away",
  "cancel_immediately": false
}
```

---

## Visit Tracking

### Record Visit

```http
POST /memberships/{membership_id}/visits
```

Called automatically on check-in, or manually.

### Get Visit History

```http
GET /memberships/{membership_id}/visits
```

---

## Billing (Phase 4)

### Get Payment History

```http
GET /memberships/{membership_id}/payments
```

### Retry Failed Payment

```http
POST /memberships/{membership_id}/payments/retry
```
