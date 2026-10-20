"""Tenancy message template defaults."""

from __future__ import annotations

DEFAULT_TENANCY_TEMPLATES: list[tuple[str, str, str, list[str]]] = [
    (
        "tenancy.invitation",
        "en",
        "You are invited to join {{ business_name }}: {{ accept_url }}",
        ["business_name", "accept_url"],
    ),
    (
        "tenancy.invitation",
        "bn",
        "আপনাকে {{ business_name }}-এ যোগ দিতে আমন্ত্রণ করা হয়েছে: {{ accept_url }}",
        ["business_name", "accept_url"],
    ),
]
