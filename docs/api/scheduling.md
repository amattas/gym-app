# Scheduling & Check-In API

Schedule and check-in management endpoints.

---

## Schedules

### List Schedules

```http
GET /schedules
```

**Query params**:
- `trainer_id`: Filter by trainer
- `client_id`: Filter by client
- `location_id`: Filter by location
- `date`: Filter by date
- `date_from`: Filter from date
- `date_to`: Filter to date
- `status`: Filter by status

### Create Schedule Entry

```http
POST /schedules
```

**Request**:
```json
{
  "client_id": "uuid",
  "trainer_id": "uuid",
  "location_id": "uuid",
  "scheduled_start": "2026-01-20T10:00:00Z",
  "scheduled_end": "2026-01-20T11:00:00Z",
  "notes": "Focus on squat form"
}
```

### Get Schedule Entry

```http
GET /schedules/{schedule_id}
```

### Update Schedule Entry

```http
PATCH /schedules/{schedule_id}
```

### Cancel Schedule Entry

```http
POST /schedules/{schedule_id}/cancel
```

**Request**:
```json
{
  "reason": "Client requested reschedule"
}
```

### Mark as No-Show

```http
POST /schedules/{schedule_id}/no-show
```

### Mark as Completed

```http
POST /schedules/{schedule_id}/complete
```

---

## Trainer Availability

### Get Trainer Availability

```http
GET /trainers/{trainer_id}/availability
```

**Response**:
```json
{
  "data": {
    "recurring": [
      {
        "day_of_week": 1,
        "location_id": "uuid",
        "start_time": "07:00",
        "end_time": "12:00"
      }
    ]
  }
}
```

### Update Trainer Availability

```http
PUT /trainers/{trainer_id}/availability
```

### Add Exception

```http
POST /trainers/{trainer_id}/exceptions
```

**Request**:
```json
{
  "exception_date": "2026-01-25",
  "exception_type": "unavailable",
  "reason": "Vacation"
}
```

### List Exceptions

```http
GET /trainers/{trainer_id}/exceptions
```

### Delete Exception

```http
DELETE /trainer-exceptions/{exception_id}
```

---

## Available Slots

### Get Available Slots

```http
GET /trainers/{trainer_id}/slots
```

**Query params**:
- `date`: Specific date
- `date_from`: Start date
- `date_to`: End date
- `location_id`: Filter by location

**Response**:
```json
{
  "data": [
    {
      "date": "2026-01-20",
      "slots": [
        { "start": "10:00", "end": "11:00", "available": true },
        { "start": "11:00", "end": "12:00", "available": false }
      ]
    }
  ]
}
```

---

## Check-Ins

### Check In Client

```http
POST /check-ins
```

**Request**:
```json
{
  "client_id": "uuid",
  "location_id": "uuid",
  "check_in_method": "manual_name",
  "schedule_id": "uuid"
}
```

### Check In via QR

```http
POST /check-ins/qr
```

**Request**:
```json
{
  "qr_code": "client_qr_code",
  "location_id": "uuid"
}
```

### Get Check-In

```http
GET /check-ins/{check_in_id}
```

### Check Out

```http
POST /check-ins/{check_in_id}/checkout
```

### Get Active Check-Ins

```http
GET /locations/{location_id}/check-ins/active
```

---

## Occupancy

### Get Current Occupancy

```http
GET /locations/{location_id}/occupancy
```

**Response**:
```json
{
  "data": {
    "current_count": 25,
    "capacity": 50,
    "percentage": 50
  }
}
```

### Get Occupancy Forecast

```http
GET /locations/{location_id}/occupancy/forecast
```

**Query params**:
- `date`: Date to forecast

**Response**:
```json
{
  "data": {
    "date": "2026-01-20",
    "slots": [
      { "time": "06:00", "predicted_count": 10 },
      { "time": "07:00", "predicted_count": 25 },
      { "time": "08:00", "predicted_count": 35 }
    ]
  }
}
```

---

## Calendar Export

### Get Calendar Feed URL

```http
GET /trainers/{trainer_id}/calendar/feed
```

**Response**:
```json
{
  "data": {
    "feed_url": "https://api.gymapp.com/calendar/abc123.ics"
  }
}
```

### Regenerate Calendar Token

```http
POST /trainers/{trainer_id}/calendar/regenerate
```
