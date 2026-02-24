# Scheduling Entities

All entities stored in PostgreSQL.

---

## Trainer

**Purpose**: Trainer/staff member at a gym.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `trainer_id` | UUID | Primary key |
| `user_id` | UUID | FK to User |
| `gym_id` | UUID | FK to Gym |
| `primary_location_id` | UUID | FK to Location |
| `hire_date` | date? | When hired |
| `status` | enum | 'active', 'inactive' |

### Calendar Settings

| Field | Type | Description |
|-------|------|-------------|
| `calendar_feed_token` | string | Unique token for .ics feed |
| `hide_client_names_in_calendar` | bool? | Override gym default |

### Relationships

- Has one TrainerAvailability
- Has many TrainerExceptions
- Has many Schedules
- Has many Clients (primary_trainer)

---

## TrainerAvailability

**Purpose**: Trainer's recurring weekly schedule.

### Storage Options

**Option 1**: JSONB column on Trainer table
**Option 2**: Separate table with normalized rows

### Structure (JSONB)

```json
{
  "trainer_id": "uuid",
  "recurring": [
    {
      "day_of_week": 1,  // 0=Sunday, 6=Saturday
      "location_id": "uuid",
      "start_time": "07:00",
      "end_time": "12:00"
    },
    {
      "day_of_week": 2,
      "location_id": "uuid",
      "start_time": "15:00",
      "end_time": "21:00"
    }
  ],
  "updated_at": "2024-01-19T10:00:00Z"
}
```

### Features

- Trainers can work at multiple locations on different days
- Time ranges define available hours for booking

---

## TrainerException

**Purpose**: One-off exceptions to recurring schedule.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `trainer_exception_id` | UUID | Primary key |
| `trainer_id` | UUID | FK to Trainer |
| `exception_date` | date | Date of exception |
| `exception_type` | enum | 'unavailable', 'available' |
| `reason` | text? | Reason (e.g., "Vacation") |
| `created_by_user_id` | UUID | Who created |

### Use Cases

- PTO/vacation tracking
- Holiday overrides
- Special availability days

---

## Schedule

**Purpose**: Scheduled session between trainer and client.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `schedule_id` | UUID | Primary key |
| `client_id` | UUID | FK to Client |
| `trainer_id` | UUID? | FK to Trainer |
| `location_id` | UUID | FK to Location |
| `scheduled_start` | datetime | Start time |
| `scheduled_end` | datetime | End time |
| `status` | enum | 'tentative', 'confirmed', 'canceled', 'no_show', 'completed' |
| `created_by_user_id` | UUID | Who created |
| `notes` | text? | Session notes |

### Status Flow

```
tentative → confirmed → completed
                     → no_show
          → canceled
```

### Relationships

- Has one GymCheckIn (optional)
- Has one Workout (optional)

---

## GymCheckIn

**Purpose**: Tracks client check-ins for occupancy and attendance.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `check_in_id` | UUID | Primary key |
| `client_id` | UUID | FK to Client |
| `location_id` | UUID | FK to Location |
| `schedule_id` | UUID? | FK to Schedule (null for self-directed) |
| `check_in_method` | enum | 'qr_scan', 'manual_name', 'mobile_app' |
| `checked_in_by_user_id` | UUID? | Front desk/trainer who checked in |
| `checked_in_at` | datetime | Check-in time |
| `checked_out_at` | datetime? | Check-out time (null if still in) |
| `expected_checkout_at` | datetime | For occupancy calculations |
| `check_in_type` | enum | 'self_directed', 'training_session' |

### Behavior

- Self-directed: Assume 60-minute duration
- Training session: Use client's avg_workout_duration_minutes
- Alert on inactive membership (don't block check-in)
