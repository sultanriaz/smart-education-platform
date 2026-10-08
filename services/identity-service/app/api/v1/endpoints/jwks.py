from fastapi import APIRouter, Response

from app.security.jwt import public_jwks

router = APIRouter(tags=["Authentication"])


@router.get("/.well-known/jwks.json")
def jwks(response: Response):
    response.headers["Cache-Control"] = "public, max-age=300"
    return public_jwks()
