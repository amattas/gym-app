# Scalability & Reliability Requirements

This document defines scalability, availability, and infrastructure requirements.

---

## Availability Targets

### SLA by Tier

| Tier | Availability | Monthly Downtime |
|------|--------------|------------------|
| Standard | 99.5% | ~3.6 hours |
| Professional | 99.9% | ~43 minutes |
| Enterprise | 99.95% | ~22 minutes |

### By Component

| Component | Target |
|-----------|--------|
| API | 99.9% |
| Web App | 99.9% |
| Database | 99.95% |
| Background Jobs | 99.5% |

---

## Scalability Targets

### Phase 1 (MVP)
- 10 gyms
- 1,000 users
- 100 requests/second
- Single region

### Phase 2
- 100 gyms
- 10,000 users
- 500 requests/second
- Single region

### Phase 3+
- 1,000+ gyms
- 100,000+ users
- 2,000+ requests/second
- Multi-region (optional)

---

## Database Scaling

### PostgreSQL

**Vertical Scaling**:
- Start with db.r6g.large
- Scale to db.r6g.2xlarge as needed

**Read Replicas**:
- Add read replicas for reporting
- Route analytics queries to replicas

**Partitioning**:
- Time-partition large tables (workouts, check_ins)
- Partition by gym_id if needed

### Connection Pooling

- Use PgBouncer or similar
- Pool size: 100 connections max
- Connection timeout: 30 seconds

---

## Application Scaling

### Horizontal Scaling

- Stateless application servers
- Auto-scaling based on CPU/request count
- Minimum 2 instances for redundancy

### Auto-Scaling Rules

| Metric | Scale Up | Scale Down |
|--------|----------|------------|
| CPU | > 70% for 5 min | < 30% for 10 min |
| Request count | > 1000 req/min | < 200 req/min |

---

## Caching Strategy

### Redis

**Use Cases**:
- Session storage
- Rate limiting
- Computed values cache
- Distributed locks

**Scaling**:
- Start with single node
- Add read replicas for reads
- Redis Cluster for horizontal scaling

**High Availability**:
- Redis Sentinel for failover
- Or managed service (ElastiCache, Upstash)

---

## Background Jobs

### Queue System

- Use Redis-based queue (Bull, Sidekiq)
- Separate queues by priority
- Dead letter queue for failed jobs

### Job Categories

| Queue | Priority | Workers |
|-------|----------|---------|
| Critical | High | 4 |
| Default | Medium | 2 |
| Low | Low | 1 |

### Job Examples

| Job | Queue |
|-----|-------|
| Email sending | Critical |
| Workout analytics | Default |
| Usage rollups | Low |
| AI summaries | Low |

---

## Disaster Recovery

### Backup Strategy

| Data | Frequency | Retention |
|------|-----------|-----------|
| Database | Daily + continuous WAL | 30 days |
| File storage | Daily | 30 days |
| Configuration | On change | 90 days |

### Recovery Objectives

| Metric | Target |
|--------|--------|
| RPO (Recovery Point Objective) | < 1 hour |
| RTO (Recovery Time Objective) | < 4 hours |

### Failover

- Automated database failover
- DNS-based traffic switching
- Documented runbooks

---

## Multi-Region (Future)

### Strategy
- Primary region: US East
- Secondary regions: US West, EU (future)

### Data Replication
- Async replication for read replicas
- Region-specific data for EU compliance

---

## Infrastructure as Code

### Requirements

- All infrastructure defined in code (Terraform)
- Version controlled
- Environment parity (dev/staging/prod)
- Automated deployments

### Environments

| Environment | Purpose |
|-------------|---------|
| Development | Local development |
| Staging | Pre-production testing |
| Production | Live system |
