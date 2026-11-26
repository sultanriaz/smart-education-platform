from __future__ import annotations

import math
from collections.abc import Sequence


def percentile(values: Sequence[float], percent: float) -> float:
    if not values:
        raise ValueError("values cannot be empty")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")

    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]

    rank = (len(ordered) - 1) * (percent / 100.0)
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return ordered[low]

    fraction = rank - low
    return ordered[low] + (ordered[high] - ordered[low]) * fraction
