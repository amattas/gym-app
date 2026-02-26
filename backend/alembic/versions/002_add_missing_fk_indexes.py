"""add missing FK indexes

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-25
"""
from alembic import op

revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_gym_check_ins_location_id", "gym_check_ins", ["location_id"]
    )
    op.create_index(
        "ix_gym_check_ins_schedule_id", "gym_check_ins", ["schedule_id"]
    )
    op.create_index(
        "ix_schedules_location_id", "schedules", ["location_id"]
    )
    op.create_index(
        "ix_schedules_created_by_user_id", "schedules", ["created_by_user_id"]
    )
    op.create_index(
        "ix_client_programs_assigned_by_trainer_id",
        "client_programs",
        ["assigned_by_trainer_id"],
    )
    op.create_index(
        "ix_program_day_exercises_exercise_id",
        "program_day_exercises",
        ["exercise_id"],
    )
    op.create_index(
        "ix_client_goals_created_by_trainer_id",
        "client_goals",
        ["created_by_trainer_id"],
    )
    op.create_index(
        "ix_client_goals_gym_id", "client_goals", ["gym_id"]
    )
    op.create_index(
        "ix_progress_photos_measurement_id",
        "progress_photos",
        ["measurement_id"],
    )
    op.create_index(
        "ix_progress_photos_uploaded_by_user_id",
        "progress_photos",
        ["uploaded_by_user_id"],
    )
    op.create_index(
        "ix_progress_photos_gym_id", "progress_photos", ["gym_id"]
    )
    op.create_index(
        "ix_client_invitations_client_id",
        "client_invitations",
        ["client_id"],
    )
    op.create_index(
        "ix_client_invitations_invited_by_user_id",
        "client_invitations",
        ["invited_by_user_id"],
    )
    op.create_index(
        "ix_data_export_requests_gym_id",
        "data_export_requests",
        ["gym_id"],
    )
    op.create_index(
        "ix_deletion_requests_gym_id", "deletion_requests", ["gym_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_deletion_requests_gym_id", "deletion_requests")
    op.drop_index("ix_data_export_requests_gym_id", "data_export_requests")
    op.drop_index(
        "ix_client_invitations_invited_by_user_id", "client_invitations"
    )
    op.drop_index("ix_client_invitations_client_id", "client_invitations")
    op.drop_index("ix_progress_photos_gym_id", "progress_photos")
    op.drop_index(
        "ix_progress_photos_uploaded_by_user_id", "progress_photos"
    )
    op.drop_index("ix_progress_photos_measurement_id", "progress_photos")
    op.drop_index("ix_client_goals_gym_id", "client_goals")
    op.drop_index(
        "ix_client_goals_created_by_trainer_id", "client_goals"
    )
    op.drop_index(
        "ix_program_day_exercises_exercise_id", "program_day_exercises"
    )
    op.drop_index(
        "ix_client_programs_assigned_by_trainer_id", "client_programs"
    )
    op.drop_index("ix_schedules_created_by_user_id", "schedules")
    op.drop_index("ix_schedules_location_id", "schedules")
    op.drop_index("ix_gym_check_ins_schedule_id", "gym_check_ins")
    op.drop_index("ix_gym_check_ins_location_id", "gym_check_ins")
