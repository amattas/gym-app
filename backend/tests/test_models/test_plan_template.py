import uuid

from gym_api.models.plan_template import PlanStatus, PlanTemplate, PlanType


def test_plan_template_instantiation():
    template = PlanTemplate(
        gym_id=uuid.uuid4(),
        name="Monthly Unlimited",
        plan_type=PlanType.membership,
        status=PlanStatus.active,
        is_addon=False,
    )
    assert template.name == "Monthly Unlimited"
    assert template.plan_type == PlanType.membership
    assert template.status == PlanStatus.active
    assert template.is_addon is False
    assert template.description is None


def test_plan_type_enum():
    assert PlanType.membership.value == "membership"
    assert PlanType.punch_card.value == "punch_card"
    assert PlanType.drop_in.value == "drop_in"


def test_plan_status_enum():
    assert PlanStatus.active.value == "active"
    assert PlanStatus.archived.value == "archived"
    assert PlanStatus.draft.value == "draft"


def test_plan_template_addon():
    template = PlanTemplate(
        gym_id=uuid.uuid4(),
        name="Personal Training Add-on",
        plan_type=PlanType.membership,
        is_addon=True,
        requires_primary_plan_type="membership",
        addon_discount_percentage=10.0,
    )
    assert template.is_addon is True
    assert template.requires_primary_plan_type == "membership"
    assert template.addon_discount_percentage == 10.0
