# Training Entities

All entities stored in PostgreSQL.

---

## Program

**Purpose**: Reusable set of program days assignable to clients.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `program_id` | UUID | Primary key |
| `gym_id` | UUID | FK to Gym |
| `name` | string | Program name |
| `description` | text? | Program description |
| `created_by_trainer_id` | UUID | FK to Trainer |

### Relationships

- Has many ProgramDays
- Has many ClientPrograms (assignments)

---

## ProgramDay

**Purpose**: A single workout template within a program.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `program_day_id` | UUID | Primary key |
| `program_id` | UUID | FK to Program |
| `name` | string | Day name (e.g., "Day A", "Push Day") |
| `order_index` | int | Order within program |
| `next_program_day_id` | UUID? | FK for circular progression |

### Constraints

- Last day should point to first day (circular)
- Validate no broken links in the chain

### Relationships

- Belongs to Program
- Has many ProgramDayExercises

---

## ProgramDayExercise

**Purpose**: Exercise template within a program day.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `program_day_exercise_id` | UUID | Primary key |
| `program_day_id` | UUID | FK to ProgramDay |
| `exercise_id` | UUID | FK to Exercise |
| `order_index` | int | Order within day |
| `default_sets` | int | Planned number of sets |
| `default_reps` | int/JSON | Planned reps (can be range) |
| `tempo` | string? | Tempo (e.g., "3-1-1-0") |
| `notes` | text? | Trainer notes |

### Weight Progression Rule (JSONB)

```json
{
  "strategy": "add_from_last_amrap",  // add_from_average, add_from_pr, manual
  "increment_amount": 5,
  "increment_unit": "lbs"
}
```

---

## ClientProgram

**Purpose**: Assignment of a program to a client.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `client_program_id` | UUID | Primary key |
| `client_id` | UUID | FK to Client |
| `program_id` | UUID | FK to Program |
| `current_program_day_id` | UUID | FK to current ProgramDay |
| `assigned_at` | datetime | When assigned |
| `assigned_by_trainer_id` | UUID | FK to Trainer |
| `status` | enum | 'active', 'completed', 'removed' |

---

## Exercise

**Purpose**: Exercise definition.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `exercise_id` | UUID | Primary key |
| `gym_id` | UUID? | Null for global exercises |
| `name` | string | Exercise name |
| `exercise_type_id` | UUID | FK to ExerciseType |
| `image_url` | string? | Demo image/video |
| `default_sets` | int? | Default number of sets |
| `default_reps_per_set` | int? | Default reps |

---

## ExerciseType

**Purpose**: Categorization of exercises with measurement rules.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `exercise_type_id` | UUID | Primary key |
| `name` | string | Type name (Lift, Exertion, etc.) |
| `measurements_allowed` | JSON | Allowed measurement types |
| `pr_direction` | enum | 'maximize' or 'minimize' |

### PR Direction Examples

- `maximize`: Weight lifted, distance, hold time, reps
- `minimize`: Sprint times, rowing for time

---

## Workout

**Purpose**: A single training session instance.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `workout_id` | UUID | Primary key |
| `client_id` | UUID | FK to Client |
| `trainer_id` | UUID? | FK to Trainer (null for self-guided) |
| `location_id` | UUID | FK to Location |
| `program_id` | UUID? | FK to Program (null for ad-hoc) |
| `program_day_id` | UUID? | FK to ProgramDay |
| `check_in_id` | UUID? | FK to GymCheckIn |
| `started_at` | datetime | When workout started |
| `ended_at` | datetime? | When workout ended |
| `status` | enum | 'in_progress', 'completed', 'abandoned' |

### Relationships

- Has many WorkoutExercises
- Has one WorkoutAnalytics

---

## WorkoutExercise

**Purpose**: Exercise instance within a workout.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `workout_exercise_id` | UUID | Primary key |
| `workout_id` | UUID | FK to Workout |
| `exercise_id` | UUID | FK to Exercise |
| `workout_exercise_group_id` | UUID? | FK for supersets |
| `status` | enum | 'incomplete', 'complete', 'skipped' |
| `order_index` | int | Order within workout |

### Relationships

- Has many WorkoutSets

---

## WorkoutSet

**Purpose**: Individual set within a workout exercise.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `workout_set_id` | UUID | Primary key |
| `workout_exercise_id` | UUID | FK to WorkoutExercise |
| `set_index` | int | Set number |
| `planned_reps` | int? | Target reps |
| `actual_reps` | int? | Performed reps |
| `is_amrap` | bool | As many reps as possible |
| `notes` | text? | Set notes |

### Relationships

- Has many WorkoutSetMeasurements

---

## WorkoutExerciseGroup

**Purpose**: Grouping for supersets/circuits.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `workout_exercise_group_id` | UUID | Primary key |
| `workout_id` | UUID | FK to Workout |
| `name` | string? | Group name (e.g., "Superset A") |
| `order_index` | int | Order within workout |

---

## WorkoutSetMeasurement

**Purpose**: Measurements for a workout set.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `measurement_id` | UUID | Primary key |
| `workout_set_id` | UUID | FK to WorkoutSet |
| `type` | enum | 'weight', 'time', 'distance', 'rpe' |
| `value` | decimal | Measurement value |
| `unit` | string | Unit of measurement |
