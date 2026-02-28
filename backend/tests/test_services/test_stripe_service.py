import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from gym_api.services.stripe_service import handle_payment_success


def _mock_scalar(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


@pytest.mark.asyncio
async def test_handle_payment_success_sets_paid_at():
    invoice = SimpleNamespace(
        invoice_id=uuid.uuid4(),
        status="open",
        paid_at=None,
        membership_id=None,
    )
    payment = SimpleNamespace(
        payment_id=uuid.uuid4(),
        invoice_id=invoice.invoice_id,
        status="pending",
    )

    db = AsyncMock()
    db.execute.side_effect = [
        _mock_scalar(payment),
        _mock_scalar(invoice),
    ]

    result = await handle_payment_success(db, payment_id=payment.payment_id)

    assert result is payment
    assert invoice.paid_at is not None
    assert invoice.status.value == "paid"
