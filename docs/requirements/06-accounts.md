# Account & Family Management

This document defines account management, family accounts, and member workflows.

---

## Account Types

| Type | Description |
|------|-------------|
| `individual` | Single-person account |
| `family` | Multi-member household account |
| `corporate` | B2B corporate wellness (future feature) |

---

## Account Creation

1. New signups create an Account with `account_type = 'individual'`
2. First Client created as `member_role = 'primary'`
3. Primary member creates User (login) during signup

---

## Member Roles

| Role | Permissions |
|------|-------------|
| `primary` | Manage account, add/remove members, control billing, grant logins to sub-members |
| `member` | Standard member, managed by primary(ies) |

### Multiple Primary Members

- Account can have multiple `member_role = 'primary'`
- Use case: Co-parents, spouses, business partners
- All primaries have equal account management permissions

---

## Adding Sub-Members

**Workflow** (by primary member):

1. Primary navigates to "Add Family Member"
2. Enter: name, date_of_birth, relationship (spouse, child, parent, etc.)
3. System creates Client with `member_role = 'member'`
4. If `date_of_birth` indicates age >= 13:
   - Primary can optionally grant login access
   - System creates User linked to Client
   - Sub-member receives email to set password
5. If age < 13:
   - No login created (COPPA compliance)
   - Trainer/gym manages all data for minor
   - Parent contact info stored for communication

---

## Age-Based Access Rules

| Age | Access |
|-----|--------|
| **Under 13** | Cannot have login (COPPA compliance), gym/trainer manages all data |
| **13-17** | Can have login if primary member grants it |
| **18+** | Can have login, can request to transfer to own account ("emancipation") |

---

## Login Management

### Grant Login (by primary member)

- Primary can create login for sub-member aged 13+
- System creates User linked to Client
- Sub-member receives email to set password

### Revoke Login (by primary member)

- Primary can disable `login_enabled` to revoke access
- User record remains (for audit), but login blocked
- Can be re-enabled later

---

## Membership Assignment

### Assign Plan to Sub-Member

1. Primary selects sub-member
2. Choose from available plans (base or addon)
3. If addon plan:
   - Validate: account has primary member with required base plan
   - Link addon to base plan
   - Apply discount
4. Create ClientMembership for sub-member
5. Billing consolidated at Account level

### Add-On Plan Rules

- Add-on plans can only be assigned to members in an account with a required base plan
- Example: "Family Member Training Add-On" requires primary member to have personal training plan
- If primary cancels base plan → all linked addon plans also cancel

---

## Member Emancipation

**Definition**: Sub-member transfers to their own independent account.

### Triggers

- Sub-member turns 18
- Sub-member requests independence
- Primary member approves transfer

### Process

1. Create new Account (`account_type = 'individual'`)
2. Update Client: `account_id = new_account`, `member_role = 'primary'`
3. Transfer active ClientMemberships to new account
4. Historical data (workouts, PRs, photos) stays with Client
5. Notify old account primary members
6. New account responsible for own billing going forward

---

## Account Deletion

### Deleting a Primary Member

**If multiple primaries exist**:
- Remove this primary only
- Account stays active
- Other primaries maintain control

**If last (only) primary**:
1. Soft-delete all Clients in account (cascade)
2. Set `client_status = 'deleted'`
3. Anonymize all PII (GDPR/CCPA compliance)
4. Retain payment history for 7 years (tax compliance)
5. Account marked as deleted
6. Send confirmation emails
7. Audit log records deletion with member numbers only (not PII)

---

## Consolidated Billing

- All family members billed together under the Account
- Single invoice/payment method for all memberships
- Primary members can view billing history
- Primary members can update payment methods

---

## Related Documents

- [Entities](01-entities.md) - Account and Client entities
- [Memberships](02-memberships.md) - Plan templates and memberships
