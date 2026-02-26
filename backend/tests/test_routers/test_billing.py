import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from gym_api.dependencies.auth import get_current_user
from gym_api.main import app
from tests.test_routers.helpers import make_mock_user

GYM_ID = uuid.uuid4()


def _make_stripe_account(**overrides):
    defaults = dict(
        stripe_account_id=uuid.uuid4(),
        gym_id=GYM_ID,
        stripe_connect_id="acct_test123",
        onboarding_status="complete",
        charges_enabled=True,
        payouts_enabled=True,
        default_currency="usd",
        processing_fee_percentage=2.9,
        pass_fees_to_client=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_payment_method(**overrides):
    defaults = dict(
        payment_method_id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        stripe_payment_method_id="pm_test123",
        type="card",
        brand="visa",
        last4="4242",
        exp_month=12,
        exp_year=2027,
        is_default=True,
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_invoice(**overrides):
    defaults = dict(
        invoice_id=uuid.uuid4(),
        gym_id=GYM_ID,
        account_id=uuid.uuid4(),
        membership_id=uuid.uuid4(),
        stripe_invoice_id=None,
        status="open",
        subtotal=5000,
        discount_amount=0,
        tax_amount=0,
        processing_fee=0,
        total=5000,
        currency="usd",
        description="Monthly membership",
        line_items=None,
        due_date=None,
        paid_at=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_payment(**overrides):
    defaults = dict(
        payment_id=uuid.uuid4(),
        gym_id=GYM_ID,
        invoice_id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        stripe_payment_intent_id=None,
        amount=5000,
        currency="usd",
        status="succeeded",
        failure_reason=None,
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_discount_code(**overrides):
    defaults = dict(
        discount_code_id=uuid.uuid4(),
        gym_id=GYM_ID,
        code="SUMMER20",
        description="Summer discount",
        discount_type="percentage",
        amount=20.0,
        max_uses=100,
        times_used=5,
        applicable_plan_types=None,
        is_active=True,
        valid_from=None,
        valid_until=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


@pytest.fixture(autouse=True)
def _auth_override():
    user = make_mock_user(gym_id=GYM_ID)
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_stripe_connect(client):
    acct = _make_stripe_account()
    with patch(
        "gym_api.routers.billing.stripe_service.create_onboarding_link",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = {"account": acct, "url": "https://connect.stripe.com/setup"}
        resp = await client.post(
            "/v1/billing/stripe/connect",
            json={"return_url": "https://gym.com/return", "refresh_url": "https://gym.com/refresh"},
        )
    assert resp.status_code == 201
    assert "onboarding_url" in resp.json()


@pytest.mark.asyncio
async def test_get_stripe_account(client):
    acct = _make_stripe_account()
    with patch(
        "gym_api.routers.billing.stripe_service.get_stripe_account",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = acct
        resp = await client.get("/v1/billing/stripe/account")
    assert resp.status_code == 200
    assert resp.json()["data"]["charges_enabled"] is True


@pytest.mark.asyncio
async def test_get_stripe_account_not_found(client):
    with patch(
        "gym_api.routers.billing.stripe_service.get_stripe_account",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.get("/v1/billing/stripe/account")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_add_payment_method(client):
    pm = _make_payment_method()
    with patch(
        "gym_api.routers.billing.stripe_service.add_payment_method",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = pm
        resp = await client.post(
            f"/v1/billing/payment-methods?account_id={uuid.uuid4()}",
            json={"stripe_payment_method_id": "pm_test123"},
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["last4"] == "4242"


@pytest.mark.asyncio
async def test_list_payment_methods(client):
    methods = [_make_payment_method(), _make_payment_method(last4="1234")]
    with patch(
        "gym_api.routers.billing.stripe_service.list_payment_methods",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = methods
        resp = await client.get(
            f"/v1/billing/payment-methods?account_id={uuid.uuid4()}"
        )
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_list_invoices(client):
    invoices = [_make_invoice()]
    with patch(
        "gym_api.routers.billing.invoice_service.list_invoices_for_membership",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = invoices
        resp = await client.get(
            f"/v1/billing/invoices?membership_id={uuid.uuid4()}"
        )
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


@pytest.mark.asyncio
async def test_get_invoice(client):
    inv = _make_invoice()
    with patch(
        "gym_api.routers.billing.invoice_service.get_invoice",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = inv
        resp = await client.get(f"/v1/billing/invoices/{inv.invoice_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 5000


@pytest.mark.asyncio
async def test_get_invoice_not_found(client):
    with patch(
        "gym_api.routers.billing.invoice_service.get_invoice",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        resp = await client.get(f"/v1/billing/invoices/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_discount_code(client):
    code = _make_discount_code()
    with patch(
        "gym_api.routers.billing.discount_service.create_discount_code",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = code
        resp = await client.post(
            "/v1/billing/discount-codes",
            json={
                "code": "SUMMER20",
                "discount_type": "percentage",
                "amount": 20.0,
            },
        )
    assert resp.status_code == 201
    assert resp.json()["data"]["code"] == "SUMMER20"


@pytest.mark.asyncio
async def test_list_discount_codes(client):
    codes = [_make_discount_code()]
    with patch(
        "gym_api.routers.billing.discount_service.list_discount_codes",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = (codes, {"next_cursor": None, "has_more": False, "limit": 20})
        resp = await client.get("/v1/billing/discount-codes")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


@pytest.mark.asyncio
async def test_delete_discount_code(client):
    code = _make_discount_code()
    with (
        patch(
            "gym_api.routers.billing.discount_service.get_discount_code",
            new_callable=AsyncMock,
        ) as get_mock,
        patch(
            "gym_api.routers.billing.discount_service.delete_discount_code",
            new_callable=AsyncMock,
        ),
    ):
        get_mock.return_value = code
        resp = await client.delete(
            f"/v1/billing/discount-codes/{code.discount_code_id}"
        )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_purchase_session_pack(client):
    from gym_api.models.plan_template import PlanType

    template = SimpleNamespace(
        plan_template_id=uuid.uuid4(),
        gym_id=GYM_ID,
        name="10 Session Pack",
        plan_type=PlanType.session_pack,
        payment_config={"price_cents": 15000},
        visit_entitlement={"total_visits": 10},
    )
    membership = SimpleNamespace(
        client_membership_id=uuid.uuid4(),
        gym_id=GYM_ID,
        client_id=uuid.uuid4(),
        plan_template_id=template.plan_template_id,
        plan_type="session_pack",
        status="pending",
        started_at=datetime.now(timezone.utc),
        expires_at=None,
        visit_entitlement={"total_visits": 10},
        visits_used_this_period=0,
        total_visits_remaining=10,
        current_period_start=None,
        current_period_end=None,
        pause_info=None,
        cancellation_info=None,
        base_membership_id=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    checkout_result = {
        "invoice_id": uuid.uuid4(),
        "payment_id": uuid.uuid4(),
        "client_secret": "pi_secret_test",
        "status": "pending",
        "total": 15000,
        "currency": "usd",
    }
    with (
        patch(
            "gym_api.routers.billing.plan_template_service.get_plan_template",
            new_callable=AsyncMock,
            return_value=template,
        ),
        patch(
            "gym_api.routers.billing.membership_service.create_membership",
            new_callable=AsyncMock,
            return_value=membership,
        ),
        patch(
            "gym_api.routers.billing.stripe_service.create_checkout",
            new_callable=AsyncMock,
            return_value=checkout_result,
        ),
    ):
        resp = await client.post(
            "/v1/billing/session-packs/purchase",
            json={
                "plan_template_id": str(template.plan_template_id),
                "client_id": str(uuid.uuid4()),
            },
        )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["total"] == 15000
    assert "membership_id" in data


@pytest.mark.asyncio
async def test_purchase_session_pack_wrong_type(client):
    from gym_api.models.plan_template import PlanType

    template = SimpleNamespace(
        plan_template_id=uuid.uuid4(),
        gym_id=GYM_ID,
        name="Monthly Membership",
        plan_type=PlanType.membership,
        payment_config={"price_cents": 5000},
    )
    with patch(
        "gym_api.routers.billing.plan_template_service.get_plan_template",
        new_callable=AsyncMock,
        return_value=template,
    ):
        resp = await client.post(
            "/v1/billing/session-packs/purchase",
            json={
                "plan_template_id": str(template.plan_template_id),
                "client_id": str(uuid.uuid4()),
            },
        )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_validate_discount_code(client):
    with patch(
        "gym_api.routers.billing.discount_service.validate_discount_code",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = {
            "valid": True,
            "discount_type": "percentage",
            "amount": 20.0,
            "message": None,
        }
        resp = await client.post(
            "/v1/billing/discount-codes/validate",
            json={"code": "SUMMER20"},
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["valid"] is True
