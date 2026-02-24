# Development Phases

This document defines the phased development approach and success criteria.

---

## Overview

The platform development is organized into four progressive phases, each building on the previous with dependencies clearly marked.

**Key Principles**:
- Phase 1 must be fully functional for basic gym operations
- Each phase delivers standalone value
- Features are ordered to minimize rework
- Payment/billing comes last (Phase 4)

---

## Phase 1 - MVP (Core Operations)

**Goal**: Enable a gym to operate day-to-day using web interface only.

**Target Users**: Admins and Trainers (web-based)

### Features

| Category | Features |
|----------|----------|
| **Authentication** | OAuth2/JWT, RBAC, password reset |
| **Core Entities** | Gyms, Locations, Trainers, Clients, Exercise library |
| **Training** | Programs, Workouts, Workout logging, Progress tracking (PRs/measurements/photos) |
| **Scheduling** | Calendar views, session status, trainer availability |
| **Check-in** | Manual check-in, client lookup, basic occupancy |
| **Web App** | Admin dashboard, trainer console, basic client portal |

### Success Criteria

- [ ] Gym can onboard trainers and clients via web
- [ ] Trainer can create programs and assign to clients
- [ ] Trainer can log workouts for clients
- [ ] Progress tracking (PRs, measurements, photos) functional

---

## Phase 2 - Enhanced Operations & Mobile

**Goal**: Add mobile apps, family accounts, and advanced scheduling features.

**Target Users**: Clients (mobile), Trainers (mobile), Admins (web)

### Features

| Category | Features |
|----------|----------|
| **Mobile Apps** | iOS + Android for clients and trainers, offline-first foundation, push notifications |
| **Family Management** | Family accounts, multiple primary members, sub-member management, emancipation workflow |
| **Advanced Scheduling** | Busyness calculations, trainer availability, calendar integrations, predictive arrival tracking |
| **Memberships** | ClientMembership entity, Plan templates, "Billing Disabled" mode |
| **Analytics** | Trainer utilization, client adherence, workout completion rates, PR progression |

### Success Criteria

- [ ] Client can log workouts from mobile app
- [ ] Family can manage multiple members under one account
- [ ] Busyness calculations show accurate gym occupancy

---

## Phase 3 - Advanced Features & Intelligence

**Goal**: Add AI features, offline mode, front desk operations, and data management.

**Target Users**: All roles + Front Desk

### Features

| Category | Features |
|----------|----------|
| **AI Features** | Workout summaries (GPT-4 or similar), trainer review capabilities |
| **Offline Mode** | Cached programs, offline workout logging, sync strategy |
| **Front Desk** | Check-in interface, QR code scanning, occupancy dashboard |
| **Compliance** | CCPA/GDPR data export, retention policies, soft delete with anonymization |
| **Health Integrations** | Apple Health, Google Fit, data provenance tracking |
| **API** | GraphQL layer, flexible querying, real-time subscriptions |

### Success Criteria

- [ ] Mobile apps work offline for core operations
- [ ] AI summaries provide actionable insights
- [ ] Data export completes within 24 hours for typical gym

---

## Phase 4 - Payments & Premium Features

**Goal**: Enable monetization through Stripe integration and premium features.

**Target Users**: Gym Owners (billing), Platform Admins

### Features

| Category | Features |
|----------|----------|
| **Stripe Integration** | Platform billing, client billing via Stripe Connect, subscription management, processing fees |
| **E-Signature** | Agreement templates, DocuSign/HelloSign integration, secure storage |
| **Advanced Billing** | Trial periods, discounts, add-on plans, payment failure handling, tax calculation |
| **Usage Metering** | Usage tracking, plan limits, overage handling |
| **Premium Features** | White-label branding, custom domains, advanced analytics, API access |

### Success Criteria

- [ ] Gym can collect membership payments via Stripe
- [ ] Platform collects subscription fees from gyms
- [ ] Usage-based billing calculates correctly

---

## Phase Dependencies

```
Phase 1 (MVP)
    ↓
    └── Mobile apps depend on Phase 1 API
    └── Account entity builds on Client entity
Phase 2 (Mobile + Accounts)
    ↓
    └── Offline mode requires mobile apps
    └── Front desk uses membership tracking
Phase 3 (AI + Offline + Compliance)
    ↓
    └── Stripe integration requires membership entities
    └── Usage metering uses operational data
Phase 4 (Payments)
```

---

## Feature-to-Phase Mapping

| Feature | Phase |
|---------|-------|
| Web app (Admin/Trainer) | 1 |
| Basic authentication | 1 |
| Programs & Workouts | 1 |
| Manual check-in | 1 |
| Mobile apps | 2 |
| Family accounts | 2 |
| Calendar integrations | 2 |
| AI summaries | 3 |
| Offline mode | 3 |
| QR code check-in | 3 |
| Health integrations | 3 |
| Stripe payments | 4 |
| Custom domains | 4 |

---

## Related Documents

- [Overview](00-overview.md) - Product overview and user roles
