def test_workspace_imports_ai_platform_package() -> None:
    import ai_platform

    assert "AI platform" in (ai_platform.__doc__ or "")
