# Product Overview

This document defines the high-level product overview, user roles, and core user journeys for the gym management system.

---

## Purpose

Build a gym management system that coordinates gyms, locations, trainers, clients, programs, workouts, exercises, and scheduling.

---

## Primary User Roles

| Role | Description |
|------|-------------|
| **Admin** | Manages gyms/locations, global settings, trainer permissions, capacity, billing rules, etc. |
| **Trainer** | Manages clients, assigns programs, records workouts, reviews progress. |
| **Front Desk** | Checks in clients, views schedule, monitors gym occupancy (read-only operations). |
| **Client** | Views schedule, follows program, logs workouts, sees history + summaries. |

**Note**: Users can have multiple roles (e.g., a trainer may also work front desk).

---

## Core User Journeys

### Client Flow
1. Onboarding
2. Program assignment
3. Scheduled visits
4. Workout logging
5. Progress/history review

### Trainer Flow
1. View schedule/busyness
2. Run sessions
3. Record measurements/PRs
4. Review AI summary

**AI Summary**: Cached on client, auto-refreshed on-demand when trainer views it (if stale from completed workouts or new measurements).

### Front Desk Flow
1. Check in members/prospects
2. View gym occupancy
3. Verify active memberships

### Admin Flow
1. Manage staff
2. Manage gyms/locations
3. Configure scheduling rules
4. Control data access

---

## Modules (High-Level)

### Web App

**Primary use**: Admin + Trainer console; optional client portal.

**Responsibilities**:
- User auth + role-based access
- CRUD for gyms/locations/trainers/clients/programs/exercises
- Scheduling management + busyness visualization
- Reporting dashboards (attendance, adherence, PRs, trainer utilization)

**Key screens (initial)**:
- **Admin**: Gym Settings, Locations, Trainers, Clients, Programs, Exercises, Schedule
- **Trainer**: Today's Schedule, Client Profile, Program Builder, Workout Log

**User Experience Requirements**:
- Highly interactive interface matching mobile app experience
- Rich data visualizations for progress tracking, analytics, and reporting
- Responsive design with polished, professional aesthetics
- Real-time updates for schedule changes and client activity
- Smooth animations and transitions for enhanced user experience

### iOS App

**Primary use**: Client-first (trainer optional later).

**Responsibilities**:
- Program view → "start workout" → log sets/reps/measurements
- Schedule view → book/cancel (if enabled)
- History + progress + AI summary (trainer-generated, view-only for clients in future releases)

### Android App

Same as iOS parity.

---

## Related Documents

- [Entities](01-entities.md) - Core business entities
- [Memberships](02-memberships.md) - Plans, memberships, visit entitlements
- [Training](03-training.md) - Programs, workouts, exercises
- [Scheduling](04-scheduling.md) - Check-ins, availability, busyness
- [Progress](05-progress.md) - Measurements, goals, photos
- [Accounts](06-accounts.md) - Account/family management
- [Phases](07-phases.md) - Development phases
- [Glossary](glossary.md) - Terms and definitions
