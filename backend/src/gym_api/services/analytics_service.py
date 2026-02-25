def compute_workout_analytics(
    exercises: list[dict],
    sets_by_exercise: dict[str, list[dict]],
) -> dict:
    total_volume = 0.0
    total_sets = 0
    total_reps = 0
    exercise_summaries = []

    for ex in exercises:
        ex_id = str(ex["workout_exercise_id"])
        ex_sets = sets_by_exercise.get(ex_id, [])
        ex_volume = 0.0
        ex_reps = 0
        completed_sets = 0

        for s in ex_sets:
            w = s.get("weight_kg") or 0
            r = s.get("reps") or 0
            if s.get("completed", True):
                ex_volume += w * r
                ex_reps += r
                completed_sets += 1

        total_volume += ex_volume
        total_sets += completed_sets
        total_reps += ex_reps

        exercise_summaries.append(
            {
                "exercise_id": str(ex.get("exercise_id", "")),
                "order_index": ex.get("order_index", 0),
                "completed_sets": completed_sets,
                "total_reps": ex_reps,
                "volume_kg": round(ex_volume, 2),
            }
        )

    return {
        "total_volume_kg": round(total_volume, 2),
        "total_sets": total_sets,
        "total_reps": total_reps,
        "exercises": exercise_summaries,
    }
