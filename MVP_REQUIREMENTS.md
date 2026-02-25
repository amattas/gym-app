# MVP Requirements - Gym Management App

**Generated**: 2026-02-04
**Status**: Approved
**Version**: 1.0.0

---

## Table of Contents

1. [Target Market & Scale](#1-target-market--scale)
2. [MVP Feature Scope](#2-mvp-feature-scope)
3. [Technical Stack](#3-technical-stack)
4. [User Experience Requirements](#4-user-experience-requirements)
5. [Feature Specifications](#5-feature-specifications)
6. [Multi-Location Support](#6-multi-location-support)
7. [User Profiles & Onboarding](#7-user-profiles--onboarding)
8. [Security Requirements](#8-security-requirements-mvp)
9. [Data Management](#9-data-management)
10. [Integration Points](#10-integration-points)
11. [Additional Clarifications](#11-additional-clarifications-resolved)
12. [Open Questions](#12-open-questions-remaining)
13. [Success Criteria](#13-success-criteria)
- [Appendix A: Comparison to Original Docs](#appendix-a-comparison-to-original-docs)
- [Appendix B: Technology Decisions](#appendix-b-technology-decisions)

---

## Executive Summary

This document defines the Minimum Viable Product (MVP) scope for the gym management platform, based on clarifications from stakeholder discussions. It supersedes the broader vision documents for the purpose of initial development prioritization.

---

## 1. Target Market & Scale

| Attribute | Value |
|-----------|-------|
| Primary Market | Personal training studios |
| Secondary Market | Small traditional gyms |
| Initial Scale | 2-10 gyms |
| Launch Strategy | 1-2 beta gyms |
| Timeline | ASAP (urgent) |

---

## 2. MVP Feature Scope

### 2.1 In Scope (Must-Have)

| Category | Features |
|----------|----------|
| **Authentication** | Email + password, MFA (TOTP), password reset |
| **User Roles** | Admin, Trainer, Client (adults 18+ only) |
| **Client Management** | Create/edit profiles, notes at all levels (profile, session, set) |
| **Programs** | Template library, trainer-created, assign to clients, advanced periodization (wave loading, deload weeks) |
| **Workouts** | Full set type support (drop sets, rest-pause, cluster, AMRAP), circuit/superset with interactive rounds |
| **Workout Logging** | Configurable fields (weight, reps, time, distance, RPE, notes), previous + PR display, full history access |
| **Scheduling** | Staff-only booking, day/week/month calendar views, no restrictions on timing |
| **Check-in** | Manual only, trainer marks in/out time |
| **Attendance** | Auto-marked when exercises logged, track show/no-show |
| **Measurements** | Comprehensive library + gym custom types, trainer decides frequency |
| **Goals** | Trainer-created only, measurement/PR/frequency types |
| **PRs** | Track 1RM, multi-rep maxes (3RM, 5RM, 10RM), volume PRs |
| **Progress Photos** | Free-form upload, visible to client + assigned trainers |
| **Analytics** | Client-focused: attendance, completion, PR progression, measurement trends |
| **Branding** | Logo + primary/accent colors per gym |
| **Exercise Library** | Shared global library + gym custom, muscle groups + movement patterns |

### 2.2 Out of Scope (Deferred)

| Category | Reason |
|----------|--------|
| AI Summaries | Post-MVP feature |
| iCal Export | Post-MVP feature |
| Mobile Apps (iOS/Android) | Web-first, mobile Phase 2 |
| Health Integrations (Apple Health, Google Fit) | Post-MVP |
| QR Check-in | Manual check-in sufficient for MVP |
| Push Notifications | Email only for MVP |
| Prospect/Lead Tracking | Removed from MVP |
| Front Desk Role | For later expansion |
| Group Classes | No group class booking for MVP |
| Timer Features | No rest timers or workout timers |
| Client Self-Booking | Staff-only scheduling |
| Membership Access Control | No enforcement for MVP |
| Custom Domains | Enterprise feature, post-MVP |
| Family Accounts | Post-MVP when needed |
| Payment/Billing (Stripe) | Phase 4 per original plan |

---

## 3. Technical Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.11+ with FastAPI |
| Frontend | React 18+ with Next.js 14+ |
| Primary Database | PostgreSQL 15+ |
| Document/Config Store | PostgreSQL JSONB (no separate document store for MVP) |
| Cache Layer | Redis |
| Hosting | Google Cloud Platform (GKE/Kubernetes) |
| Email Service | Resend |
| API Style | REST (GraphQL deferred) |
| Authentication | OAuth2 with JWT tokens |

---

## 4. User Experience Requirements

### 4.1 Platform Access

| Role | Web | Mobile |
|------|-----|--------|
| Admin | Full access | Deferred |
| Trainer | Full access | Deferred |
| Client | Read-only dashboard (view schedule, history, progress) | Deferred |

### 4.2 UI/UX Specifications

| Feature | Specification |
|---------|--------------|
| Dark Mode | Follow system preference (light/dark toggle) |
| Language | English only |
| Units | Gym-level setting (metric or imperial) |
| Responsive | Must work on desktop, tablet, mobile browsers |

### 4.3 Calendar Views

- **Day View**: Hourly time slots, drag-drop scheduling
- **Week View**: 7-day overview with appointments
- **Month View**: Calendar grid with session indicators

### 4.4 Workout History Display

- **Primary View**: Exercise-centric (view all squats, all bench press, etc.)
- **During Logging**: Show last workout data + PR for comparison
- **Expandable**: Full exercise history available on demand

---

## 5. Feature Specifications

### 5.1 Programs & Workouts

#### Program Structure
- Programs contain multiple workouts (unlimited count)
- Workouts are ordered sequentially
- Programs end after last workout (no auto-loop)
- Trainer manually reassigns programs
- **Template Library**:
  - Admin creates gym-wide templates (visible to all trainers)
  - Trainers can also create personal templates

#### Program Builder (Advanced)
- Exercise list with target sets/reps
- Rest periods and tempo notation
- Periodization support (wave loading, deload weeks)
- Notes per exercise

#### Workout Structure
- **Circuits/Supersets**: Full support with interactive round counter (Round 1 of 3)
- **Exercise Grouping**: A1/A2/A3 notation for paired/grouped exercises

#### Set Types Supported
- Standard sets
- Drop sets
- Rest-pause sets
- Cluster sets
- AMRAP (As Many Reps As Possible)
- Warmup sets
- Custom-labeled sets

#### Set Logging Fields (Configurable)
- Weight
- Reps
- Time/Duration
- Distance
- RPE (Rate of Perceived Exertion)
- Notes

#### Workout Logging UX
- Show current workout exercises only (not full program)
- **Auto-Save**: Continuously save as sets are logged
- Partial completion supported (saves whatever is logged)
- Display: previous workout data + PR for each exercise

### 5.2 Exercise Library

#### Global Library
- Platform-provided common exercises
- Muscle group tags (primary/secondary)
- Movement pattern tags (push, pull, hinge, squat, lunge, carry, rotate)
- Text descriptions only (no video for MVP)

#### Gym Custom Exercises
- Gyms can add custom exercises
- Custom exercises inherit tagging system
- Custom exercises visible only to that gym

### 5.3 Measurements

#### System Measurements (Shared Library)
- Weight
- Body fat percentage
- BMI (calculated)
- Circumferences: chest, waist, hips, arms, legs, neck
- Blood pressure (systolic/diastolic)
- Resting heart rate
- Flexibility tests

#### Gym Custom Measurements
- Gyms can define additional measurement types
- Specify unit and normal range
- Custom measurements visible only to that gym

#### Measurement Recording
- Trainer initiates measurement session
- Record multiple measurements at once
- Optionally link progress photo
- Frequency determined by trainer per client

### 5.4 Goals

#### Goal Types
- **Measurement**: Target value for body metric (e.g., lose 10 lbs)
- **Exercise PR**: Target weight/reps for specific exercise
- **Workout Frequency**: Target sessions per week/month

#### Goal Workflow
- Trainers only can create goals
- System captures baseline automatically
- Auto-update progress when relevant data logged
- Mark achieved when target reached

### 5.5 PR Tracking

#### PR Types (Auto-Tracked)
- **1RM**: One-rep max
- **Rep Maxes**: 3RM, 5RM, 10RM (weight at specific rep count)
- **Volume PR**: Highest total volume (weight × reps × sets)

#### PR Display
- Highlight when new PR achieved during workout
- Show PR in exercise history
- Include in client progress analytics

### 5.6 Scheduling

#### Booking Rules
- Staff-only (trainers/admins create sessions)
- No restrictions on booking time
- No cancellation penalties for MVP
- **Trainer double-booking**: Gym configurable (prevent, warn, or allow)
- **Client double-booking**: Gym configurable (prevent, warn, or allow)
- **Default session duration**: Gym sets default, trainers can override per session

#### Session Tracking
- Scheduled time
- Actual in/out time (trainer marked)
- Attendance status (auto-marked when exercises logged)
- Session notes

#### Trainer Availability
- Recurring weekly availability
- One-off exceptions (PTO, vacation)
- Linked to gym location

#### Data Refresh
- Manual refresh only (no WebSocket/polling for MVP)
- Users click refresh to see schedule updates

### 5.7 Check-In

#### MVP Implementation
- Manual check-in by trainer/admin
- Mark client arrival time
- Mark client departure time
- Links to scheduled session (if applicable)

### 5.8 Progress Photos

#### Upload
- Free-form (no pose requirements)
- Tagged with date/time
- Optional: link to measurement session
- Storage: Encrypted at rest

#### Privacy
- Visible to: uploading client + assigned trainers + gym admins
- Signed URLs for secure access

### 5.9 Notes System

#### Note Levels
- **Client Profile Notes**: General info (injuries, preferences, history)
- **Session Notes**: Notes for specific workout session
- **Set Notes**: Notes on individual sets within workout

#### Visibility
- All notes visible to client and assigned trainers
- Admin can view all notes

### 5.10 Analytics Dashboard

#### Client Metrics (Priority)
- Attendance rate (sessions attended vs scheduled)
- Workout completion rate
- PR progression over time (charts)
- Measurement trends over time (charts)
- Goal progress
- **Time Range**: Last 30 days (fixed range for MVP)

#### Trainer Metrics
- Sessions per trainer per week/month
- Client load (active clients assigned)
- Basic utilization metrics

#### Business Metrics
- Active clients count
- Sessions this week/month
- New signups

---

## 6. Multi-Location Support

### Configuration
- Gym admin configures access model
- Options: single location only, trainer multi-location, full flexibility

### Default Behavior
- Trainers assigned to specific location(s)
- Clients can be restricted or allowed to train at any location
- Sessions linked to specific location

### Location Entity
- **Fields**: Name, physical address
- Each gym must have at least one location

---

## 7. User Profiles & Onboarding

### 7.1 Gym Onboarding
- **Manual Provisioning**: Platform admin creates gym accounts
- New gym receives: gym_id, initial admin account
- Gym admin completes branding and settings

### 7.2 Trainer Profiles
- **Fields**: Name, email, phone (basic contact info)
- **Onboarding**: Admin creates account directly, sends credentials
- **Location Assignment**: Admin assigns trainer to location(s)
- **Deactivation**: Soft delete for MVP (block login, data retained, refine process post-MVP)

### 7.3 Client Profiles
- **Required Fields**:
  - Name (first, last)
  - Email
  - Phone
  - Date of birth (adults 18+ only)
  - Gender (optional)
  - Height, Weight (initial baseline)
  - Fitness goals (text)
  - Emergency contact (required)
- **Onboarding**: Trainer creates basic profile → client receives email invite to complete profile and set password
- **No Medical Data**: Health conditions/injuries captured in trainer notes, not structured fields

### 7.4 Search & Filtering
- Basic filters: status, date range, trainer assignment
- Name search for clients and exercises
- Advanced search deferred to post-MVP

---

## 8. Security Requirements (MVP)

### Authentication
- Email + password login
- MFA required for Admin/Trainer (TOTP via authenticator app)
- MFA optional for Clients
- Password requirements per docs (12+ chars, complexity, breach check)

### Authorization
- Role-based access control:
  - **Platform Admin**: Manages all gyms, provisions new gyms
  - **Gym Admin**: Manages their gym, creates trainers/clients
  - **Trainer**: Manages assigned clients, creates programs/workouts
  - **Client**: Read-only access to their own data
- Trainers can self-assign clients
- Object-level access (trainers see only their clients unless admin)

### Audit Logging (Minimal)
- Login/logout events
- Failed login attempts
- Password changes
- Critical data deletions

---

## 9. Data Management

### Soft Delete
- Client data soft-deleted (marked deleted, not removed)
- Workout data retained for history

### Workout Editing/Deletion
- Edit: Allowed (gym-configurable who can edit)
- Delete: Allowed for MVP (may revisit)

### Data Retention
- Follow legal requirements (7 years for financial, GDPR for EU)

---

## 10. Integration Points

### Email (Resend)
- Password reset
- Email verification
- Session reminders (if enabled)
- Goal achievement notifications

### Future Integrations (Not MVP)
- Apple Health / Google Fit
- Stripe payments
- Calendar sync (iCal)
- AI/LLM for summaries

---

## 11. Additional Clarifications (Resolved)

| Question | Decision |
|----------|----------|
| Real-time Updates | Manual refresh only for MVP (no WebSocket/polling) |
| Exercise Import | Manual entry only for custom exercises |
| Client Portal | Read-only dashboard (view schedule, history, progress - no editing) |
| Report Export | No export for MVP (view in app only) |
| Session Reminders | No email reminders for MVP |
| Workout Confirmation | No notification - just save data silently |
| Double-Booking | Gym configurable (prevent, warn, or allow) |
| Session Duration | Gym sets default, trainers can override per session |

## 12. Open Questions (Remaining)

1. **Exercise Video Library**: Confirmed text-only for MVP. Consider third-party integration (ExRx, ACE) for post-MVP?

2. **Offline Support**: Web-only for MVP. When mobile apps added, offline-first approach per original docs?

---

## 13. Success Criteria

### MVP Launch Readiness
- [ ] Gym can create trainers and clients
- [ ] Trainer can create exercise library entries
- [ ] Trainer can create program templates
- [ ] Trainer can assign programs to clients
- [ ] Trainer can schedule sessions
- [ ] Trainer/client can log workouts with full set type support
- [ ] System tracks PRs automatically
- [ ] Trainer can record measurements
- [ ] Trainer can set goals
- [ ] Progress photos can be uploaded and viewed
- [ ] Analytics dashboard shows client metrics
- [ ] Multi-location support configurable

---

## Appendix A: Comparison to Original Docs

| Original Requirement | MVP Decision |
|---------------------|--------------|
| 4 user roles | 3 roles (defer Front Desk) |
| Family accounts | Adults only, defer families |
| Prospect tracking | Removed |
| QR check-in | Manual only |
| AI summaries | Deferred |
| Health integrations | Deferred |
| Mobile apps | Web-only |
| Group classes | Not included |
| Custom domains | Deferred |
| Stripe payments | Phase 4 |
| GraphQL | REST only |
| Push notifications | Email only |

---

## Appendix B: Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend framework | FastAPI | Modern async Python, good performance, auto-docs |
| Frontend framework | Next.js | React ecosystem, SSR, good DX |
| Database | PostgreSQL | ACID compliance, complex queries, proven |
| Document store | PostgreSQL JSONB | Config flexibility via JSONB, no separate document DB for MVP |
| Cache | Redis | Performance, pub/sub potential |
| Hosting | GKE | Kubernetes portability, GCP services |
| Email | Resend | Good deliverability, reasonable pricing |
| API style | REST | Simplicity, wider tooling support |
