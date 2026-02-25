"""Seed script — idempotent. Creates global exercises, platform admin, and sample gym."""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import async_session
from gym_api.models.exercise import Exercise
from gym_api.models.gym import Gym
from gym_api.models.user import User, UserRole
from gym_api.services.password_service import hash_password

PLATFORM_ADMIN_EMAIL = "admin@gymplatform.io"

GLOBAL_EXERCISES = [
    {
        "name": "Barbell Back Squat",
        "muscle_groups": ["quadriceps", "glutes", "hamstrings"],
        "equipment": "Barbell",
    },
    {
        "name": "Barbell Front Squat",
        "muscle_groups": ["quadriceps", "core"],
        "equipment": "Barbell",
    },
    {
        "name": "Barbell Bench Press",
        "muscle_groups": ["chest", "triceps", "shoulders"],
        "equipment": "Barbell",
    },
    {
        "name": "Incline Barbell Bench Press",
        "muscle_groups": ["upper chest", "triceps", "shoulders"],
        "equipment": "Barbell",
    },
    {
        "name": "Barbell Overhead Press",
        "muscle_groups": ["shoulders", "triceps"],
        "equipment": "Barbell",
    },
    {
        "name": "Barbell Deadlift",
        "muscle_groups": ["hamstrings", "glutes", "back"],
        "equipment": "Barbell",
    },
    {
        "name": "Sumo Deadlift",
        "muscle_groups": ["hamstrings", "glutes", "inner thighs"],
        "equipment": "Barbell",
    },
    {
        "name": "Romanian Deadlift",
        "muscle_groups": ["hamstrings", "glutes"],
        "equipment": "Barbell",
    },
    {"name": "Barbell Row", "muscle_groups": ["back", "biceps"], "equipment": "Barbell"},
    {"name": "Pendlay Row", "muscle_groups": ["back", "biceps"], "equipment": "Barbell"},
    {"name": "Pull-Up", "muscle_groups": ["back", "biceps"], "equipment": "Pull-up Bar"},
    {"name": "Chin-Up", "muscle_groups": ["back", "biceps"], "equipment": "Pull-up Bar"},
    {"name": "Lat Pulldown", "muscle_groups": ["back", "biceps"], "equipment": "Cable Machine"},
    {"name": "Seated Cable Row", "muscle_groups": ["back", "biceps"], "equipment": "Cable Machine"},
    {
        "name": "Dumbbell Bench Press",
        "muscle_groups": ["chest", "triceps"],
        "equipment": "Dumbbells",
    },
    {
        "name": "Dumbbell Shoulder Press",
        "muscle_groups": ["shoulders", "triceps"],
        "equipment": "Dumbbells",
    },
    {"name": "Dumbbell Lateral Raise", "muscle_groups": ["shoulders"], "equipment": "Dumbbells"},
    {"name": "Dumbbell Bicep Curl", "muscle_groups": ["biceps"], "equipment": "Dumbbells"},
    {"name": "Hammer Curl", "muscle_groups": ["biceps", "forearms"], "equipment": "Dumbbells"},
    {"name": "Tricep Pushdown", "muscle_groups": ["triceps"], "equipment": "Cable Machine"},
    {
        "name": "Overhead Tricep Extension",
        "muscle_groups": ["triceps"],
        "equipment": "Cable Machine",
    },
    {
        "name": "Leg Press",
        "muscle_groups": ["quadriceps", "glutes"],
        "equipment": "Leg Press Machine",
    },
    {
        "name": "Leg Extension",
        "muscle_groups": ["quadriceps"],
        "equipment": "Leg Extension Machine",
    },
    {"name": "Leg Curl", "muscle_groups": ["hamstrings"], "equipment": "Leg Curl Machine"},
    {"name": "Calf Raise", "muscle_groups": ["calves"], "equipment": "Smith Machine"},
    {"name": "Hip Thrust", "muscle_groups": ["glutes", "hamstrings"], "equipment": "Barbell"},
    {
        "name": "Bulgarian Split Squat",
        "muscle_groups": ["quadriceps", "glutes"],
        "equipment": "Dumbbells",
    },
    {"name": "Lunges", "muscle_groups": ["quadriceps", "glutes"], "equipment": "Dumbbells"},
    {"name": "Cable Fly", "muscle_groups": ["chest"], "equipment": "Cable Machine"},
    {
        "name": "Face Pull",
        "muscle_groups": ["rear delts", "upper back"],
        "equipment": "Cable Machine",
    },
    {"name": "Dumbbell Row", "muscle_groups": ["back", "biceps"], "equipment": "Dumbbells"},
    {"name": "T-Bar Row", "muscle_groups": ["back", "biceps"], "equipment": "T-Bar"},
    {"name": "Plank", "muscle_groups": ["core"], "equipment": "Bodyweight"},
    {
        "name": "Hanging Leg Raise",
        "muscle_groups": ["core", "hip flexors"],
        "equipment": "Pull-up Bar",
    },
    {"name": "Cable Crunch", "muscle_groups": ["core"], "equipment": "Cable Machine"},
    {"name": "Ab Wheel Rollout", "muscle_groups": ["core"], "equipment": "Ab Wheel"},
    {"name": "Chest Dip", "muscle_groups": ["chest", "triceps"], "equipment": "Dip Station"},
    {"name": "Tricep Dip", "muscle_groups": ["triceps", "chest"], "equipment": "Dip Station"},
    {"name": "Barbell Shrug", "muscle_groups": ["traps"], "equipment": "Barbell"},
    {"name": "Dumbbell Shrug", "muscle_groups": ["traps"], "equipment": "Dumbbells"},
    {
        "name": "Machine Chest Press",
        "muscle_groups": ["chest", "triceps"],
        "equipment": "Chest Press Machine",
    },
    {
        "name": "Machine Shoulder Press",
        "muscle_groups": ["shoulders", "triceps"],
        "equipment": "Shoulder Press Machine",
    },
    {"name": "Pec Deck Fly", "muscle_groups": ["chest"], "equipment": "Pec Deck Machine"},
    {"name": "Reverse Pec Deck", "muscle_groups": ["rear delts"], "equipment": "Pec Deck Machine"},
    {
        "name": "Hack Squat",
        "muscle_groups": ["quadriceps", "glutes"],
        "equipment": "Hack Squat Machine",
    },
    {
        "name": "Smith Machine Squat",
        "muscle_groups": ["quadriceps", "glutes"],
        "equipment": "Smith Machine",
    },
    {"name": "Preacher Curl", "muscle_groups": ["biceps"], "equipment": "Preacher Bench"},
    {"name": "Concentration Curl", "muscle_groups": ["biceps"], "equipment": "Dumbbells"},
    {"name": "Barbell Hip Thrust", "muscle_groups": ["glutes"], "equipment": "Barbell"},
    {"name": "Good Morning", "muscle_groups": ["hamstrings", "lower back"], "equipment": "Barbell"},
]


