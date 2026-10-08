from __future__ import annotations

from fastapi import FastAPI, Request

app = FastAPI()


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def echo(path: str, request: Request):
    return {
        "path": "/" + path,
        "method": request.method,
        "request_id": request.headers.get("x-request-id"),
        "authorization": request.headers.get("authorization"),
    }
