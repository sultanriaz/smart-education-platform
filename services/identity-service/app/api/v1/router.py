from fastapi import APIRouter

from app.api.v1.endpoints import auth, internal, roles, users, data_jobs

api_router = APIRouter()
api_router.include_router(auth.router)

try:
    from app.sprint18_security.router import get_security_router
    api_router.include_router(get_security_router())
except Exception:
    pass

api_router.include_router(users.router)
api_router.include_router(roles.router)

api_router.include_router(internal.router)
api_router.include_router(data_jobs.router)
