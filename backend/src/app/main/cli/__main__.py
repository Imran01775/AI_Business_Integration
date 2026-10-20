"""CLI entrypoint: python -m app.main.cli seed"""

from __future__ import annotations

import argparse
import asyncio
import sys

from app.core.config import AppConfig
from app.core.db.engine import create_engine
from app.core.db.session import create_session_factory
from app.core.ids import Uuid7Generator
from app.main.container import build_container
from app.main.seed.defaults import seed_default_templates
from app.modules.settings.application.bootstrap import build_settings_registry
from app.modules.settings.infrastructure.definition_sync import SettingDefinitionSync
from app.modules.settings.infrastructure.sql_templates import SqlTemplateStore


async def _run_seed(config: AppConfig) -> int:
    registry = build_settings_registry()
    engine = create_engine(config)
    session_factory = create_session_factory(engine)
    ids = Uuid7Generator()
    try:
        sync = SettingDefinitionSync(session_factory, ids)
        defs = await sync.sync_registry(registry)
        templates = await seed_default_templates(SqlTemplateStore(session_factory, ids))
        print(f"Seed complete: {defs} definitions, {templates} templates.")
        return 0
    finally:
        await engine.dispose()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="app.main.cli")
    parser.add_argument("command", choices=["seed", "seed-super-admin"])
    parser.add_argument("--email", default="admin@localhost")
    parser.add_argument("--password", default="ChangeMeNow123!")
    parser.add_argument("--name", default="Platform Admin")
    args = parser.parse_args(argv)
    config = AppConfig()
    if args.command == "seed":
        return asyncio.run(_run_seed(config))
    if args.command == "seed-super-admin":
        container = build_container(config)

        async def _seed_admin() -> int:
            user_id = await container.identity.seed_super_admin(
                args.email,
                args.password,
                args.name,
            )
            print(f"Super admin ready: {args.email} ({user_id})")
            await container.engine.dispose()
            return 0

        return asyncio.run(_seed_admin())
    return 1


if __name__ == "__main__":
    sys.exit(main())
