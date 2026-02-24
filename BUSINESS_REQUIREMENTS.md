# Gym Management App — Business Requirements

**CONFIDENTIAL**: This document contains proprietary business information. Access restricted to authorized team members, contractors, and partners only. Do not share publicly or with competitors.

This document defines the business requirements, user workflows, and business rules for the gym management system. For technical implementation details, see TECHNICAL_SPECIFICATIONS.md.

---

## Document Metadata

- **Version**: 1.1.0
- **Last Updated**: 2026-01-19
- **Owner**: Product Team
- **Status**: Approved
- **Related Documents**:
  - [TECHNICAL_SPECIFICATIONS.md](TECHNICAL_SPECIFICATIONS.md) - Technical implementation
  - [API_SPECIFICATIONS.md](API_SPECIFICATIONS.md) - API contracts
  - [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) - Performance, security, compliance

---

## Table of Contents

1. [Product Overview](#1-product-overview)
   - 1.1 [Purpose](#11-purpose)
   - 1.2 [Primary User Roles](#12-primary-user-roles)
   - 1.3 [Core User Journeys](#13-core-user-journeys)
2. [Modules (High-Level)](#2-modules-high-level)
   - 2.1 [Web App](#21-web-app)
   - 2.2 [iOS App](#22-ios-app)
   - 2.3 [Android App](#23-android-app)
3. [Core Business Entities](#3-core-business-entities)
   - 3.1 [Gym](#31-gym)
   - 3.2 [Account](#32-account)
   - 3.3 [Client](#33-client)
   - 3.4 [PlanTemplate (Membership Plans)](#34-plantemplate-membership-plans)
   - 3.5 [ClientMembership](#35-clientmembership)
   - 3.6 [ClientGoal](#36-clientgoal)
4. [Business Rules & Workflows](#4-business-rules--workflows)
   - 4.1 [Account & Member Management](#41-account--member-management)
   - 4.2 [Membership Lifecycle & Visit Entitlements](#42-membership-lifecycle--visit-entitlements)
   - 4.3 [Progress Photos](#43-progress-photos)
   - 4.4 [Health Data Integrations](#44-health-data-integrations)
   - 4.5 [Check-In System & Gym Occupancy](#45-check-in-system--gym-occupancy)
   - 4.6 [Manual Measurements & Goal Tracking](#46-manual-measurements--goal-tracking)
   - 4.7 [Program Progression](#47-program-progression)
   - 4.8 [Scheduling & Calendar Export](#48-scheduling--calendar-export)
5. [Business Decisions & Key Constraints](#5-business-decisions--key-constraints)
   - 5.1 [Payments & Billing](#51-payments--billing)
   - 5.2 [Plan & Program Architecture](#52-plan--program-architecture)
   - 5.3 [Account Hierarchy & Family Management](#53-account-hierarchy--family-management)
   - 5.4 [Workflows](#54-workflows)
6. [Glossary](#6-glossary)

---

## 1. Product Overview

### 1.1 Purpose

Build a gym management system that coordinates gyms, locations, trainers, clients, programs, workouts, exercises, and scheduling.

### 1.2 Primary User Roles

- **Admin**: Manages gyms/locations, global settings, trainer permissions, capacity, billing rules, etc.
- **Trainer**: Manages clients, assigns programs, records workouts, reviews progress.
- **Front Desk**: Checks in clients, views schedule, monitors gym occupancy (read-only operations).
- **Client**: Views schedule, follows program, logs workouts, sees history + summaries.

**Note**: Users can have multiple roles (e.g., a trainer may also work front desk).

### 1.3 Core User Journeys

- **Client flow**: Onboarding → program assignment → scheduled visits → workout logging → progress/history.
- **Trainer flow**: View schedule/busyness → run sessions → record measurements/PRs → review AI summary.
  - **AI Summary**: Cached on client, auto-refreshed on-demand when trainer views it (if stale from completed workouts or new measurements)
- **Front Desk flow**: Check in members/prospects → view gym occupancy → verify active memberships.
- **Admin flow**: Manage staff, gyms/locations, scheduling rules, and data access.

---

## 2. Modules (High-Level)

### 2.1 Web App

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
- **Highly interactive** interface matching mobile app experience
- **Rich data visualizations** for progress tracking, analytics, and reporting
- **Responsive design** with polished, professional aesthetics
- **Real-time updates** for schedule changes and client activity
- **Smooth animations** and transitions for enhanced user experience

### 2.2 iOS App

**Primary use**: Client-first (trainer optional later).

**Responsibilities**:
- Program view → "start workout" → log sets/reps/measurements
- Schedule view → book/cancel (if enabled)
- History + progress + AI summary (trainer-generated, view-only for clients in future releases)

### 2.3 Android App

Same as iOS parity.

---

## 3. Core Business Entities

### 3.1 Gym

A gym represents a business that uses the platform. Each gym can have multiple locations, trainers, and clients.

**Branding**:
- Logo and colors used in mobile apps and web app for gym-specific branding
- Provides white-label experience for each gym

**Measurement & Progress Settings**:
- `measurement_reminders_enabled`: Enable automatic measurement reminders for trainers
- `measurement_reminder_frequency_days`: How often to remind (e.g., 30 for monthly)
- `allow_peer_comparison`: Show client stats vs gym average
- `progress_photo_required_for_measurements`: Encourage photo with measurements

**Calendar & Integration Settings**:
- `hide_client_names_in_calendar`: Gym-wide default for trainer calendar privacy. If true, trainer .ics feeds show "Training Session" instead of client name (privacy)
  - **Precedence**: Gym default can be overridden per-trainer via their individual calendar settings

### 3.2 Account

**Definition**: Billing and access management entity. Represents a household, individual, or corporate account. Multiple members can belong to one account for consolidated billing and family management.

**Account types**:
- `individual`: Single-person account
- `family`: Multi-member household account
- `corporate`: B2B corporate wellness (future feature)

**Key features**:
- Consolidated billing (all family members billed together)
- Multiple primary members supported (co-parents, spouses, business partners)
- Primary members manage sub-members and grant/revoke login access

### 3.3 Client

**Definition**: Represents an individual member/person within an Account. Can be primary member (manages account) or sub-member (managed by primary).

**Client status**:
- `prospect`: Not yet a paying member
- `trial`: Temporary trial period
- `active`: Paying, active member
- `inactive`: Former member, no active membership
- `lost`: Churned, no longer engaged
- `deleted`: Soft-deleted for compliance

**Account member roles**:
- `primary`: Can manage account, add/remove members, control billing, grant logins to sub-members
- `member`: Standard member, managed by primary(ies)

**Age-based access rules**:
- **Under 13**: Cannot have login (COPPA compliance), gym/trainer manages all data
- **13-17**: Can have login if primary member grants it
- **18+**: Can have login, can request to transfer to own account ("emancipation")

### 3.4 PlanTemplate (Membership Plans)

**Definition**: A gym's sellable membership plan definition (what clients buy). Drives module enablement, visit entitlements, and payment structure.

**Plan types**:
- `gym_access`: General gym access
- `personal_training`: One-on-one training sessions
- `group_classes`: Group fitness classes
- (extensible for gym-specific needs)

**Constraint**: Client can only have ONE active membership per `plan_type`

**Visit entitlement models**:
- `unlimited`: No visit limits
- `per_week`: X visits per week (e.g., 3x/week)
- `per_month`: X visits per month (e.g., 8/month)
- `per_plan_duration`: Total visits over plan lifetime (e.g., 10-pack training)

**Plan duration**:
- `month` / `year`: Time-based plans with specific duration
- `until_used`: No fixed end date, expires when visits consumed or expiration period reached

**Payment configuration**:
- `one_time`: Single payment (e.g., 10-pack sessions)
- `monthly`: Recurring monthly payment
- `annually`: Recurring annual payment

**Processing fees**:
- `gym_absorbs`: Gym pays all Stripe processing fees
- `pass_to_client`: Fees added to client invoice (percentage/flat/both)

**Modules enabled** (per plan):
- Programming (custom workout programs)
- Progress photos
- Health integrations (Apple Health, Google Fit)
- Self-scheduling

**Add-on plans** (family member discounts):
- Add-on plans can only be assigned to members in an account with a required base plan
- Example: "Family Member Training Add-On" at 50% off, requires primary member to have personal training plan
- If primary cancels base plan → all linked addon plans also cancel

**Example plan templates**:

*10-Pack Personal Training (Session Pack)*:
- Plan type: `personal_training`
- Visit entitlement: 10 visits over plan duration
- Duration: Until used (expires in 180 days if not consumed)
- Payment: One-time $500

*Monthly Unlimited Gym Access*:
- Plan type: `gym_access`
- Visit entitlement: Unlimited
- Duration: 1 month, auto-renews
- Payment: $199/month recurring

*Annual 3x/Week Training with Monthly Billing*:
- Plan type: `personal_training`
- Visit entitlement: 3 visits per week, no rollover
- Duration: 1 year
- Payment: $150/month (12 months)

*Family Member Training Add-On (50% discount)*:
- Plan type: `personal_training`
- Is addon: Yes, requires primary member with personal training plan
- Visit entitlement: 2 visits per week
- Duration: 1 month
- Payment: $75/month (50% off base price)

### 3.5 ClientMembership

**Definition**: An active or historical membership linking a client to a plan template. Tracks visit entitlements, payment status, and membership lifecycle.

**Membership status**:
- `active`: Currently active, client can use services
- `paused`: Temporarily paused (extends expiration date)
- `expired`: Ended naturally (time or visits exhausted)
- `canceled`: Gym-initiated cancellation

**Visit tracking**:
- Tracks current period (week/month) visit usage
- Tracks total remaining visits (for until-used plans)
- Supports rollover (if plan allows)
- Automatically resets periods based on plan configuration

**Pause functionality**:
- Only gym admin/trainer can pause
- Pausing extends expiration date by days paused
- Useful for injuries, vacations, etc.

**Cancellation**:
- Only gym admin can cancel (clients cannot self-cancel)
- Recurring subscriptions: remain active until period end
- One-time/session packs: canceled immediately, remaining visits forfeited

### 3.6 ClientGoal

**Definition**: Trackable goals set by trainer or client for progress measurement.

**Goal types**:
- `measurement`: Target body measurement (e.g., lose 10 lbs, reach 12% body fat)
- `exercise_pr`: Target personal record for exercise (e.g., 300 lb squat 1RM)
- `workout_frequency`: Target workout consistency (e.g., 3x per week for 12 weeks)
- `custom`: Free-form goal with manual tracking

**Goal lifecycle**:
- `active`: Currently working toward goal
- `achieved`: Goal successfully reached
- `abandoned`: Goal discontinued

**Auto-tracking**:
- System automatically updates progress when measurements recorded or PRs achieved
- Triggers notifications when goals achieved
- Calculates progress percentage: (current - baseline) / (target - baseline) * 100

---

## 4. Business Rules & Workflows

### 4.1 Account & Member Management

#### Account creation

- New signups create an Account with `account_type = 'individual'`
- First Client created as `member_role = 'primary'`
- Primary member creates User (login) during signup

#### Add sub-member (by primary member)

1. Primary navigates to "Add Family Member"
2. Enter: name, date_of_birth, relationship (spouse, child, parent, etc.)
3. System creates Client with `member_role = 'member'`
4. If `date_of_birth` indicates age >= 13:
   - Primary can optionally grant login access
   - System creates User linked to Client
   - Sub-member receives email to set password
5. If age < 13:
   - No login created (COPPA compliance)
   - Trainer/gym manages all data for minor
   - Parent contact info stored for communication

#### Grant/revoke login (by primary member)

- Primary can create login for sub-member (13+)
- Primary can disable `login_enabled` to revoke access
- User record remains (for audit), but login blocked

#### Multiple primary members

- Account can have multiple `member_role = 'primary'`
- Use case: Co-parents, spouses, business partners
- All primaries have equal account management permissions

#### Assign membership plan to sub-member

1. Primary selects sub-member
2. Choose from available plans (base or addon)
3. If addon plan:
   - Validate: account has primary member with required base plan
   - Link addon to base plan
   - Apply discount
4. Create ClientMembership for sub-member
5. Billing consolidated at Account level

#### Member emancipation (transfer to own account)

- **Trigger**: Sub-member turns 18, requests independence, or primary approves
- **Process**:
  1. Create new Account (`account_type = 'individual'`)
  2. Update Client: `account_id = new_account`, `member_role = 'primary'`
  3. Transfer active ClientMemberships to new account
  4. Historical data (workouts, PRs, photos) stays with Client
  5. Notify old account primary members
  6. New account responsible for own billing going forward

#### Primary member deletion

- Check if multiple primaries exist
- If yes: Remove this primary only, account stays active
- If no (last primary):
  1. Soft-delete all Clients in account (cascade)
  2. Set `client_status = 'deleted'`
  3. Anonymize all PII (see NON_FUNCTIONAL_REQUIREMENTS.md section 4.2 "Data Anonymization")
  4. Retain payment history for 7 years (tax compliance)
  5. Account marked as deleted
  6. Send confirmation emails
  7. Audit log records deletion with member numbers only (not PII)

### 4.2 Membership Lifecycle & Visit Entitlements

#### Membership creation

- When a gym assigns a plan to a client, a ClientMembership is created with `status = 'active'`
- System validates: client cannot have another active membership of the same `plan_type`
- Set `started_at` to current timestamp
- Calculate `expires_at` based on `plan_duration` (null for `until_used` without expiration)
- Initialize visit entitlement tracking based on plan's `visit_entitlement` configuration

#### Visit deduction

When a client checks in / workout starts:
- Determine which active membership(s) apply (based on plan_type and schedule context)
- If visit entitlement is limited (not unlimited):
  - Check if visits remain in current period or total (for until_used)
  - Deduct 1 from visits used
  - Reject check-in if no visits remain
- If unlimited: allow check-in without deduction

#### Period resets

- For `per_week` entitlements: reset visits used every week on configured day (e.g., Monday)
- For `per_month` entitlements: reset on the monthly anniversary of `started_at`
- If `rollover_enabled = true`: carry unused visits to next period (up to configured max)
- If `rollover_enabled = false`: reset to plan's default count

#### Pause/unpause

- Only gym admin/trainer can pause a membership
- **On pause**:
  - Set `status = 'paused'`
  - Record `paused_at` timestamp and who paused it
- **On unpause**:
  - Calculate days paused = (unpause_timestamp - paused_at)
  - Add days paused to `expires_at` (extends expiration)
  - Adjust period end dates if necessary
  - Set `status = 'active'`

#### Cancellation

- Only gym admin can cancel (clients cannot self-cancel)
- **For recurring subscriptions**:
  - Set `cancels_at_period_end = true`
  - Membership remains `active` until `expires_at`
  - Cancel Stripe subscription with `at_period_end = true`
  - After expiration, status becomes `expired`
- **For one-time/until-used plans**:
  - Set `status = 'canceled'` immediately
  - Remaining visits are forfeited (gym can issue manual refund if desired)

#### Expiration

- Nightly job (scheduled using `Gym.timezone`) checks for memberships where `current_time > expires_at`
- Set `status = 'expired'`
- Client loses access to plan modules and visit entitlements

#### Processing fees

- When `processing_fee_handling = 'pass_to_client'`:
  - Calculate fee based on plan's `processing_fee_config`
  - Add fee to invoice/payment intent
  - Record actual amounts charged
- When `processing_fee_handling = 'gym_absorbs'`:
  - Gym pays full Stripe fees
  - Client pays only the plan amount

### 4.3 Progress Photos

- Client can upload progress photos tied to a date/time
- Photos can be private to client + assigned trainer(s) + gym admins (configurable)
- Optional tagging: weight, notes, body measurements snapshot, goal phase
- Storage must support secure, signed URL access
- Trainers can view photo trends to help clients stay on track with goals

### 4.4 Health Data Integrations

- Users can connect/disconnect Apple Health / Android health source
- Data is imported on a schedule (or on app open) with explicit user permission
- Imported metrics are stored as time-series records and can be summarized for trainers
- Users can restrict which metrics are shared with trainers
- Optionally sync health/fitness metrics from:
  - Apple Health (HealthKit) on iOS
  - Android equivalent (Google Fit / Health Connect)
- Trainers can view trends to inform coaching

### 4.5 Check-In System & Gym Occupancy

#### Check-in methods

- **QR scan**: Client scans unique QR code on mobile app at gym entrance
- **Manual entry**: Front desk looks up client by name and checks them in
- **Mobile app**: Client checks in via mobile app when arriving

#### Check-in types

1. **Self-directed gym visits** (no trainer):
   - Client checks in via scan/front desk/app
   - No schedule entry required
   - Assumed duration: 60 minutes

2. **Training sessions** (scheduled with trainer):
   - May or may not explicitly check in
   - System predicts arrival based on schedule + historical patterns
   - Duration: uses client's average workout duration

#### Access control

- On check-in, system checks if client has active membership
- If no active membership: **Alert** front desk/trainer (don't block check-in)
- Front desk can choose to allow check-in despite alert

#### Check-out

- For MVP: assume duration, don't track explicit check-outs
- Use expected checkout time for occupancy calculations

### 4.6 Manual Measurements & Goal Tracking

#### Measurement recording workflow

1. Trainer navigates to client profile → "Record Measurements"
2. Select measurement types to record (from gym's active measurement types)
3. Enter values with appropriate units
4. Optional: Add trainer notes
5. Optional: Link to progress photo from same session
6. On save:
   - Create measurement record(s)
   - System auto-updates any active goals related to these measurements
   - Check if any goals achieved → trigger notification
   - If measurement reminders enabled: update last measured timestamp

#### Goal creation workflow

1. Trainer or client creates goal (depends on gym settings)
2. Select goal type:
   - `measurement`: Choose measurement type, target value, optional deadline
   - `exercise_pr`: Choose exercise, rep scheme (1RM/5RM/etc), target weight/time/distance
   - `workout_frequency`: Target # workouts per week/month, date range
   - `custom`: Free-form goal with manual tracking
3. System captures baseline value from latest measurement/PR
4. Set status = 'active'
5. Goal appears in client dashboard and trainer view

#### Goal auto-update triggers

**When new measurement recorded**:
1. Query for active goals where target measurement type matches
2. Update current value with latest measurement
3. Recalculate progress percentage = (current - baseline) / (target - baseline) * 100
4. If current value >= target value (or <= for minimize goals):
   - Set status = 'achieved'
   - Create notification for client + trainer
   - Optional: Trigger celebration animation in mobile app

**When new PR achieved**:
1. Query for active goals where target exercise matches
2. Update current value with new PR value
3. Recalculate progress
4. Check for achievement

**When workout completed**:
1. Query for active `workout_frequency` goals for this client
2. Increment workout count for current period
3. Check if target reached → mark as achieved

#### Measurement reminders workflow

**Nightly job** (scheduled using `Gym.timezone`, e.g., 2 AM in "America/New_York"):
1. Query all gyms where `measurement_reminders_enabled = true`
2. For each gym, get all active clients with assigned trainers
3. For each client:
   - Check each active measurement type
   - If `(today - last_measured_at) > frequency_days` and not snoozed
4. If overdue:
   - Create in-app notification for client's primary trainer
   - Optional: Send email to trainer (if gym setting enabled)
5. Group reminders per trainer: "5 clients due for measurements today"

**When trainer records measurement**:
1. Update last measured timestamp
2. Calculate next reminder date = now + frequency_days
3. Clear reminder and snooze flags

**Snooze reminder** (trainer action):
1. Trainer views notification, clicks "Snooze"
2. Choose snooze duration: 3 days, 1 week, 2 weeks
3. Reminder won't trigger again until after snooze period

#### Peer comparison (if enabled)

1. Client views their measurement/goal progress
2. Optional toggle: "Compare with gym average"
3. System calculates anonymized gym average for same measurement type
4. Display: "You: 180 lbs | Gym average: 175 lbs" (no individual client data exposed)
5. Only show if >= 10 clients have this measurement (privacy threshold)

#### Progress photos integration

1. When recording measurements, trainer can optionally take progress photo
2. Photo linked to measurement record
3. Client measurement history shows thumbnails next to measurements
4. Trainer can view side-by-side photo comparisons over time
5. If `progress_photo_required_for_measurements = true`: System reminds trainer to take photo

### 4.7 Program Progression

#### Core concepts

- A **Program** is a set of multiple Workouts designed by a trainer
- Programs are separate from **Plans** (payment/membership)
- Plans control module access (feature enable/disable), e.g. programming, health integration, progress photos
- A client can have one active Program at a time (unless trainer assigns a new program)

#### Program Structure

- A **Program** contains multiple **Workouts** (formerly called "ProgramDays")
- Each **Workout** is a collection of planned exercises for a single training session
- Workouts are ordered sequentially within the program
- The client progresses through workouts in order with each visit

#### Visit assignment (one workout per visit)

- Each gym visit executes one Workout from the client's active Program
- On check-in / workout start:
  - The system loads exercises from the client's current/next Workout in their active Program
  - Trainer can optionally select a different workout from the program if needed

#### Advancement

- After visit completion:
  - The Program advances its pointer to the next Workout
  - The final Workout loops back to the beginning unless the trainer removes/changes the program

### 4.8 Scheduling & Calendar Export

#### Trainer schedule management

- Trainers have recurring weekly availability
- One-off exceptions for PTO/vacation
- Schedule entries link trainer + client + time slot
- Busyness calculations use schedule + predicted arrivals

#### iCalendar (.ics) export for trainers

- Each trainer has a unique, private calendar URL
- Trainers can subscribe to this URL in any calendar app (Apple Calendar, Google Calendar, Outlook, etc.)
- Calendar feed contains all scheduled training sessions
- Updates: Calendar feed regenerated on schedule changes (15-minute cache)
- Privacy: If gym enables `hide_client_names_in_calendar`, events show "Training Session" instead of client names

---

## 5. Business Decisions & Key Constraints

### 5.1 Payments & Billing

- **Stripe** will be used and payments will be built last
- **Memberships**: gym is merchant of record via Stripe Connect
- **Gym sales tax**: gyms are responsible for their own sales tax reporting for memberships
- **Processing fees**: Gyms can configure whether to absorb Stripe fees or pass them to clients
- **Membership types**: Support both subscription (recurring) and session packs (one-time)
  - Subscriptions: monthly or annual billing
  - Session packs: one-time payment for X visits (until-used)
  - Plans can have optional expiration for until-used (e.g., 180 days)
- **Cancellation**: Only gym can cancel memberships (clients cannot self-cancel)
  - Recurring subscriptions: cancel at period end, remain active until expiration
  - One-time/session packs: canceled immediately, remaining visits forfeited
- **Proration/refunds**: No automatic proration; gym handles refunds manually if desired

### 5.2 Plan & Program Architecture

- **Plan vs Program**:
  - **Plan** = what a client pays for (membership/entitlement bundle)
  - **Program** = prescribed set of training activities
  - Plans control module access (feature enable/disable)
  - A client can have multiple active Programs (subject to Plan entitlements)
- **Plan types**: Plans categorized by type (`gym_access`, `personal_training`, `group_classes`, etc.)
  - **Constraint**: Client can only have ONE active membership per `plan_type`
  - **Valid combo**: "Monthly Gym Access" + "10-Pack Training" (different types)
  - **Invalid combo**: "Monthly Training" + "10-Pack Training" (same type)
- **Visit entitlements**: Support multiple models
  - `unlimited`: No visit limits
  - `per_week`: X visits per week (e.g., 3x/week)
  - `per_month`: X visits per month (e.g., 8/month)
  - `per_plan_duration`: Total visits over plan lifetime (e.g., 10-pack)
- **Rollover**: Configurable per plan (unused visits can roll over or expire)
- **Until-used expiration**: Session packs can have optional expiration (e.g., 180 days)
- **Pause**: Only gym can pause memberships; pausing extends expiration date by days paused

### 5.3 Account Hierarchy & Family Management

- Account can have multiple members (family, household)
- Multiple primary members supported (co-parents, spouses)
- Primary members control sub-member access and billing
- Add-on plans for discounted family member pricing
- Emancipation workflow for sub-members to transfer to own account
- Age-based access: <13 no login (COPPA), 13-17 with parental consent, 18+ independent

### 5.4 Workflows

- **Visit-Workout Relationship**: Workouts are tied to a specific gym visit (GymCheckIn). The visit may be from a scheduled session or a walk-in. This enables tracking which training sessions occurred during which gym visits.
- **Editing completed workouts** is gym-configurable: trainer-only OR trainer+client
- **Client prospects**: Single `Client` entity with `client_status` field
  - Status: `prospect` | `trial` | `active` | `inactive` | `lost` | `deleted`
  - Allows basic lead tracking without full CRM

### 5.5 Custom Domain Features (Enterprise Only)

**Feature Status**: Later-stage premium feature for highest plan tier (Enterprise). Not part of MVP or initial launch.

#### Custom Email Domains

**Business Purpose**: Allow gyms to send emails from their own domain (e.g., `notifications@powerliftgym.com`) for professional branding.

**Features**:
- Gym admin configures custom email domain
- DNS verification via SPF/DKIM/DMARC records
- Emails sent from verified custom domain
- Configurable reply-to address
- Falls back to default platform domain if not configured

**Access Control**:
- Only gym admins can configure domains
- Domain ownership verified via DNS (mandatory)
- One email domain per gym (unique constraint)
- Rate limiting on verification attempts (10 attempts per hour)
- Verification expires after 72 hours

**Email Service Provider**: Resend ($20/month for 50k emails)

#### Custom Login Domains

**Business Purpose**: Enable white-label branded login experience (e.g., `app.powerliftgym.com`).

**Features**:
- Gym admin configures custom login domain
- DNS verification via CNAME record
- Automatic SSL certificate provisioning (Let's Encrypt)
- Custom domain routing resolves to correct gym
- Falls back to default path-based routing if not configured

**Access Control**:
- Only gym admins can configure domains
- Domain ownership verified via DNS
- One login domain per gym (unique constraint)
- Rate limiting on verification attempts
- Verification expires after 72 hours

**Infrastructure**:
- CDN/Hosting: Digital Ocean Spaces + CDN initially (lower cost)
- SSL Certificates: Let's Encrypt (free, automated)
- Migration path to Azure long-term if project scales

**Plan Tier**: Enterprise tier only (exclusive premium feature)

#### Email Templates

**Business Purpose**: Provide branded, consistent email communication with customizable templates.

**Template System**:
- **Templating Engine**: Jinja2 for variable substitution and logic
- **Initial Implementation**: System templates only (platform administrator controlled)
- **Future Enhancement**: Per-gym template overrides (gym admins can customize)

**System Templates** (required, must always exist):
- **Authentication**:
  - `password_reset` - Password reset link email
  - `password_changed` - Password change confirmation
  - `welcome_email` - New user signup welcome
  - `email_verification` - Email verification link
- **Multi-Factor Authentication**:
  - `mfa_code` - MFA verification code
  - `mfa_enabled` - MFA enabled confirmation
  - `mfa_disabled` - MFA disabled confirmation
- **Operations**:
  - `membership_reminder` - Measurement reminder for trainers
  - `session_scheduled` - Training session scheduled
  - `session_canceled` - Training session canceled
  - `goal_achieved` - Goal achievement congratulations

**Template Categories**:
- **Transactional**: Password resets, MFA codes, email verification (CAN-SPAM exempt)
- **Operational**: Reminders, session notifications, goal achievements (relationship messages)
- **Marketing**: Promotional content (future feature, requires unsubscribe)

**Template Resolution**:
1. Check for gym-specific override (future feature)
2. Fall back to system template
3. Render with Jinja2 using gym branding variables
4. Send via Resend with appropriate sender domain

**Branding Variables** (injected into all templates):
- Gym name, logo URL, brand colors (from Gym entity)
- Platform support email
- User name and email
- Template-specific variables (reset tokens, MFA codes, etc.)

**Access Control**:
- **System templates**: Platform admin only (create/modify)
- **Gym override templates**: Gym admin only (future feature)
- System templates cannot be deleted or deactivated (critical infrastructure, always active)
- Gym overrides can be deactivated or deleted (falls back to system template)

**Email Type by Template**:
- **Password reset/MFA**: Always transactional, no unsubscribe
- **Session notifications**: Operational, optional unsubscribe
- **Marketing emails**: Always include unsubscribe (CAN-SPAM)

---

## 6. Development Phases

### Overview

The platform development is organized into four progressive phases, each building on the previous with dependencies clearly marked.

**Key Principles**:
- Phase 1 must be fully functional for basic gym operations
- Each phase delivers standalone value
- Features are ordered to minimize rework
- Payment/billing comes last (Phase 4)

### Phase 1 - MVP (Core Operations)

**Goal**: Enable a gym to operate day-to-day using web interface only.

**Target Users**: Admins and Trainers (web-based)

**Features**:
- Authentication & User Management (OAuth2/JWT, RBAC, password reset)
- Core Entities (Gyms, Locations, Trainers, Clients, Exercise library)
- Training Operations (Programs, Workouts, Workout logging, Progress tracking with PRs/measurements/photos)
- Basic Scheduling (Calendar views, session status, trainer availability)
- Check-in System (Manual check-in, client lookup, basic occupancy)
- Web Application (Admin dashboard, trainer console, basic client portal)

### Phase 2 - Enhanced Operations & Mobile

**Goal**: Add mobile apps, family accounts, and advanced scheduling features.

**Target Users**: Clients (mobile), Trainers (mobile), Admins (web)

**Features**:
- Mobile Applications (iOS + Android for clients and trainers, offline-first foundation, push notifications)
- Family & Account Management (Family accounts, multiple primary members, sub-member management, emancipation workflow)
- Advanced Scheduling (Busyness calculations, trainer availability, calendar integrations, predictive arrival tracking)
- Memberships Pre-Payment (ClientMembership entity, Plan templates, "Billing Disabled" mode)
- Reporting & Analytics (Trainer utilization, client adherence, workout completion rates, PR progression)

### Phase 3 - Advanced Features & Intelligence

**Goal**: Add AI features, offline mode, front desk operations, and data management.

**Target Users**: All roles + Front Desk

**Features**:
- AI Workout Summaries (GPT-4 or similar, trainer review capabilities)
- Offline Mode (Cached programs, offline workout logging, sync strategy)
- Front Desk Role & Features (Check-in interface, QR code scanning, occupancy dashboard)
- Data Management & Compliance (CCPA/GDPR data export, retention policies, soft delete with anonymization)
- Health & Fitness Integrations (Apple Health, Google Fit, data provenance tracking)
- GraphQL API Layer (Flexible querying, reduced mobile data usage, real-time subscriptions)

### Phase 4 - Payments & Premium Features

**Goal**: Enable monetization through Stripe integration and premium features.

**Target Users**: Gym Owners (billing), Platform Admins

**Features**:
- Stripe Integration (Platform billing, client billing via Stripe Connect, subscription management, processing fees)
- E-Signature & Agreements (Agreement templates, DocuSign/HelloSign integration, secure storage)
- Advanced Billing (Trial periods, discounts, add-on plans, payment failure handling, tax calculation)
- Usage Metering & Limits (Usage tracking, plan limits, overage handling)
- Premium Features (White-label branding, custom domains, advanced analytics, API access)

### Phase Dependencies

- **Phase 1 → Phase 2**: Mobile apps depend on Phase 1 API; Account entity builds on Client entity
- **Phase 2 → Phase 3**: Offline mode requires mobile apps; Front desk uses membership tracking
- **Phase 3 → Phase 4**: Stripe integration requires membership entities; Usage metering uses operational data

### Success Criteria

**Phase 1 (MVP)**:
- ✅ Gym can onboard trainers and clients via web
- ✅ Trainer can create programs and assign to clients
- ✅ Trainer can log workouts for clients
- ✅ Progress tracking (PRs, measurements, photos) functional

**Phase 2**:
- ✅ Client can log workouts from mobile app
- ✅ Family can manage multiple members under one account
- ✅ Busyness calculations show accurate gym occupancy

**Phase 3**:
- ✅ Mobile apps work offline for core operations
- ✅ AI summaries provide actionable insights
- ✅ Data export completes within 24 hours for typical gym

**Phase 4**:
- ✅ Gym can collect membership payments via Stripe
- ✅ Platform collects subscription fees from gyms
- ✅ Usage-based billing calculates correctly

---

## 7. Glossary

**Business Terms**:
- **Account**: Billing entity; represents household, individual, or corporate account
- **Plan**: What a client pays for (membership/entitlement bundle)
- **Program**: Prescribed set of training activities
- **Membership**: Active or historical plan assignment to a client
- **Visit entitlement**: Rules governing how many visits a membership includes
- **Rollover**: Unused visits carrying forward to next period
- **Pause**: Temporary suspension of membership (extends expiration)
- **Emancipation**: Sub-member transferring to own independent account
- **Add-on plan**: Discounted membership for family members

**Fitness Terms**:
- **AMRAP**: As many reps as possible
- **PR**: Personal record
- **RPE**: Rate of perceived exertion
- **Program day**: A single workout within a program
- **Rep scheme**: Number of repetitions (e.g., 1RM, 5RM, 10RM)


## Appendix: Merged from REQUIREMENTS.md (legacy)

### 0. Product Overview

### 0.1 Purpose

Build a gym management system that coordinates gyms, locations, trainers, clients, programs, workouts, exercises, and scheduling.

### 0.2 Primary User Roles

- **Admin**: Manages gyms/locations, global settings, trainer permissions, capacity, billing rules, etc.
- **Trainer**: Manages clients, assigns programs, records workouts, reviews progress.
- **Front Desk**: Checks in clients, views schedule, monitors gym occupancy (read-only operations).
- **Client**: Views schedule, follows program, logs workouts, sees history + summaries.

**Note**: Users can have multiple roles (e.g., a trainer may also work front desk).

### 0.3 Core User Journeys

- **Client flow**: Onboarding → program assignment → scheduled visits → workout logging → progress/history.
- **Trainer flow**: View schedule/busyness → run sessions → record measurements/PRs → review AI summary.
- **Front Desk flow**: Check in members/prospects → view gym occupancy → verify active memberships.
- **Admin flow**: Manage staff, gyms/locations, scheduling rules, and data access.

---

### 1. Modules and Responsibilities

### 1.1 Web App

**Primary use**: Admin + Trainer console; optional client portal.

**Responsibilities**:
- User auth + role-based access
- CRUD for gyms/locations/trainers/clients/programs/exercises
- Scheduling management + busyness visualization
- Reporting dashboards (attendance, adherence, PRs, trainer utilization)

**Key screens (initial)**:
- **Admin**: Gym Settings, Locations, Trainers, Clients, Programs, Exercises, Schedule
- **Trainer**: Today's Schedule, Client Profile, Program Builder, Workout Log

### 1.2 API Layer

**Primary use**: Single source of truth for all clients.

**Responsibilities**:
- Authentication + authorization
- Domain services (program assignment, workout start/finish, schedule booking)
- Validation + business rules enforcement
- Audit logging

### 1.3 Data Layer

**Primary use**: Durable persistence + analytics.

**Storage strategy (hybrid: SQL + NoSQL)**:

Use **SQL** for highly relational, transactional data where joins/constraints matter:
- Gyms, locations, trainers, clients
- Programs/program days/exercises
- Workouts, sets, measurements
- Schedule bookings
- Agreements metadata (except large blobs)

Use **NoSQL** for fast-changing configuration, metering, and limits where flexibility/versioning matters:
- Gym usage metering (API calls, AI API calls, counts)
- Billing plan configuration + feature flags/limits (even before Stripe)
- Per-gym overrides and experimentation toggles

Store large binaries (photos, signed PDFs) in object storage; store references/metadata in DB.

**Responsibilities**:
- OLTP schema for transactional operations
- Event/audit tables for history
- Derived aggregates (busyness, adherence, PR rollups)

### 1.4 iOS App

**Primary use**: Client-first (trainer optional later).

**Responsibilities**:
- Program view → "start workout" → log sets/reps/measurements
- Schedule view → book/cancel (if enabled)
- History + progress + AI summary

### 1.5 Android App

Same as iOS parity.

---

### 2. Domain Model (Entities + Fields)

For each entity: define ID, required fields, optional fields, relationships, and constraints.

### 2.0 Progress Pictures + Health Integrations (Cross-Cutting)

**Progress pictures**:
- Clients can upload progress photos over time
- Trainers can view trends to help clients stay on track with goals

**Health integrations**:
- Optionally sync health/fitness metrics from:
  - Apple Health (HealthKit) on iOS
  - Android equivalent (Google Fit / Health Connect)
- Trainers can view trends to inform coaching

### 2.1 Gym

**Fields**:
- `gym_id` (UUID)
- `name` (string, required)
- `logo_url` (string, optional)
- `primary_color` (string, optional; hex color code e.g., "#FF5733")
- `accent_color` (string, optional; hex color code e.g., "#33C1FF")

**Branding**:
- Logo and colors used in mobile apps and web app for gym-specific branding
- Provides white-label experience for each gym

**Measurement & Progress Settings**:
- `measurement_reminders_enabled` (bool; default false)
- `measurement_reminder_frequency_days` (int; e.g., 30 for monthly reminders)
- `allow_peer_comparison` (bool; default false; show client stats vs gym average)
- `progress_photo_required_for_measurements` (bool; default false; encourage photo with measurements)

**Calendar & Integration Settings**:
- `hide_client_names_in_calendar` (bool; default false; if true, trainer .ics feeds show "Training Session" instead of client name)

**Usage metrics** (for billing later; tracked now):
- `usage_clients_count` (derived)
- `usage_locations_count` (derived)
- `usage_trainers_count` (derived)
- `usage_api_calls_count` (derived, time-windowed)
- `usage_ai_api_calls_count` (derived, time-windowed)

**Relationships**:
- Gym has many Locations
- Gym has many Trainers (either directly or via Locations)
- Gym has many UsageMetricRollups

### 2.2 UsageMetricRollup

**Definition**: Time-windowed rollups for gym usage metering (billing later; track now).

**Recommended storage**: Store rollups in NoSQL (time-series friendly, schema-flexible) keyed by `gym_id + window`. Optionally mirror a subset into SQL for reporting joins.

**Fields**:
- `usage_rollup_id` (UUID)
- `gym_id` (FK)
- `window_start` (datetime)
- `window_end` (datetime)
- `clients_count` (int)
- `locations_count` (int)
- `trainers_count` (int)
- `api_calls_count` (int)
- `ai_api_calls_count` (int)
- `computed_at` (datetime)

**Notes**:
- Counts may be computed nightly/hourly and cached; source-of-truth can be event logs
- Keep raw event logs where feasible for audit/reconciliation

### 2.3 GymPlanLimits (NoSQL)

**Definition**: Gym-level plan/limits/config document for platform billing and gym capabilities.

**Fields** (example):
- `gym_id`
- `platform_plan_id`
- `effective_at`
- `limits`:
  - `max_locations`
  - `max_trainers`
  - `max_clients`
  - `api_calls_per_month`
  - `ai_api_calls_per_month`
- `features`:
  - `self_scheduling_enabled`
  - `progress_photos_enabled`
  - `health_integrations_enabled`
  - `esign_enabled`
- `overrides` (optional)
- `updated_by`, `updated_at`

### 2.4 PlanTemplate (NoSQL)

**Definition**: A gym's sellable membership plan definition (what clients buy). Drives module enablement, visit entitlements, and payment structure.

**Fields**:
- `plan_template_id`
- `gym_id`
- `name` (e.g., "10-Pack Personal Training", "Monthly Gym Access")
- `description`
- `plan_type` (enum: `gym_access` | `personal_training` | `group_classes` | etc.)
  - **Constraint**: Client can only have ONE active membership per `plan_type`
- `status` (enum: `active` | `inactive`)
- `version`, `effective_at`

**Visit entitlement**:
- `visit_entitlement`:
  - `type` (enum: `per_week` | `per_month` | `per_plan_duration` | `unlimited`)
  - `count` (int, nullable; null means unlimited)
  - `rollover_enabled` (bool; do unused visits carry over to next period?)

**Plan duration**:
- `plan_duration`:
  - `type` (enum: `month` | `year` | `until_used`)
  - `value` (int; e.g., 12 for 12 months, null for until_used)
  - `until_used_expiration_days` (int, nullable; e.g., 180 = expires in 6 months if not used)

**Payment configuration**:
- `payment_config`:
  - `frequency` (enum: `one_time` | `monthly` | `annually`)
  - `amount` (decimal)
  - `currency` (string; e.g., "USD")
  - `stripe_price_id` (string, nullable)
  - `processing_fee_handling` (enum: `gym_absorbs` | `pass_to_client`)
  - `processing_fee_config` (nullable; only if `pass_to_client`):
    - `fee_type` (enum: `percentage` | `flat` | `percentage_plus_flat`)
    - `percentage` (decimal, nullable; e.g., 2.9 for 2.9%)
    - `flat_amount` (decimal, nullable; e.g., 0.30)

**Modules enabled**:
- `modules_enabled`:
  - `programming` (bool)
  - `progress_photos` (bool)
  - `health_integrations` (bool)
  - `self_scheduling` (bool)

**Limits**:
- `limits`:
  - `max_active_programs` (int, nullable)
  - `session_duration_minutes` (int, nullable)

**Add-on plan configuration** (for family member discounts):
- `is_addon` (bool; default false)
- `requires_primary_plan_type` (string, nullable; e.g., "personal_training")
- `addon_discount_percentage` (decimal, nullable; e.g., 50 for 50% off base price)

**Add-on plan rules**:
- Addon plans can only be assigned to members in an account that has a primary member with the required base plan
- If primary cancels base plan → all linked addon plans also cancel
- Addon discount applied to `payment_config.amount`

**Example plan templates**:

*10-Pack Personal Training (Session Pack)*:
```json
{
  "plan_type": "personal_training",
  "visit_entitlement": { "type": "per_plan_duration", "count": 10 },
  "plan_duration": { "type": "until_used", "until_used_expiration_days": 180 },
  "payment_config": { "frequency": "one_time", "amount": 500.00 }
}
```

*Monthly Unlimited Gym Access*:
```json
{
  "plan_type": "gym_access",
  "visit_entitlement": { "type": "unlimited", "count": null },
  "plan_duration": { "type": "month", "value": 1 },
  "payment_config": { "frequency": "monthly", "amount": 199.00 }
}
```

*Annual 3x/Week Training with Monthly Billing*:
```json
{
  "plan_type": "personal_training",
  "visit_entitlement": { "type": "per_week", "count": 3, "rollover_enabled": false },
  "plan_duration": { "type": "year", "value": 1 },
  "payment_config": { "frequency": "monthly", "amount": 150.00 }
}
```

*Family Member Training Add-On (50% discount)*:
```json
{
  "name": "Family Member Training Add-On",
  "plan_type": "personal_training",
  "is_addon": true,
  "requires_primary_plan_type": "personal_training",
  "addon_discount_percentage": 50,
  "visit_entitlement": { "type": "per_week", "count": 2 },
  "plan_duration": { "type": "month", "value": 1 },
  "payment_config": { "frequency": "monthly", "amount": 75.00 }
}
```
**Note**: Addon plan links to primary member's base training plan. If primary cancels, addon auto-cancels.

### 2.5 Account (SQL)

**Definition**: Billing and access management entity. Represents a household, individual, or corporate account. Multiple members can belong to one account for consolidated billing and family management.

**Fields**:
- `account_id` (UUID)
- `account_type` (enum: `individual` | `family` | `corporate`)
- `billing_email` (email)
- `billing_address` (structured; same as Location address)
- `stripe_customer_id` (string, nullable)
- `created_at` (datetime)
- `deleted` (bool; soft delete flag)

**Relationships**:
- Account has many Clients (members)
- Account can have multiple primary Clients (member_role = 'primary')
- Account has consolidated billing (all ClientMemberships billed together)

**Account types**:
- `individual`: Single-person account
- `family`: Multi-member household account
- `corporate`: B2B corporate wellness (future feature)

### 2.6 Location

**Fields**:
- `location_id` (UUID)
- `gym_id` (FK)
- `name` (string, optional if address is primary identifier)
- `picture_url` (string, optional)
- `address` (structured)

**Address structure**:
- `street1`, `street2`, `city`, `state`, `postal_code`, `country`

### 2.7 User (SQL)

**Definition**: Authentication entity. Represents login credentials for a Client. Managed by primary account members.

**Fields**:
- `user_id` (UUID)
- `client_id` (FK → Client; one-to-one relationship)
- `email` (string, unique)
- `password_hash` (string, nullable; Argon2id hash, null if only using passkeys)
- `password_hash_version` (int; hash algorithm version for future migrations, e.g., 1=argon2id)
- `roles` (JSON array; e.g., ["admin"], ["trainer", "front_desk"], ["client"])
- `login_enabled` (bool; can be revoked by primary member)
- `created_by_client_id` (FK → Client; which primary member granted this login)
- `created_at` (datetime)
- `last_login_at` (datetime, nullable)

**Password Requirements** (if using password auth):
- Minimum 12 characters
- Must contain: uppercase, lowercase, number, special character
- Cannot contain user's email or name
- Cannot be in common password breach list (check against Have I Been Pwned API)
- Password hash algorithm: **Argon2id only**

**Password hash versioning**:
- `password_hash_version` tracks which algorithm version was used
- Version mapping:
  - `1`: Argon2id (current standard)
  - Future versions (2, 3, etc.): Can add stronger algorithms as cryptographic standards evolve
- **Argon2id parameters** (version 1):
  - Memory cost: 64 MB minimum
  - Time cost: 3 iterations minimum
  - Parallelism: 4 threads
  - Output length: 32 bytes
  - **Salt**: Cryptographically secure random salt (128-bit minimum), unique per password, automatically generated by Argon2id
  - Salt stored with hash (Argon2id includes salt in output)
- **Hash migration strategy**:
  - On successful login: Check if user's hash version < current version
  - If outdated: Rehash password with current algorithm, update version
  - No user action required (transparent migration during normal login)
  - Allows gradual migration to stronger algorithms over time

**Multi-Factor Authentication** (MFA):
- `mfa_enabled` (bool; default true for admin/trainer, required after grace period)
- `mfa_method` (enum: `totp` | `email` | `passkey_only`; default totp)
- `totp_secret` (string, encrypted; for TOTP-based MFA)
- `totp_backup_codes` (JSON array, encrypted; one-time use backup codes, 10 codes generated)
- `mfa_enforced_at` (datetime; when MFA became required, nullable during grace period)

**MFA Methods**:
- `totp`: Time-based One-Time Password (Google Authenticator, Authy, 1Password, etc.)
- `email`: One-time code sent to user's email (fallback method, less secure than TOTP)
- `passkey_only`: Passkeys act as both authentication and MFA (no additional factor needed)

**Security notes**:
- **SMS MFA is NOT supported** (insecure, vulnerable to SIM swapping attacks)
- Email MFA acceptable as fallback, but TOTP or passkeys strongly recommended
- Passkey-only authentication is most secure (FIDO2 certified, phishing-resistant)

**Constraints**:
- One Client can have at most ONE User (one login per person)
- Email must be unique across all Users
- MFA required for all admin and trainer roles (grace period: 7 days after account creation)

**Roles**:
- `admin`: Gym administrator
- `trainer`: Trainer at gym
- `front_desk`: Front desk staff
- `client`: Regular client (default for non-staff)

**Note**: Users can have multiple roles (e.g., a trainer who also works front desk)

**Relationships**:
- User has many UserPasskeys
- User has many OAuth2AccessTokens (for integrations)

### 2.7.1 UserPasskey (SQL)

**Definition**: WebAuthn/FIDO2 passkey credentials for passwordless authentication. Users can register multiple passkeys (e.g., YubiKey, TouchID, FaceID, Windows Hello).

**Fields**:
- `passkey_id` (UUID)
- `user_id` (FK → User)
- `credential_id` (string; WebAuthn credential ID, unique)
- `public_key` (text; COSE-encoded public key)
- `counter` (bigint; signature counter for replay protection)
- `device_name` (string; user-friendly name, e.g., "iPhone 15", "YubiKey 5")
- `device_type` (enum: `platform` | `cross_platform`)
  - `platform`: Built-in authenticator (TouchID, FaceID, Windows Hello)
  - `cross_platform`: External security key (YubiKey, Titan Key)
- `aaguid` (string; Authenticator Attestation GUID from device)
- `transports` (JSON array; e.g., ["usb", "nfc", "ble", "internal"])
- `created_at` (datetime)
- `last_used_at` (datetime, nullable)

**Constraints**:
- `credential_id` must be unique globally (WebAuthn requirement)
- User can have multiple passkeys for redundancy

**Passkey-only authentication**:
- If user has passkeys and `password_hash IS NULL`: passkey-only mode
- No password required, passkey acts as both factor 1 and MFA
- Recommended for high-security accounts (admins, trainers)

### 2.7.2 OAuth2Client (SQL)

**Definition**: OAuth2 client applications registered by **gym administrators only** for third-party integrations (CRM systems, analytics dashboards, custom tools, etc.).

**Important**: This entity is for gym-level integrations only. MCP (trainer AI assistant access) uses a separate authorization flow and does NOT create OAuth2Client records.

**Access control**:
- **Only gym admins** can create OAuth2 clients
- **Trainers CANNOT** create OAuth2 clients (trainers can only authorize MCP)
- OAuth2 clients are gym-scoped (not user-scoped)

**Fields**:
- `client_id` (UUID; OAuth2 client_id)
- `client_secret` (string, hashed; OAuth2 client_secret)
- `gym_id` (FK → Gym; which gym owns this integration)
- `created_by_user_id` (FK → User; admin who created it)
- `name` (string; e.g., "Custom CRM Integration", "Analytics Dashboard")
- `description` (text, optional)
- `redirect_uris` (JSON array; allowed OAuth2 redirect URIs)
- `grant_types` (JSON array; e.g., ["authorization_code", "refresh_token", "client_credentials"])
- `scopes_allowed` (JSON array; which scopes this client can request)
- `is_active` (bool; admin can revoke client)
- `created_at` (datetime)
- `last_used_at` (datetime, nullable)

**Available OAuth2 Scopes** (for gym-level integrations):
- `gym:read` - Read gym settings, locations
- `clients:read` - Read client profiles (no PII without explicit consent)
- `clients:write` - Create/update clients
- `workouts:read` - Read workout data
- `workouts:write` - Log workouts
- `schedule:read` - Read schedules
- `schedule:write` - Book/cancel sessions
- `measurements:read` - Read measurements
- `measurements:write` - Record measurements
- `analytics:read` - Read analytics/reports

**Note**: The `mcp:trainer` scope is NOT available for OAuth2Client. MCP uses a separate, trainer-specific authorization flow (see section 3.1.1).

**Client credentials grant**:
- For server-to-server integrations (no user involved)
- Use `grant_type=client_credentials`
- Scoped to gym level, not specific users

**Authorization code grant**:
- For user-authorized integrations (e.g., trainer authorizes MCP access)
- Use standard OAuth2 authorization code flow with PKCE

### 2.7.3 OAuth2AccessToken (SQL)

**Definition**: Issued OAuth2 access tokens for API access.

**Fields**:
- `token_id` (UUID)
- `client_id` (FK → OAuth2Client, nullable; null for MCP tokens)
- `user_id` (FK → User, nullable; null for client_credentials grant, required for MCP)
- `token_type` (enum: `oauth_client` | `mcp` | `calendar`; type of token)
- `token_hash` (string; SHA-256 hash of access token)
- `refresh_token_hash` (string, nullable; SHA-256 hash of refresh token)
- `scopes` (JSON array; granted scopes)
- `expires_at` (datetime; access token expiration, typically 1 hour)
- `refresh_token_expires_at` (datetime, nullable; refresh token expiration, typically 30 days)
- `created_at` (datetime)
- `revoked_at` (datetime, nullable; if manually revoked)
- `last_used_at` (datetime, nullable)

**Token types**:
- `oauth_client`: Regular OAuth2 tokens from OAuth2Client (gym admin integrations)
- `mcp`: MCP tokens for trainer AI assistant access (no OAuth2Client, user-scoped)
- `calendar`: Calendar feed tokens for trainer .ics export (long-lived, read-only)

**Token lifecycle**:
- Access tokens: short-lived (1 hour)
- Refresh tokens: long-lived (30 days)
- Users/admins can revoke tokens at any time
- Tokens automatically revoked if user disabled or client deactivated

**Token storage security**:
- Never store plaintext tokens in database
- Store SHA-256 hash only
- Client receives plaintext token once at issuance
- For verification: hash incoming token and compare to stored hash

### 2.7.4 OAuth2AuthorizationCode (SQL)

**Definition**: Temporary authorization codes for OAuth2 authorization code flow.

**Fields**:
- `code_id` (UUID)
- `code_hash` (string; SHA-256 hash of authorization code)
- `client_id` (FK → OAuth2Client)
- `user_id` (FK → User)
- `redirect_uri` (string; must match one of client's registered redirect_uris)
- `scopes` (JSON array; requested scopes)
- `code_challenge` (string; PKCE code challenge)
- `code_challenge_method` (enum: `S256` | `plain`; PKCE method)
- `expires_at` (datetime; very short-lived, typically 10 minutes)
- `used_at` (datetime, nullable; one-time use)

**PKCE requirement**:
- All authorization code flows MUST use PKCE (RFC 7636)
- Prevents authorization code interception attacks
- Mobile apps and SPAs: public clients, must use PKCE

### 2.7.5 PasswordResetToken (SQL)

**Definition**: Temporary tokens for password reset workflow. Single-use, short-lived tokens sent via email.

**Fields**:
- `token_id` (UUID)
- `user_id` (FK → User)
- `token_hash` (string; SHA-256 hash of reset token)
- `expires_at` (datetime; 1 hour expiration)
- `created_at` (datetime)
- `used_at` (datetime, nullable; null until token used)
- `ip_address` (string, optional; IP that requested reset, for audit)

**Security requirements**:
- Tokens are 256-bit cryptographically secure random
- Never store plaintext tokens (SHA-256 hash only)
- Tokens expire after 1 hour
- Tokens are single-use (marked as used after consumption)
- Rate limiting: Max 3 reset requests per email per hour

**Cleanup**:
- Expired/used tokens can be purged after 7 days (keep for audit trail)

### 2.8 Trainer

**Fields**:
- `trainer_id` (UUID)
- `primary_location_id` (FK)

**Relationships**:
- Trainer has one TrainerAvailability (NoSQL)
- Trainer has many TrainerExceptions (SQL)

### 2.8.1 TrainerAvailability (NoSQL)

**Definition**: Trainer's recurring weekly schedule, stored as flexible JSON document per trainer.

**Storage**: One document per trainer_id in NoSQL (allows multi-location schedules).

**Fields** (JSON structure):
- `trainer_id`
- `recurring` (array of availability windows):
  - `day_of_week` (int; 0=Sunday, 6=Saturday)
  - `location_id` (UUID; trainer can work different locations on different days)
  - `start_time` (time; e.g., "07:00")
  - `end_time` (time; e.g., "12:00")
- `updated_at` (datetime)

**Example**:
```json
{
  "trainer_id": "uuid",
  "recurring": [
    {
      "day_of_week": 1,
      "location_id": "location-a-uuid",
      "start_time": "07:00",
      "end_time": "12:00"
    },
    {
      "day_of_week": 2,
      "location_id": "location-b-uuid",
      "start_time": "15:00",
      "end_time": "21:00"
    }
  ],
  "updated_at": "2026-01-19T10:00:00Z"
}
```

### 2.8.2 TrainerException (SQL)

**Definition**: One-off exceptions to trainer's recurring schedule (vacation, holidays, sick days).

**Fields**:
- `trainer_exception_id` (UUID)
- `trainer_id` (FK)
- `exception_date` (date)
- `exception_type` (enum: `unavailable` | `available`)
- `reason` (text, optional; e.g., "Vacation", "Holiday")
- `created_at` (datetime)
- `created_by_user_id` (FK; who created this exception)

**Purpose**: Allows tracking of PTO/vacation for reporting purposes.

### 2.9 Client

**Definition**: Represents an individual member/person within an Account. Can be primary member (manages account) or sub-member (managed by primary).

**Fields**:
- `client_id` (UUID)
- `account_id` (FK → Account)
- `member_role` (enum: `primary` | `member`)
- `client_status` (enum: `prospect` | `trial` | `active` | `inactive` | `lost` | `deleted`)
- `date_of_birth` (date)
- `relationship_to_primary` (string, nullable; e.g., "spouse", "child", "self")
- `primary_location_id` (FK)
- `primary_trainer_id` (FK, nullable; may be null for prospects)
- `qr_code` (string; unique identifier for scan-based check-in)
- `deleted` (bool; soft delete flag)

**Behavioral stats** (derived):
- `avg_workout_duration_minutes` (float)
- `avg_schedule_variance_minutes` (float; actual start - scheduled time)

**AI Summary**:
- `ai_summary_latest` (text)
- `ai_summary_updated_at` (datetime)

**Relationships**:
- Client belongs to Account
- Client may have one User (login, if primary member granted access)
- Client has many ClientMemberships
- Client has many GymCheckIns
- Client has many ProgressPhotos
- Client has many HealthMetricSamples
- Client has many Workouts
- Client has many PRs

**Account member roles**:
- `primary`: Can manage account, add/remove members, control billing, grant logins to sub-members
- `member`: Standard member, managed by primary(ies)

**Age-based access rules**:
- **Under 13**: Cannot have login (User), gym/trainer manages all data
- **13-17**: Can have login if primary member grants it
- **18+**: Can have login, can request to transfer to own account ("emancipation")

**History** (relationships):
- Visit History: derived from schedule + attendance events
- Exercise History: derived from workout logs

**PRs**:
- Client has PR per exercise + measurement type + rep scheme (e.g., Back Squat: weight 1RM, 5RM; 400m Row: time)

### 2.10 GymCheckIn (SQL)

**Definition**: Tracks client check-ins and check-outs for gym occupancy, attendance tracking, and busyness calculations.

**Fields**:
- `check_in_id` (UUID)
- `client_id` (FK)
- `location_id` (FK)
- `schedule_id` (FK, nullable; null for self-directed gym visits)
- `check_in_method` (enum: `qr_scan` | `manual_name` | `mobile_app`)
- `checked_in_by_user_id` (FK; front desk worker or trainer who checked them in)
- `checked_in_at` (datetime)
- `checked_out_at` (datetime, nullable; null if still in gym)
- `expected_checkout_at` (datetime; calculated at check-in based on duration)
- `check_in_type` (enum: `self_directed` | `training_session`)

**Behavior**:
- **Self-directed check-ins**: No schedule required, assume 60-minute duration
- **Training session check-ins**: May have associated schedule, use client's `avg_workout_duration_minutes`
- **Check-out**: For MVP, assume duration and don't track explicit check-outs (checked_out_at remains null)
- **Alert on inactive membership**: When checking in, alert front desk if client has no active membership

### 2.11 ClientMembership (SQL)

**Definition**: An active or historical membership linking a client to a plan template. Tracks visit entitlements, payment status, and membership lifecycle.

**Fields**:
- `client_membership_id` (UUID)
- `client_id` (FK)
- `plan_template_id` (FK)
- `plan_type` (string; denormalized from PlanTemplate for fast queries)
- `status` (enum: `active` | `paused` | `expired` | `canceled`)

**Dates**:
- `started_at` (datetime)
- `expires_at` (datetime, nullable; null for until_used plans without expiration)

**Pause information** (nullable):
- `pause_info`:
  - `paused_at` (datetime)
  - `paused_by_user_id` (FK; admin/trainer who paused it)
  - `pause_reason` (text, optional)
  - `days_paused_total` (int; extends expiration by this amount)

**Visit entitlement tracking**:
- `visit_entitlement`:
  - `current_period_start` (datetime)
  - `current_period_end` (datetime)
  - `visits_allowed_this_period` (int, nullable; null = unlimited)
  - `visits_used_this_period` (int)
  - `total_visits_remaining` (int, nullable; for until_used/per_plan_duration only)

**Cancellation information** (nullable):
- `cancellation_info`:
  - `canceled_at` (datetime)
  - `canceled_by_user_id` (FK; admin who canceled)
  - `cancellation_reason` (text, optional)
  - `cancels_at_period_end` (bool; if true, remains active until expires_at)

**Stripe metadata**:
- `stripe_metadata`:
  - `stripe_subscription_id` (string, nullable; for recurring payments)
  - `stripe_payment_intent_id` (string, nullable; for one-time payments)
  - `last_payment_at` (datetime)
  - `last_payment_amount` (decimal; actual amount charged including fees)
  - `last_processing_fee` (decimal; processing fee passed to client, if any)

**Constraints**:
- Unique constraint on (`client_id`, `plan_type`) where `status = 'active'`
- A client can only have one active membership per plan_type

**Valid combinations**:
- ✅ "Monthly Gym Access" (`gym_access`) + "10-Pack Training" (`personal_training`)
- ✅ "Annual Gym Access" (`gym_access`) + "8 Group Classes/Month" (`group_classes`)
- ❌ "Monthly Unlimited Training" (`personal_training`) + "10-Pack Training" (`personal_training`)

### 2.12 ProgressPhoto

**Fields**:
- `progress_photo_id` (UUID)
- `client_id` (FK)
- `captured_at` (datetime; when photo was taken)
- `uploaded_at` (datetime)
- `photo_url` (string; typically signed access via CDN/object storage)
- `visibility` (enum: `client_only` | `trainer` | `gym_admin`)
- `notes` (text, optional)
- `tags_json` (optional; e.g., "cut", "bulk", bodyweight snapshot)

**Constraints**:
- Enforce access control by visibility + trainer assignment
- Store derivatives/thumbnails for fast browsing

### 2.13 HealthConnection

**Fields**:
- `health_connection_id` (UUID)
- `client_id` (FK)
- `provider` (enum: `apple_health` | `google_fit` | `health_connect`)
- `status` (enum: `connected` | `disconnected` | `error`)
- `connected_at`, `disconnected_at`
- `scopes_granted_json` (which metrics permitted)
- `last_sync_at` (datetime)

### 2.14 HealthMetricSample

**Fields**:
- `health_metric_sample_id` (UUID)
- `client_id` (FK)
- `provider` (enum)
- `metric_type` (enum-like string: `steps` | `active_energy` | `resting_hr` | `sleep_duration` | `weight` | etc.)
- `start_at` (datetime)
- `end_at` (datetime, nullable)
- `value` (decimal)
- `unit` (string)
- `source_device` (string, optional)
- `ingested_at` (datetime)

**Constraints**:
- Idempotency key for imports to avoid duplicates (provider_sample_id or hash of timestamp+value+type)

### 2.15 Program

**Definition**: A reusable set of program days assignable to clients.

**Fields**:
- `program_id` (UUID)
- `name` (string)
- `description` (text)

**Relationships**:
- Program has many ProgramDays

### 2.16 ProgramDay

**Definition**: A named day containing a list of exercises. Linked list behavior for automatic progression.

**Fields**:
- `program_day_id` (UUID)
- `program_id` (FK)
- `name` (string; e.g., Day A, Day B)
- `next_program_day_id` (FK → ProgramDay)

**Constraints**:
- Last day must point to first day (circular)
- Validate no broken links; optionally validate exactly one cycle

**Relationships**:
- ProgramDay has many ProgramDayExercises

### 2.17 ProgramDayExercise

**Definition**: An exercise definition within a program day, with program-specific configurations.

**Fields**:
- `program_day_exercise_id` (UUID)
- `program_day_id` (FK)
- `exercise_id` (FK)
- `order_index` (int)
- `default_sets` (int)
- `default_reps` (int or reps schema)
- `tempo` (string, nullable; e.g., "3-1-1-0" for eccentric-pause-concentric-pause)
- `weight_progression_rule` (JSON, nullable):
  - `strategy` (enum: `add_from_average` | `add_from_pr` | `add_from_last_amrap` | `manual`)
  - `increment_amount` (decimal; e.g., 5 for "+5 lbs")
  - `increment_unit` (string; e.g., "lbs", "kg")
- `notes` (text, optional; trainer notes for this exercise in this program)

### 2.18 Exercise

**Fields**:
- `exercise_id` (UUID)
- `name` (string)
- `exercise_type_id` (FK)
- `image_url` (string, optional)
- `defaults` (schema; see below)

**Defaults** (proposal):
- `default_sets`
- `default_reps_per_set`
- `default_measurements` (e.g., weight, time)

### 2.19 ExerciseType

**Fields**:
- `exercise_type_id` (UUID)
- `name` (enum-like string): `Lift` | `Exertion` | (expand later)
- `measurements_allowed` (many)
- `pr_direction` (enum: `maximize` | `minimize`; determines if higher or lower is better for PRs)

**Measurement types**:
- Weight
- Time
- Distance
- Reps
- RPE (rate of perceived exertion)

**PR direction examples**:
- `minimize`: Sprint times, rowing for time, running for time
- `maximize`: Max weight lifted, max distance, max hold time, max reps

### 2.20 Workout

**Definition**: A single training session instance.

**Fields**:
- `workout_id` (UUID)
- `client_id` (FK)
- `trainer_id` (FK, optional; may be null for self-guided)
- `location_id` (FK)
- `program_id` (FK, nullable; if ad-hoc)
- `program_day_id` (FK, nullable)
- `started_at` (datetime)
- `ended_at` (datetime, nullable)

**Behavior**:
- When started, program day exercises become WorkoutExercises with status incomplete

### 2.21 WorkoutExercise

**Fields**:
- `workout_exercise_id` (UUID)
- `workout_id` (FK)
- `exercise_id` (FK)
- `status` (enum: `incomplete` | `complete` | `skipped`)
- `order_index` (int)

**Sets + measurements**:
- Each WorkoutExercise has one or more WorkoutSets

### 2.22 WorkoutSet

**Fields**:
- `workout_set_id` (UUID)
- `workout_exercise_id` (FK)
- `set_index` (int)
- `planned_reps` (int, nullable)
- `actual_reps` (int, nullable)
- `is_amrap` (bool)
- `notes` (text, optional)

**Measurements**:
- `measurements` (structured records; see WorkoutSetMeasurement)

**Reps schema rules**:
- Store each set explicitly to support patterns like 10 / 8 / 4 and varying weights
- Supersets are modeled via an optional grouping layer (see WorkoutExerciseGroup)

### 2.23 WorkoutExerciseGroup (Superset / Circuit)

**Definition**: Optional grouping of workout exercises to support supersets/circuits.

**Fields**:
- `workout_exercise_group_id` (UUID)
- `workout_id` (FK)
- `name` (string, optional; e.g., "Superset A")
- `order_index` (int)

**Relationships**:
- Group has many WorkoutExercises (add `workout_exercise_group_id` FK on WorkoutExercise, nullable)

### 2.24 WorkoutSetMeasurement

**Fields**:
- `measurement_id` (UUID)
- `workout_set_id` (FK)
- `type` (enum: `weight` | `time` | `distance` | etc.)
- `value` (decimal/string depending)
- `unit` (string)

### 2.25 Schedule

**Definition**: A tentative plan of visits with capacity/busyness computed at 15-min granularity.

**Fields**:
- `schedule_id` (UUID)
- `client_id` (FK)
- `location_id` (FK)
- `trainer_id` (FK, nullable)
- `scheduled_start` (datetime)
- `scheduled_end` (datetime)
- `status` (enum: `tentative` | `confirmed` | `canceled` | `no_show` | `completed`)

**Rules**:
- Admin can enable/disable self-scheduling
- Busyness computed every 15 minutes using active scheduled sessions + expected session duration

### 2.26 GymMeasurementType (SQL)

**Definition**: Gym-configurable measurement types (standard + custom). Allows gyms to track custom body measurements beyond system defaults.

**Fields**:
- `measurement_type_id` (UUID)
- `gym_id` (FK, nullable; null for system-wide standard types)
- `name` (string; e.g., "Body Weight", "Bicep Circumference Left")
- `category` (enum: `body_composition` | `circumference` | `vitals` | `performance` | `custom`)
- `default_unit` (string; e.g., "lbs", "in", "bpm", "%")
- `is_standard` (bool; true for system-provided, false for gym-custom)
- `is_active` (bool; gym can disable standard types they don't use)
- `sort_order` (int; for display ordering in UI)

**Standard measurement types** (system-seeded, `is_standard = true`, `gym_id = null`):

*Body Composition*:
- Body Weight, Body Fat %, Muscle Mass %, BMI

*Circumference*:
- Bicep Left, Bicep Right, Chest, Waist, Hips, Thigh Left, Thigh Right, Calf Left, Calf Right, Neck

*Vitals*:
- Blood Pressure Systolic, Blood Pressure Diastolic, Resting Heart Rate

*Performance*:
- VO2 Max, 1-Mile Run Time, Vertical Jump Height

**Custom types**:
- Gyms can create custom measurement types
- Custom types only visible to that gym
- Examples: "Flexibility Score", "Balance Test", "Grip Strength"

**Constraints**:
- Standard types shared across all gyms
- Custom types (`gym_id != null`) only visible to that gym
- Gyms can deactivate standard types they don't use (`is_active = false`)

### 2.27 ClientMeasurement (SQL)

**Definition**: Manually-recorded body measurements taken by trainer during sessions. Separate from auto-synced HealthMetricSample data.

**Fields**:
- `measurement_id` (UUID)
- `client_id` (FK)
- `measurement_type_id` (FK → GymMeasurementType)
- `recorded_by_user_id` (FK → User; trainer who took measurement)
- `recorded_at` (datetime)
- `value` (decimal)
- `unit` (string)
- `notes` (text, optional; trainer notes)
- `progress_photo_id` (FK → ProgressPhoto, nullable; link to photo from same session)

**Permissions**:
- Trainers can add measurements for assigned clients
- Clients can view their own measurements (read-only)
- Clients CANNOT edit or delete trainer-entered measurements
- Primary account members can view sub-member measurements

**Relationships**:
- Client has many ClientMeasurements
- Measurement links to one GymMeasurementType
- Measurement optionally links to ProgressPhoto

### 2.28 ClientGoal (SQL)

**Definition**: Client goals for measurements, exercise PRs, or workout frequency. System automatically tracks progress toward goals.

**Fields**:
- `goal_id` (UUID)
- `client_id` (FK)
- `created_by_user_id` (FK → User; trainer or client who created goal)
- `goal_type` (enum: `measurement` | `exercise_pr` | `workout_frequency` | `custom`)
- `status` (enum: `active` | `achieved` | `abandoned` | `expired`)

**Goal targets**:
- `target_measurement_type_id` (FK → GymMeasurementType, nullable; for measurement goals)
- `target_exercise_id` (FK → Exercise, nullable; for exercise PR goals)
- `target_value` (decimal; e.g., 180 for "weigh 180 lbs", 300 for "squat 300 lbs")
- `target_unit` (string)
- `target_date` (date, nullable; deadline for goal)

**Progress tracking** (auto-updated):
- `baseline_value` (decimal; starting point when goal created)
- `current_value` (decimal, nullable; updated automatically as new data comes in)
- `progress_percentage` (decimal; calculated: (current - baseline) / (target - baseline) * 100)

**Timestamps**:
- `created_at` (datetime)
- `achieved_at` (datetime, nullable; set when goal met)

**Metadata**:
- `notes` (text, optional; description/motivation)
- `visibility` (enum: `client_only` | `trainer` | `public`; for optional peer comparison feature)

**Auto-update triggers**:
- When new ClientMeasurement recorded → update `current_value` for matching goals
- When new PR achieved → update `current_value` for exercise PR goals
- When goal achieved → set `status = 'achieved'`, `achieved_at = now()`, notify client + trainer

**Goal types explained**:
- `measurement`: Target body weight, body fat %, circumference, etc.
- `exercise_pr`: Target PR for specific exercise (e.g., "Back Squat 1RM: 300 lbs")
- `workout_frequency`: Target # workouts per week/month
- `custom`: Trainer-defined goal with custom criteria

### 2.29 WorkoutAnalytics (SQL)

**Definition**: Pre-calculated workout session metrics for fast dashboard queries and progress visualization.

**Fields**:
- `analytics_id` (UUID)
- `workout_id` (FK)
- `client_id` (FK; denormalized for fast queries)
- `computed_at` (datetime)

**Volume & Intensity Metrics**:
- `total_weight_lifted_lbs` (decimal; normalized to lbs for comparison across units)
- `total_reps` (int; sum of all actual_reps across all sets)
- `total_sets` (int; count of all sets)
- `duration_minutes` (int; ended_at - started_at)

**Completion Metrics**:
- `exercises_completed` (int; count of WorkoutExercises where status = complete)
- `exercises_skipped` (int; count where status = skipped)
- `completion_rate` (decimal; exercises_completed / total_exercises)

**Performance Metrics**:
- `prs_achieved_count` (int; count of new PRs set this workout)
- `volume_by_muscle_group` (JSON, nullable; if exercises tagged with muscle groups)
- `intensity_score` (decimal, nullable; proprietary calculation based on weight as % of PR)

**Calculation timing**:
- **Async** (after workout completion via background job):
  - Total volume, PRs achieved, intensity score
  - Triggered when `POST /workouts/{id}/complete` called
- **Real-time** (during workout, not persisted):
  - Current sets, reps, duration displayed in UI

### 2.30 GymAnalytics (NoSQL - Time-Series)

**Definition**: Admin dashboard metrics for gym business reporting. Pre-calculated rollups for fast queries.

**Fields**:
- `analytics_id` (UUID)
- `gym_id` (FK)
- `period_start` (datetime)
- `period_end` (datetime)
- `period_type` (enum: `day` | `week` | `month` | `quarter` | `year`)
- `computed_at` (datetime)

**Revenue Metrics**:
- `revenue_metrics`:
  - `total_revenue` (decimal)
  - `new_revenue` (decimal; from new memberships this period)
  - `recurring_revenue` (decimal; from existing memberships)
  - `churned_revenue` (decimal; from cancellations)
  - `avg_revenue_per_client` (decimal)

**Client Metrics**:
- `client_metrics`:
  - `total_clients` (int; count at end of period)
  - `active_clients` (int; had at least 1 workout this period)
  - `new_clients` (int; joined this period)
  - `churned_clients` (int; canceled this period)
  - `client_retention_rate` (decimal; percentage)
  - `prospects_count` (int; clients with status = prospect)

**Engagement Metrics**:
- `engagement_metrics`:
  - `total_workouts` (int)
  - `total_check_ins` (int)
  - `avg_workouts_per_client` (decimal)
  - `avg_session_duration_minutes` (decimal)
  - `workout_completion_rate` (decimal; % of scheduled workouts completed)

**Trainer Metrics**:
- `trainer_metrics`:
  - `total_trainers` (int)
  - `active_trainers` (int; trainers with at least 1 session)
  - `avg_clients_per_trainer` (decimal)
  - `trainer_utilization_rate` (decimal; % of available hours used)

**Calculation timing**:
- Nightly rollup jobs calculate previous day, week, month
- Historical data archived after 1 year to cold storage

### 2.31 MeasurementReminder (SQL)

**Definition**: Optional reminders for trainers to take client measurements on a schedule.

**Fields**:
- `reminder_id` (UUID)
- `client_id` (FK)
- `measurement_type_id` (FK → GymMeasurementType)
- `last_measured_at` (datetime, nullable)
- `next_reminder_at` (datetime; calculated based on frequency)
- `frequency_days` (int; from gym setting, e.g., 30 for monthly)
- `reminder_sent_at` (datetime, nullable; last time reminder was sent)
- `is_snoozed` (bool; trainer can snooze reminder)
- `snoozed_until` (datetime, nullable)

**Behavior**:
- Nightly job checks all clients at gyms with `measurement_reminders_enabled = true`
- For each client: check `(today - last_measured_at) > frequency_days`
- If overdue:
  - Create in-app notification for primary trainer
  - Optional: Send email (if gym setting enabled)
  - Update `reminder_sent_at`
- When measurement recorded: update `last_measured_at`, clear reminder

---

### 3. System Behaviors (Formal Rules)

### 3.1 Account & Member Management

**Account creation**:
- New signups create an Account with `account_type = 'individual'`
- First Client created as `member_role = 'primary'`
- Primary member creates User (login) during signup

**Add sub-member** (by primary member):
1. Primary navigates to "Add Family Member"
2. Enter: name, date_of_birth, relationship (spouse, child, parent, etc.)
3. System creates Client with `member_role = 'member'`
4. If `date_of_birth` indicates age >= 13:
   - Primary can optionally grant login access
   - System creates User linked to Client
   - Sub-member receives email to set password
5. If age < 13:
   - No login created (COPPA compliance)
   - Trainer/gym manages all data for minor
   - Parent contact info stored for communication

**Grant/revoke login** (by primary member):
- Primary can create login for sub-member (13+)
- Primary can disable `login_enabled` to revoke access
- User record remains (for audit), but login blocked

**Multiple primary members**:
- Account can have multiple `member_role = 'primary'`
- Use case: Co-parents, spouses, business partners
- All primaries have equal account management permissions

**Assign membership plan to sub-member**:
1. Primary selects sub-member
2. Choose from available plans (base or addon)
3. If addon plan:
   - Validate: account has primary member with required base plan
   - Link addon to base plan
   - Apply discount
4. Create ClientMembership for sub-member
5. Billing consolidated at Account level

**Member emancipation** (transfer to own account):
- Trigger: Sub-member turns 18, requests independence, or primary approves
- Process:
  1. Create new Account (`account_type = 'individual'`)
  2. Update Client: `account_id = new_account`, `member_role = 'primary'`
  3. Transfer active ClientMemberships to new account
  4. Historical data (workouts, PRs, photos) stays with Client
  5. Notify old account primary members
  6. New account responsible for own billing going forward

**Primary member deletion**:
- Check if multiple primaries exist
- If yes: Remove this primary only, account stays active
- If no (last primary):
  1. Soft-delete all Clients in account (cascade)
  2. Set `client_status = 'deleted'`, `deleted = true`
  3. Anonymize all PII (see Data Anonymization rules)
  4. Retain payment history for 7 years (tax compliance)
  5. Account marked as deleted
  6. Send confirmation emails
  7. Audit log records deletion with member numbers only (not PII)

### 3.1.1 Authentication & Authorization (OAuth2)

**User registration workflow**:
1. User provides email and password (must meet password requirements)
2. System checks password against breach database (Have I Been Pwned API)
3. Hash password using Argon2id (version 1: 64 MB memory, 3 iterations, 4 threads)
4. Create User record with `mfa_enabled = true`, `mfa_enforced_at = now() + 7 days`, `password_hash_version = 1`
5. Send email verification link
6. User must verify email before login enabled

**Password login flow** (OAuth2 Resource Owner Password Credentials):
1. User submits email + password
2. System verifies password hash using algorithm specified in `password_hash_version`
3. **Hash migration check** (if password valid):
   - If `password_hash_version < current_version`: Rehash with current algorithm, update version
   - This transparently migrates users to stronger hashing over time
4. If MFA enabled:
   - If `mfa_method = 'totp'`: Prompt for TOTP code
   - If `mfa_method = 'email'`: Generate 6-digit code, send to email, prompt user
   - Verify MFA code (TOTP window: ±1 period, email code expires in 10 minutes)
5. Generate OAuth2 tokens:
   - Access token (JWT, expires in 1 hour)
   - Refresh token (opaque, expires in 30 days)
6. Return tokens to client
7. Update `last_login_at` timestamp

**Passkey registration workflow**:
1. User navigates to "Add Passkey" (or during account setup)
2. System generates WebAuthn challenge
3. User's device prompts for biometric/PIN
4. Device generates key pair, returns public key + attestation
5. System verifies attestation, stores public key
6. User provides friendly name for device
7. Create UserPasskey record
8. If user has no password: enable passkey-only mode (`password_hash = NULL`)

**Passkey login flow** (WebAuthn):
1. User navigates to login, clicks "Use Passkey"
2. System generates authentication challenge
3. User's device prompts for biometric/PIN
4. Device signs challenge with private key
5. System verifies signature using stored public key
6. Check signature counter (prevent replay attacks)
7. Generate OAuth2 tokens (no MFA needed, passkey is both factors)
8. Update `last_used_at` on UserPasskey

**Password reset workflow** (forgot password):

*Step 1: Request reset*:
1. User clicks "Forgot Password" on login page
2. User enters email address
3. System looks up user by email
4. **Security**: Even if email not found, show same success message (prevent email enumeration)
5. If user found:
   - Generate secure random reset token (256-bit cryptographically secure random)
   - Hash token with SHA-256, store hash in database
   - Set expiration: 1 hour from now
   - Store in `PasswordResetToken` table: `token_hash`, `user_id`, `expires_at`, `created_at`
6. Send password reset email with link: `https://app.gymapp.com/reset-password?token={plaintext_token}`
7. Display message: "If that email exists, we've sent a password reset link. Check your inbox."

*Step 2: Verify token and reset password*:
1. User clicks link in email
2. Client extracts token from URL, displays password reset form
3. User enters new password (must meet password requirements)
4. System validates token:
   - Hash submitted token with SHA-256
   - Look up token hash in database
   - Check: token not expired (`expires_at > now()`)
   - Check: token not already used (`used_at IS NULL`)
5. If valid:
   - Check new password against breach database (Have I Been Pwned API)
   - Hash new password with Argon2id (generate new salt)
   - Update User: `password_hash`, `password_hash_version = 1`
   - Mark reset token as used: `used_at = now()`
   - Invalidate all existing sessions (revoke all OAuth2 tokens for this user)
   - Send confirmation email: "Your password was changed"
   - Display success message: "Password reset successful. Please log in."
6. If invalid:
   - Display error: "Invalid or expired reset link. Please request a new one."

*Security considerations*:
- Reset tokens are single-use only
- Tokens expire after 1 hour
- Never store plaintext tokens (SHA-256 hash only)
- Invalidate all sessions on password reset (force re-login)
- Rate limit reset requests: Max 3 per email per hour (prevent abuse)
- Log all password reset attempts in audit trail
- Send notification email even if token invalid (alert user of reset attempt)

*Password change workflow* (logged-in user):
1. User navigates to "Security Settings" → "Change Password"
2. User enters: current password, new password, confirm new password
3. System verifies current password
4. Check new password meets requirements and not breached
5. Hash new password with Argon2id (generate new salt)
6. Update User: `password_hash`, `password_hash_version = 1`
7. Invalidate all other sessions (keep current session active)
8. Send confirmation email: "Your password was changed"

**MFA setup workflow (TOTP)**:
1. User navigates to "Security Settings" → "Enable MFA"
2. System generates TOTP secret (32-byte random)
3. Display QR code for authenticator app (otpauth:// URI)
4. User scans QR with app (Google Authenticator, Authy, 1Password, etc.)
5. User enters current TOTP code to verify setup
6. System verifies code, enables MFA
7. Generate 10 backup codes, display once (user must save)
8. Store encrypted TOTP secret and backup codes

**MFA enforcement**:
- Admin and trainer roles: MFA required after 7-day grace period
- During grace period: Show warning banner "MFA required in X days"
- After grace period: Block login until MFA enabled
- Client roles: MFA optional but recommended

**Backup code usage**:
1. User chooses "Use backup code" during MFA prompt
2. User enters one backup code
3. System verifies and marks code as used (one-time use)
4. User logs in successfully
5. System notifies user: "X backup codes remaining. Generate new codes in Security Settings"

**OAuth2 token refresh flow**:
1. Client submits refresh token
2. System verifies refresh token hash, checks not expired/revoked
3. Generate new access token (1 hour expiry)
4. Optionally rotate refresh token (recommended for mobile)
5. Return new tokens

**OAuth2 client registration** (gym admin only):
1. Admin navigates to "Integrations" → "Create OAuth Client"
2. Admin provides:
   - Client name (e.g., "Custom CRM Integration")
   - Redirect URIs (for authorization code flow)
   - Grant types needed
   - Scopes requested (cannot include `mcp:trainer`)
3. System generates `client_id` (UUID) and `client_secret` (secure random)
4. Display `client_secret` ONCE (admin must save securely)
5. Create OAuth2Client record (hash client_secret before storing)

**Important**: Only gym admins can create OAuth2 clients. Trainers cannot access this functionality.

**OAuth2 authorization code flow** (PKCE required):

*Step 1: Authorization request*:
1. Third-party app redirects user to: `/oauth/authorize?client_id=...&redirect_uri=...&scope=...&code_challenge=...&code_challenge_method=S256`
2. User logs in (if not already logged in)
3. System displays consent screen: "App X requests access to: [scopes]"
4. User approves or denies

*Step 2: Authorization code issuance*:
1. If approved: Generate authorization code (32-byte random, 10-minute expiry)
2. Store OAuth2AuthorizationCode with code_challenge
3. Redirect to: `{redirect_uri}?code={authorization_code}`

*Step 3: Token exchange*:
1. App posts to `/oauth/token` with:
   - `grant_type=authorization_code`
   - `code={authorization_code}`
   - `code_verifier={PKCE verifier}`
2. System verifies:
   - Code not expired/used
   - redirect_uri matches
   - PKCE verifier matches challenge (SHA256 hash)
   - Client credentials valid
3. Mark code as used
4. Generate access token + refresh token
5. Return tokens

**OAuth2 client credentials flow** (server-to-server):
1. App posts to `/oauth/token` with:
   - `grant_type=client_credentials`
   - `client_id` + `client_secret` (Basic Auth header)
   - `scope` (requested scopes)
2. System verifies client credentials
3. Check scopes allowed for this client
4. Generate access token (no refresh token for client credentials)
5. Token scoped to gym level, not specific user

**Token revocation**:
- User can revoke individual tokens from "Active Sessions" page
- Admin can revoke all tokens for a client
- Automatic revocation when user disabled or client deactivated
- Tokens checked on every API request (verify not revoked)

**MCP (Model Context Protocol) integration for trainers**:

MCP is a **trainer-specific OAuth2 authorization** that allows AI assistants (like Claude) to access trainer data. This is separate from general OAuth2 clients.

*Authorization flow*:
1. Trainer navigates to "AI Integrations" → "Enable MCP"
2. System generates OAuth2 authorization request specifically for MCP
3. System shows consent screen: "Claude/AI Assistant requests access to: clients:read, workouts:read, schedule:read, measurements:read"
4. Trainer approves
5. System creates OAuth2 access token with scope `mcp:trainer` tied to trainer's user context
6. AI assistant receives token and can now query API on behalf of trainer
7. All API calls include trainer's user context (row-level security enforced)

*Important distinctions*:
- **Trainers can ONLY authorize MCP** (AI assistant access to their own data)
- **Trainers CANNOT create general OAuth2 clients** for other API integrations
- **Only gym admins** can create OAuth2 clients for third-party integrations (CRM, analytics tools, etc.)
- MCP authorization is user-scoped (trainer's data only), not gym-scoped

*MCP scope restrictions*:
- `mcp:trainer` scope grants read-only access to:
  - Trainer's own schedule
  - Trainer's assigned clients only
  - Those clients' workouts, measurements, goals, progress
  - Cannot read other trainers' data (row-level security)
  - Cannot write/modify any data (read-only for AI safety)
  - Cannot access gym admin functions or settings

*Token management*:
- MCP tokens follow same OAuth2 standards (1-hour access token, 30-day refresh token)
- Trainer can revoke MCP access from "AI Integrations" page
- Automatic revocation if trainer account disabled or user deleted

### 3.2 Progress Photos

- Client can upload progress photos tied to a date/time
- Photos can be private to client + assigned trainer(s) + gym admins (configurable)
- Optional tagging: weight, notes, body measurements snapshot, goal phase
- Storage must support secure, signed URL access; avoid exposing raw object keys

### 3.3 Health Data Integrations

- Users can connect/disconnect Apple Health / Android health source
- Data is imported on a schedule (or on app open) with explicit user permission
- Imported metrics are stored as time-series records and can be summarized for trainers
- Users can restrict which metrics are shared with trainers

### 3.4 Membership Lifecycle & Visit Entitlements

**Membership creation**:
- When a gym assigns a plan to a client, a ClientMembership is created with `status = 'active'`
- System validates: client cannot have another active membership of the same `plan_type`
- Set `started_at` to current timestamp
- Calculate `expires_at` based on `plan_duration` (null for `until_used` without expiration)
- Initialize visit entitlement tracking based on plan's `visit_entitlement` configuration

**Visit deduction**:
- When a client checks in / workout starts:
  - Determine which active membership(s) apply (based on plan_type and schedule context)
  - If visit entitlement is limited (not unlimited):
    - Check if visits remain in current period or total (for until_used)
    - Deduct 1 from `visits_used_this_period` or `total_visits_remaining`
    - Reject check-in if no visits remain
  - If unlimited: allow check-in without deduction

**Period resets**:
- For `per_week` entitlements: reset `visits_used_this_period` every week on configured day (e.g., Monday)
- For `per_month` entitlements: reset on the monthly anniversary of `started_at`
- If `rollover_enabled = true`: carry unused visits to next period (up to configured max)
- If `rollover_enabled = false`: reset to plan's default count

**Pause/unpause**:
- Only gym admin/trainer can pause a membership
- On pause:
  - Set `status = 'paused'`
  - Record `paused_at` timestamp and `paused_by_user_id`
- On unpause:
  - Calculate `days_paused` = (unpause_timestamp - paused_at)
  - Add `days_paused` to `expires_at` (extends expiration)
  - Adjust period end dates if necessary
  - Set `status = 'active'`
  - Increment `days_paused_total`

**Cancellation**:
- Only gym admin can cancel (clients cannot self-cancel)
- For recurring subscriptions:
  - Set `cancels_at_period_end = true`
  - Membership remains `active` until `expires_at`
  - Cancel Stripe subscription with `at_period_end = true`
  - After expiration, status becomes `expired`
- For one-time/until-used plans:
  - Set `status = 'canceled'` immediately
  - Remaining visits are forfeited (gym can issue manual refund if desired)

**Expiration**:
- Nightly job checks for memberships where `current_time > expires_at`
- Set `status = 'expired'`
- Client loses access to plan modules and visit entitlements

**Processing fees**:
- When `processing_fee_handling = 'pass_to_client'`:
  - Calculate fee based on `processing_fee_config`
  - Add fee to invoice/payment intent
  - Record actual amounts in `last_payment_amount` and `last_processing_fee`
- When `processing_fee_handling = 'gym_absorbs'`:
  - Gym pays full Stripe fees
  - Client pays only the plan `amount`

### 3.5 Program Progression

**Core concepts**:
- A Program is a set of multiple ProgramDays (workouts) designed by a trainer
- Programs are separate from Plans (payment), but Plans can enable/disable the programming module

**Visit assignment** (supports multiple active programs):
- A client may have multiple active Programs
- On check-in / workout start for a visit:
  - The system assigns exercises from the client's next ProgramDay for each active Program to that visit (i.e., a composite workout made of multiple program-day blocks)
  - The client can optionally skip one or more Programs for that visit

**Advancement**:
- After visit completion:
  - Each non-skipped Program advances its pointer to `next_program_day_id`
  - Any skipped Program does not advance
  - The final day loops back to the beginning unless the trainer removes/changes the program

### 3.5.1 Scheduling & Calendar Export

**Trainer schedule management**:
- Trainers have recurring weekly availability (stored in TrainerAvailability)
- One-off exceptions for PTO/vacation (stored in TrainerException)
- Schedule entries (Schedule entity) link trainer + client + time slot
- Busyness calculations use schedule + predicted arrivals

**iCalendar (.ics) export for trainers**:
- Each trainer has a unique, private calendar URL
- URL format: `https://api.gymapp.com/trainers/{trainer_id}/calendar.ics?token={secret_token}`
- Secret token: Long-lived, revocable OAuth2 token with `schedule:read` scope
- Trainers can subscribe to this URL in any calendar app (Apple Calendar, Google Calendar, Outlook, etc.)

**Calendar feed contents**:
- All scheduled training sessions for this trainer
- Event details:
  - **Summary**: "Training: {Client Name}" (or "Training Session" if client name privacy enabled)
  - **Start/End time**: From Schedule entity
  - **Location**: Gym location address
  - **Description**: Client notes, program name (optional)
  - **Status**: CONFIRMED for confirmed sessions, TENTATIVE for tentative
  - **UID**: Stable identifier (e.g., `schedule-{schedule_id}@gymapp.com`)
- Updates: Calendar feed regenerated on schedule changes (15-minute cache)
- Cancellations: Marked with `STATUS:CANCELLED` in iCal format

**Calendar URL generation**:
1. Trainer navigates to "Settings" → "Calendar Integration"
2. System generates long-lived OAuth2 token with `schedule:read` scope
3. Token tied to trainer's user, auto-revoked if user disabled
4. Display calendar URL with instructions for subscribing
5. Trainer can revoke and regenerate URL at any time

**Privacy considerations**:
- Calendar URL must be kept secret (contains access token)
- If token leaked: trainer can revoke and get new URL
- Gym setting: `hide_client_names_in_calendar` (shows "Training Session" instead of client name)
- Only trainer's own schedule visible (cannot see other trainers)

**Calendar sync frequency**:
- Most calendar apps check URL every 15-60 minutes
- System caches .ics output for 15 minutes
- Manual refresh: trainer can force sync in calendar app

### 3.6 PR Tracking

- PRs are derived from workouts
- PR uniqueness key: `client_id + exercise_id + measurement_type + rep_scheme`
- Rep scheme is required (e.g., 1RM, 5RM, 10RM are tracked separately)
- For time/distance exercises: PR direction is determined by `ExerciseType.pr_direction`:
  - `minimize`: Lower is better (e.g., 400m sprint time, 2000m row time)
  - `maximize`: Higher is better (e.g., max distance in 10 min, plank hold time)

### 3.7 Check-In System & Gym Occupancy

**Check-in methods**:
- **QR scan**: Client scans unique QR code on mobile app at gym entrance
- **Manual entry**: Front desk looks up client by name and checks them in
- **Mobile app**: Client checks in via mobile app when arriving

**Check-in types**:

1. **Self-directed gym visits** (no trainer):
   - Client checks in via scan/front desk/app
   - No schedule entry required
   - Assumed duration: 60 minutes
   - Creates `GymCheckIn` record with `check_in_type = 'self_directed'`

2. **Training sessions** (scheduled with trainer):
   - May or may not explicitly check in
   - System predicts arrival based on schedule + historical patterns
   - Duration: uses `client.avg_workout_duration_minutes`
   - Creates `GymCheckIn` record with `check_in_type = 'training_session'` and `schedule_id`

**Access control**:
- On check-in, system checks if client has active membership
- If no active membership: **Alert** front desk/trainer (don't block check-in)
- Front desk can choose to allow check-in despite alert

**Check-out**:
- For MVP: assume duration, don't track explicit check-outs
- `checked_out_at` remains null
- Use `expected_checkout_at` for busyness calculations

### 3.8 Busyness Calculations & Predictive Analytics

**Time granularity**: 15-minute buckets

**Behavioral stats for predictions**:
- `avg_workout_duration_minutes`: Average session length per client
- `avg_schedule_variance_minutes`: Average early/late arrival (positive = late, negative = early)
- Calculate using seasonality-aware algorithms (see below)

**Three busyness views**:

#### View 1: Self-Directed Busyness
Shows gym occupancy from members without training sessions.

```
For each 15-min time slot:
  count = number of active GymCheckIns where:
    - check_in_type = 'self_directed'
    - checked_in_at <= slot_start
    - (checked_out_at >= slot_end OR checked_out_at IS NULL)
    - expected_checkout_at >= slot_end
```

#### View 2: Training Busyness
Shows expected gym occupancy from scheduled training sessions.

```
For each 15-min time slot:
  count = number of training sessions where:
    - Session is scheduled in this time window, OR
    - Session is already checked in and overlaps this window

  For scheduled (not yet checked in):
    - Use predicted_arrival_time ± confidence_interval
    - predicted_arrival = scheduled_time + avg_schedule_variance_minutes
    - confidence_interval = 1.28 * std_dev (80% confidence)

  For already checked in:
    - Use actual checked_in_at + avg_workout_duration_minutes
```

#### View 3: Per-Trainer Busyness
Shows individual trainer's load.

```
For each trainer, for each 15-min time slot:
  count = number of their scheduled/active training sessions in this slot

Trainers can view:
  - Their own schedule load
  - Likelihood each client will actually show up (based on confidence interval)
```

**Seasonality-aware historical calculations**:

Calculate `avg_workout_duration_minutes` and `avg_schedule_variance_minutes` using:

- **New clients** (<90 days tenure): Last 90 days of data
- **Regular clients** (90-365 days tenure): Last 180 days of data
- **Long-term clients** (>365 days tenure): Year-over-year comparison for same time period
  - Example: For January 2026, use data from January 2025, January 2024, etc.
  - Accounts for seasonal patterns (New Year's rush, summer dropoff, etc.)

**Fallback durations**:
1. Use client's `avg_workout_duration_minutes` (preferred)
2. Fallback to plan's `session_duration_minutes` if no history
3. Fallback to global default (60 minutes) if neither exists

### 3.9 Manual Measurements & Goal Tracking

**Measurement recording workflow**:
1. Trainer navigates to client profile → "Record Measurements"
2. Select measurement types to record (from gym's active GymMeasurementTypes)
3. Enter values with appropriate units
4. Optional: Add trainer notes
5. Optional: Link to progress photo from same session
6. On save:
   - Create ClientMeasurement record(s)
   - System auto-updates any active ClientGoals related to these measurements
   - Check if any goals achieved → trigger notification
   - If `measurement_reminders_enabled = true`: update `last_measured_at` on MeasurementReminder

**Goal creation workflow**:
1. Trainer or client creates goal (depends on gym settings)
2. Select goal type:
   - `measurement`: Choose measurement type, target value, optional deadline
   - `exercise_pr`: Choose exercise, rep scheme (1RM/5RM/etc), target weight/time/distance
   - `workout_frequency`: Target # workouts per week/month, date range
   - `custom`: Free-form goal with manual tracking
3. System captures `baseline_value` from latest measurement/PR
4. Set `status = 'active'`
5. Goal appears in client dashboard and trainer view

**Goal auto-update triggers**:

*When new ClientMeasurement recorded*:
1. Query for active goals where `target_measurement_type_id` matches
2. Update `current_value` with latest measurement
3. Recalculate `progress_percentage` = (current - baseline) / (target - baseline) * 100
4. If `current_value` >= `target_value` (or <= for minimize goals):
   - Set `status = 'achieved'`, `achieved_at = now()`
   - Create notification for client + trainer
   - Optional: Trigger celebration animation in mobile app

*When new PR achieved*:
1. Query for active goals where `target_exercise_id` matches
2. Update `current_value` with new PR value
3. Recalculate progress
4. Check for achievement (same as above)

*When workout completed*:
1. Query for active `workout_frequency` goals for this client
2. Increment workout count for current period
3. Check if target reached → mark as achieved

**Measurement reminders workflow**:

*Nightly job* (runs at gym's configured time, e.g., 2 AM local time):
1. Query all gyms where `measurement_reminders_enabled = true`
2. For each gym, get all active clients with assigned trainers
3. For each client:
   - Check each active GymMeasurementType
   - Query MeasurementReminder: if `(today - last_measured_at) > frequency_days`
   - Skip if `is_snoozed = true` AND `snoozed_until > today`
4. If overdue:
   - Create in-app notification for `client.primary_trainer_id`
   - Optional: Send email to trainer (if gym setting enabled)
   - Update `reminder_sent_at` timestamp
5. Group reminders per trainer: "5 clients due for measurements today"

*When trainer records measurement*:
1. System checks if MeasurementReminder exists for this client + measurement type
2. Update `last_measured_at = now()`
3. Calculate `next_reminder_at = now() + frequency_days`
4. Clear `reminder_sent_at`
5. Clear snooze flags

*Snooze reminder* (trainer action):
1. Trainer views notification, clicks "Snooze"
2. Choose snooze duration: 3 days, 1 week, 2 weeks
3. Set `is_snoozed = true`, `snoozed_until = now() + duration`
4. Reminder won't trigger again until after `snoozed_until`

**Peer comparison** (if `gym.allow_peer_comparison = true`):
1. Client views their measurement/goal progress
2. Optional toggle: "Compare with gym average"
3. System calculates anonymized gym average for same measurement type
4. Display: "You: 180 lbs | Gym average: 175 lbs" (no individual client data exposed)
5. Only show if >= 10 clients have this measurement (privacy threshold)

**Progress photos integration**:
1. When recording measurements, trainer can optionally take progress photo
2. Photo linked via `progress_photo_id` on ClientMeasurement
3. Client measurement history shows thumbnails next to measurements
4. Trainer can view side-by-side photo comparisons over time
5. If `gym.progress_photo_required_for_measurements = true`: System reminds trainer to take photo

### 3.10 Analytics & Reporting

**WorkoutAnalytics calculation** (async, after workout completion):

*Trigger*: When `POST /workouts/{id}/complete` called

*Calculation job* (background worker):
1. Query all WorkoutExercises + WorkoutSets for this workout
2. Calculate volume metrics:
   - Sum all weight lifted (normalize to lbs for consistency)
   - Count total reps (sum of `actual_reps` across all sets)
   - Count total sets
3. Calculate completion metrics:
   - Count exercises where `status = 'complete'`
   - Count exercises where `status = 'skipped'`
   - Calculate `completion_rate` = completed / total
4. Calculate performance metrics:
   - Query PRs: check if any new PRs set this workout
   - Count `prs_achieved_count`
   - Optional: Calculate intensity score (avg weight as % of PR)
5. Calculate duration:
   - `duration_minutes = (ended_at - started_at) / 60`
6. Create WorkoutAnalytics record with all calculated metrics
7. Update client's `avg_workout_duration_minutes` (rolling average)

*Real-time preview* (during workout, not persisted):
- As trainer logs sets, UI shows live calculations:
  - Current total weight lifted
  - Current total reps
  - Estimated workout duration
- Displayed in UI but not saved until workout complete

**GymAnalytics calculation** (nightly rollup):

*Trigger*: Nightly job at 2 AM gym local time

*Daily rollup*:
1. Calculate previous day metrics:
   - **Revenue**: Sum payments from `ClientMembership.stripe_metadata.last_payment_at` where date = yesterday
   - **Clients**: Count clients where `client_status IN ('active', 'trial')`
   - **New clients**: Count clients where `created_at` between yesterday start/end
   - **Churned clients**: Count ClientMemberships where `status = 'canceled'` AND `canceled_at` = yesterday
   - **Workouts**: Count workouts where `ended_at` between yesterday start/end
   - **Check-ins**: Count GymCheckIns where `checked_in_at` = yesterday
   - **Active trainers**: Count trainers with at least 1 workout yesterday
2. Create GymAnalytics record with `period_type = 'day'`

*Weekly rollup*:
- Run on Mondays
- Aggregate last 7 days of daily rollups
- Calculate weekly averages and totals

*Monthly rollup*:
- Run on 1st of month
- Aggregate last 30 days
- Calculate retention rate: `(clients_end - churned) / clients_start * 100`

*Quarterly/Yearly rollups*:
- Same pattern, larger time windows

**Admin dashboard queries**:
- Pre-calculated rollups enable fast queries
- "Revenue this month": `SELECT total_revenue FROM GymAnalytics WHERE period_type = 'month' AND period_start = first_of_month`
- "Client growth": Query monthly rollups, chart `new_clients - churned_clients`
- Historical data: Archive to cold storage after 1 year

---

### 6. Open Questions / Decisions Log

### 6.1 Decisions

#### Payments & Billing

- **Stripe** will be used and payments will be built last
- **Memberships**: gym is merchant of record via Stripe Connect (platform avoids gym accounting)
- **Gym sales tax**: gyms are responsible for their own sales tax reporting for memberships
- **Platform-side tax**: platform sales tax reporting remains TBD
- **Payment data**: all sensitive payment data stays in Stripe (platform avoids PCI scope as much as possible)
- **Processing fees**: Gyms can configure whether to absorb Stripe fees or pass them to clients
  - `gym_absorbs`: Gym pays all Stripe processing fees
  - `pass_to_client`: Fees added to client invoice based on configurable percentage/flat/both
- **Membership types**: Support both subscription (recurring) and session packs (one-time)
  - Subscriptions: monthly or annual billing
  - Session packs: one-time payment for X visits (until-used)
  - Plans can have optional expiration for until-used (e.g., 180 days)
- **Cancellation**: Only gym can cancel memberships (clients cannot self-cancel)
  - Recurring subscriptions: cancel at period end, remain active until expiration
  - One-time/session packs: canceled immediately, remaining visits forfeited
- **Proration/refunds**: No automatic proration; gym handles refunds manually if desired

#### Plan & Program Architecture

- **Plan vs Program**:
  - **Plan** = what a client pays for (membership/entitlement bundle)
  - **Program** = prescribed set of training activities
  - Plans control module access (feature enable/disable), e.g. programming, health integration, progress photos, etc.
  - A client can have multiple active Programs (subject to Plan entitlements)
- **Plan types**: Plans categorized by type (`gym_access`, `personal_training`, `group_classes`, etc.)
  - **Constraint**: Client can only have ONE active membership per `plan_type`
  - **Valid combo**: "Monthly Gym Access" + "10-Pack Training" (different types)
  - **Invalid combo**: "Monthly Training" + "10-Pack Training" (same type)
- **Visit entitlements**: Support multiple models
  - `unlimited`: No visit limits
  - `per_week`: X visits per week (e.g., 3x/week)
  - `per_month`: X visits per month (e.g., 8/month)
  - `per_plan_duration`: Total visits over plan lifetime (e.g., 10-pack)
- **Rollover**: Configurable per plan (unused visits can roll over or expire)
- **Until-used expiration**: Session packs can have optional expiration (e.g., 180 days)
- **Pause**: Only gym can pause memberships; pausing extends expiration date by days paused

#### Data Model

- **Client payment tracking**: Use ClientMembership entity with flexible visit entitlement tracking
  - Replaces simple `paid_through_date` with comprehensive membership lifecycle
- **PR tracking**:
  - PR uniqueness key: `client_id + exercise_id + measurement_type + rep_scheme`
  - Rep scheme IS required (1RM, 5RM, 10RM tracked separately)
  - For time/distance: `ExerciseType.pr_direction` determines if higher or lower is better
    - `minimize`: Sprint times, row times (lower is better)
    - `maximize`: Max distance, hold times (higher is better)

#### Workflows

- **Programs/workouts** are tied to a specific visit (Schedule)
- **Editing completed workouts** is gym-configurable: trainer-only OR trainer+client
- **Reps representation**: sets are line-itemed (supports supersets and variable reps like 10/8/4, differing weights, AMRAP per set)

#### Technical Implementation

- **User roles**: Multiple roles per user
  - Users can have multiple roles (e.g., Trainer + Front Desk)
  - Roles: Admin, Trainer, Front Desk, Client
  - Front Desk: Check-in operations, view schedules, monitor occupancy (read-only)
- **Client prospects**: Single `Client` entity with `client_status` field
  - Status: `prospect` | `trial` | `active` | `inactive` | `lost`
  - Allows basic lead tracking without full CRM
- **Trainer availability**:
  - Store in NoSQL as JSON (flexible, supports multi-location schedules)
  - Trainers can work different locations with different hours
  - Exceptions stored in SQL (TrainerException) for PTO/vacation tracking
  - No recurring exceptions needed (part of standard availability)
- **Exercise configuration**:
  - Exercise entity: Keep simple (default sets/reps/measurements only)
  - ProgramDayExercise: Add program-specific fields:
    - `tempo` (e.g., "3-1-1-0" for eccentric-pause-concentric-pause)
    - `weight_progression_rule` with strategies: add from average, add from PR, add from last AMRAP, manual
  - RPE: Track as measurement (not as default/target)
  - No rest time defaults
- **Authentication & Security**:
  - **OAuth2**: All API authentication uses OAuth2 2.0 standard
  - **Password storage**: Argon2id only (64 MB memory, 3 iterations, 4 threads)
  - **Password salting**: Cryptographically secure random salt (128-bit minimum), unique per password, automatically handled by Argon2id
  - **Password hash versioning**: Track hash algorithm version for future migrations (transparent upgrade on login)
  - **Password requirements**: 12+ chars, uppercase + lowercase + number + special char, breach check via Have I Been Pwned API
  - **Password reset**: Secure token-based reset (256-bit random, SHA-256 hashed, 1-hour expiration, single-use)
  - **Password reset rate limiting**: Max 3 reset requests per email per hour (prevent abuse)
  - **MFA**: Required for admin/trainer roles after 7-day grace period, optional for clients
  - **MFA methods**: TOTP (preferred), email (fallback), passkey-only (most secure)
  - **SMS MFA**: NOT supported (insecure, SIM swap attacks)
  - **Passkeys**: WebAuthn/FIDO2 support for passwordless authentication
  - **Passkey-only mode**: Users can delete password and use only passkeys (most secure)
  - **OAuth2 grants**: Support password, authorization_code (with PKCE), refresh_token, client_credentials
  - **PKCE**: Required for all authorization code flows (mobile/SPA security)
  - **Token lifetime**: Access tokens 1 hour, refresh tokens 30 days
  - **Token storage**: Never store plaintext, use SHA-256 hash
  - **OAuth2 clients**: Gym admins can create OAuth2 clients for third-party integrations
  - **OAuth2 scopes**: Fine-grained permissions (gym:read, clients:read, workouts:write, mcp:trainer, etc.)
- **MCP (Model Context Protocol) integration**:
  - **Trainer-only OAuth2 authorization** for AI assistant access (separate from general OAuth2 clients)
  - Trainers can authorize AI assistants (Claude, etc.) to access their data via OAuth2
  - **Trainers CANNOT create general OAuth2 clients** - MCP authorization is the only OAuth2 access trainers can grant
  - **Only gym admins** can create OAuth2 clients for third-party integrations
  - Scope: `mcp:trainer` grants read-only access to trainer's schedule, assigned clients, workouts
  - Security: Row-level filtering ensures trainers can only access their own data
  - Read-only: MCP cannot write/modify data (AI safety)
  - User-scoped: MCP tokens are tied to individual trainer, not gym-wide
- **Calendar export**:
  - Trainers can generate .ics calendar feed with unique OAuth2 token
  - Subscribe in any calendar app (Apple Calendar, Google Calendar, Outlook)
  - Privacy: Optional setting to hide client names in calendar
  - Token revocation: Trainers can revoke and regenerate calendar URL
- **API latency targets** (formally defined):
  - Real-time ops (auth, workout logging, scheduling, check-in): p95 < 200ms, p99 < 500ms
  - Dashboard/reporting: p95 < 1s, p99 < 2s
  - Background ops (AI, metering, notifications): Best effort, no SLA
- **Offline-first**: Full offline capability for mobile apps
  - Mobile (iOS/Android): All critical operations work offline
  - Web app: Online-only (admins on stable connections)
  - Offline operations: Check-in, workout logging, view cached data (30 days)
  - Online-only: Admin functions, program creation, reports, billing
  - Conflict resolution: Log both if two trainers edit same workout (edge case)
  - Cache: Last 30 days of data
- **Check-in & occupancy**:
  - Two check-in types: self-directed (60 min assumed) and training sessions
  - Methods: QR scan, manual name lookup, mobile app
  - Access control: Alert (don't block) when no active membership
  - Track with GymCheckIn entity
  - No explicit check-outs for MVP (assume duration)
- **Busyness calculations**: Three separate views
  - Self-directed busyness: Count active gym check-ins
  - Training busyness: Scheduled + checked-in sessions with predictive arrival
  - Per-trainer busyness: Individual trainer load
  - Predictive analytics: Use `avg_schedule_variance_minutes` + confidence intervals
  - Seasonality-aware: Different algorithms based on client tenure
    - New (<90 days): Last 90 days
    - Regular (90-365 days): Last 180 days
    - Long-term (>365 days): Year-over-year for seasonality

- **Account hierarchy & family management**:
  - Account can have multiple members (family, household)
  - Multiple primary members supported (co-parents, spouses)
  - Primary members control sub-member access and billing
  - Add-on plans for discounted family member pricing
  - Emancipation workflow for sub-members to transfer to own account
  - Age-based access: <13 no login, 13-17 with parental consent, 18+ independent
- **Compliance & privacy** (US-only, fitness/wellness):
  - Data retention: Unlimited for active, 3 years for inactive, 7 years for payment data
  - Soft delete with anonymization ("Deleted User" placeholder)
  - Right to be forgotten: Anonymize all except payment data (7-year tax retention)
  - Data export: JSON + CSV + PDF + photos (async, 7-day download link)
  - CCPA compliance met, GDPR deferred until international expansion
  - COPPA compliance: <13 must be sub-members (no independent accounts)

- **Accessibility**:
  - **WCAG 2.1 Level AA compliance** for all user-facing applications (web, iOS, Android)
  - **Color contrast**: Minimum 4.5:1 for normal text, 3:1 for large text
  - **Keyboard navigation**: All functionality accessible via keyboard
  - **Screen readers**: Full support for VoiceOver (iOS/macOS), TalkBack (Android), NVDA/JAWS (Windows)
  - **Dynamic Type**: Support system font scaling up to 200%
  - **Focus indicators**: Visible focus indicators with 2:1 contrast minimum
  - **Alternative text**: All images, icons, and non-text content have descriptive alt text
  - **Error messages**: Clear, descriptive error messages for form validation
  - **Testing**: Automated (axe DevTools, Lighthouse) + manual (keyboard-only, screen reader) + user testing with actual assistive technology users
  - **Accessibility statement**: Public page with conformance claim and contact for feedback
  - **Continuous improvement**: Audits every 6 months, accessibility training for team

### 6.2 Open Questions

#### Payment & Billing (deferred until implementation)

- **Gym subscription tiers**: per location? per trainer? per active client? flat tiers?
- **Taxes/VAT handling**: Specific requirements for different jurisdictions
- **Trial periods**: Should plans support free trial periods? How long?
- **Discounts/coupons**: Coupon system design (percentage vs flat, one-time vs recurring)
- **Payment failure behavior**: Grace period duration, access restrictions, notification sequence
- **Webhooks + reconciliation**: Specific Stripe events to handle, idempotency strategy
- **Stripe data model**: Which Stripe IDs to store (customer, subscription, payment_intent, invoice)

---

### 7. Glossary

**Fitness Terms**:
- **AMRAP**: As many reps as possible
- **PR**: Personal record
- **RPE**: Rate of perceived exertion

**Security & Authentication**:
- **Argon2id**: Memory-hard password hashing algorithm resistant to GPU/ASIC attacks
- **MFA**: Multi-Factor Authentication - requires two or more verification factors
- **TOTP**: Time-based One-Time Password (e.g., Google Authenticator)
- **WebAuthn**: Web Authentication API standard for passkeys/FIDO2
- **PKCE**: Proof Key for Code Exchange - security extension for OAuth2
- **OAuth2**: Industry-standard protocol for authorization

**Accessibility**:
- **WCAG**: Web Content Accessibility Guidelines
- **ARIA**: Accessible Rich Internet Applications - semantic markup for assistive technologies
- **Screen reader**: Software that reads screen content aloud for blind/low-vision users
- **VoiceOver**: Apple's built-in screen reader (iOS/macOS)
- **TalkBack**: Android's built-in screen reader
- **Dynamic Type**: iOS feature for system-wide font size scaling
- **Keyboard navigation**: Using Tab, Enter, Space, Arrow keys instead of mouse/touch
