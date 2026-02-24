# AI Workout Summaries — Design

**Epic**: #102
**Story**: #113
**Date**: 2026-02-24
**Status**: Approved

---

## Overview

A section on the client profile page showing an AI-generated summary of the client's last 3-5 workout sessions. Covers a recap of what they did plus trend insights. Generated on-demand when a trainer views the client profile, cached until the underlying data changes.

---

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM provider | Provider-agnostic, Claude default | Flexibility to swap providers |
| Summary content | Recap + insights | Trends are high-value; recommendations deferred |
| Generation trigger | On-demand (trainer views page) | Saves tokens vs auto-generate |
| History window | Last 3-5 sessions | Enough for trend detection, bounded token cost |
| Caching | Persist in DB, invalidate on new data | Cost-effective, simple invalidation |
| UI location | Client profile page | Rolling client summary, not per-workout |

---

## API

### Endpoint

```
GET /api/v1/gyms/{gym_id}/clients/{client_id}/workout-summary
```

### Response

```json
{
  "summary_id": "uuid",
  "client_id": "uuid",
  "summary_text": "Over the last 4 sessions...",
  "workouts_included": ["uuid", "uuid", "uuid", "uuid"],
  "generated_at": "2026-02-24T10:30:00Z",
  "is_cached": true
}
```

### Behavior

1. Trainer opens client profile — frontend requests summary
2. Backend checks for cached `ClientWorkoutSummary`
3. **Cache valid** (exists and no workouts completed after `generated_at`) — return cached
4. **Cache stale or missing** — gather last 3-5 workouts + analytics, call LLM, cache result, return
5. If client has no completed workouts, return `null` with appropriate message

### Authorization

- Trainer must be assigned to client, or gym admin
- Client cannot access their own summary (trainer-facing feature)

---

## Data Model

### New Table: `client_workout_summary`

| Field | Type | Description |
|-------|------|-------------|
| `summary_id` | UUID | Primary key |
| `client_id` | UUID | FK to Client (unique — one summary per client) |
| `gym_id` | UUID | FK to Gym |
| `summary_text` | text | The generated summary |
| `workouts_included` | UUID[] | Workout IDs that were summarized |
| `generated_at` | datetime | When the summary was generated |
| `model_provider` | string | Provider used (e.g. "anthropic", "openai") |
| `model_id` | string | Model used (e.g. "claude-sonnet-4-20250514") |
| `token_usage` | JSONB | `{"prompt_tokens": 1200, "completion_tokens": 350}` |

### Indexes

- Unique: `client_id` (one cached summary per client)
- Index: `gym_id`

### Cache Invalidation

Compare `MAX(workout.ended_at)` for the client against `summary.generated_at`. If any workout ended after the summary was generated, the cache is stale — regenerate on next request.

---

## LLM Integration

### Provider Interface

```python
class SummaryProvider(ABC):
    @abstractmethod
    async def generate_summary(self, context: WorkoutSummaryContext) -> SummaryResult:
        ...

class AnthropicProvider(SummaryProvider):
    """Default provider using Claude API."""
    ...

class OpenAIProvider(SummaryProvider):
    """Alternative provider using OpenAI API."""
    ...
```

### Configuration

Provider selection via gym settings or environment variable:

```
AI_SUMMARY_PROVIDER=anthropic  # or "openai"
AI_SUMMARY_MODEL=claude-sonnet-4-20250514
```

### Prompt Input

Structured context sent to the LLM:

- Client name, current program name
- Last 3-5 completed workouts, each containing:
  - Date, duration
  - Exercises performed with sets/reps/weight
  - Completion rate
  - PRs achieved
- `WorkoutAnalytics` data for each session (total volume, intensity, muscle group breakdown)

### Prompt Output

Natural language summary (2-3 paragraphs) covering:

- **Recap**: What they did — exercises, volume, session frequency, completion
- **Trends**: Volume changes, consistency patterns, muscle group balance shifts
- **Notable events**: New PRs, skipped exercises, performance changes

---

## Out of Scope

- Recommendations / actionable suggestions (future upgrade)
- Trainer review/edit workflow (#114 — shelved)
- Per-workout summaries (this is a per-client rolling window)
- Real-time generation during active workouts
- Client-facing summaries (trainer-only for now)
- Streaming responses

---

## Dependencies

- Completed workouts with `WorkoutAnalytics` data (MVP entities)
- LLM API credentials configured
- Client profile page in frontend

---

## Related Issues

- #102 — [Epic] AI Workout Summaries
- #113 — AI workout summary generation
- #114 — Trainer review of AI summaries (shelved)
