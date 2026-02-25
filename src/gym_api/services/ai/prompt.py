from gym_api.services.ai.types import WorkoutSummaryContext


def build_summary_prompt(context: WorkoutSummaryContext) -> str:
    lines = []
    lines.append(f"Client: {context.client_name}")
    if context.program_name:
        lines.append(f"Current Program: {context.program_name}")
    lines.append(f"Number of recent sessions: {len(context.workouts)}")
    lines.append("")

    for i, w in enumerate(context.workouts, 1):
        lines.append(f"--- Session {i} ({w.date.strftime('%Y-%m-%d')}) ---")
        lines.append(f"Duration: {w.duration_minutes or 'N/A'} minutes")
        lines.append(f"Total Volume: {w.total_volume_lbs:.0f} lbs")
        lines.append(f"Completion Rate: {w.completion_rate:.0%}")
        lines.append(f"PRs Achieved: {w.prs_achieved}")
        lines.append("Exercises:")
        for ex in w.exercises:
            weight = f" @ {ex['weight_lbs']} lbs" if ex.get("weight_lbs") else ""
            lines.append(f"  - {ex['name']}: {ex.get('sets', '?')}x{ex.get('reps', '?')}{weight}")
        lines.append("")

    return "\n".join(lines)


SYSTEM_PROMPT = """You are a fitness analytics assistant for personal trainers. Given a client's recent workout data, write a concise summary (2-3 short paragraphs) covering:

1. **Recap**: What they did — exercises, volume, session frequency, completion.
2. **Trends**: Volume changes, consistency patterns, muscle group balance.
3. **Notable events**: New PRs, skipped exercises, performance changes.

Write in third person, professional but approachable tone. Be specific with numbers. Do not give recommendations or advice — only observations and insights."""
