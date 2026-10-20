"""Refresh token rotation and reuse detection."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.auth.password_hasher import Argon2PasswordHasher
from app.core.auth.secure_token import generate_opaque_token
from app.core.db.session import session_scope
from app.core.ids import Uuid7Generator
from app.modules.identity.domain.errors import RefreshTokenReuseError
from app.modules.identity.infrastructure.repositories import SqlIdentityRepository


@pytest.mark.integration
async def test_refresh_rotation_and_reuse_revokes_family(
    pg_session_factory: async_sessionmaker,
) -> None:
    ids = Uuid7Generator()
    repo = SqlIdentityRepository(pg_session_factory, ids)
    hasher = Argon2PasswordHasher()
    raw_initial = generate_opaque_token()
    raw_rotated = generate_opaque_token()
    expires = datetime.now(UTC) + timedelta(days=7)

    async with session_scope(pg_session_factory) as session:
        user = await repo.create_user(
            email=f"rotate-{ids.uuid7().hex[:8]}@example.com",
            display_name="Rotate",
            password_hash=hasher.hash("Password123!"),
            locale="en",
            session=session,
        )
        user.email_verified_at = datetime.now(UTC)
        device = await repo.create_session(
            user_id=user.id,
            client_type="mobile",
            device_name=None,
            ip_address=None,
            user_agent=None,
            csrf_token_hash=None,
            session=session,
        )
        family_id = ids.uuid7()
        await repo.issue_refresh_token(
            session_id=device.id,
            user_id=user.id,
            family_id=family_id,
            raw_token=raw_initial,
            expires_at=expires,
            session=session,
        )

    await repo.rotate_refresh_token(raw_initial, raw_rotated, expires)
    with pytest.raises(RefreshTokenReuseError):
        await repo.rotate_refresh_token(raw_initial, generate_opaque_token(), expires)
