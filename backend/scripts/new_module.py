#!/usr/bin/env python3
"""Generate a new backend module skeleton (R-ARCH-01)."""

from __future__ import annotations

import argparse
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1] / "src" / "app" / "modules"

LAYERS = ("domain", "application", "infrastructure", "api")
DOMAIN_FILES = (
    "entities.py",
    "value_objects.py",
    "events.py",
    "repositories.py",
    "services.py",
    "errors.py",
)
APPLICATION_FILES = ("facade.py", "commands.py", "queries.py", "dto.py", "ports.py")
USE_CASES = ("__init__.py",)
INFRA_FILES = ("models.py", "repositories.py", "handlers.py", "jobs.py")
API_FILES = ("router.py", "schemas.py", "dependencies.py")
ROOT_FILES = ("settings.py", "templates.py", "permissions.py")


def write(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def scaffold(name: str) -> Path:
    module_dir = MODULE_ROOT / name
    if module_dir.exists():
        raise SystemExit(f"module already exists: {module_dir}")
    write(module_dir / "__init__.py")
    for layer in LAYERS:
        write(module_dir / layer / "__init__.py")
    for fname in DOMAIN_FILES:
        write(module_dir / "domain" / fname, '"""Domain layer."""\n\n')
    write(module_dir / "application" / "use_cases" / "__init__.py")
    for fname in APPLICATION_FILES:
        write(module_dir / "application" / fname, '"""Application layer."""\n\n')
    for fname in INFRA_FILES:
        write(module_dir / "infrastructure" / fname, '"""Infrastructure layer."""\n\n')
    write(module_dir / "infrastructure" / "adapters" / "__init__.py")
    for fname in API_FILES:
        write(module_dir / "api" / fname, '"""API layer."""\n\n')
    write(module_dir / "settings.py", '"""Settings registry declarations."""\n\n')
    write(module_dir / "templates.py", '"""Message template declarations."""\n\n')
    write(module_dir / "permissions.py", '"""Permission constants."""\n\n')
    return module_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a new backend module skeleton.")
    parser.add_argument("name", help="module directory name (snake_case)")
    args = parser.parse_args()
    path = scaffold(args.name)
    print(f"Created module at {path}")


if __name__ == "__main__":
    main()
