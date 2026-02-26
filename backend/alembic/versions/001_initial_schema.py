"""initial schema

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-02-25
"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = None
branch_labels = None
depends_on = None

UUID = postgresql.UUID(as_uuid=True)
JSONB = postgresql.JSONB(astext_type=sa.Text())
gen_uuid = sa.text("gen_random_uuid()")
now = sa.text("now()")

# --- enum definitions ---

accounttype = postgresql.ENUM(
    "individual", "family", name="accounttype", create_type=False
)
checkinmethod = postgresql.ENUM(
    "manual", "qr_code", "card_scan", name="checkinmethod", create_type=False
)
clientprogramstatus = postgresql.ENUM(
    "active", "completed", "paused", name="clientprogramstatus", create_type=False
)
clientstatus = postgresql.ENUM(
    "active", "inactive", "suspended", name="clientstatus", create_type=False
)
deletionstatus = postgresql.ENUM(
    "pending", "approved", "processing", "completed", "rejected",
    name="deletionstatus", create_type=False,
)
discounttype = postgresql.ENUM(
    "percentage", "fixed_amount", name="discounttype", create_type=False
)
domainstatus = postgresql.ENUM(
    "pending", "verifying", "active", "failed", name="domainstatus", create_type=False
)
domaintype = postgresql.ENUM(
    "email", "login", name="domaintype", create_type=False
)
envelopestatus = postgresql.ENUM(
    "draft", "sent", "viewed", "signed", "declined", "expired",
    name="envelopestatus", create_type=False,
)
exceptiontype = postgresql.ENUM(
    "unavailable", "modified_hours", name="exceptiontype", create_type=False
)
exportstatus = postgresql.ENUM(
    "pending", "processing", "completed", "failed",
    name="exportstatus", create_type=False,
)
gender_enum = postgresql.ENUM(
    "male", "female", "other", "prefer_not_to_say", name="gender", create_type=False
)
goalstatus = postgresql.ENUM(
    "active", "completed", "abandoned", name="goalstatus", create_type=False
)
invoicestatus = postgresql.ENUM(
    "draft", "open", "paid", "void", "uncollectible",
    name="invoicestatus", create_type=False,
)
measurementtype = postgresql.ENUM(
    "weight", "body_fat", "chest", "waist", "hips", "bicep", "thigh", "calf",
    name="measurementtype", create_type=False,
)
membershipstatus = postgresql.ENUM(
    "active", "paused", "cancelled", "expired", "pending",
    name="membershipstatus", create_type=False,
)
onboardingstatus = postgresql.ENUM(
    "pending", "in_progress", "complete", "restricted",
    name="onboardingstatus", create_type=False,
)
prtype = postgresql.ENUM(
    "1RM", "3RM", "5RM", "10RM", "volume", name="prtype", create_type=False
)
paymentstatus = postgresql.ENUM(
    "pending", "processing", "succeeded", "failed", "refunded",
    name="paymentstatus", create_type=False,
)
planstatus = postgresql.ENUM(
    "active", "archived", "draft", name="planstatus", create_type=False
)
plantype = postgresql.ENUM(
    "membership", "punch_card", "drop_in", name="plantype", create_type=False
)
schedulestatus = postgresql.ENUM(
    "tentative", "confirmed", "completed", "canceled", "no_show",
    name="schedulestatus", create_type=False,
)
templatescope = postgresql.ENUM(
    "personal", "gym_wide", name="templatescope", create_type=False
)
userrole = postgresql.ENUM(
    "platform_admin", "gym_admin", "trainer", "client",
    name="userrole", create_type=False,
)
workoutstatus = postgresql.ENUM(
    "scheduled", "in_progress", "completed", "cancelled",
    name="workoutstatus", create_type=False,
)

ALL_ENUMS = [
    accounttype, checkinmethod, clientprogramstatus, clientstatus,
    deletionstatus, discounttype, domainstatus, domaintype,
    envelopestatus, exceptiontype, exportstatus, gender_enum,
    goalstatus, invoicestatus, measurementtype, membershipstatus,
    onboardingstatus, prtype, paymentstatus, planstatus,
    plantype, schedulestatus, templatescope, userrole, workoutstatus,
]


def upgrade() -> None:
    # create all enum types
    for enum in ALL_ENUMS:
        enum.create(op.get_bind(), checkfirst=True)

    # 1. gyms (no FK dependencies)
    op.create_table(
        "gyms",
        sa.Column("gym_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("unit_system", sa.String(20), nullable=False),
        sa.Column("timezone", sa.String(50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("settings", JSONB),
        sa.Column("contact_email", sa.String(255)),
        sa.Column("contact_phone", sa.String(30)),
        sa.Column("address", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("gym_id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_gyms_slug", "gyms", ["slug"])

    # 2. users
    op.create_table(
        "users",
        sa.Column("user_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", userrole, nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("email_verified", sa.Boolean(), nullable=False),
        sa.Column("mfa_secret", sa.Text()),
        sa.Column("mfa_enabled", sa.Boolean(), nullable=False),
        sa.Column("backup_codes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_gym_id", "users", ["gym_id"])

    # 3. clients
    op.create_table(
        "clients",
        sa.Column("client_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("user_id", UUID),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255)),
        sa.Column("phone", sa.String(30)),
        sa.Column("date_of_birth", sa.Date()),
        sa.Column("gender", gender_enum),
        sa.Column("height_cm", sa.Numeric(5, 1)),
        sa.Column("weight_kg", sa.Numeric(5, 1)),
        sa.Column("fitness_goals", sa.Text()),
        sa.Column("emergency_contact_name", sa.String(200)),
        sa.Column("emergency_contact_phone", sa.String(30)),
        sa.Column("status", clientstatus, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint("client_id"),
        sa.UniqueConstraint("user_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
    )
    op.create_index("ix_clients_gym_id", "clients", ["gym_id"])
    op.create_index("ix_clients_user_id", "clients", ["user_id"])
    op.create_index("ix_clients_email", "clients", ["email"])

    # 4. trainers
    op.create_table(
        "trainers",
        sa.Column("trainer_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("user_id", UUID),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("specializations", sa.String(500)),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("trainer_id"),
        sa.UniqueConstraint("user_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
    )
    op.create_index("ix_trainers_gym_id", "trainers", ["gym_id"])
    op.create_index("ix_trainers_user_id", "trainers", ["user_id"])

    # 5. exercises
    op.create_table(
        "exercises",
        sa.Column("exercise_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("muscle_groups", postgresql.ARRAY(sa.String)),
        sa.Column("equipment", sa.String(200)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("exercise_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
    )
    op.create_index("ix_exercises_gym_id", "exercises", ["gym_id"])

    # 6. programs
    op.create_table(
        "programs",
        sa.Column("program_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("created_by_trainer_id", UUID),
        sa.Column("template_scope", templatescope, nullable=False),
        sa.Column("num_days", sa.Integer(), nullable=False),
        sa.Column("periodization_config", JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("program_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
        sa.ForeignKeyConstraint(["created_by_trainer_id"], ["trainers.trainer_id"]),
    )
    op.create_index("ix_programs_gym_id", "programs", ["gym_id"])

    # 7. workouts
    op.create_table(
        "workouts",
        sa.Column("workout_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("client_id", UUID, nullable=False),
        sa.Column("trainer_id", UUID),
        sa.Column("program_id", UUID),
        sa.Column("status", workoutstatus, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.Column("notes", sa.String(1000)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("workout_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.client_id"]),
        sa.ForeignKeyConstraint(["trainer_id"], ["trainers.trainer_id"]),
        sa.ForeignKeyConstraint(["program_id"], ["programs.program_id"]),
    )
    op.create_index("ix_workouts_gym_id", "workouts", ["gym_id"])
    op.create_index("ix_workouts_client_id", "workouts", ["client_id"])
    op.create_index("ix_workouts_trainer_id", "workouts", ["trainer_id"])

    # 8. workout_exercises
    op.create_table(
        "workout_exercises",
        sa.Column("workout_exercise_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("workout_id", UUID, nullable=False),
        sa.Column("exercise_id", UUID, nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("target_sets", sa.Integer()),
        sa.Column("target_reps", sa.Integer()),
        sa.PrimaryKeyConstraint("workout_exercise_id"),
        sa.ForeignKeyConstraint(["workout_id"], ["workouts.workout_id"]),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.exercise_id"]),
    )
    op.create_index("ix_workout_exercises_workout_id", "workout_exercises", ["workout_id"])

    # 9. workout_sets
    op.create_table(
        "workout_sets",
        sa.Column("set_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("workout_exercise_id", UUID, nullable=False),
        sa.Column("set_index", sa.Integer(), nullable=False),
        sa.Column("weight_kg", sa.Numeric(7, 2)),
        sa.Column("reps", sa.Integer()),
        sa.Column("duration_seconds", sa.Integer()),
        sa.Column("completed", sa.Boolean()),
        sa.PrimaryKeyConstraint("set_id"),
        sa.ForeignKeyConstraint(["workout_exercise_id"], ["workout_exercises.workout_exercise_id"]),
    )
    op.create_index("ix_workout_sets_workout_exercise_id", "workout_sets", ["workout_exercise_id"])

    # 10. measurements
    op.create_table(
        "measurements",
        sa.Column("measurement_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("client_id", UUID, nullable=False),
        sa.Column("type", measurementtype, nullable=False),
        sa.Column("value", sa.Numeric(8, 2), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("bmi", sa.Numeric(5, 1)),
        sa.Column("measured_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("measurement_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.client_id"]),
    )
    op.create_index("ix_measurements_client_id", "measurements", ["client_id"])
    op.create_index("ix_measurements_gym_id", "measurements", ["gym_id"])

    # 11. personal_records
    op.create_table(
        "personal_records",
        sa.Column("record_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("client_id", UUID, nullable=False),
        sa.Column("exercise_id", UUID, nullable=False),
        sa.Column("pr_type", prtype, nullable=False),
        sa.Column("weight_kg", sa.Numeric(7, 2)),
        sa.Column("reps", sa.Integer()),
        sa.Column("volume_kg", sa.Numeric(10, 2)),
        sa.Column("exercise_name", sa.String(200), nullable=False),
        sa.Column("achieved_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("record_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.client_id"]),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.exercise_id"]),
    )
    op.create_index("ix_personal_records_client_id", "personal_records", ["client_id"])
    op.create_index("ix_personal_records_exercise_id", "personal_records", ["exercise_id"])

    # 12. email_verification_tokens
    op.create_table(
        "email_verification_tokens",
        sa.Column("token_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("user_id", UUID, nullable=False),
        sa.Column("token_hash", sa.String(128), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("token_id"),
        sa.UniqueConstraint("token_hash"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
    )
    op.create_index(
        "ix_email_verification_tokens_user_id",
        "email_verification_tokens", ["user_id"],
    )
    op.create_index(
        "ix_email_verification_tokens_token_hash",
        "email_verification_tokens", ["token_hash"],
    )

    # 13. password_reset_tokens
    op.create_table(
        "password_reset_tokens",
        sa.Column("token_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("user_id", UUID, nullable=False),
        sa.Column("token_hash", sa.String(128), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("token_id"),
        sa.UniqueConstraint("token_hash"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
    )
    op.create_index("ix_password_reset_tokens_user_id", "password_reset_tokens", ["user_id"])
    op.create_index("ix_password_reset_tokens_token_hash", "password_reset_tokens", ["token_hash"])

    # 14. refresh_tokens
    op.create_table(
        "refresh_tokens",
        sa.Column("token_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("user_id", UUID, nullable=False),
        sa.Column("token_hash", sa.String(128), nullable=False),
        sa.Column("family_id", UUID, nullable=False),
        sa.Column("is_revoked", sa.Boolean(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("token_id"),
        sa.UniqueConstraint("token_hash"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"])
    op.create_index("ix_refresh_tokens_family_id", "refresh_tokens", ["family_id"])

    # 15. user_sessions
    op.create_table(
        "user_sessions",
        sa.Column("session_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("user_id", UUID, nullable=False),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("user_agent", sa.String(500)),
        sa.Column("last_used_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("session_id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
    )
    op.create_index("ix_user_sessions_user_id", "user_sessions", ["user_id"])

    # 16. trainer_invitations
    op.create_table(
        "trainer_invitations",
        sa.Column("invitation_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("invited_by_user_id", UUID, nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("invitation_id"),
        sa.UniqueConstraint("token_hash"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
        sa.ForeignKeyConstraint(["invited_by_user_id"], ["users.user_id"]),
    )
    op.create_index("ix_trainer_invitations_gym_id", "trainer_invitations", ["gym_id"])
    op.create_index("ix_trainer_invitations_token_hash", "trainer_invitations", ["token_hash"])

    # 17. accounts
    op.create_table(
        "accounts",
        sa.Column("account_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("account_type", accounttype, nullable=False),
        sa.Column("billing_email", sa.String(255)),
        sa.Column("billing_address", JSONB),
        sa.Column("stripe_customer_id", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("account_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
    )
    op.create_index("ix_accounts_gym_id", "accounts", ["gym_id"])

    # 18. locations
    op.create_table(
        "locations",
        sa.Column("location_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("address", sa.String(500)),
        sa.Column("city", sa.String(100)),
        sa.Column("state", sa.String(100)),
        sa.Column("postal_code", sa.String(20)),
        sa.Column("country", sa.String(100)),
        sa.Column("timezone", sa.String(50)),
        sa.Column("capacity", sa.Integer()),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("location_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
    )
    op.create_index("ix_locations_gym_id", "locations", ["gym_id"])

    # 19. plan_templates
    op.create_table(
        "plan_templates",
        sa.Column("plan_template_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("plan_type", plantype, nullable=False),
        sa.Column("status", planstatus, nullable=False),
        sa.Column("visit_entitlement", JSONB),
        sa.Column("plan_duration", JSONB),
        sa.Column("payment_config", JSONB),
        sa.Column("modules_enabled", JSONB),
        sa.Column("is_addon", sa.Boolean(), nullable=False),
        sa.Column("requires_primary_plan_type", sa.String(50)),
        sa.Column("addon_discount_percentage", sa.Numeric(5, 2)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("plan_template_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
    )
    op.create_index("ix_plan_templates_gym_id", "plan_templates", ["gym_id"])

    # 20. client_memberships
    op.create_table(
        "client_memberships",
        sa.Column("client_membership_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("client_id", UUID, nullable=False),
        sa.Column("plan_template_id", UUID, nullable=False),
        sa.Column("plan_type", sa.String(50), nullable=False),
        sa.Column("status", membershipstatus, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("visit_entitlement", JSONB),
        sa.Column("visits_used_this_period", sa.Integer(), nullable=False),
        sa.Column("total_visits_remaining", sa.Integer()),
        sa.Column("current_period_start", sa.DateTime(timezone=True)),
        sa.Column("current_period_end", sa.DateTime(timezone=True)),
        sa.Column("pause_info", JSONB),
        sa.Column("cancellation_info", JSONB),
        sa.Column("base_membership_id", UUID),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("client_membership_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.client_id"]),
        sa.ForeignKeyConstraint(["plan_template_id"], ["plan_templates.plan_template_id"]),
    )
    op.create_index("ix_client_memberships_gym_id", "client_memberships", ["gym_id"])
    op.create_index("ix_client_memberships_client_id", "client_memberships", ["client_id"])

    # 21. trainer_client_assignments (composite PK)
    op.create_table(
        "trainer_client_assignments",
        sa.Column("trainer_id", UUID, nullable=False),
        sa.Column("client_id", UUID, nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("assigned_by", UUID),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("trainer_id", "client_id"),
        sa.ForeignKeyConstraint(["trainer_id"], ["trainers.trainer_id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.client_id"]),
    )

    # 22. schedules
    op.create_table(
        "schedules",
        sa.Column("schedule_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("client_id", UUID, nullable=False),
        sa.Column("trainer_id", UUID, nullable=False),
        sa.Column("location_id", UUID),
        sa.Column("scheduled_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("scheduled_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", schedulestatus, nullable=False),
        sa.Column("notes", sa.Text()),
        sa.Column("created_by_user_id", UUID),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("schedule_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.client_id"]),
        sa.ForeignKeyConstraint(["trainer_id"], ["trainers.trainer_id"]),
        sa.ForeignKeyConstraint(["location_id"], ["locations.location_id"]),
    )
    op.create_index("ix_schedules_gym_id", "schedules", ["gym_id"])
    op.create_index("ix_schedules_client_id", "schedules", ["client_id"])
    op.create_index("ix_schedules_trainer_id", "schedules", ["trainer_id"])
    op.create_index("ix_schedules_scheduled_start", "schedules", ["scheduled_start"])

    # 23. trainer_availability (composite PK)
    op.create_table(
        "trainer_availability",
        sa.Column("trainer_id", UUID, nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("location_id", UUID),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.PrimaryKeyConstraint("trainer_id", "day_of_week"),
        sa.ForeignKeyConstraint(["trainer_id"], ["trainers.trainer_id"]),
        sa.ForeignKeyConstraint(["location_id"], ["locations.location_id"]),
    )

    # 24. trainer_exceptions
    op.create_table(
        "trainer_exceptions",
        sa.Column("trainer_exception_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("trainer_id", UUID, nullable=False),
        sa.Column("exception_date", sa.Date(), nullable=False),
        sa.Column("exception_type", exceptiontype, nullable=False),
        sa.Column("reason", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("trainer_exception_id"),
        sa.ForeignKeyConstraint(["trainer_id"], ["trainers.trainer_id"]),
    )
    op.create_index("ix_trainer_exceptions_trainer_id", "trainer_exceptions", ["trainer_id"])

    # 25. gym_check_ins
    op.create_table(
        "gym_check_ins",
        sa.Column("check_in_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("client_id", UUID, nullable=False),
        sa.Column("location_id", UUID),
        sa.Column("schedule_id", UUID),
        sa.Column("check_in_method", checkinmethod, nullable=False),
        sa.Column("checked_in_by_user_id", UUID),
        sa.Column("checked_in_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("checked_out_at", sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint("check_in_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.client_id"]),
        sa.ForeignKeyConstraint(["location_id"], ["locations.location_id"]),
        sa.ForeignKeyConstraint(["schedule_id"], ["schedules.schedule_id"]),
    )
    op.create_index("ix_gym_check_ins_gym_id", "gym_check_ins", ["gym_id"])
    op.create_index("ix_gym_check_ins_client_id", "gym_check_ins", ["client_id"])
    op.create_index("ix_gym_check_ins_checked_in_at", "gym_check_ins", ["checked_in_at"])

    # 26. client_goals
    op.create_table(
        "client_goals",
        sa.Column("goal_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("client_id", UUID, nullable=False),
        sa.Column("goal_type", sa.String(100), nullable=False),
        sa.Column("target_value", sa.Numeric(10, 2)),
        sa.Column("current_value", sa.Numeric(10, 2)),
        sa.Column("target_date", sa.Date()),
        sa.Column("status", goalstatus, nullable=False),
        sa.Column("notes", sa.Text()),
        sa.Column("created_by_trainer_id", UUID),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("goal_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.client_id"]),
    )
    op.create_index("ix_client_goals_client_id", "client_goals", ["client_id"])

    # 27. client_programs
    op.create_table(
        "client_programs",
        sa.Column("client_program_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("client_id", UUID, nullable=False),
        sa.Column("program_id", UUID, nullable=False),
        sa.Column("status", clientprogramstatus, nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("assigned_by_trainer_id", UUID),
        sa.PrimaryKeyConstraint("client_program_id"),
        sa.ForeignKeyConstraint(["client_id"], ["clients.client_id"]),
        sa.ForeignKeyConstraint(["program_id"], ["programs.program_id"]),
    )
    op.create_index("ix_client_programs_client_id", "client_programs", ["client_id"])
    op.create_index("ix_client_programs_program_id", "client_programs", ["program_id"])

    # 28. program_days
    op.create_table(
        "program_days",
        sa.Column("program_day_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("program_id", UUID, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("program_day_id"),
        sa.ForeignKeyConstraint(["program_id"], ["programs.program_id"]),
    )
    op.create_index("ix_program_days_program_id", "program_days", ["program_id"])

    # 29. program_day_exercises
    op.create_table(
        "program_day_exercises",
        sa.Column("program_day_exercise_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("program_day_id", UUID, nullable=False),
        sa.Column("exercise_id", UUID, nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("default_sets", sa.Integer()),
        sa.Column("default_reps", sa.Integer()),
        sa.Column("rest_seconds", sa.Integer()),
        sa.Column("notes", sa.Text()),
        sa.PrimaryKeyConstraint("program_day_exercise_id"),
        sa.ForeignKeyConstraint(["program_day_id"], ["program_days.program_day_id"]),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.exercise_id"]),
    )
    op.create_index(
        "ix_program_day_exercises_program_day_id",
        "program_day_exercises", ["program_day_id"],
    )

    # 30. audit_logs
    op.create_table(
        "audit_logs",
        sa.Column("audit_log_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("user_id", UUID),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(255)),
        sa.Column("details", JSONB),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("audit_log_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
    )
    op.create_index("ix_audit_logs_gym_id", "audit_logs", ["gym_id"])
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])
    op.create_index("ix_audit_logs_resource_type", "audit_logs", ["resource_type"])

    # 31. notes
    op.create_table(
        "notes",
        sa.Column("note_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("notable_type", sa.String(50), nullable=False),
        sa.Column("notable_id", UUID, nullable=False),
        sa.Column("author_user_id", UUID, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("note_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
        sa.ForeignKeyConstraint(["author_user_id"], ["users.user_id"]),
    )
    op.create_index("ix_notes_gym_id", "notes", ["gym_id"])
    op.create_index("ix_notes_notable_type_notable_id", "notes", ["notable_type", "notable_id"])

    # 32. client_invitations
    op.create_table(
        "client_invitations",
        sa.Column("invitation_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("client_id", UUID, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("token_hash", sa.String(128), nullable=False),
        sa.Column("invited_by_user_id", UUID, nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("invitation_id"),
        sa.UniqueConstraint("token_hash"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.client_id"]),
        sa.ForeignKeyConstraint(["invited_by_user_id"], ["users.user_id"]),
    )
    op.create_index("ix_client_invitations_gym_id", "client_invitations", ["gym_id"])
    op.create_index("ix_client_invitations_token_hash", "client_invitations", ["token_hash"])

    # 33. progress_photos
    op.create_table(
        "progress_photos",
        sa.Column("photo_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("client_id", UUID, nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("notes", sa.Text()),
        sa.Column("tags", JSONB),
        sa.Column("measurement_id", UUID),
        sa.Column("uploaded_by_user_id", UUID),
        sa.Column("captured_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("photo_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.client_id"]),
    )
    op.create_index("ix_progress_photos_client_id", "progress_photos", ["client_id"])

    # 34. webhook_endpoints
    op.create_table(
        "webhook_endpoints",
        sa.Column("webhook_endpoint_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("url", sa.String(2000), nullable=False),
        sa.Column("secret", sa.String(255), nullable=False),
        sa.Column("events", postgresql.ARRAY(sa.String)),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("webhook_endpoint_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
    )
    op.create_index("ix_webhook_endpoints_gym_id", "webhook_endpoints", ["gym_id"])

    # 35. device_tokens
    op.create_table(
        "device_tokens",
        sa.Column("device_token_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("user_id", UUID, nullable=False),
        sa.Column("platform", sa.String(20), nullable=False),
        sa.Column("token", sa.String(500), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("device_token_id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
    )
    op.create_index("ix_device_tokens_user_id", "device_tokens", ["user_id"])

    # 36. notification_preferences
    op.create_table(
        "notification_preferences",
        sa.Column("preference_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("user_id", UUID, nullable=False),
        sa.Column("session_reminders", sa.Boolean(), nullable=False),
        sa.Column("workout_updates", sa.Boolean(), nullable=False),
        sa.Column("membership_alerts", sa.Boolean(), nullable=False),
        sa.Column("marketing", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("preference_id"),
        sa.UniqueConstraint("user_id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
    )

    # 37. calendar_tokens
    op.create_table(
        "calendar_tokens",
        sa.Column("token_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("owner_type", sa.String(20), nullable=False),
        sa.Column("owner_id", UUID, nullable=False),
        sa.Column("token_hash", sa.String(128), nullable=False),
        sa.Column("is_revoked", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("token_id"),
        sa.UniqueConstraint("token_hash"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
    )
    op.create_index("ix_calendar_tokens_token_hash", "calendar_tokens", ["token_hash"])

    # 38. workout_summaries
    op.create_table(
        "workout_summaries",
        sa.Column("summary_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("client_id", UUID, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("model_used", sa.String(100)),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("is_stale", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("summary_id"),
        sa.ForeignKeyConstraint(["client_id"], ["clients.client_id"]),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
    )
    op.create_index("ix_workout_summaries_client_id", "workout_summaries", ["client_id"])

    # 39. data_export_requests
    op.create_table(
        "data_export_requests",
        sa.Column("export_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("client_id", UUID, nullable=False),
        sa.Column("status", exportstatus, nullable=False),
        sa.Column("format", sa.String(10), nullable=False),
        sa.Column("download_url", sa.Text()),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint("export_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.client_id"]),
    )
    op.create_index("ix_data_export_requests_client_id", "data_export_requests", ["client_id"])

    # 40. deletion_requests
    op.create_table(
        "deletion_requests",
        sa.Column("deletion_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("client_id", UUID, nullable=False),
        sa.Column("status", deletionstatus, nullable=False),
        sa.Column("reason", sa.Text()),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("scheduled_for", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint("deletion_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.client_id"]),
    )
    op.create_index("ix_deletion_requests_client_id", "deletion_requests", ["client_id"])

    # 41. stripe_accounts
    op.create_table(
        "stripe_accounts",
        sa.Column("stripe_account_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("stripe_connect_id", sa.String(255)),
        sa.Column("onboarding_status", onboardingstatus, nullable=False),
        sa.Column("charges_enabled", sa.Boolean(), nullable=False),
        sa.Column("payouts_enabled", sa.Boolean(), nullable=False),
        sa.Column("default_currency", sa.String(3), nullable=False),
        sa.Column("processing_fee_percentage", sa.Float()),
        sa.Column("pass_fees_to_client", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("stripe_account_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
    )
    op.create_index("ix_stripe_accounts_gym_id", "stripe_accounts", ["gym_id"])

    # 42. payment_methods
    op.create_table(
        "payment_methods",
        sa.Column("payment_method_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("account_id", UUID, nullable=False),
        sa.Column("stripe_payment_method_id", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("brand", sa.String(50)),
        sa.Column("last4", sa.String(4)),
        sa.Column("exp_month", sa.Integer()),
        sa.Column("exp_year", sa.Integer()),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("payment_method_id"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.account_id"]),
    )
    op.create_index("ix_payment_methods_account_id", "payment_methods", ["account_id"])

    # 43. invoices
    op.create_table(
        "invoices",
        sa.Column("invoice_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("account_id", UUID, nullable=False),
        sa.Column("membership_id", UUID),
        sa.Column("stripe_invoice_id", sa.String(255)),
        sa.Column("status", invoicestatus, nullable=False),
        sa.Column("subtotal", sa.Integer(), nullable=False),
        sa.Column("discount_amount", sa.Integer(), nullable=False),
        sa.Column("tax_amount", sa.Integer(), nullable=False),
        sa.Column("processing_fee", sa.Integer(), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("line_items", JSONB),
        sa.Column("due_date", sa.DateTime(timezone=True)),
        sa.Column("paid_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("invoice_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.account_id"]),
    )
    op.create_index("ix_invoices_gym_id", "invoices", ["gym_id"])
    op.create_index("ix_invoices_account_id", "invoices", ["account_id"])
    op.create_index("ix_invoices_status", "invoices", ["status"])

    # 44. payments
    op.create_table(
        "payments",
        sa.Column("payment_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("invoice_id", UUID, nullable=False),
        sa.Column("account_id", UUID, nullable=False),
        sa.Column("stripe_payment_intent_id", sa.String(255)),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("status", paymentstatus, nullable=False),
        sa.Column("failure_reason", sa.Text()),
        sa.Column("extra_data", JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("payment_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.invoice_id"]),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.account_id"]),
    )
    op.create_index("ix_payments_gym_id", "payments", ["gym_id"])
    op.create_index("ix_payments_invoice_id", "payments", ["invoice_id"])
    op.create_index("ix_payments_status", "payments", ["status"])

    # 45. discount_codes
    op.create_table(
        "discount_codes",
        sa.Column("discount_code_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("discount_type", discounttype, nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("max_uses", sa.Integer()),
        sa.Column("times_used", sa.Integer(), nullable=False),
        sa.Column("applicable_plan_types", sa.String(255)),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("valid_from", sa.DateTime(timezone=True)),
        sa.Column("valid_until", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("discount_code_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
    )
    op.create_index("ix_discount_codes_gym_id", "discount_codes", ["gym_id"])
    op.create_index("ix_discount_codes_code", "discount_codes", ["code"])

    # 46. agreement_templates
    op.create_table(
        "agreement_templates",
        sa.Column("agreement_template_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("requires_signature", sa.Boolean(), nullable=False),
        sa.Column("extra_data", JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("agreement_template_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
    )
    op.create_index("ix_agreement_templates_gym_id", "agreement_templates", ["gym_id"])

    # 47. agreement_envelopes
    op.create_table(
        "agreement_envelopes",
        sa.Column("envelope_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("template_id", UUID, nullable=False),
        sa.Column("client_id", UUID, nullable=False),
        sa.Column("status", envelopestatus, nullable=False),
        sa.Column("signer_email", sa.String(320), nullable=False),
        sa.Column("signer_name", sa.String(200), nullable=False),
        sa.Column("external_envelope_id", sa.String(255)),
        sa.Column("provider", sa.String(50)),
        sa.Column("signed_at", sa.DateTime(timezone=True)),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("signed_document_url", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("envelope_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
        sa.ForeignKeyConstraint(["template_id"], ["agreement_templates.agreement_template_id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.client_id"]),
    )
    op.create_index("ix_agreement_envelopes_gym_id", "agreement_envelopes", ["gym_id"])
    op.create_index("ix_agreement_envelopes_client_id", "agreement_envelopes", ["client_id"])
    op.create_index("ix_agreement_envelopes_status", "agreement_envelopes", ["status"])

    # 48. usage_metric_rollups
    op.create_table(
        "usage_metric_rollups",
        sa.Column("rollup_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("metric_name", sa.String(100), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column("limit_value", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("rollup_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
    )
    op.create_index(
        "ix_usage_metric_rollups_gym_id",
        "usage_metric_rollups", ["gym_id"],
    )
    op.create_index(
        "ix_usage_metric_rollups_metric_name",
        "usage_metric_rollups", ["metric_name"],
    )
    op.create_index(
        "ix_usage_metric_rollups_period",
        "usage_metric_rollups", ["period_start", "period_end"],
    )

    # 49. custom_domains
    op.create_table(
        "custom_domains",
        sa.Column("domain_id", UUID, server_default=gen_uuid, nullable=False),
        sa.Column("gym_id", UUID, nullable=False),
        sa.Column("domain", sa.String(255), nullable=False),
        sa.Column("domain_type", domaintype, nullable=False),
        sa.Column("status", domainstatus, nullable=False),
        sa.Column("dns_records", JSONB),
        sa.Column("verified_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now),
        sa.PrimaryKeyConstraint("domain_id"),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.gym_id"]),
    )
    op.create_index("ix_custom_domains_gym_id", "custom_domains", ["gym_id"])
    op.create_index("ix_custom_domains_domain", "custom_domains", ["domain"])


def downgrade() -> None:
    # drop all tables in reverse dependency order
    op.drop_table("custom_domains")
    op.drop_table("usage_metric_rollups")
    op.drop_table("agreement_envelopes")
    op.drop_table("agreement_templates")
    op.drop_table("discount_codes")
    op.drop_table("payments")
    op.drop_table("invoices")
    op.drop_table("payment_methods")
    op.drop_table("stripe_accounts")
    op.drop_table("deletion_requests")
    op.drop_table("data_export_requests")
    op.drop_table("workout_summaries")
    op.drop_table("calendar_tokens")
    op.drop_table("notification_preferences")
    op.drop_table("device_tokens")
    op.drop_table("webhook_endpoints")
    op.drop_table("progress_photos")
    op.drop_table("client_invitations")
    op.drop_table("notes")
    op.drop_table("audit_logs")
    op.drop_table("program_day_exercises")
    op.drop_table("program_days")
    op.drop_table("client_programs")
    op.drop_table("client_goals")
    op.drop_table("gym_check_ins")
    op.drop_table("trainer_exceptions")
    op.drop_table("trainer_availability")
    op.drop_table("schedules")
    op.drop_table("trainer_client_assignments")
    op.drop_table("client_memberships")
    op.drop_table("plan_templates")
    op.drop_table("locations")
    op.drop_table("accounts")
    op.drop_table("trainer_invitations")
    op.drop_table("user_sessions")
    op.drop_table("refresh_tokens")
    op.drop_table("password_reset_tokens")
    op.drop_table("email_verification_tokens")
    op.drop_table("personal_records")
    op.drop_table("measurements")
    op.drop_table("workout_sets")
    op.drop_table("workout_exercises")
    op.drop_table("workouts")
    op.drop_table("programs")
    op.drop_table("exercises")
    op.drop_table("trainers")
    op.drop_table("clients")
    op.drop_table("users")
    op.drop_table("gyms")

    # drop all enum types
    for enum in reversed(ALL_ENUMS):
        enum.drop(op.get_bind(), checkfirst=True)
