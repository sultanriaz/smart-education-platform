from __future__ import annotations

import argparse
import asyncio
import os
import statistics
import time

from redis.asyncio import Redis


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=os.getenv("REDIS_CACHE_URL", "redis://localhost:56379/0"))
    parser.add_argument("--operations", type=int, default=5000)
    parser.add_argument("--concurrency", type=int, default=50)
    parser.add_argument("--ttl", type=int, default=60)
    args = parser.parse_args()

    client = Redis.from_url(args.url, decode_responses=False)
    semaphore = asyncio.Semaphore(args.concurrency)
    latencies: list[float] = []
    failures = 0

    async def one(index: int):
        nonlocal failures
        async with semaphore:
            key = f"smartedu:perf:{index % 1000}".encode()
            payload = b"x" * 512
            started = time.perf_counter()
            try:
                await client.set(key, payload, ex=args.ttl)
                value = await client.get(key)
                if value != payload:
                    failures += 1
            except Exception:
                failures += 1
            finally:
                latencies.append((time.perf_counter() - started) * 1000)

    try:
        started = time.perf_counter()
        await asyncio.gather(*(one(i) for i in range(args.operations)))
        elapsed = time.perf_counter() - started
    finally:
        await client.aclose()

    ordered = sorted(latencies)
    p95 = ordered[max(0, int(len(ordered) * 0.95) - 1)]
    p99 = ordered[max(0, int(len(ordered) * 0.99) - 1)]
    print(f"operations={args.operations}")
    print(f"failures={failures}")
    print(f"elapsed_seconds={elapsed:.3f}")
    print(f"ops_per_second={args.operations / elapsed:.2f}")
    print(f"avg_ms={statistics.mean(latencies):.3f}")
    print(f"p95_ms={p95:.3f}")
    print(f"p99_ms={p99:.3f}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
