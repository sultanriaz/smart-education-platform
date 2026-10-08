from __future__ import annotations

from app.core.errors import TemplateRenderError


class _StrictDict(dict):
    def __missing__(self, key):
        raise KeyError(key)


def render_template(value: str, context: dict) -> str:
    try:
        return value.format_map(_StrictDict(context))
    except (KeyError, ValueError) as exc:
        raise TemplateRenderError(f"Template rendering failed: {exc}") from exc
