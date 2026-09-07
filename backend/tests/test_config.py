from app.core.config import Settings
import pytest


def test_session_cookie_defaults_to_secure_in_production() -> None:
    assert Settings(database_url="sqlite+pysqlite:///:memory:", app_env="production").session_cookie_secure is True
    assert Settings(database_url="sqlite+pysqlite:///:memory:", app_env="development").session_cookie_secure is False


def test_credentialed_cors_rejects_wildcard_and_empty_cookie_override_uses_default() -> None:
    with pytest.raises(ValueError, match="cannot include"):
        Settings(database_url="sqlite+pysqlite:///:memory:", cors_origins="*").cors_origin_list
    assert Settings(database_url="sqlite+pysqlite:///:memory:", app_env="production", cookie_secure="").session_cookie_secure is True
