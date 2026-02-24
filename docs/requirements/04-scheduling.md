# Scheduling & Check-In

This document defines the check-in system, scheduling, gym occupancy, and calendar features.

---

## Check-In System

### Check-In Methods

| Method | Description |
|--------|-------------|
| **QR scan** | Client scans unique QR code on mobile app at gym entrance |
| **Manual entry** | Front desk looks up client by name and checks them in |
| **Mobile app** | Client checks in via mobile app when arriving |

### Check-In Types

#### Self-Directed Gym Visits (no trainer)
- Client checks in via scan/front desk/app
- No schedule entry required
- Assumed duration: 60 minutes

#### Training Sessions (scheduled with trainer)
- May or may not explicitly check in
- System predicts arrival based on schedule + historical patterns
- Duration: uses client's average workout duration

### Access Control

- On check-in, system checks if client has active membership
- If no active membership: **Alert** front desk/trainer (don't block check-in)
- Front desk can choose to allow check-in despite alert

### Check-Out

- For MVP: assume duration, don't track explicit check-outs
- Use expected checkout time for occupancy calculations

---

## Gym Occupancy

### Calculation

- Occupancy calculated at 15-minute granularity
- Based on:
  - Active check-ins (checked_in_at until expected_checkout_at)
  - Scheduled sessions (predicted arrivals)
  - Historical patterns

### Busyness Visualization

- Display current occupancy vs. capacity
- Show predicted busyness for upcoming time slots
- Help clients choose optimal visit times

---

## Trainer Schedule Management

### Availability

- Trainers have recurring weekly availability
- Availability can vary by location (trainers can work at multiple locations)
- Example: Mon 7am-12pm at Location A, Tue 3pm-9pm at Location B

### Exceptions

- One-off exceptions for PTO/vacation
- Can mark specific dates as:
  - `unavailable`: Trainer not working
  - `available`: Override for normally unavailable day

### Schedule Entries

Each schedule entry links:
- Trainer
- Client
- Location
- Time slot (start/end)
- Status: `tentative` | `confirmed` | `canceled` | `no_show` | `completed`

---

## Calendar Export (iCalendar)

### Trainer Calendar Feed

- Each trainer has a unique, private calendar URL
- Trainers can subscribe to this URL in any calendar app (Apple Calendar, Google Calendar, Outlook, etc.)
- Calendar feed contains all scheduled training sessions

### Feed Updates

- Calendar feed regenerated on schedule changes
- 15-minute cache for performance

### Privacy Options

- Gym setting: `hide_client_names_in_calendar`
- If enabled, events show "Training Session" instead of client names
- Can be overridden per-trainer

---

## Self-Scheduling (Optional)

- Admin can enable/disable self-scheduling per gym
- When enabled:
  - Clients can view available time slots
  - Clients can book/cancel sessions within rules
  - Rules may include: advance booking window, cancellation policy

---

## Schedule Status Flow

```
tentative → confirmed → completed
                     → no_show
          → canceled
```

| Status | Description |
|--------|-------------|
| `tentative` | Proposed but not confirmed |
| `confirmed` | Both trainer and client confirmed |
| `canceled` | Session was canceled |
| `no_show` | Client didn't show up |
| `completed` | Session occurred |

---

## Related Documents

- [Memberships](02-memberships.md) - Visit entitlements and deduction
- [Training](03-training.md) - Workout execution during visits
