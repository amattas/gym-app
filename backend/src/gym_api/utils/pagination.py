import base64
import uuid
from datetime import datetime

from sqlalchemy import Select, asc, desc


def encode_cursor(value: str) -> str:
    return base64.urlsafe_b64encode(value.encode()).decode()


def decode_cursor(cursor: str) -> str:
    return base64.urlsafe_b64decode(cursor.encode()).decode()


def apply_cursor_pagination(
    query: Select,
    *,
    order_column,
    cursor: str | None = None,
    limit: int = 20,
    ascending: bool = True,
) -> Select:
    direction = asc if ascending else desc
    query = query.order_by(direction(order_column))

    if cursor:
        raw = decode_cursor(cursor)
        if isinstance(order_column.type, type) and hasattr(order_column.type, "impl"):
            cursor_val = raw
        else:
            col_type = order_column.type
            type_name = type(col_type).__name__
            if type_name in ("DateTime", "TIMESTAMP"):
                cursor_val = datetime.fromisoformat(raw)
            elif type_name == "Uuid":
                cursor_val = uuid.UUID(raw)
            else:
                cursor_val = raw

        if ascending:
            query = query.where(order_column > cursor_val)
        else:
            query = query.where(order_column < cursor_val)

    query = query.limit(limit + 1)
    return query


def build_pagination_meta(items: list, limit: int, cursor_field: str) -> tuple[list, dict]:
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]

    next_cursor = None
    if has_more and items:
        last = items[-1]
        if hasattr(last, cursor_field):
            val = getattr(last, cursor_field, None)
        else:
            val = last[cursor_field]
        if isinstance(val, datetime):
            next_cursor = encode_cursor(val.isoformat())
        elif isinstance(val, uuid.UUID):
            next_cursor = encode_cursor(str(val))
        else:
            next_cursor = encode_cursor(str(val))

    return items, {"next_cursor": next_cursor, "has_more": has_more, "limit": limit}
