# Training: Programs, Workouts & Exercises

This document defines how training programs, workouts, and exercises work in the system.

---

## Plan vs Program

| Concept | Definition |
|---------|------------|
| **Plan** | What a client pays for (membership/entitlement bundle) |
| **Program** | Prescribed set of training activities designed by a trainer |

- Plans control module access (feature enable/disable)
- A client can have one active Program at a time (unless trainer assigns a new program)
- Programs are separate from Plans (payment/membership)

---

## Program Structure

### Core Concepts

- A **Program** is a set of multiple Workouts designed by a trainer
- A **Program** contains multiple **Workouts** (formerly called "ProgramDays")
- Each **Workout** is a collection of planned exercises for a single training session
- Workouts are ordered sequentially within the program
- The client progresses through workouts in order with each visit

### Hierarchy

```
Program
├── Workout 1 (Day A)
│   ├── Exercise 1 (Squats)
│   ├── Exercise 2 (Bench Press)
│   └── Exercise 3 (Rows)
├── Workout 2 (Day B)
│   ├── Exercise 1 (Deadlifts)
│   ├── Exercise 2 (Overhead Press)
│   └── Exercise 3 (Pull-ups)
└── Workout 3 (Day C)
    └── ...
```

---

## Visit Assignment

- Each gym visit executes one Workout from the client's active Program
- On check-in / workout start:
  - The system loads exercises from the client's current/next Workout in their active Program
  - Trainer can optionally select a different workout from the program if needed

### Advancement

After visit completion:
1. The Program advances its pointer to the next Workout
2. The final Workout loops back to the beginning unless the trainer removes/changes the program

---

## Workouts

### Definition

A single training session instance tied to a gym visit.

### States

| State | Description |
|-------|-------------|
| In Progress | Client is actively working out |
| Completed | All exercises finished or skipped |
| Abandoned | Session ended without completion |

### Visit-Workout Relationship

- Workouts are tied to a specific gym visit (GymCheckIn)
- The visit may be from a scheduled session or a walk-in
- This enables tracking which training sessions occurred during which gym visits

---

## Exercises

### Exercise Properties

- Name
- Exercise type (Lift, Exertion, etc.)
- Image/video (optional)
- Default sets/reps
- Measurements allowed (weight, time, distance, reps, RPE)

### Exercise Types

| Type | Examples | Measurements |
|------|----------|--------------|
| Lift | Squat, Bench, Deadlift | Weight, Reps, RPE |
| Exertion | Running, Rowing, Cycling | Time, Distance, Calories |
| Bodyweight | Push-ups, Pull-ups | Reps, Time (holds) |

### PR Direction

| Direction | Use Case |
|-----------|----------|
| `maximize` | Max weight lifted, max distance, max hold time, max reps |
| `minimize` | Sprint times, rowing for time, running for time |

---

## Workout Logging

### Sets & Reps

- Each exercise in a workout has one or more sets
- Each set tracks:
  - Planned reps
  - Actual reps
  - Is AMRAP (as many reps as possible)
  - Measurements (weight, time, distance)
  - Notes

### Supersets & Circuits

- Exercises can be grouped into supersets or circuits
- Grouped exercises are performed back-to-back
- Example: Superset A = Bench Press + Rows (alternate between exercises)

---

## Editing Completed Workouts

- Gym-configurable setting
- Options:
  - **Trainer-only**: Only trainers can edit completed workouts
  - **Trainer + Client**: Both can edit

---

## Related Documents

- [Memberships](02-memberships.md) - Plans control which modules are enabled
- [Progress](05-progress.md) - PRs, measurements, and goals
- [Scheduling](04-scheduling.md) - Session scheduling
