from __future__ import annotations

import asyncio
import signal

from .messaging import EventRouter, RabbitEventBus


async def run_event_worker(
    bus: RabbitEventBus,
    router: EventRouter,
) -> None:
    if not router.routing_keys:
        raise ValueError("Event worker has no registered routing keys")

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()

    def request_stop() -> None:
        stop.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, request_stop)
        except NotImplementedError:
            # Windows Proactor event loop can lack signal handlers.
            pass

    await bus.connect()
    try:
        await bus.consume(router.routing_keys, router.handle)
        await stop.wait()
    finally:
        await bus.close()
