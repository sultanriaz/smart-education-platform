from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from threading import Barrier
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class ConcurrentResult(Generic[T]):
    values: tuple[T, ...]
    errors: tuple[BaseException, ...]


def run_concurrently(
    workers: int,
    operation: Callable[[int], T],
) -> ConcurrentResult[T]:
    if workers < 2:
        raise ValueError("workers must be at least 2")

    barrier = Barrier(workers)

    def wrapped(index: int) -> T:
        barrier.wait(timeout=10)
        return operation(index)

    values: list[T] = []
    errors: list[BaseException] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(wrapped, index) for index in range(workers)]
        for future in futures:
            try:
                values.append(future.result(timeout=30))
            except BaseException as exc:
                errors.append(exc)

    return ConcurrentResult(tuple(values), tuple(errors))
