from __future__ import annotations

import argparse
import asyncio
import json
import os
import time
import uuid

import aio_pika


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        default=os.getenv("RABBITMQ_URL", "amqp://smartedu:smartedu@localhost:5672/smartedu"),
    )
    parser.add_argument("--messages", type=int, default=5000)
    parser.add_argument("--payload-bytes", type=int, default=512)
    args = parser.parse_args()

    connection = await aio_pika.connect_robust(args.url)
    channel = await connection.channel(publisher_confirms=True)
    exchange = await channel.declare_exchange(
        "smartedu.perf.events",
        aio_pika.ExchangeType.DIRECT,
        durable=False,
        auto_delete=True,
    )
    queue = await channel.declare_queue(
        f"smartedu.perf.{uuid.uuid4()}",
        durable=False,
        auto_delete=True,
    )
    await queue.bind(exchange, routing_key="perf")

    consumed = 0
    done = asyncio.Event()

    async def on_message(message: aio_pika.IncomingMessage) -> None:
        nonlocal consumed
        async with message.process():
            consumed += 1
            if consumed >= args.messages:
                done.set()

    await queue.consume(on_message)

    body = json.dumps({"data": "x" * args.payload_bytes}).encode()
    started = time.perf_counter()

    for i in range(args.messages):
        await exchange.publish(
            aio_pika.Message(
                body=body,
                delivery_mode=aio_pika.DeliveryMode.NOT_PERSISTENT,
                message_id=str(i),
            ),
            routing_key="perf",
        )

    publish_done = time.perf_counter()
    await asyncio.wait_for(done.wait(), timeout=60)
    finished = time.perf_counter()

    print(f"messages={args.messages}")
    print(f"publish_seconds={publish_done - started:.3f}")
    print(f"end_to_end_seconds={finished - started:.3f}")
    print(f"publish_mps={args.messages / (publish_done - started):.2f}")
    print(f"consume_mps={args.messages / (finished - started):.2f}")

    await channel.close()
    await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
