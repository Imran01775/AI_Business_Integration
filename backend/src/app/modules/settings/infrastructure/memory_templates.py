"""In-memory template store for unit tests."""

from __future__ import annotations

from uuid import UUID

from datetime import UTC, datetime

from app.modules.settings.application.ports import TemplateDetail, TemplateStorePort


class InMemoryTemplateStore(TemplateStorePort):
    def __init__(self) -> None:
        self._templates: dict[tuple[UUID | None, str, str], tuple[str, list[str], int]] = {}
        self._history: list[dict[str, object]] = []

    async def upsert(
        self,
        key: str,
        locale: str,
        body: str,
        variables: list[str],
        *,
        tenant_id: UUID | None = None,
    ) -> int:
        version = self._templates.get((tenant_id, key, locale), ("", [], 0))[2] + 1
        self._templates[(tenant_id, key, locale)] = (body, variables, version)
        self._history.append(
            {
                "tenant_id": tenant_id,
                "key": key,
                "locale": locale,
                "version": version,
                "body": body,
            },
        )
        return version

    async def get_template(
        self,
        key: str,
        locale: str,
        *,
        tenant_id: UUID | None = None,
    ) -> tuple[str, list[str]] | None:
        item = self._templates.get((tenant_id, key, locale))
        if item is None:
            return None
        return item[0], item[1]

    async def get_template_detail(
        self,
        key: str,
        locale: str,
        *,
        tenant_id: UUID | None = None,
    ) -> TemplateDetail | None:
        item = self._templates.get((tenant_id, key, locale))
        if item is None:
            return None
        body, variables, version = item
        return TemplateDetail(
            body=body,
            variables=variables,
            version=version,
            locale=locale,
            updated_at=datetime.now(tz=UTC),
        )

    async def rollback(
        self,
        key: str,
        locale: str,
        to_version: int,
        *,
        tenant_id: UUID | None = None,
    ) -> None:
        for entry in reversed(self._history):
            if (
                entry["tenant_id"] == tenant_id
                and entry["key"] == key
                and entry["locale"] == locale
                and entry["version"] == to_version
            ):
                await self.upsert(key, locale, str(entry["body"]), [], tenant_id=tenant_id)
                return
        raise LookupError(f"version {to_version} not found")
