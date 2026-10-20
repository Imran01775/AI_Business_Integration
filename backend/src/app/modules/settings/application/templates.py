"""Sandboxed template renderer (R-CFG-05)."""

from __future__ import annotations

from typing import Any

from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment

from app.core.errors.exceptions import ValidationError
from app.modules.settings.application.ports import TemplateStorePort
from app.shared.context import SettingsResolveContext


class TemplateRenderer:
    def __init__(self, store: TemplateStorePort | None = None) -> None:
        self._env = SandboxedEnvironment(autoescape=True, undefined=StrictUndefined)
        self._store = store
        self._templates: dict[str, dict[str, str]] = {}
        self._variable_schemas: dict[str, list[str]] = {}

    def register(self, key: str, locale: str, body: str, variables: list[str]) -> None:
        self._templates.setdefault(key, {})[locale] = body
        self._variable_schemas[key] = variables

    async def render(
        self,
        key: str,
        ctx: SettingsResolveContext,
        vars: dict[str, Any],
        locale: str = "en",
    ) -> str:
        body: str | None = None
        expected_vars: list[str] = []
        if self._store is not None:
            loaded = await self._store.get_template(key, locale, tenant_id=ctx.tenant_id)
            if loaded is not None:
                body, expected_vars = loaded
        if body is None:
            if key not in self._templates:
                raise ValidationError(details={"key": key}, code="templates.not_found")
            body = self._templates[key].get(locale) or self._templates[key].get("en")
            if body is None:
                raise ValidationError(
                    details={"key": key, "locale": locale}, code="templates.not_found"
                )
            expected_vars = self._variable_schemas.get(key, [])
        missing = [v for v in expected_vars if v not in vars]
        extra = [v for v in vars if v not in expected_vars]
        if missing or extra:
            raise ValidationError(
                details={"missing": missing, "unexpected": extra},
                code="templates.invalid_variables",
            )
        template = self._env.from_string(body)
        return template.render(**vars)
