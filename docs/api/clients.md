# Clients & Accounts API

Client and account management endpoints.

---

## Accounts

### Create Account

```http
POST /accounts
```

**Request**:
```json
{
  "account_type": "individual",
  "billing_email": "john@example.com",
  "primary_member": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "date_of_birth": "1990-01-15"
  }
}
```

### Get Account

```http
GET /accounts/{account_id}
```

### Update Account

```http
PATCH /accounts/{account_id}
```

### Add Family Member

```http
POST /accounts/{account_id}/members
```

**Request**:
```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "date_of_birth": "2010-05-20",
  "relationship": "child",
  "grant_login": false
}
```

### Remove Family Member

```http
DELETE /accounts/{account_id}/members/{client_id}
```

### Grant Login Access

```http
POST /accounts/{account_id}/members/{client_id}/login
```

### Revoke Login Access

```http
DELETE /accounts/{account_id}/members/{client_id}/login
```

---

## Clients

### List Clients

```http
GET /clients
```

**Query params**:
- `status`: Filter by status (prospect, trial, active, inactive)
- `trainer_id`: Filter by assigned trainer
- `location_id`: Filter by primary location
- `search`: Search by name/email

### Create Client (Prospect)

```http
POST /clients
```

**Request**:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "date_of_birth": "1990-01-15",
  "primary_location_id": "uuid",
  "primary_trainer_id": "uuid"
}
```

### Get Client

```http
GET /clients/{client_id}
```

### Update Client

```http
PATCH /clients/{client_id}
```

### Update Client Status

```http
PATCH /clients/{client_id}/status
```

**Request**:
```json
{
  "status": "active",
  "reason": "Converted from trial"
}
```

### Assign Trainer

```http
PATCH /clients/{client_id}/trainer
```

**Request**:
```json
{
  "trainer_id": "uuid"
}
```

### Get Client Summary

```http
GET /clients/{client_id}/summary
```

Returns overview including recent workouts, goals, measurements.

### Get Client AI Summary

```http
GET /clients/{client_id}/ai-summary
```

Returns AI-generated summary of client's progress.

---

## Member Emancipation

### Request Emancipation

```http
POST /accounts/{account_id}/members/{client_id}/emancipate
```

Sub-member (18+) requests to transfer to own account.

### Approve Emancipation

```http
POST /accounts/{account_id}/members/{client_id}/emancipate/approve
```

Primary member approves the transfer.
