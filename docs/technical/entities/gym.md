# Gym & Location Entities

All entities stored in PostgreSQL.

---

## Gym

**Purpose**: Top-level organization entity representing a gym business.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `gym_id` | UUID | Primary key |
| `name` | string | Required |
| `timezone` | string | IANA timezone (e.g., "America/New_York") |

### Branding & Theming

Gyms can fully customize their visual appearance across web and mobile apps.

| Field | Type | Description |
|-------|------|-------------|
| `logo_url` | string? | CDN URL for gym logo |
| `logo_dark_url` | string? | Logo variant for dark mode |
| `favicon_url` | string? | Favicon for web app |
| `theme_preset` | string? | Predefined theme name (null for custom) |

### Theme Configuration (JSONB or separate table)

```json
{
  "mode": "light",           // "light", "dark", or "system"
  "colors": {
    "primary": "#3B82F6",      // Primary brand color
    "primary_hover": "#2563EB",
    "secondary": "#10B981",    // Secondary/accent color
    "background": "#FFFFFF",   // Page background
    "surface": "#F3F4F6",      // Cards, panels
    "text_primary": "#111827", // Main text
    "text_secondary": "#6B7280", // Muted text
    "link": "#3B82F6",         // Link color
    "link_hover": "#2563EB",
    "success": "#10B981",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "border": "#E5E7EB"
  },
  "dark_mode_colors": {
    "background": "#111827",
    "surface": "#1F2937",
    "text_primary": "#F9FAFB",
    "text_secondary": "#9CA3AF",
    "border": "#374151"
  },
  "typography": {
    "font_family": "Inter, system-ui, sans-serif",
    "heading_font": null       // Optional different heading font
  },
  "border_radius": "md"        // "none", "sm", "md", "lg", "full"
}
```

### Predefined Theme Presets

| Preset | Description |
|--------|-------------|
| `default` | Clean blue/gray professional theme |
| `fitness-dark` | Dark theme with energetic accent colors |
| `minimal-light` | Minimal white/black theme |
| `bold-red` | Red primary with dark accents |
| `nature-green` | Earthy greens and browns |
| `premium-gold` | Dark with gold accents (luxury feel) |

### Theme Behavior

- If `theme_preset` is set, use predefined colors (can be partially overridden)
- If `theme_preset` is null, use custom `theme_config`
- `mode: "system"` respects user's OS preference for light/dark
- Dark mode colors override light mode colors when active
- All apps (web, iOS, Android) respect theme settings

### Settings (stored in Gym or separate settings table)

**Measurement & Progress**:
- `measurement_reminders_enabled`: bool
- `measurement_reminder_frequency_days`: int
- `allow_peer_comparison`: bool
- `progress_photo_required_for_measurements`: bool

**Calendar**:
- `hide_client_names_in_calendar`: bool (gym-wide default)

**Custom Domains (Enterprise)**:
- `custom_email_domain`, `custom_email_status`, `custom_email_verified_at`
- `custom_login_domain`, `custom_login_status`, `custom_login_verified_at`

### Usage Metrics (derived)

| Field | Description |
|-------|-------------|
| `usage_clients_count` | Total clients |
| `usage_locations_count` | Total locations |
| `usage_trainers_count` | Total trainers |
| `usage_api_calls_count` | API calls (time-windowed) |

### Relationships

- Has many Locations
- Has many Trainers
- Has many PlanTemplates
- Has many GymMeasurementTypes
- Has one GymPlanLimits (JSONB or separate table)

---

## Location

**Purpose**: Physical gym location.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `location_id` | UUID | Primary key |
| `gym_id` | UUID | FK to Gym |
| `name` | string? | Location name |
| `picture_url` | string? | CDN URL |

### Address (structured)

| Field | Type |
|-------|------|
| `street1` | string |
| `street2` | string? |
| `city` | string |
| `state` | string |
| `postal_code` | string |
| `country` | string |

### Relationships

- Belongs to Gym
- Has many Trainers (primary_location)
- Has many Clients (primary_location)
- Has many GymCheckIns
- Has many Schedules

---

## DomainVerification

**Purpose**: Tracks DNS verification for custom email/login domains.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `domain_verification_id` | UUID | Primary key |
| `gym_id` | UUID | FK to Gym |
| `domain_type` | enum | 'email' or 'login' |
| `domain` | string | Domain being verified |
| `verification_token` | string | Random 64-char hex token |
| `status` | enum | 'pending', 'verified', 'failed' |
| `expires_at` | datetime | 72 hours from creation |

### Business Rules

- Only one active verification per (gym_id, domain_type)
- Verification expires after 72 hours
- Max 10 retry attempts before marking as failed

---

## EmailTemplate

**Purpose**: Email templates for transactional/operational emails.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `template_id` | UUID | Primary key |
| `gym_id` | UUID? | Null for system templates |
| `template_key` | string | Unique key (e.g., 'password_reset') |
| `name` | string | Human-readable name |
| `subject_template` | string | Jinja2 template for subject |
| `body_html_template` | text | Jinja2 template for HTML body |
| `body_text_template` | text | Jinja2 template for plaintext |
| `category` | enum | 'transactional', 'operational', 'marketing' |
| `is_system` | bool | True for platform-provided templates |

### System Templates (required)

- `password_reset`, `password_changed`, `welcome_email`, `email_verification`
- `mfa_code`, `mfa_enabled`, `mfa_disabled`
- `session_scheduled`, `session_canceled`, `goal_achieved`

### Business Rules

- System templates cannot be deleted or deactivated
- Gym templates override system templates when present
- Marketing emails must include unsubscribe link
