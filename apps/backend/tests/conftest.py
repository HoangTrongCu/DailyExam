"""Shared fixtures."""

import pytest


@pytest.fixture(scope="session", autouse=True)
def _load_templates_once():
    from app.template_engine import load_all_templates, list_templates
    if not list_templates():
        load_all_templates()
    yield


@pytest.fixture
def db(tmp_path, monkeypatch):
    """Per-test isolated SQLite."""
    monkeypatch.setenv("DAILYEXAM_DATABASE_URL", f"sqlite:///{tmp_path / 't.db'}")
    monkeypatch.setenv("DAILYEXAM_LLM_MOCK_MODE", "true")
    import app.db as db_mod
    db_mod.reset_engine()
    from app.db import get_session_factory, init_db
    init_db()
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    monkeypatch.setenv("DAILYEXAM_DATABASE_URL", f"sqlite:///{tmp_path / 'api.db'}")
    monkeypatch.setenv("DAILYEXAM_LLM_MOCK_MODE", "true")
    monkeypatch.setenv("DAILYEXAM_EMAIL_PROVIDER", "mock")
    import app.db as db_mod
    db_mod.reset_engine()
    from app.main import create_app
    from app.services.email_service import reset_backend
    reset_backend()
    app = create_app()
    with TestClient(app) as c:
        yield c
