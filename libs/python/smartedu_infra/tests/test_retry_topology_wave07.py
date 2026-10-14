import asyncio
from types import SimpleNamespace
from unittest.mock import patch

from smartedu_infra.messaging import RabbitEventBus, binding_plan
from smartedu_infra.settings import MessagingSettings


class Queue:
    def __init__(self): self.bindings = []
    async def bind(self, exchange, routing_key): self.bindings.append((exchange, routing_key))


class Channel:
    def __init__(self): self.queues = {}
    async def declare_queue(self, name, **kwargs):
        self.queues[name] = kwargs
        return Queue()


class Exchange:
    def __init__(self): self.published = []
    async def publish(self, value, routing_key, mandatory):
        self.published.append((value, routing_key, mandatory))


class Message:
    def __init__(self, attempt):
        self.headers = {"x-smartedu-attempt": attempt}
        self.acked = False
    async def ack(self): self.acked = True


def instance():
    bus = RabbitEventBus(service_name="notification-service", settings=MessagingSettings(
        EVENT_RETRY_DELAY_MS=5000, EVENT_MAX_DELIVERY_ATTEMPTS=5
    ))
    bus._channel = Channel()
    bus._event_exchange = object()
    bus._retry_exchange = Exchange()
    bus._dlx = Exchange()
    bus._plan = binding_plan(prefix="smartedu", service_name="notification-service", routing_keys=("attendance.#",))
    bus._connection = SimpleNamespace(is_closed=False)
    return bus


def test_exponential_retry_queues_are_durable_and_legacy_queue_is_unchanged():
    bus = instance()
    async def run(): await bus.declare_consumer_queue(("attendance.#",))
    # override _ensure_connected because fake channel is not a real aio_pika object
    async def connected(): pass
    bus._ensure_connected = connected
    asyncio.run(run())
    q = bus._channel.queues
    assert q[bus._plan.retry_queue_name]["arguments"]["x-message-ttl"] == 5000
    assert q[bus._plan.retry_queue_name + ".stage2"]["arguments"]["x-message-ttl"] == 20000
    assert q[bus._plan.retry_queue_name + ".stage3"]["arguments"]["x-message-ttl"] == 80000
    assert all(x["durable"] for x in q.values())


def test_retries_back_off_then_enter_dlq_only_after_exhaustion():
    bus = instance()
    bus._copy_message = lambda message, headers: SimpleNamespace(headers=headers)
    for attempt in (1, 2, 3, 4):
        m = Message(attempt)
        asyncio.run(bus._retry_or_dead_letter(m))
        assert m.acked
    keys = [item[1] for item in bus._retry_exchange.published]
    assert keys == [
        bus._plan.retry_routing_key,
        bus._plan.retry_routing_key + ".stage2",
        bus._plan.retry_routing_key + ".stage3",
        bus._plan.retry_routing_key + ".stage3",
    ]
    poison = Message(5)
    asyncio.run(bus._retry_or_dead_letter(poison))
    assert poison.acked
    assert len(bus._dlx.published) == 1
