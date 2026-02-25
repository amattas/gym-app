from gym_api.scripts.seed import GLOBAL_EXERCISES


def test_seed_has_minimum_exercises():
    assert len(GLOBAL_EXERCISES) >= 50


def test_seed_exercises_have_required_fields():
    for ex in GLOBAL_EXERCISES:
        assert "name" in ex
        assert "muscle_groups" in ex
        assert isinstance(ex["muscle_groups"], list)
        assert len(ex["muscle_groups"]) > 0


def test_seed_exercise_names_unique():
    names = [ex["name"] for ex in GLOBAL_EXERCISES]
    assert len(names) == len(set(names))
