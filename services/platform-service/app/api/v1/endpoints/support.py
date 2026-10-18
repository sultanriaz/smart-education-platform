from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_platform_service
from app.core.errors import DomainError
from app.schemas.support import (
    MessageCreate,
    MessageOut,
    TicketCreate,
    TicketOut,
    TicketUpdateAdmin,
)
from app.security.auth import Principal, current_principal, require_roles
from app.services.platform_service import PlatformService

router = APIRouter(prefix="/support", tags=["Support"])


def ticket_view(ticket, is_admin):
    # Serialize a detached response; never mutate the ORM relationship while filtering.
    view = TicketOut.model_validate(ticket)
    if not is_admin:
        view.messages = [message for message in view.messages if not message.is_internal]
    return view


def fail(exc: DomainError):
    raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.post("/tickets", response_model=TicketOut)
def create_ticket(
    payload: TicketCreate,
    principal: Principal = Depends(current_principal),
    service: PlatformService = Depends(get_platform_service),
):
    return ticket_view(service.create_ticket(payload, principal.user_id), "admin" in principal.roles)


@router.get("/tickets", response_model=list[TicketOut])
def list_tickets(
    principal: Principal = Depends(current_principal),
    service: PlatformService = Depends(get_platform_service),
):
    return [ticket_view(row, "admin" in principal.roles) for row in service.list_tickets(principal.user_id, "admin" in principal.roles)]


@router.get("/tickets/{ticket_id}", response_model=TicketOut)
def get_ticket(
    ticket_id: uuid.UUID,
    principal: Principal = Depends(current_principal),
    service: PlatformService = Depends(get_platform_service),
):
    try:
        return ticket_view(service.get_ticket(ticket_id, principal.user_id, "admin" in principal.roles), "admin" in principal.roles)
    except DomainError as exc:
        fail(exc)


@router.post("/tickets/{ticket_id}/messages", response_model=MessageOut)
def add_message(
    ticket_id: uuid.UUID,
    payload: MessageCreate,
    principal: Principal = Depends(current_principal),
    service: PlatformService = Depends(get_platform_service),
):
    try:
        return service.add_message(
            ticket_id,
            payload,
            principal.user_id,
            "admin" in principal.roles,
        )
    except DomainError as exc:
        fail(exc)


@router.patch("/tickets/{ticket_id}", response_model=TicketOut)
def update_ticket(
    ticket_id: uuid.UUID,
    payload: TicketUpdateAdmin,
    _admin=Depends(require_roles("admin")),
    service: PlatformService = Depends(get_platform_service),
):
    try:
        return ticket_view(service.update_ticket_admin(ticket_id, payload), True)
    except DomainError as exc:
        fail(exc)
