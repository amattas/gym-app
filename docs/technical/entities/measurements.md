# Measurement & Goal Entities

All entities stored in PostgreSQL.

---

## GymMeasurementType

**Purpose**: Gym-configurable measurement types (standard + custom).

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `measurement_type_id` | UUID | Primary key |
| `gym_id` | UUID? | Null for system-wide standard types |
| `name` | string | Measurement name |
| `category` | enum | 'body_composition', 'circumference', 'vitals', 'performance', 'custom' |
| `default_unit` | string | Default unit (lbs, in, bpm, %) |
| `is_standard` | bool | True for system-provided |
| `is_active` | bool | Gym can disable |
| `sort_order` | int | Display ordering |

### Standard Types (system-seeded)

**Body Composition**: Body Weight, Body Fat %, Muscle Mass %, BMI

**Circumference**: Bicep L/R, Chest, Waist, Hips, Thigh L/R, Calf L/R, Neck

**Vitals**: Blood Pressure Systolic/Diastolic, Resting Heart Rate

**Performance**: VO2 Max, 1-Mile Run Time, Vertical Jump Height

### Rules

- Standard types shared across all gyms
- Custom types only visible to creating gym
- Gyms can deactivate standard types they don't use

---

## ClientMeasurement

**Purpose**: Manually-recorded body measurements.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `measurement_id` | UUID | Primary key |
| `client_id` | UUID | FK to Client |
| `measurement_type_id` | UUID | FK to GymMeasurementType |
| `recorded_by_user_id` | UUID | FK to User (trainer) |
| `recorded_at` | datetime | When measured |
| `value` | decimal | Measurement value |
| `unit` | string | Unit of measurement |
| `notes` | text? | Trainer notes |
| `progress_photo_id` | UUID? | FK to ProgressPhoto |

### Permissions

- Trainers can add for assigned clients
- Clients can view their own (read-only)
- Clients cannot edit/delete trainer entries
- Primary members can view sub-member measurements

---

## ClientGoal

**Purpose**: Trackable goals for progress measurement.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `goal_id` | UUID | Primary key |
| `client_id` | UUID | FK to Client |
| `created_by_user_id` | UUID | FK to User |
| `goal_type` | enum | 'measurement', 'exercise_pr', 'workout_frequency', 'custom' |
| `status` | enum | 'active', 'achieved', 'abandoned', 'expired' |

### Target Fields

| Field | Type | Description |
|-------|------|-------------|
| `target_measurement_type_id` | UUID? | For measurement goals |
| `target_exercise_id` | UUID? | For PR goals |
| `target_value` | decimal | Target value |
| `target_unit` | string | Unit |
| `target_date` | date? | Optional deadline |

### Progress Tracking (auto-updated)

| Field | Type | Description |
|-------|------|-------------|
| `baseline_value` | decimal | Starting value |
| `current_value` | decimal? | Current value |
| `progress_percentage` | decimal | (current - baseline) / (target - baseline) * 100 |
| `achieved_at` | datetime? | When goal was met |

### Metadata

| Field | Type | Description |
|-------|------|-------------|
| `notes` | text? | Description/motivation |
| `visibility` | enum | 'client_only', 'trainer', 'public' |

### Auto-Update Triggers

- New ClientMeasurement → update matching goals
- New PR achieved → update exercise PR goals
- Workout completed → update frequency goals

---

## MeasurementReminder

**Purpose**: Reminders for trainers to take client measurements.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `reminder_id` | UUID | Primary key |
| `client_id` | UUID | FK to Client |
| `measurement_type_id` | UUID | FK to GymMeasurementType |
| `last_measured_at` | datetime? | Last measurement date |
| `next_reminder_at` | datetime | Next reminder date |
| `frequency_days` | int | From gym setting |
| `reminder_sent_at` | datetime? | Last reminder sent |
| `is_snoozed` | bool | Trainer snoozed |
| `snoozed_until` | datetime? | Snooze end date |

### Behavior

- Nightly job checks for overdue measurements
- Creates in-app notification for primary trainer
- Optional email notification
- Snooze options: 3 days, 1 week, 2 weeks
