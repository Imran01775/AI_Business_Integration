"""Identity / platform permission constants."""

from __future__ import annotations

from typing import Final

PERM_PLATFORM_ADMIN: Final = "platform.admin:write"
PERM_PLATFORM_REVIEW: Final = "platform.subscription:review"
PERM_PLATFORM_PAYMENT_VERIFY: Final = "platform.payment:verify"
PERM_PLATFORM_SUPPORT: Final = "platform.support:impersonate"
PERM_PLATFORM_CONTENT: Final = "platform.content:write"

PLATFORM_ROLE_PERMISSIONS: dict[str, tuple[str, ...]] = {
    "super_admin": (
        PERM_PLATFORM_ADMIN,
        PERM_PLATFORM_REVIEW,
        PERM_PLATFORM_PAYMENT_VERIFY,
        PERM_PLATFORM_SUPPORT,
        PERM_PLATFORM_CONTENT,
        "platform:*",
    ),
    "reviewer": (PERM_PLATFORM_REVIEW,),
    "payment_verifier": (PERM_PLATFORM_PAYMENT_VERIFY,),
    "support": (PERM_PLATFORM_SUPPORT,),
    "content_manager": (PERM_PLATFORM_CONTENT,),
}
