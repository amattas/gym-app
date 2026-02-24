# Performance Requirements

This document defines performance targets and requirements.

---

## API Latency Targets

### Real-time Operations (User Waiting)

Operations where users are actively waiting and delays are immediately noticeable.

| Operations | p95 | p99 |
|------------|-----|-----|
| Authentication (login, token refresh) | < 200ms | < 500ms |
| Workout logging (start, log set, complete) | < 200ms | < 500ms |
| Scheduling (check availability, book) | < 200ms | < 500ms |
| Check-in operations | < 200ms | < 500ms |

### Dashboard/Reporting Operations

Operations where users expect some delay but need results within reasonable timeframe.

| Operations | p95 | p99 |
|------------|-----|-----|
| Analytics queries | < 1s | < 2s |
| Trainer dashboards | < 1s | < 2s |
| Client progress reports | < 1s | < 2s |
| Workout history | < 1s | < 2s |

### Background Operations (Async)

Operations that run asynchronously with no immediate user feedback.

| Operations | Target |
|------------|--------|
| AI summary generation | Best effort |
| Usage metering rollups | Best effort |
| Email/push notifications | Best effort |

---

## Database Performance

### Query Guidelines

- All queries should use indexes
- Avoid N+1 query patterns
- Use connection pooling
- Implement query timeouts (30s default)

### Index Requirements

| Table | Indexed Columns |
|-------|-----------------|
| clients | gym_id, status, trainer_id |
| workouts | client_id, started_at |
| schedules | trainer_id, scheduled_start |
| check_ins | location_id, checked_in_at |

### Connection Limits

| Environment | Max Connections |
|-------------|-----------------|
| Production | 100 |
| Staging | 25 |
| Development | 10 |

---

## Caching Strategy

### Cache Layers

1. **Application Cache** (Redis)
   - Session data
   - Computed values
   - Rate limiting counters

2. **CDN Cache**
   - Static assets
   - Images/media
   - Calendar feeds

### Cache TTLs

| Data Type | TTL |
|-----------|-----|
| Gym plan limits | 5-15 minutes |
| Trainer availability | 1-5 minutes |
| Schedule data | 1-5 minutes |
| Static assets | 1 hour - 1 week |

---

## Scalability Targets

### Phase 1 (MVP)
- 10 concurrent gyms
- 1,000 total users
- 100 requests/second

### Phase 2
- 100 concurrent gyms
- 10,000 total users
- 500 requests/second

### Phase 3+
- 1,000+ concurrent gyms
- 100,000+ total users
- 2,000+ requests/second

---

## Mobile Performance

### App Launch Time
- Cold start: < 3 seconds
- Warm start: < 1 second

### Offline Support (Phase 3)
- Cache current program locally
- Queue workout logs for sync
- Sync within 30 seconds when online

### Data Usage
- Minimize API payload sizes
- Use pagination for lists
- Compress images before upload

---

## Monitoring & Alerts

### Key Metrics
- API response times (p50, p95, p99)
- Error rates (4xx, 5xx)
- Database query times
- Cache hit rates

### Alert Thresholds
| Metric | Warning | Critical |
|--------|---------|----------|
| p99 latency | > 500ms | > 2s |
| Error rate | > 1% | > 5% |
| Database CPU | > 70% | > 90% |
