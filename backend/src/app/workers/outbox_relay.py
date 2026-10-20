"""ARQ / CLI entrypoint for outbox relay."""

from __future__ import annotations

import asyncio

from app.core.config import AppConfig
from app.main.container import build_container, shutdown_container


async def run_outbox_relay_once() -> int:
    config = AppConfig()
    container = build_container(config)
    try:
        return await container.outbox_relay.run_once()
    finally:
        await shutdown_container(container)


def main() -> None:
    published = asyncio.run(run_outbox_relay_once())
    print(f"published={published}")


if __name__ == "__main__":
    main()
