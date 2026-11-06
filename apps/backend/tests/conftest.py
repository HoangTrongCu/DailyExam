"""Shared pytest fixtures."""

import pytest


@pytest.fixture(scope="session", autouse=True)
def _load_templates_once_for_session():
    """Templates register at module import; ensure the loader has run."""
    from app.template_engine import list_templates, load_all_templates
    if not list_templates():
        import app.templates.loader as loader
        loader._loaded = False
        load_all_templates()
    yield
