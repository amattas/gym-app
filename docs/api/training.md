# Training API

Programs, workouts, and exercises endpoints.

---

## Programs

### List Programs

```http
GET /gyms/{gym_id}/programs
```

### Create Program

```http
POST /gyms/{gym_id}/programs
```

**Request**:
```json
{
  "name": "Beginner Strength",
  "description": "3-day full body program"
}
```

### Get Program

```http
GET /programs/{program_id}
```

### Update Program

```http
PATCH /programs/{program_id}
```

### Delete Program

```http
DELETE /programs/{program_id}
```

---

## Program Days

### List Program Days

```http
GET /programs/{program_id}/days
```

### Add Program Day

```http
POST /programs/{program_id}/days
```

**Request**:
```json
{
  "name": "Day A - Push",
  "order_index": 1
}
```

### Get Program Day

```http
GET /program-days/{program_day_id}
```

### Update Program Day

```http
PATCH /program-days/{program_day_id}
```

### Delete Program Day

```http
DELETE /program-days/{program_day_id}
```

### Reorder Program Days

```http
POST /programs/{program_id}/days/reorder
```

**Request**:
```json
{
  "order": ["day_id_1", "day_id_2", "day_id_3"]
}
```

---

## Program Day Exercises

### Add Exercise to Day

```http
POST /program-days/{program_day_id}/exercises
```

**Request**:
```json
{
  "exercise_id": "uuid",
  "default_sets": 3,
  "default_reps": 10,
  "tempo": "3-1-1-0",
  "notes": "Focus on form"
}
```

### Update Exercise in Day

```http
PATCH /program-day-exercises/{id}
```

### Remove Exercise from Day

```http
DELETE /program-day-exercises/{id}
```

### Reorder Exercises

```http
POST /program-days/{program_day_id}/exercises/reorder
```

---

## Client Programs

### Assign Program to Client

```http
POST /clients/{client_id}/programs
```

**Request**:
```json
{
  "program_id": "uuid"
}
```

### Get Client's Active Program

```http
GET /clients/{client_id}/programs/active
```

### Remove Program from Client

```http
DELETE /clients/{client_id}/programs/{client_program_id}
```

---

## Exercises

### List Exercises

```http
GET /exercises
```

**Query params**:
- `gym_id`: Filter by gym (null for global)
- `type`: Filter by exercise type
- `search`: Search by name

### Create Exercise

```http
POST /gyms/{gym_id}/exercises
```

**Request**:
```json
{
  "name": "Barbell Back Squat",
  "exercise_type_id": "uuid",
  "default_sets": 3,
  "default_reps_per_set": 5
}
```

### Get Exercise

```http
GET /exercises/{exercise_id}
```

### Update Exercise

```http
PATCH /exercises/{exercise_id}
```

---

## Workouts

### Start Workout

```http
POST /clients/{client_id}/workouts
```

**Request**:
```json
{
  "program_day_id": "uuid",
  "location_id": "uuid"
}
```

### Get Active Workout

```http
GET /clients/{client_id}/workouts/active
```

### Get Workout

```http
GET /workouts/{workout_id}
```

### Complete Workout

```http
POST /workouts/{workout_id}/complete
```

### Abandon Workout

```http
POST /workouts/{workout_id}/abandon
```

### List Workout History

```http
GET /clients/{client_id}/workouts
```

---

## Workout Exercises

### Update Exercise Status

```http
PATCH /workout-exercises/{id}
```

**Request**:
```json
{
  "status": "complete"
}
```

### Skip Exercise

```http
POST /workout-exercises/{id}/skip
```

---

## Workout Sets

### Log Set

```http
POST /workout-exercises/{id}/sets
```

**Request**:
```json
{
  "set_index": 1,
  "actual_reps": 10,
  "measurements": [
    { "type": "weight", "value": 135, "unit": "lbs" }
  ],
  "notes": "Easy"
}
```

### Update Set

```http
PATCH /workout-sets/{set_id}
```

### Delete Set

```http
DELETE /workout-sets/{set_id}
```

---

## Personal Records

### Get Client PRs

```http
GET /clients/{client_id}/prs
```

### Get PRs for Exercise

```http
GET /clients/{client_id}/exercises/{exercise_id}/prs
```

**Response**:
```json
{
  "data": {
    "exercise_id": "uuid",
    "prs": [
      { "rep_scheme": "1RM", "value": 315, "unit": "lbs", "achieved_at": "..." },
      { "rep_scheme": "5RM", "value": 275, "unit": "lbs", "achieved_at": "..." }
    ]
  }
}
```