async def _seed_exercises(db: AsyncSession) -> int:
    created = 0
    for ex_data in GLOBAL_EXERCISES:
        result = await db.execute(
            select(Exercise).where(Exercise.name == ex_data["name"], Exercise.gym_id.is_(None))
        )
        if not result.scalar_one_or_none():
            db.add(Exercise(**ex_data))
            created += 1
    if created:
        await db.commit()
    return created


async def _seed_platform_admin(db: AsyncSession) -> bool:
    result = await db.execute(select(User).where(User.email == PLATFORM_ADMIN_EMAIL))
    if result.scalar_one_or_none():
        return False
    admin = User(
        email=PLATFORM_ADMIN_EMAIL,
        password_hash=hash_password("ChangeMe123!"),
        first_name="Platform",
        last_name="Admin",
        role=UserRole.platform_admin,
    )
    db.add(admin)
    await db.commit()
    return True


async def _seed_sample_gym(db: AsyncSession) -> bool:
    result = await db.execute(select(Gym).where(Gym.slug == "demo-gym"))
    if result.scalar_one_or_none():
        return False
    gym = Gym(
        name="Demo Gym",
        slug="demo-gym",
        unit_system="imperial",
        timezone="America/New_York",
        contact_email="info@demo-gym.com",
    )
    db.add(gym)
    await db.commit()
    return True


async def run_seed():
    async with async_session() as db:
        exercises_created = await _seed_exercises(db)
        admin_created = await _seed_platform_admin(db)
        gym_created = await _seed_sample_gym(db)

    print(f"Exercises seeded: {exercises_created}/{len(GLOBAL_EXERCISES)}")
    print(f"Platform admin: {'created' if admin_created else 'already exists'}")
    print(f"Demo gym: {'created' if gym_created else 'already exists'}")


if __name__ == "__main__":
    asyncio.run(run_seed())
