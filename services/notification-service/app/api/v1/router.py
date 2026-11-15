from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    internal,
    notifications,
    preferences,
    teacher,
)

api_router = APIRouter()
api_router.include_router(notifications.router)

# Direct alias router so both /unread-count and /notifications/unread-count resolve
direct_notifications = APIRouter(tags=["Notifications"])
for route in notifications.router.routes:
    path = getattr(route, "path", "")
    if path.startswith("/notifications"):
        subpath = path[len("/notifications"):] or "/"
        direct_notifications.add_api_route(
            subpath,
            route.endpoint,
            methods=list(getattr(route, "methods", None) or ["GET"]),
            response_model=getattr(route, "response_model", None),
            status_code=getattr(route, "status_code", 200),
            name=getattr(route, "name", None),
        )
api_router.include_router(direct_notifications)

api_router.include_router(preferences.router)
api_router.include_router(teacher.router)
api_router.include_router(admin.router)
api_router.include_router(internal.router)
