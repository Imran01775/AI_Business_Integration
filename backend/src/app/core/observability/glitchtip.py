"""GlitchTip / Sentry SDK init."""

from __future__ import annotations

import sentry_sdk

from app.core.config import AppConfig


def init_glitchtip(config: AppConfig) -> None:
    if not config.glitchtip_dsn:
        return
    sentry_sdk.init(
        dsn=config.glitchtip_dsn,
        environment=config.app_env.value,
        traces_sample_rate=0.1,
    )
