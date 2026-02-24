# Progress Tracking

This document defines measurements, goals, progress photos, and health data integrations.

---

## Measurements

### Measurement Types

Gyms can configure which measurement types they track:

**Body Composition**:
- Body Weight, Body Fat %, Muscle Mass %, BMI

**Circumference**:
- Bicep (L/R), Chest, Waist, Hips, Thigh (L/R), Calf (L/R), Neck

**Vitals**:
- Blood Pressure (Systolic/Diastolic), Resting Heart Rate

**Performance**:
- VO2 Max, 1-Mile Run Time, Vertical Jump Height

**Custom Types**:
- Gyms can create custom measurement types (e.g., "Flexibility Score", "Grip Strength")

### Recording Workflow

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

### Measurement Reminders

**Nightly job** (scheduled using `Gym.timezone`):
1. Query all gyms where `measurement_reminders_enabled = true`
2. For each gym, get all active clients with assigned trainers
3. For each client: check if `(today - last_measured_at) > frequency_days` and not snoozed
4. If overdue: Create notification for trainer
5. Group reminders per trainer: "5 clients due for measurements today"

**When trainer records measurement**:
1. Update last measured timestamp
2. Calculate next reminder date = now + frequency_days
3. Clear reminder and snooze flags

**Snooze reminder**:
1. Trainer views notification, clicks "Snooze"
2. Choose snooze duration: 3 days, 1 week, 2 weeks
3. Reminder won't trigger again until after snooze period

---

## Goals (ClientGoal)

### Goal Types

| Type | Description | Example |
|------|-------------|---------|
| `measurement` | Target body measurement | Lose 10 lbs, reach 12% body fat |
| `exercise_pr` | Target personal record | 300 lb squat 1RM |
| `workout_frequency` | Target workout consistency | 3x per week for 12 weeks |
| `custom` | Free-form goal with manual tracking | Run a 5K |

### Goal Lifecycle

| Status | Description |
|--------|-------------|
| `active` | Currently working toward goal |
| `achieved` | Goal successfully reached |
| `abandoned` | Goal discontinued |

### Goal Creation Workflow

1. Trainer or client creates goal (depends on gym settings)
2. Select goal type and target value
3. System captures baseline value from latest measurement/PR
4. Set status = 'active'
5. Goal appears in client dashboard and trainer view

### Auto-Update Triggers

**When new measurement recorded**:
1. Query for active goals where target measurement type matches
2. Update current value with latest measurement
3. Recalculate progress: `(current - baseline) / (target - baseline) * 100`
4. If goal achieved:
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

---

## Progress Photos

### Features

- Client can upload progress photos tied to a date/time
- Photos can be private to client + assigned trainer(s) + gym admins (configurable)
- Optional tagging: weight, notes, body measurements snapshot, goal phase
- Storage must support secure, signed URL access
- Trainers can view photo trends to help clients stay on track with goals

### Visibility Levels

| Level | Who Can See |
|-------|-------------|
| `client_only` | Only the client |
| `trainer` | Client + assigned trainers |
| `gym_admin` | Client + trainers + gym admins |

### Integration with Measurements

1. When recording measurements, trainer can optionally take progress photo
2. Photo linked to measurement record
3. Client measurement history shows thumbnails next to measurements
4. Trainer can view side-by-side photo comparisons over time
5. If `progress_photo_required_for_measurements = true`: System reminds trainer to take photo

---

## Personal Records (PRs)

### PR Tracking

- Client has PR per exercise + measurement type + rep scheme
- Examples:
  - Back Squat: weight 1RM, weight 5RM
  - 400m Row: time (minimize)
  - Plank: hold time (maximize)

### PR Direction

| Direction | Description |
|-----------|-------------|
| `maximize` | Higher is better (weight, reps, distance) |
| `minimize` | Lower is better (time for sprints, runs) |

### Auto-Detection

- When workout is logged, system checks if any set is a new PR
- PRs are tracked per rep scheme (1RM, 5RM, 10RM, etc.)
- Notifications sent when new PR is achieved

---

## Health Data Integrations

### Supported Sources

| Platform | Source |
|----------|--------|
| iOS | Apple Health (HealthKit) |
| Android | Google Fit / Health Connect |

### Connection Management

- Users can connect/disconnect health sources
- Data is imported on a schedule (or on app open) with explicit user permission
- Users can restrict which metrics are shared with trainers

### Metrics Imported

- Steps
- Active energy/calories
- Resting heart rate
- Sleep duration
- Weight (from smart scales)
- Other supported metrics

### Privacy

- Imported metrics stored as time-series records
- Summarized for trainers (not raw data)
- User controls what is shared

---

## Peer Comparison (Optional)

If gym enables `allow_peer_comparison`:

1. Client views their measurement/goal progress
2. Optional toggle: "Compare with gym average"
3. System calculates anonymized gym average for same measurement type
4. Display: "You: 180 lbs | Gym average: 175 lbs"
5. Only show if >= 10 clients have this measurement (privacy threshold)

---

## Related Documents

- [Training](03-training.md) - Workout logging and PR tracking
- [Entities](01-entities.md) - ClientGoal entity
