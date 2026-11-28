from decimal import Decimal

import pytest

from decision_mirror.profiling.self_consistency import shift_flag


def test_shift_flag_exact_decimal_threshold_equality():
    assert shift_flag([0.40, 0.40, 0.50, 0.50], 2, Decimal("0.10"))


def test_shift_flag_just_below_threshold():
    assert not shift_flag([0.40, 0.40, 0.499, 0.499], 2, Decimal("0.10"))


def test_shift_flag_just_above_threshold():
    assert shift_flag([0.40, 0.40, 0.501, 0.501], 2, Decimal("0.10"))


def test_shift_flag_requires_two_complete_windows():
    assert not shift_flag([0.20, 0.80], 2, Decimal("0.10"))


def test_shift_window_must_be_positive():
    with pytest.raises(ValueError):
        shift_flag([0.2, 0.8], 0, Decimal("0.10"))
