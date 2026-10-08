import pytest

from smartedu_perf import percentile


def test_percentile_interpolates():
    assert percentile([1, 2, 3, 4, 5], 50) == 3
    assert percentile([1, 2, 3, 4], 50) == 2.5


def test_percentile_rejects_invalid_input():
    with pytest.raises(ValueError):
        percentile([], 95)
    with pytest.raises(ValueError):
        percentile([1], 101)
