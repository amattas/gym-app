# Core Business Entities

This document defines the core business entities in the gym management system.

---

## Gym

A gym represents a business that uses the platform. Each gym can have multiple locations, trainers, and clients.

**Branding**:
- Logo and colors used in mobile apps and web app for gym-specific branding
- Provides white-label experience for each gym

**Measurement & Progress Settings**:
- `measurement_reminders_enabled`: Enable automatic measurement reminders for trainers
- `measurement_reminder_frequency_days`: How often to remind (e.g., 30 for monthly)
- `allow_peer_comparison`: Show client stats vs gym average
- `progress_photo_required_for_measurements`: Encourage photo with measurements

**Calendar & Integration Settings**:
- `hide_client_names_in_calendar`: Gym-wide default for trainer calendar privacy. If true, trainer .ics feeds show "Training Session" instead of client name (privacy)
  - **Precedence**: Gym default can be overridden per-trainer via their individual calendar settings

---

## Account

**Definition**: Billing and access management entity. Represents a household, individual, or corporate account. Multiple members can belong to one account for consolidated billing and family management.

**Account types**:
| Type | Description |
|------|-------------|
| `individual` | Single-person account |
| `family` | Multi-member household account |
| `corporate` | B2B corporate wellness (future feature) |

**Key features**:
- Consolidated billing (all family members billed together)
- Multiple primary members supported (co-parents, spouses, business partners)
- Primary members manage sub-members and grant/revoke login access

---

## Client

**Definition**: Represents an individual member/person within an Account. Can be primary member (manages account) or sub-member (managed by primary).

**Client status**:
| Status | Description |
|--------|-------------|
| `prospect` | Not yet a paying member |
| `trial` | Temporary trial period |
| `active` | Paying, active member |
| `inactive` | Former member, no active membership |
| `lost` | Churned, no longer engaged |
| `deleted` | Soft-deleted for compliance |

**Account member roles**:
| Role | Description |
|------|-------------|
| `primary` | Can manage account, add/remove members, control billing, grant logins to sub-members |
| `member` | Standard member, managed by primary(ies) |

**Age-based access rules**:
| Age | Access |
|-----|--------|
| Under 13 | Cannot have login (COPPA compliance), gym/trainer manages all data |
| 13-17 | Can have login if primary member grants it |
| 18+ | Can have login, can request to transfer to own account ("emancipation") |

---

## Related Documents

- [Memberships](02-memberships.md) - PlanTemplate and ClientMembership details
- [Progress](05-progress.md) - ClientGoal and measurement tracking
- [Accounts](06-accounts.md) - Account management workflows
