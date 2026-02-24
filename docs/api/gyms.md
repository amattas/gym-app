# Gyms & Locations API

Gym and location management endpoints.

---

## Gyms

### Get Current Gym

```http
GET /gyms/current
```

Returns the gym for the current user's context.

### Get Gym by ID

```http
GET /gyms/{gym_id}
```

### Update Gym

```http
PATCH /gyms/{gym_id}
```

**Request**:
```json
{
  "name": "PowerLift Gym",
  "timezone": "America/New_York",
  "settings": {
    "measurement_reminders_enabled": true,
    "measurement_reminder_frequency_days": 30
  }
}
```

### Update Gym Theming

```http
PATCH /gyms/{gym_id}/theme
```

**Request**:
```json
{
  "theme_preset": "fitness-dark",
  "theme_config": {
    "mode": "dark",
    "colors": {
      "primary": "#3B82F6"
    }
  },
  "logo_url": "https://cdn.example.com/logo.png"
}
```

---

## Locations

### List Locations

```http
GET /gyms/{gym_id}/locations
```

### Create Location

```http
POST /gyms/{gym_id}/locations
```

**Request**:
```json
{
  "name": "Downtown Branch",
  "address": {
    "street1": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "US"
  }
}
```

### Get Location

```http
GET /locations/{location_id}
```

### Update Location

```http
PATCH /locations/{location_id}
```

### Delete Location

```http
DELETE /locations/{location_id}
```

---

## Gym Settings

### Get Settings

```http
GET /gyms/{gym_id}/settings
```

### Update Settings

```http
PATCH /gyms/{gym_id}/settings
```

**Request**:
```json
{
  "measurement_reminders_enabled": true,
  "allow_peer_comparison": false,
  "hide_client_names_in_calendar": true
}
```

---

## Custom Domains (Enterprise)

### Configure Email Domain

```http
POST /gyms/{gym_id}/domains/email
```

**Request**:
```json
{
  "domain": "powerliftgym.com"
}
```

**Response**:
```json
{
  "data": {
    "domain": "powerliftgym.com",
    "status": "pending_verification",
    "dns_records": [
      {
        "type": "TXT",
        "host": "_gymapp-verify.powerliftgym.com",
        "value": "gymapp-verify=abc123..."
      }
    ]
  }
}
```

### Verify Domain

```http
POST /gyms/{gym_id}/domains/email/verify
```

### Get Domain Status

```http
GET /gyms/{gym_id}/domains/email
```

### Configure Login Domain

```http
POST /gyms/{gym_id}/domains/login
```

---

## Plan Limits

### Get Plan Limits

```http
GET /gyms/{gym_id}/limits
```

**Response**:
```json
{
  "data": {
    "plan": "pro",
    "limits": {
      "max_locations": 5,
      "max_trainers": 20,
      "max_clients": 500
    },
    "usage": {
      "locations": 2,
      "trainers": 8,
      "clients": 125
    }
  }
}
```
