# Analytics Entities

All entities stored in PostgreSQL.

---

## UsageMetricRollup

**Purpose**: Time-windowed rollups for gym usage metering (billing).

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `usage_rollup_id` | UUID | Primary key |
| `gym_id` | UUID | FK to Gym |
| `window_start` | datetime | Period start |
| `window_end` | datetime | Period end |
| `clients_count` | int | Client count in window |
| `locations_count` | int | Location count |
| `trainers_count` | int | Trainer count |
| `api_calls_count` | int | API calls |
| `ai_api_calls_count` | int | AI API calls |
| `computed_at` | datetime | When calculated |

### Implementation

- Use PostgreSQL table partitioned by time
- Compute nightly/hourly via background jobs
- Keep raw event logs for audit/reconciliation
- Archive after 1 year to cold storage

### Indexing

- Primary: `usage_rollup_id`
- Index: (`gym_id`, `window_start`)
- Partition by month on `window_start`

---

## WorkoutAnalytics

**Purpose**: Pre-calculated workout session metrics for dashboards.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `analytics_id` | UUID | Primary key |
| `workout_id` | UUID | FK to Workout |
| `client_id` | UUID | FK to Client (denormalized) |
| `computed_at` | datetime | When calculated |

### Volume & Intensity Metrics

| Field | Type | Description |
|-------|------|-------------|
| `total_weight_lifted_lbs` | decimal | Normalized to lbs |
| `total_reps` | int | Sum of all reps |
| `total_sets` | int | Count of sets |
| `duration_minutes` | int | ended_at - started_at |

### Completion Metrics

| Field | Type | Description |
|-------|------|-------------|
| `exercises_completed` | int | Completed exercises |
| `exercises_skipped` | int | Skipped exercises |
| `completion_rate` | decimal | completed / total |

### Performance Metrics

| Field | Type | Description |
|-------|------|-------------|
| `prs_achieved_count` | int | New PRs this workout |
| `volume_by_muscle_group` | JSON? | Volume breakdown |
| `intensity_score` | decimal? | Based on weight vs PR |

### Calculation Timing

- **Async**: After workout completion via background job
- **Real-time**: Current sets/reps displayed in UI (not persisted)

---

## GymAnalytics

**Purpose**: Admin dashboard metrics for gym business reporting.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `analytics_id` | UUID | Primary key |
| `gym_id` | UUID | FK to Gym |
| `period_start` | datetime | Period start |
| `period_end` | datetime | Period end |
| `period_type` | enum | 'day', 'week', 'month', 'quarter', 'year' |
| `computed_at` | datetime | When calculated |

### Revenue Metrics (JSONB)

```json
{
  "total_revenue": 15000.00,
  "new_revenue": 2500.00,
  "recurring_revenue": 12000.00,
  "churned_revenue": 500.00,
  "avg_revenue_per_client": 150.00
}
```

### Client Metrics (JSONB)

```json
{
  "total_clients": 100,
  "active_clients": 85,
  "new_clients": 12,
  "churned_clients": 3,
  "client_retention_rate": 97.0,
  "prospects_count": 15
}
```

### Engagement Metrics (JSONB)

```json
{
  "total_workouts": 450,
  "total_check_ins": 520,
  "avg_workouts_per_client": 5.3,
  "avg_session_duration_minutes": 52,
  "workout_completion_rate": 94.5
}
```

### Trainer Metrics (JSONB)

```json
{
  "total_trainers": 8,
  "active_trainers": 7,
  "avg_clients_per_trainer": 12.5,
  "trainer_utilization_rate": 78.5
}
```

### Implementation

- Nightly rollup jobs calculate previous day/week/month
- Partitioned by `period_start`
- Archive historical data after 1 year
- Cache current period in Redis for dashboard performance
