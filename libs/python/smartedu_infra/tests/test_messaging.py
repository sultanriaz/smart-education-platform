import pytest

from smartedu_infra.messaging import (
    binding_plan,
    dead_letter_queue_name,
    service_queue_name,
)


def test_service_queue_names_are_stable():
    assert (
        service_queue_name("smartedu.prod", "notification-service")
        == "smartedu.prod.notification-service.events"
    )
    assert (
        dead_letter_queue_name("smartedu.prod", "notification-service")
        == "smartedu.prod.notification-service.events.dlq"
    )


def test_binding_plan_deduplicates_keys_in_order():
    plan = binding_plan(
        prefix="smartedu.dev",
        service_name="reporting-service",
        routing_keys=["schedule.changed", "schedule.changed", "attendance.#"],
    )
    assert plan.routing_keys == ("schedule.changed", "attendance.#")
    assert plan.retry_queue_name.endswith(".retry")
    assert plan.retry_routing_key == "smartedu.dev.retry.reporting-service"
    assert plan.dead_letter_queue_name.endswith(".dlq")


def test_binding_plan_rejects_empty_subscription():
    with pytest.raises(ValueError):
        binding_plan(
            prefix="smartedu",
            service_name="x-service",
            routing_keys=[],
        )
