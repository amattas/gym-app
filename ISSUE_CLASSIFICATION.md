# Issue Classification for gym-app Project

This document describes how the 132 issues in the gym-app repository are classified into iterations for the GitHub Project.

## Overview

The gym-app project uses a phased development approach with 4 main iterations:

| Iteration | Description | Issue Count | Labels |
|-----------|-------------|-------------|--------|
| MVP (Phase 1) - Current Iteration | Minimum Viable Product | 76 issues | `mvp` |
| Phase 2 - Next Iteration | Enhanced Operations & Mobile Apps | 25 issues | `phase-2` |
| Phase 3 - Prioritized Backlog | Advanced Features & Intelligence | 14 issues | `phase-3` |
| Phase 4 - Prioritized Backlog | Payments & Premium Features | 17 issues | `phase-4` |

**Total: 132 issues**

## Classification Rules

Issues are classified based on their GitHub labels:

1. **MVP (Phase 1)**: Issues with label `mvp` → Issues #1-76
2. **Phase 2**: Issues with label `phase-2` → Issues #77-101
3. **Phase 3**: Issues with label `phase-3` → Issues #102-120
4. **Phase 4**: Issues with label `phase-4` → Issues #121-132

## Detailed Issue Mapping

### MVP (Phase 1) - Current Iteration (76 issues)

**Epics:**
- #1: [Epic] Authentication & Security System
- #2: [Epic] User & Role Management
- #3: [Epic] Gym & Location Management
- #4: [Epic] Client Management
- #5: [Epic] Exercise Library
- #6: [Epic] Programs & Workouts
- #7: [Epic] Workout Logging

**Authentication & Security (Issues #1-26):**
- User registration, login, MFA, password reset
- JWT token management, RBAC
- Security audit logging

**Gym & Client Management (Issues #27-35):**
- Gym entity and location setup
- Trainer and client account management
- Client profile creation and editing

**Exercise & Workout Features (Issues #36-50):**
- Exercise library management
- Program and workout creation
- Workout logging and tracking
- Progress photos and goals

**Scheduling & Attendance (Issues #51-57):**
- Calendar views and session scheduling
- Trainer availability and booking rules
- Client check-in and attendance tracking

**Analytics & Dashboards (Issues #58-68):**
- Client, trainer, and business analytics
- Various dashboard interfaces
- Branding and theming

**Infrastructure (Issues #69-76):**
- Email notifications (password reset, verification, etc.)
- Frontend (Next.js) and API (FastAPI) setup
- Database schema design

### Phase 2 - Next Iteration (25 issues)

**Epics:**
- #77: [Epic] Mobile Applications (iOS & Android)
- #78: [Epic] Family & Account Management
- #79: [Epic] Advanced Scheduling & Busyness
- #80: [Epic] Memberships & Plans (Pre-Payment)
- #81: [Epic] Enhanced Reporting & Analytics

**Features:**
- iOS and Android mobile apps (#82-84)
- Push notifications (#85)
- Family accounts and sub-member management (#86-90)
- Gym busyness calculations (#91)
- Calendar export (#92)
- Membership management (#93-97)
- Enhanced reporting (#98-101)

### Phase 3 - Prioritized Backlog (14 issues)

**Epics:**
- #102: [Epic] AI Workout Summaries
- #103: [Epic] Full Offline Mode
- #104: [Epic] Front Desk Role & Features
- #105: [Epic] Data Management & Compliance
- #106: [Epic] Health & Fitness Integrations
- #107: [Epic] GraphQL API Layer

**Features:**
- AI-powered workout summary generation (#113-114)
- QR code check-in (#115)
- Occupancy dashboard (#116)
- GDPR/CCPA compliance and data export (#117-118)
- Apple Health and Google Fit integrations (#119-120)

### Phase 4 - Prioritized Backlog (17 issues)

**Epics:**
- #108: [Epic] Stripe Payment Integration
- #109: [Epic] E-Signature & Agreements
- #110: [Epic] Advanced Billing Features
- #111: [Epic] Usage Metering & Plan Limits
- #112: [Epic] Premium Features (Enterprise)

**Features:**
- Stripe Connect onboarding (#121)
- Subscription and one-time payments (#122-124)
- Custom branding domains (#125-126)
- E-signature integrations (#127-128)
- Usage metering dashboard (#129)
- Trial periods and discounts (#130-131)
- Processing fee configuration (#132)

## Scripts

Two scripts are provided to automate the classification:

### Shell Script (classify-issues.sh)

```bash
# Make executable
chmod +x classify-issues.sh

# Authenticate with GitHub CLI
gh auth login

# Run the script
./classify-issues.sh
```

### Python Script (classify_issues.py)

```bash
# Install dependencies
pip install requests

# Set your GitHub token
export GITHUB_TOKEN=your_personal_access_token

# Run the script
python3 classify_issues.py
```

**Required GitHub Token Scopes:**
- `project` - Full control of projects
- `repo` - Access to repository issues

## Manual Classification

If you prefer to manually classify issues:

1. Create a GitHub Project (v2) named "gym-app"
2. Add an Iteration field with 4 iterations:
   - MVP (Phase 1) - Current Iteration
   - Phase 2 - Next Iteration
   - Phase 3 - Prioritized Backlog
   - Phase 4 - Prioritized Backlog
3. Add issues to the project using the filter:
   - `label:mvp` → Assign to Phase 1
   - `label:phase-2` → Assign to Phase 2
   - `label:phase-3` → Assign to Phase 3
   - `label:phase-4` → Assign to Phase 4
