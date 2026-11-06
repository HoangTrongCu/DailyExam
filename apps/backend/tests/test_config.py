"""Tests for config module."""

from app.config import Settings, get_settings


def test_defaults() -> None:
    s = Settings()
    assert s.app_name == "DailyExam API"
    assert s.environment == "development"
    assert s.gate_open_hour == 8
    assert s.gate_close_hour == 9


def test_get_settings_returns_settings_instance() -> None:
    s = get_settings()
    assert isinstance(s, Settings)
