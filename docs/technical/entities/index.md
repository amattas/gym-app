# Domain Entities Index

This directory contains technical specifications for all domain entities. All entities are stored in PostgreSQL.

---

## Entity Categories

| Category | File | Entities |
|----------|------|----------|
| **Gym & Location** | [gym.md](gym.md) | Gym, Location, DomainVerification, EmailTemplate |
| **User & Auth** | [user-auth.md](user-auth.md) | User, UserPasskey, OAuth2Client, OAuth2AccessToken, PasswordResetToken |
| **Account & Client** | [client.md](client.md) | Account, Client, ProgressPhoto, HealthConnection, HealthMetricSample |
| **Membership** | [membership.md](membership.md) | PlanTemplate, ClientMembership, GymPlanLimits |
| **Training** | [training.md](training.md) | Program, ProgramDay, ProgramDayExercise, ClientProgram, Exercise, ExerciseType, Workout, WorkoutExercise, WorkoutSet, WorkoutExerciseGroup, WorkoutSetMeasurement |
| **Scheduling** | [scheduling.md](scheduling.md) | Trainer, TrainerAvailability, TrainerException, Schedule, GymCheckIn |
| **Measurements & Goals** | [measurements.md](measurements.md) | GymMeasurementType, ClientMeasurement, ClientGoal, MeasurementReminder |
| **Analytics** | [analytics.md](analytics.md) | UsageMetricRollup, WorkoutAnalytics, GymAnalytics |

---

## Entity Relationship Overview

```
Gym (top-level)
├── Location[]
├── Trainer[]
├── PlanTemplate[]
├── GymMeasurementType[]
└── GymPlanLimits (JSONB)

Account (billing entity)
├── Client[] (members)
│   ├── User (optional login)
│   ├── ClientMembership[]
│   ├── Workout[]
│   ├── ClientGoal[]
│   ├── ClientMeasurement[]
│   ├── ProgressPhoto[]
│   └── HealthConnection[]
└── Billing info

Program (training template)
├── ProgramDay[]
│   └── ProgramDayExercise[]
└── ClientProgram[] (assignments)

Workout (session instance)
├── WorkoutExercise[]
│   ├── WorkoutSet[]
│   │   └── WorkoutSetMeasurement[]
│   └── WorkoutExerciseGroup (optional)
└── WorkoutAnalytics
```

---

## Common Field Patterns

### Primary Keys
- All entities use UUID primary keys
- Format: `{entity}_id` (e.g., `gym_id`, `client_id`)

### Timestamps
- `created_at`: When the record was created
- `updated_at`: Last modification time
- `deleted_at`: Soft delete timestamp (nullable)

### Soft Deletes
- Use `deleted` boolean flag or `deleted_at` timestamp
- Soft-deleted records excluded from normal queries
- Required for compliance (GDPR/CCPA data retention)

### JSONB Columns
Used for flexible configuration data:
- `GymPlanLimits`: Feature flags, plan limits
- `PlanTemplate.payment_config`: Payment configuration
- `PlanTemplate.visit_entitlement`: Visit rules
- `TrainerAvailability.recurring`: Weekly schedule
