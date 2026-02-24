# Data Layer Architecture

This document defines the storage strategy and database architecture.

---

## Storage Strategy (PostgreSQL + Redis)

The system uses PostgreSQL as the primary database with Redis for caching and coordination.

---

## PostgreSQL (System of Record)

Use **PostgreSQL** as the authoritative system of record for all data:

| Category | Data |
|----------|------|
| **User & Auth** | users, roles, sessions, MFA credentials, OAuth2 clients/tokens |
| **Organizational Hierarchy** | gyms, locations, accounts, clients, trainers |
| **Membership & Billing** | plan templates, client memberships, plan assignments |
| **Scheduling & Check-ins** | schedule bookings, check-in events, trainer availability |
| **Training Data** | programs, program days, exercises, workouts, sets, measurements |
| **Configuration** | gym settings, plan limits, feature flags |
| **Usage Metering** | API call counts, usage rollups (time-series in PostgreSQL) |
| **Analytics** | Pre-computed aggregates, dashboard metrics |
| **Audit & Compliance** | audit logs, change tracking, event history |

**Rationale**: PostgreSQL provides ACID guarantees, foreign key constraints, complex joins, and transactional integrity. Using a single database simplifies operations, eliminates cross-database consistency issues, and reduces infrastructure complexity.

### PostgreSQL Features Used

- **JSONB columns**: For flexible configuration data (gym settings, plan limits, feature flags)
- **Partitioning**: For time-series data (usage metrics, analytics)
- **Full-text search**: For client/exercise search
- **Row-level security**: For multi-tenant isolation (if needed)

---

## Redis (Ephemeral Performance & Coordination Layer)

Use **Redis** as a cache-aside and coordination layer for performance optimization and rate limiting:

| Use Case | Details |
|----------|---------|
| **Cache-Aside Reads** | Plan limits, trainer availability, "today's schedule", dashboard widgets |
| **Derived Aggregates** | Busyness time-slot calculations (15-min granularity), client analytics summaries |
| **Rate Limiting** | Login attempts, password resets, API throttles (per-user, per-gym) |
| **Idempotency Keys** | 24-hour TTL for deduplication |
| **Distributed Locks** | Short-lived locks for scheduling/booking to prevent double-booking |

### Cache Key Patterns

```
gym:{gym_id}:plan_limits          # 5-15 minute TTL
trainer:{trainer_id}:availability  # 1-5 minute TTL
schedule:{date}:{location_id}     # 1-5 minute TTL
```

### Design Assumptions

- **Redis is ephemeral**: All cached data has a source of truth in PostgreSQL
- **Cache misses are not failures**: Trigger recomputation and cache population
- **System must function without Redis**: The system must remain fully functional if Redis is flushed or restarted

---

## Binary Storage

Store large binaries (photos, signed PDFs) in object storage; store references/metadata in PostgreSQL.

**Implementation**: Use object storage (S3/similar) with CDN for serving. Store only URLs and metadata in the database.

---

## Database Responsibilities

### OLTP Schema
- Transactional operations with immediate consistency requirements
- User-facing read/write operations
- Real-time data access for mobile and web apps

### Event/Audit Tables
- History tracking for compliance
- Audit logging for security
- Change tracking for business analytics

### Derived Aggregates
- Pre-calculated metrics for dashboard performance
- Busyness calculations (15-minute granularity)
- Adherence tracking
- PR rollups

---

## Data Migration Strategy

For entities previously designated for MongoDB (GymPlanLimits, PlanTemplate, UsageMetricRollup, TrainerAvailability):

| Entity | PostgreSQL Approach |
|--------|---------------------|
| **GymPlanLimits** | JSONB column in `gyms` table for flexible limits/features |
| **PlanTemplate** | Standard PostgreSQL table with JSONB for flexible config |
| **UsageMetricRollup** | Time-partitioned PostgreSQL table |
| **TrainerAvailability** | Normalized PostgreSQL tables or JSONB column |
| **GymAnalytics** | Time-partitioned PostgreSQL table |

---

## Related Documents

- [Entities](entities/) - Domain entity definitions
- [Auth](02-auth.md) - Authentication and authorization
