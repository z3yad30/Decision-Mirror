from decimal import Decimal
from typing import Iterable


def _decimal(value: object) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def shift_flag(
    usable_scores: Iterable[object],
    shift_window: int,
    shift_threshold: object,
) -> bool:
    """Return whether the last complete window differs from the earlier one."""
    scores = [_decimal(value) for value in usable_scores]
    if shift_window < 1:
        raise ValueError("shift_window must be at least 1")
    if len(scores) < 2 * shift_window:
        return False

    threshold = _decimal(shift_threshold)
    recent = scores[-shift_window:]
    earlier = scores[-2 * shift_window:-shift_window]
    recent_mean = sum(recent, Decimal(0)) / Decimal(shift_window)
    earlier_mean = sum(earlier, Decimal(0)) / Decimal(shift_window)
    return abs(recent_mean - earlier_mean) >= threshold
