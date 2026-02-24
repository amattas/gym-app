# Compliance & Privacy Requirements

This document defines compliance requirements for GDPR, CCPA, COPPA, and other regulations.

---

## GDPR (EU)

### Applicability
Applies to all EU residents, regardless of where gym is located.

### Key Requirements

#### Lawful Basis for Processing

| Data | Lawful Basis |
|------|--------------|
| Account data | Contract performance |
| Workout history | Contract performance |
| Health data | Explicit consent |
| Marketing | Explicit consent |
| Analytics | Legitimate interest |

#### Data Subject Rights

| Right | Implementation |
|-------|----------------|
| Access | Export all personal data |
| Rectification | Edit profile data |
| Erasure | Delete account (soft delete + anonymize) |
| Portability | Export in machine-readable format |
| Restriction | Pause data processing |
| Object | Opt-out of marketing, analytics |

#### Consent Management

- Explicit opt-in for marketing
- Separate consent for health data
- Record consent timestamp and version
- Easy withdrawal mechanism

---

## CCPA (California)

### Applicability
Applies to California residents if gym meets thresholds.

### Key Requirements

| Right | Implementation |
|-------|----------------|
| Know | Disclose data collected |
| Delete | Delete personal information |
| Opt-out | "Do Not Sell" option |
| Non-discrimination | Equal service regardless of rights exercised |

### Notice Requirements

- Privacy policy link in footer
- "Do Not Sell My Personal Information" link
- Notice at collection

---

## COPPA (Children Under 13)

### Applicability
Applies to children under 13 in the United States.

### Key Requirements

- **No login for children under 13**
- Parental/guardian consent required
- Minimal data collection
- Data managed by trainer/gym

### Implementation

| Age | Access |
|-----|--------|
| Under 13 | No User account, managed by parent/gym |
| 13-17 | Account with parental consent |
| 18+ | Full account access |

### Parental Controls

- Parent can view child's data
- Parent can request data deletion
- Parent can revoke consent

---

## PCI DSS (Payment Cards)

### Approach
Use Stripe Connect to avoid PCI scope.

### Requirements

- Never store card numbers
- Never log card data
- Use Stripe.js for tokenization
- HTTPS for all payment pages

### Stripe Integration

| Component | Handling |
|-----------|----------|
| Card entry | Stripe Elements |
| Payment processing | Stripe API |
| Subscriptions | Stripe Billing |
| Refunds | Stripe Dashboard/API |

---

## Data Retention

### Retention Periods

| Data Type | Active | After Deletion |
|-----------|--------|----------------|
| Account data | Indefinite | Anonymized |
| Workout history | Indefinite | Anonymized |
| Payment records | 7 years | 7 years (tax) |
| Audit logs | 7 years | 7 years |
| Session logs | 90 days | Deleted |
| Marketing consent | Until withdrawn | Deleted |

### Anonymization

When data is deleted:
1. Replace name with "Deleted User #{id}"
2. Replace email with hash
3. Remove phone, address
4. Keep workout data for analytics (anonymized)
5. Retain payment records (legal requirement)

---

## Data Export

### Format
- JSON (machine-readable)
- CSV (human-readable)

### Included Data
- Profile information
- Workout history
- Measurements
- Goals
- Progress photos (download links)

### Timeline
- Automated export available immediately
- Large exports: within 24 hours
- Manual requests: within 30 days (GDPR max)

---

## Privacy by Design

### Data Minimization
- Only collect necessary data
- Default to minimal permissions
- Regularly review data collected

### Purpose Limitation
- Use data only for stated purposes
- Separate consent for new purposes

### Storage Limitation
- Automatic deletion after retention period
- Regular data cleanup jobs

---

## Health Data (HIPAA Considerations)

### Current Approach
- Not a covered entity (no healthcare providers)
- Not handling PHI in HIPAA sense

### If Applicable Later
- BAA with health data providers
- Additional encryption
- Access controls
- Audit requirements

---

## International Data Transfers

### EU to US
- Standard Contractual Clauses
- Or EU-US Data Privacy Framework

### Data Residency
- Option for EU data residency (Phase 3+)
- Store EU user data in EU region
