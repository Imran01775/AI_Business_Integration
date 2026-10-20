"""Public (unauthenticated) API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query, Request

from app.core.errors.exceptions import NotFoundError
from app.modules.public.templates import LEGAL_DOCUMENT_KEYS
from app.modules.settings.application.ports import TemplateStorePort

router = APIRouter(prefix="/api/v1/public", tags=["public"])


def _store(request: Request) -> TemplateStorePort:
    return request.app.state.container.template_store


@router.get("/legal/{document}")
async def get_legal_document(
    document: str,
    request: Request,
    locale: Annotated[str, Query(max_length=8)] = "en",
) -> dict[str, object]:
    template_key = LEGAL_DOCUMENT_KEYS.get(document)
    if template_key is None:
        raise NotFoundError(details={"document": document})
    store = _store(request)
    detail = await store.get_template_detail(template_key, locale, tenant_id=None)
    if detail is None and locale != "en":
        detail = await store.get_template_detail(template_key, "en", tenant_id=None)
    if detail is None:
        raise NotFoundError(details={"document": document, "locale": locale})
    return {
        "document": document,
        "key": template_key,
        "locale": detail.locale,
        "version": detail.version,
        "updated_at": detail.updated_at.isoformat(),
        "body_html": detail.body,
    }
