import pytest

from config.settings import Settings


def test_settings_parses_typed_environment(monkeypatch):
    monkeypatch.setenv("ASYNC_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("DEBUG_MODE", "true")
    monkeypatch.setenv("DATABASE_POOL_SIZE", "5")
    monkeypatch.setenv("CORS_ORIGINS", "http://one.test, http://two.test")

    settings = Settings.from_env()

    assert settings.debug_mode is True
    assert settings.database_pool_size == 5
    assert settings.cors_origins == ("http://one.test", "http://two.test")


def test_settings_rejects_invalid_pool_size(monkeypatch):
    monkeypatch.setenv("ASYNC_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("DATABASE_POOL_SIZE", "0")

    with pytest.raises(RuntimeError, match="DATABASE_POOL_SIZE"):
        Settings.from_env()
