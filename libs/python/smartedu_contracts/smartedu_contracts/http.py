from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PageMeta(BaseModel):
    offset: int = Field(ge=0)
    limit: int = Field(ge=1)
    count: int = Field(ge=0)
    total: int | None = Field(default=None, ge=0)


class Page(BaseModel, Generic[T]):
    items: list[T]
    page: PageMeta


def page(
    items: list[T],
    *,
    offset: int,
    limit: int,
    total: int | None = None,
) -> Page[T]:
    return Page(
        items=items,
        page=PageMeta(
            offset=offset,
            limit=limit,
            count=len(items),
            total=total,
        ),
    )
