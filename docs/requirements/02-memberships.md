# Memberships & Plans

This document defines plan templates, memberships, and visit entitlements.

---

## PlanTemplate (Membership Plans)

**Definition**: A gym's sellable membership plan definition (what clients buy). Drives module enablement, visit entitlements, and payment structure.

### Plan Types

| Type | Description |
|------|-------------|
| `gym_access` | General gym access |
| `personal_training` | One-on-one training sessions |
| `group_classes` | Group fitness classes |

**Constraint**: Client can only have ONE active membership per `plan_type`

### Visit Entitlement Models

| Model | Description |
|-------|-------------|
| `unlimited` | No visit limits |
| `per_week` | X visits per week (e.g., 3x/week) |
| `per_month` | X visits per month (e.g., 8/month) |
| `per_plan_duration` | Total visits over plan lifetime (e.g., 10-pack training) |

### Plan Duration

| Type | Description |
|------|-------------|
| `month` / `year` | Time-based plans with specific duration |
| `until_used` | No fixed end date, expires when visits consumed or expiration period reached |

### Payment Configuration

| Frequency | Description |
|-----------|-------------|
| `one_time` | Single payment (e.g., 10-pack sessions) |
| `monthly` | Recurring monthly payment |
| `annually` | Recurring annual payment |

### Processing Fees

| Handling | Description |
|----------|-------------|
| `gym_absorbs` | Gym pays all Stripe processing fees |
| `pass_to_client` | Fees added to client invoice (percentage/flat/both) |

### Modules Enabled (per plan)

- Programming (custom workout programs)
- Progress photos
- Health integrations (Apple Health, Google Fit)
- Self-scheduling

### Add-on Plans (Family Discounts)

- Add-on plans can only be assigned to members in an account with a required base plan
- Example: "Family Member Training Add-On" at 50% off, requires primary member to have personal training plan
- If primary cancels base plan → all linked addon plans also cancel

---

## Example Plan Templates

### 10-Pack Personal Training (Session Pack)
- Plan type: `personal_training`
- Visit entitlement: 10 visits over plan duration
- Duration: Until used (expires in 180 days if not consumed)
- Payment: One-time $500

### Monthly Unlimited Gym Access
- Plan type: `gym_access`
- Visit entitlement: Unlimited
- Duration: 1 month, auto-renews
- Payment: $199/month recurring

### Annual 3x/Week Training with Monthly Billing
- Plan type: `personal_training`
- Visit entitlement: 3 visits per week, no rollover
- Duration: 1 year
- Payment: $150/month (12 months)

### Family Member Training Add-On (50% discount)
- Plan type: `personal_training`
- Is addon: Yes, requires primary member with personal training plan
- Visit entitlement: 2 visits per week
- Duration: 1 month
- Payment: $75/month (50% off base price)

---

## ClientMembership

**Definition**: An active or historical membership linking a client to a plan template. Tracks visit entitlements, payment status, and membership lifecycle.

### Membership Status

| Status | Description |
|--------|-------------|
| `active` | Currently active, client can use services |
| `paused` | Temporarily paused (extends expiration date) |
| `expired` | Ended naturally (time or visits exhausted) |
| `canceled` | Gym-initiated cancellation |

### Visit Tracking

- Tracks current period (week/month) visit usage
- Tracks total remaining visits (for until-used plans)
- Supports rollover (if plan allows)
- Automatically resets periods based on plan configuration

### Pause Functionality

- Only gym admin/trainer can pause
- Pausing extends expiration date by days paused
- Useful for injuries, vacations, etc.

### Cancellation

- Only gym admin can cancel (clients cannot self-cancel)
- Recurring subscriptions: remain active until period end
- One-time/session packs: canceled immediately, remaining visits forfeited

---

## Membership Lifecycle Workflows

### Membership Creation

1. Gym assigns a plan to a client → ClientMembership created with `status = 'active'`
2. System validates: client cannot have another active membership of the same `plan_type`
3. Set `started_at` to current timestamp
4. Calculate `expires_at` based on `plan_duration` (null for `until_used` without expiration)
5. Initialize visit entitlement tracking

### Visit Deduction

When a client checks in / workout starts:
1. Determine which active membership(s) apply (based on plan_type and schedule context)
2. If visit entitlement is limited (not unlimited):
   - Check if visits remain in current period or total (for until_used)
   - Deduct 1 from visits used
   - Reject check-in if no visits remain
3. If unlimited: allow check-in without deduction

### Period Resets

- For `per_week` entitlements: reset visits used every week on configured day (e.g., Monday)
- For `per_month` entitlements: reset on the monthly anniversary of `started_at`
- If `rollover_enabled = true`: carry unused visits to next period (up to configured max)
- If `rollover_enabled = false`: reset to plan's default count

### Pause/Unpause

**On pause**:
1. Set `status = 'paused'`
2. Record `paused_at` timestamp and who paused it

**On unpause**:
1. Calculate days paused = (unpause_timestamp - paused_at)
2. Add days paused to `expires_at` (extends expiration)
3. Adjust period end dates if necessary
4. Set `status = 'active'`

### Cancellation

**For recurring subscriptions**:
1. Set `cancels_at_period_end = true`
2. Membership remains `active` until `expires_at`
3. Cancel Stripe subscription with `at_period_end = true`
4. After expiration, status becomes `expired`

**For one-time/until-used plans**:
1. Set `status = 'canceled'` immediately
2. Remaining visits are forfeited (gym can issue manual refund if desired)

### Expiration

- Nightly job (scheduled using `Gym.timezone`) checks for memberships where `current_time > expires_at`
- Set `status = 'expired'`
- Client loses access to plan modules and visit entitlements

### Processing Fees

**When `processing_fee_handling = 'pass_to_client'`**:
- Calculate fee based on plan's `processing_fee_config`
- Add fee to invoice/payment intent
- Record actual amounts charged

**When `processing_fee_handling = 'gym_absorbs'`**:
- Gym pays full Stripe fees
- Client pays only the plan amount

---

## Related Documents

- [Entities](01-entities.md) - Account and Client entities
- [Scheduling](04-scheduling.md) - Check-in and visit tracking
