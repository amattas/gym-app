# Glossary

This document defines business and fitness terms used throughout the requirements.

---

## Business Terms

| Term | Definition |
|------|------------|
| **Account** | Billing entity; represents household, individual, or corporate account |
| **Plan** | What a client pays for (membership/entitlement bundle) |
| **Program** | Prescribed set of training activities |
| **Membership** | Active or historical plan assignment to a client |
| **Visit entitlement** | Rules governing how many visits a membership includes |
| **Rollover** | Unused visits carrying forward to next period |
| **Pause** | Temporary suspension of membership (extends expiration) |
| **Emancipation** | Sub-member transferring to own independent account |
| **Add-on plan** | Discounted membership for family members |
| **Plan type** | Category of membership (gym_access, personal_training, group_classes) |
| **Processing fee** | Stripe transaction fee (can be gym-absorbed or passed to client) |

---

## User Roles

| Role | Definition |
|------|------------|
| **Admin** | Manages gyms/locations, global settings, trainer permissions, billing rules |
| **Trainer** | Manages clients, assigns programs, records workouts, reviews progress |
| **Front Desk** | Checks in clients, views schedule, monitors gym occupancy (read-only) |
| **Client** | Views schedule, follows program, logs workouts, sees history |
| **Primary Member** | Account member who manages billing and can add/remove family members |
| **Sub-Member** | Account member managed by primary member(s) |

---

## Fitness Terms

| Term | Definition |
|------|------------|
| **AMRAP** | As Many Reps As Possible - perform maximum reps in given time/set |
| **PR** | Personal Record - best performance for a given exercise |
| **RPE** | Rate of Perceived Exertion - subjective measure of workout intensity (1-10 scale) |
| **Program Day** | A single workout within a program |
| **Rep Scheme** | Number of repetitions (e.g., 1RM, 5RM, 10RM) |
| **1RM** | One-Rep Max - maximum weight for a single repetition |
| **5RM** | Five-Rep Max - maximum weight for five repetitions |
| **Superset** | Two exercises performed back-to-back without rest |
| **Circuit** | Multiple exercises performed in sequence with minimal rest |
| **Tempo** | Speed of exercise execution (e.g., "3-1-1-0" for eccentric-pause-concentric-pause) |

---

## Membership Status

| Status | Definition |
|--------|------------|
| **Active** | Currently active, client can use services |
| **Paused** | Temporarily suspended (extends expiration date) |
| **Expired** | Ended naturally (time or visits exhausted) |
| **Canceled** | Gym-initiated cancellation |

---

## Client Status

| Status | Definition |
|--------|------------|
| **Prospect** | Not yet a paying member |
| **Trial** | Temporary trial period |
| **Active** | Paying, active member |
| **Inactive** | Former member, no active membership |
| **Lost** | Churned, no longer engaged |
| **Deleted** | Soft-deleted for compliance |

---

## Schedule Status

| Status | Definition |
|--------|------------|
| **Tentative** | Proposed but not confirmed |
| **Confirmed** | Both trainer and client confirmed |
| **Canceled** | Session was canceled |
| **No-Show** | Client didn't show up |
| **Completed** | Session occurred |

---

## Measurement Categories

| Category | Examples |
|----------|----------|
| **Body Composition** | Body Weight, Body Fat %, Muscle Mass %, BMI |
| **Circumference** | Bicep, Chest, Waist, Hips, Thigh, Calf, Neck |
| **Vitals** | Blood Pressure, Resting Heart Rate |
| **Performance** | VO2 Max, 1-Mile Run Time, Vertical Jump |
