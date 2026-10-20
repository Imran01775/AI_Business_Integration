def test_workspace_imports_app_package() -> None:
    import app

    assert app.__doc__ is None or isinstance(app.__doc__, str)
