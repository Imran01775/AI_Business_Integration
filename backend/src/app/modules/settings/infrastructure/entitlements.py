"""Stub entitlement checker until billing module exists."""

from __future__ import annotations

from app.modules.settings.application.ports import EntitlementCheckerPort


class AllowAllEntitlements(EntitlementCheckerPort):
    async def has_entitlement(self, entitlement: str, tenant_id: str | None) -> bool:
        _ = (entitlement, tenant_id)
        return True
