from __future__ import annotations

from app.queue.dispatcher import TaskDispatcher, get_task_dispatcher
from app.services.target_resolver import TargetResolver


def get_target_resolver() -> TargetResolver:
    return TargetResolver()


def get_dispatcher() -> TaskDispatcher:
    return get_task_dispatcher()
