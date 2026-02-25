from datetime import datetime, timezone
from uuid import UUID

from gym_api.utils.pagination import (
    build_pagination_meta,
    decode_cursor,
    encode_cursor,
)


def test_encode_decode_roundtrip():
    original = "2024-01-15T10:30:00+00:00"
    encoded = encode_cursor(original)
    assert decode_cursor(encoded) == original


def test_encode_produces_url_safe_string():
    encoded = encode_cursor("some-value/with+special=chars")
    assert "/" not in encoded or encoded.replace("/", "").isalnum() is False
    assert decode_cursor(encoded) == "some-value/with+special=chars"


class FakeRow:
    def __init__(self, created_at):
        self.created_at = created_at


def test_build_pagination_meta_has_more():
    items = [FakeRow(datetime(2024, 1, i, tzinfo=timezone.utc)) for i in range(1, 22)]
    result_items, meta = build_pagination_meta(items, limit=20, cursor_field="created_at")
    assert len(result_items) == 20
    assert meta["has_more"] is True
    assert meta["next_cursor"] is not None


def test_build_pagination_meta_no_more():
    items = [FakeRow(datetime(2024, 1, i, tzinfo=timezone.utc)) for i in range(1, 11)]
    result_items, meta = build_pagination_meta(items, limit=20, cursor_field="created_at")
    assert len(result_items) == 10
    assert meta["has_more"] is False
    assert meta["next_cursor"] is None


def test_build_pagination_meta_empty():
    result_items, meta = build_pagination_meta([], limit=20, cursor_field="created_at")
    assert len(result_items) == 0
    assert meta["has_more"] is False


def test_build_pagination_meta_uuid_cursor():
    class UUIDRow:
        def __init__(self, id):
            self.id = id

    items = [UUIDRow(UUID(f"00000000-0000-0000-0000-{str(i).zfill(12)}")) for i in range(21)]
    result_items, meta = build_pagination_meta(items, limit=20, cursor_field="id")
    assert meta["has_more"] is True
    decoded = decode_cursor(meta["next_cursor"])
    assert decoded == "00000000-0000-0000-0000-000000000019"
