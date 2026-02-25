from gym_api.models.personal_record import PRType
from gym_api.services.pr_service import calculate_volume, detect_rep_prs


def test_detect_1rm():
    results = detect_rep_prs(100.0, 1)
    types = [r[0] for r in results]
    assert PRType.one_rm in types
    assert PRType.three_rm in types
    assert PRType.five_rm in types
    assert PRType.ten_rm in types


def test_detect_5rm():
    results = detect_rep_prs(80.0, 5)
    types = [r[0] for r in results]
    assert PRType.one_rm not in types
    assert PRType.three_rm not in types
    assert PRType.five_rm in types
    assert PRType.ten_rm in types


def test_detect_10rm():
    results = detect_rep_prs(60.0, 10)
    types = [r[0] for r in results]
    assert PRType.one_rm not in types
    assert PRType.five_rm not in types
    assert PRType.ten_rm in types


def test_detect_over_10_reps():
    results = detect_rep_prs(50.0, 15)
    assert len(results) == 0


def test_calculate_volume():
    sets = [
        {"weight_kg": 80.0, "reps": 10, "completed": True},
        {"weight_kg": 80.0, "reps": 8, "completed": True},
        {"weight_kg": 80.0, "reps": 6, "completed": True},
    ]
    assert calculate_volume(sets) == 80.0 * (10 + 8 + 6)


def test_calculate_volume_skips_incomplete():
    sets = [
        {"weight_kg": 80.0, "reps": 10, "completed": True},
        {"weight_kg": 80.0, "reps": 5, "completed": False},
    ]
    assert calculate_volume(sets) == 800.0


def test_calculate_volume_empty():
    assert calculate_volume([]) == 0.0
