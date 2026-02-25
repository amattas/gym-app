from gym_api.services.analytics_service import compute_workout_analytics


def test_analytics_basic():
    exercises = [
        {
            "workout_exercise_id": "ex1",
            "exercise_id": "bench",
            "order_index": 0,
        }
    ]
    sets_by_exercise = {
        "ex1": [
            {"weight_kg": 80.0, "reps": 10, "completed": True},
            {"weight_kg": 80.0, "reps": 8, "completed": True},
        ]
    }
    result = compute_workout_analytics(exercises, sets_by_exercise)
    assert result["total_volume_kg"] == 80.0 * 10 + 80.0 * 8
    assert result["total_sets"] == 2
    assert result["total_reps"] == 18
    assert len(result["exercises"]) == 1


def test_analytics_incomplete_sets():
    exercises = [
        {
            "workout_exercise_id": "ex1",
            "exercise_id": "squat",
            "order_index": 0,
        }
    ]
    sets_by_exercise = {
        "ex1": [
            {"weight_kg": 100.0, "reps": 5, "completed": True},
            {"weight_kg": 100.0, "reps": 3, "completed": False},
        ]
    }
    result = compute_workout_analytics(exercises, sets_by_exercise)
    assert result["total_volume_kg"] == 500.0
    assert result["total_sets"] == 1


def test_analytics_empty():
    result = compute_workout_analytics([], {})
    assert result["total_volume_kg"] == 0.0
    assert result["total_sets"] == 0
    assert result["total_reps"] == 0


def test_analytics_multiple_exercises():
    exercises = [
        {
            "workout_exercise_id": "ex1",
            "exercise_id": "bench",
            "order_index": 0,
        },
        {
            "workout_exercise_id": "ex2",
            "exercise_id": "row",
            "order_index": 1,
        },
    ]
    sets_by_exercise = {
        "ex1": [{"weight_kg": 80.0, "reps": 10, "completed": True}],
        "ex2": [{"weight_kg": 60.0, "reps": 12, "completed": True}],
    }
    result = compute_workout_analytics(exercises, sets_by_exercise)
    assert result["total_volume_kg"] == 800.0 + 720.0
    assert len(result["exercises"]) == 2
