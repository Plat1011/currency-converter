import os
from typing import List


def _get_env_list(name: str, default: List[str]) -> List[str]:
    raw_value = os.getenv(name)
    if not raw_value:
        return default
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def _get_env_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if not raw_value:
        return default
    try:
        return int(raw_value)
    except ValueError:
        return default


def _get_env_float(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if not raw_value:
        return default
    try:
        return float(raw_value)
    except ValueError:
        return default


CORS_ORIGINS: list[str] = _get_env_list(
    "CORS_ORIGINS",
    [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
)

FRANKFURTER_BASE_URL: str = os.getenv(
    "FRANKFURTER_BASE_URL",
    "https://api.frankfurter.app",
)
FRANKFURTER_TIMEOUT_SECONDS: float = _get_env_float(
    "FRANKFURTER_TIMEOUT_SECONDS",
    5.0,
)
FRANKFURTER_MAX_RETRIES: int = _get_env_int(
    "FRANKFURTER_MAX_RETRIES",
    2,
)
