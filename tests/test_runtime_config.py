import pytest

from destiny_saju.runtime_config import api_runtime_config


def test_api_runtime_config_has_safe_local_defaults() -> None:
    assert api_runtime_config({}).allowed_origins == ("http://localhost:5173", "http://127.0.0.1:5173")


def test_api_runtime_config_accepts_explicit_deployment_origins() -> None:
    config = api_runtime_config({"DESTINY_ALLOWED_ORIGINS": "https://app.example.com, https://preview.example.com"})
    assert config.allowed_origins == ("https://app.example.com", "https://preview.example.com")


@pytest.mark.parametrize("value", ("", "*", "app.example.com", "https://app.example.com/path"))
def test_api_runtime_config_rejects_unsafe_origins(value: str) -> None:
    with pytest.raises(ValueError, match="DESTINY_ALLOWED_ORIGINS"):
        api_runtime_config({"DESTINY_ALLOWED_ORIGINS": value})
