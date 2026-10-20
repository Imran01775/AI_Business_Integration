from __future__ import annotations

import pytest

from app.core.errors.exceptions import ValidationError
from app.modules.settings.application.templates import TemplateRenderer
from app.shared.context import SettingsResolveContext


@pytest.mark.asyncio
async def test_template_renders_variables() -> None:
    renderer = TemplateRenderer()
    renderer.register("greeting", "en", "Hello {{ name }}", ["name"])
    out = await renderer.render("greeting", SettingsResolveContext(), {"name": "Ada"})
    assert out == "Hello Ada"


@pytest.mark.asyncio
async def test_template_rejects_unknown_variables() -> None:
    renderer = TemplateRenderer()
    renderer.register("greeting", "en", "Hello {{ name }}", ["name"])
    with pytest.raises(ValidationError):
        await renderer.render("greeting", SettingsResolveContext(), {"name": "Ada", "extra": "x"})
