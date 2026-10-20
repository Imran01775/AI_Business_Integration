"""Identity message template defaults."""

from __future__ import annotations

DEFAULT_IDENTITY_TEMPLATES: list[tuple[str, str, str, list[str]]] = [
    (
        "identity.verify_email",
        "en",
        "Verify your email: {{ verify_url }}",
        ["verify_url"],
    ),
    (
        "identity.verify_email",
        "bn",
        "আপনার ইমেইল যাচাই করুন: {{ verify_url }}",
        ["verify_url"],
    ),
    (
        "identity.reset_password",
        "en",
        "Reset your password: {{ reset_url }}",
        ["reset_url"],
    ),
    (
        "identity.reset_password",
        "bn",
        "পাসওয়ার্ড রিসেট করুন: {{ reset_url }}",
        ["reset_url"],
    ),
]
