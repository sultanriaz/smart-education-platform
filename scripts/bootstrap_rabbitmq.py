from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from smartedu_infra import MessagingSettings, RabbitEventBus


async def main() -> None:
    config_path = Path(
        os.getenv(
            "EVENT_SUBSCRIPTIONS_FILE",
            "contracts/event-subscriptions.json",
        )
    )
    data = json.loads(config_path.read_text(encoding="utf-8"))
    subscriptions = data.get("subscriptions", {})
    if not isinstance(subscriptions, dict):
        raise RuntimeError("event subscriptions file is invalid")

    settings = MessagingSettings()

    for service_name, routing_keys in subscriptions.items():
        if not isinstance(routing_keys, list):
            raise RuntimeError(
                f"Routing keys for {service_name} must be a list"
            )
        bus = RabbitEventBus(
            service_name=service_name,
            settings=settings,
        )
        try:
            queue = await bus.declare_consumer_queue(routing_keys)
            print(
                f"{service_name}: {queue.name} <- "
                + ", ".join(routing_keys)
            )
        finally:
            await bus.close()


if __name__ == "__main__":
    asyncio.run(main())
