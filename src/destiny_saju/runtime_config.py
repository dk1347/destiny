"""Small, validated deployment settings for the guarded internal API."""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse


_DEFAULT_ALLOWED_ORIGINS = ("http://localhost:5173", "http://127.0.0.1:5173")


@dataclass(frozen=True)
class ApiRuntimeConfig:
    """Public, non-secret settings that control browser access to the API."""

    allowed_origins: tuple[str, ...]


def api_runtime_config(environ: dict[str, str] | None = None) -> ApiRuntimeConfig:
    """Load comma-separated ``DESTINY_ALLOWED_ORIGINS`` without accepting wildcards."""

    values = (environ if environ is not None else os.environ).get("DESTINY_ALLOWED_ORIGINS")
    origins = _DEFAULT_ALLOWED_ORIGINS if values is None else tuple(item.strip() for item in values.split(",") if item.strip())
    if not origins:
        raise ValueError("DESTINY_ALLOWED_ORIGINS must contain at least one origin")
    for origin in origins:
        parsed = urlparse(origin)
        if (parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.path not in {"", "/"}
                or parsed.params or parsed.query or parsed.fragment or origin == "*"):
            raise ValueError("DESTINY_ALLOWED_ORIGINS must contain complete http(s) origins without paths")
    return ApiRuntimeConfig(tuple(dict.fromkeys(origin.rstrip("/") for origin in origins)))
