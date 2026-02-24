# Theming & Branding

This document defines theming and branding requirements for the gym management system.

---

## Overview

Gyms can fully customize their visual appearance to provide a white-label branded experience across all platforms (web app, iOS app, Android app).

---

## Branding Assets

### Logo

| Asset | Purpose | Recommended Size |
|-------|---------|------------------|
| Primary Logo | Main logo for headers | 200x50px (SVG preferred) |
| Dark Mode Logo | Logo variant for dark backgrounds | 200x50px |
| Favicon | Browser tab icon | 32x32px, 180x180px |
| App Icon | Mobile app icon (if white-label) | 1024x1024px |

### Requirements

- Support PNG, SVG, and WebP formats
- Auto-generate dark mode logo if not provided (invert or add contrast)
- Store in CDN with appropriate caching

---

## Color Theming

### Core Colors

| Color | Purpose | Example |
|-------|---------|---------|
| **Primary** | Main brand color, buttons, links | `#3B82F6` (blue) |
| **Secondary** | Accent color, highlights | `#10B981` (green) |
| **Background** | Page/screen background | `#FFFFFF` |
| **Surface** | Cards, panels, modals | `#F3F4F6` |
| **Text Primary** | Main text color | `#111827` |
| **Text Secondary** | Muted/helper text | `#6B7280` |

### Semantic Colors

| Color | Purpose |
|-------|---------|
| **Success** | Positive feedback, completions |
| **Warning** | Cautions, pending states |
| **Error** | Errors, destructive actions |
| **Link** | Clickable text links |

---

## Light/Dark Mode

### Mode Options

| Mode | Behavior |
|------|----------|
| **Light** | Always use light theme |
| **Dark** | Always use dark theme |
| **System** | Follow user's OS preference |

### Dark Mode Requirements

- All colors must have accessible dark mode variants
- Text must meet WCAG AA contrast ratios (4.5:1 for normal text)
- Images should have dark-appropriate variants where needed
- Smooth transition animation when switching modes

---

## Predefined Theme Presets

Provide ready-to-use themes for gyms that don't want to customize:

### Default
- Clean, professional blue/gray palette
- High readability, neutral feel

### Fitness Dark
- Dark background with energetic accent colors
- Popular for modern fitness brands

### Minimal Light
- High contrast black/white
- Clean, magazine-style aesthetic

### Bold Red
- Red primary with dark accents
- High energy, aggressive feel

### Nature Green
- Earthy greens and browns
- Wellness/holistic vibe

### Premium Gold
- Dark background with gold accents
- Luxury, high-end positioning

---

## Typography

### Font Options

| Setting | Options |
|---------|---------|
| Body font | System default, Inter, Roboto, Open Sans |
| Heading font | Same as body or custom |

### Requirements

- Use system fonts where possible for performance
- Support custom web fonts (Google Fonts integration)
- Maintain readable font sizes (minimum 16px body text)

---

## Additional Customization

### Border Radius

| Setting | Effect |
|---------|--------|
| `none` | Sharp corners (0px) |
| `sm` | Slightly rounded (4px) |
| `md` | Standard rounded (8px) |
| `lg` | More rounded (12px) |
| `full` | Pill-shaped buttons, fully rounded |

### Spacing Scale

- Use consistent spacing scale (4px increments)
- Allow gyms to choose "compact" or "comfortable" density

---

## Implementation Priority

### Phase 1 (MVP)
- Primary and secondary colors
- Logo upload
- Light mode only
- One predefined theme

### Phase 2
- Dark mode support
- All predefined themes
- Custom color picker
- Typography options

### Phase 3 (Enterprise)
- Custom CSS injection
- Complete white-label (remove platform branding)
- Custom app icons (mobile)

---

## Preview & Testing

### Requirements

- Live preview when editing theme
- Preview on both light and dark backgrounds
- Preview key screens (dashboard, client profile, workout log)
- Save draft themes before publishing
- Rollback to previous theme

---

## Related Documents

- [Entities - Gym](../technical/entities/gym.md) - Technical implementation of theming
- [Overview](00-overview.md) - Product overview
