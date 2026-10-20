"""Default platform seed data (idempotent)."""

from __future__ import annotations

from app.modules.identity.templates import DEFAULT_IDENTITY_TEMPLATES
from app.modules.public.templates import DEFAULT_PUBLIC_TEMPLATES
from app.modules.settings.application.ports import TemplateStorePort
from app.modules.tenancy.templates import DEFAULT_TENANCY_TEMPLATES

DEFAULT_TEMPLATES: list[tuple[str, str, str, list[str]]] = [
    (
        "platform.welcome",
        "en",
        "Welcome to {{ business_name }}.",
        ["business_name"],
    ),
    (
        "platform.welcome",
        "bn",
        "{{ business_name }}-এ স্বাগতম।",
        ["business_name"],
    ),
    (
        "rules.redirect_message",
        "en",
        "Please ask about our products or services.",
        [],
    ),
    (
        "rules.redirect_message",
        "bn",
        "অনুগ্রহ করে আমাদের পণ্য বা সেবা সম্পর্কে জিজ্ঞাসা করুন।",
        [],
    ),
] + DEFAULT_IDENTITY_TEMPLATES + DEFAULT_TENANCY_TEMPLATES + DEFAULT_PUBLIC_TEMPLATES


async def seed_default_templates(store: TemplateStorePort) -> int:
    count = 0
    for key, locale, body, variables in DEFAULT_TEMPLATES:
        await store.upsert(key, locale, body, variables, tenant_id=None)
        count += 1
    return count
