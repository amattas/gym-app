import uuid
from datetime import datetime, timezone

from gym_api.models.client_membership import ClientMembership, MembershipStatus


def test_client_membership_instantiation():
    membership = ClientMembership(
        gym_id=uuid.uuid4(),
        client_id=uuid.uuid4(),
        plan_template_id=uuid.uuid4(),
        plan_type="membership",
        status=MembershipStatus.active,
        started_at=datetime.now(timezone.utc),
        visits_used_this_period=0,
    )
    assert membership.status == MembershipStatus.active
    assert membership.visits_used_this_period == 0
    assert membership.total_visits_remaining is None
    assert membership.pause_info is None


def test_membership_status_enum():
    assert MembershipStatus.active.value == "active"
    assert MembershipStatus.paused.value == "paused"
    assert MembershipStatus.cancelled.value == "cancelled"
    assert MembershipStatus.expired.value == "expired"
    assert MembershipStatus.pending.value == "pending"


def test_client_membership_with_visits():
    membership = ClientMembership(
        gym_id=uuid.uuid4(),
        client_id=uuid.uuid4(),
        plan_template_id=uuid.uuid4(),
        plan_type="punch_card",
        status=MembershipStatus.active,
        started_at=datetime.now(timezone.utc),
        total_visits_remaining=10,
        visit_entitlement={"total_visits": 10},
    )
    assert membership.total_visits_remaining == 10
    assert membership.visit_entitlement == {"total_visits": 10}


def test_client_membership_with_base():
    base_id = uuid.uuid4()
    membership = ClientMembership(
        gym_id=uuid.uuid4(),
        client_id=uuid.uuid4(),
        plan_template_id=uuid.uuid4(),
        plan_type="membership",
        status=MembershipStatus.active,
        started_at=datetime.now(timezone.utc),
        base_membership_id=base_id,
    )
    assert membership.base_membership_id == base_id
