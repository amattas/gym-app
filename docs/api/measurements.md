# Measurements & Goals API

Measurements, goals, and progress tracking endpoints.

---

## Measurement Types

### List Measurement Types

```http
GET /gyms/{gym_id}/measurement-types
```

**Query params**:
- `category`: Filter by category
- `include_inactive`: Include deactivated types

### Create Custom Measurement Type

```http
POST /gyms/{gym_id}/measurement-types
```

**Request**:
```json
{
  "name": "Grip Strength",
  "category": "performance",
  "default_unit": "lbs"
}
```

### Update Measurement Type

```http
PATCH /measurement-types/{measurement_type_id}
```

### Deactivate Measurement Type

```http
POST /measurement-types/{measurement_type_id}/deactivate
```

---

## Client Measurements

### List Measurements

```http
GET /clients/{client_id}/measurements
```

**Query params**:
- `measurement_type_id`: Filter by type
- `from_date`: Filter from date
- `to_date`: Filter to date

### Record Measurement

```http
POST /clients/{client_id}/measurements
```

**Request**:
```json
{
  "measurements": [
    { "measurement_type_id": "uuid", "value": 180, "unit": "lbs" },
    { "measurement_type_id": "uuid", "value": 15, "unit": "%" }
  ],
  "notes": "Morning weigh-in",
  "progress_photo_id": "uuid"
}
```

### Get Measurement

```http
GET /measurements/{measurement_id}
```

### Delete Measurement

```http
DELETE /measurements/{measurement_id}
```

### Get Measurement History

```http
GET /clients/{client_id}/measurements/{measurement_type_id}/history
```

**Response**:
```json
{
  "data": [
    { "value": 185, "unit": "lbs", "recorded_at": "2026-01-01T00:00:00Z" },
    { "value": 182, "unit": "lbs", "recorded_at": "2026-01-15T00:00:00Z" },
    { "value": 180, "unit": "lbs", "recorded_at": "2026-01-29T00:00:00Z" }
  ]
}
```

---

## Goals

### List Goals

```http
GET /clients/{client_id}/goals
```

**Query params**:
- `status`: Filter by status (active, achieved, abandoned)
- `goal_type`: Filter by type

### Create Goal

```http
POST /clients/{client_id}/goals
```

**Request** (Measurement goal):
```json
{
  "goal_type": "measurement",
  "target_measurement_type_id": "uuid",
  "target_value": 175,
  "target_unit": "lbs",
  "target_date": "2026-06-01",
  "notes": "Lose 10 lbs by summer"
}
```

**Request** (Exercise PR goal):
```json
{
  "goal_type": "exercise_pr",
  "target_exercise_id": "uuid",
  "target_value": 315,
  "target_unit": "lbs",
  "notes": "3 plate squat"
}
```

**Request** (Workout frequency goal):
```json
{
  "goal_type": "workout_frequency",
  "target_value": 12,
  "target_unit": "workouts",
  "target_date": "2026-02-01",
  "notes": "12 workouts this month"
}
```

### Get Goal

```http
GET /goals/{goal_id}
```

### Update Goal

```http
PATCH /goals/{goal_id}
```

### Abandon Goal

```http
POST /goals/{goal_id}/abandon
```

### Get Goal Progress

```http
GET /goals/{goal_id}/progress
```

**Response**:
```json
{
  "data": {
    "baseline_value": 185,
    "current_value": 180,
    "target_value": 175,
    "progress_percentage": 50,
    "trend": "on_track"
  }
}
```

---

## Progress Photos

### List Progress Photos

```http
GET /clients/{client_id}/photos
```

### Upload Progress Photo

```http
POST /clients/{client_id}/photos
```

**Request** (multipart/form-data):
- `file`: Image file
- `captured_at`: When photo was taken
- `visibility`: client_only, trainer, gym_admin
- `notes`: Optional notes

### Get Progress Photo

```http
GET /photos/{photo_id}
```

### Update Progress Photo

```http
PATCH /photos/{photo_id}
```

### Delete Progress Photo

```http
DELETE /photos/{photo_id}
```

### Get Photo Comparison

```http
GET /clients/{client_id}/photos/compare
```

**Query params**:
- `photo_id_1`: First photo
- `photo_id_2`: Second photo

---

## Measurement Reminders

### Get Pending Reminders

```http
GET /trainers/{trainer_id}/reminders/measurements
```

### Snooze Reminder

```http
POST /measurement-reminders/{reminder_id}/snooze
```

**Request**:
```json
{
  "snooze_days": 7
}
```

### Dismiss Reminder

```http
POST /measurement-reminders/{reminder_id}/dismiss
```

---

## Peer Comparison (if enabled)

### Get Gym Averages

```http
GET /gyms/{gym_id}/measurements/averages
```

**Query params**:
- `measurement_type_id`: Filter by type

**Response**:
```json
{
  "data": [
    {
      "measurement_type_id": "uuid",
      "name": "Body Weight",
      "average_value": 175,
      "unit": "lbs",
      "sample_size": 45
    }
  ]
}
```

Only returns data if sample_size >= 10 (privacy threshold).
