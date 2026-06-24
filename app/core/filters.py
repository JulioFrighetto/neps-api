from datetime import date
from typing import Any

from sqlalchemy.orm import Query

def _parse_bool(v: str) -> bool | None:
    return v.lower() in ("true", "1", "yes") if v is not None else None

def _parse_date(v: str) -> date | None:
    try:
        return date.fromisoformat(v)
    except (ValueError, TypeError):
        return None

def apply_filters(
    query: Query,
    model: Any,
    filter_params: dict[str, Any],
) -> tuple[Query, list[str]]:
    applied = []

    for raw_key, raw_value in filter_params.items():
        if raw_value is None:
            continue

        key: str = raw_key

        if key.endswith("_like"):
            field = key[:-5]
            col = getattr(model, field, None)
            if col is not None:
                query = query.filter(col.ilike(f"%{raw_value}%"))
                applied.append(key)

        elif key.endswith("_min"):
            field = key[:-4]
            col = getattr(model, field, None)
            if col is not None:
                query = query.filter(col >= int(raw_value))
                applied.append(key)

        elif key.endswith("_max"):
            field = key[:-4]
            col = getattr(model, field, None)
            if col is not None:
                query = query.filter(col <= int(raw_value))
                applied.append(key)

        elif key.endswith("_from"):
            field = key[:-5]
            col = getattr(model, field, None)
            if col is not None:
                d = _parse_date(raw_value)
                if d:
                    query = query.filter(col >= d)
                    applied.append(key)

        elif key.endswith("_to"):
            field = key[:-3]
            col = getattr(model, field, None)
            if col is not None:
                d = _parse_date(raw_value)
                if d:
                    query = query.filter(col <= d)
                    applied.append(key)

        elif key.endswith("_in"):
            field = key[:-3]
            col = getattr(model, field, None)
            if col is not None:
                values = [v.strip() for v in str(raw_value).split(",") if v.strip()]
                if values:
                    query = query.filter(col.in_(values))
                    applied.append(key)

        elif key.endswith("_isnull"):
            field = key[:-7]
            col = getattr(model, field, None)
            if col is not None:
                if _parse_bool(str(raw_value)):
                    query = query.filter(col.is_(None))
                    applied.append(key)
                else:
                    query = query.filter(col.is_not(None))
                    applied.append(key)

        else:
            col = getattr(model, key, None)
            if col is not None:
                query = query.filter(col == raw_value)
                applied.append(key)

    return query, applied
