import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"{name} 必须是 true 或 false")


def _get_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError as exc:
        raise RuntimeError(f"{name} 必须是整数") from exc
    if not minimum <= value <= maximum:
        raise RuntimeError(f"{name} 必须在 {minimum} 到 {maximum} 之间")
    return value


def _get_float(name: str, default: float, minimum: float, maximum: float) -> float:
    try:
        value = float(os.getenv(name, str(default)))
    except ValueError as exc:
        raise RuntimeError(f"{name} 必须是数字") from exc
    if not minimum <= value <= maximum:
        raise RuntimeError(f"{name} 必须在 {minimum} 到 {maximum} 之间")
    return value


@dataclass(frozen=True)
class Settings:
    database_url: str
    debug_mode: bool
    database_pool_size: int
    database_max_overflow: int
    redis_url: str
    redis_timeout_seconds: float
    cors_origins: tuple[str, ...]
    log_level: str

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        database_url = os.getenv("ASYNC_DATABASE_URL", "").strip()
        if not database_url:
            raise RuntimeError(
                "缺少 ASYNC_DATABASE_URL 环境变量，请参考 .env.example 配置"
            )

        origins = tuple(
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173",
            ).split(",")
            if origin.strip()
        )
        if not origins:
            raise RuntimeError("CORS_ORIGINS 至少需要配置一个来源")

        log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
        if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise RuntimeError("LOG_LEVEL 配置无效")

        return cls(
            database_url=database_url,
            debug_mode=_get_bool("DEBUG_MODE", False),
            database_pool_size=_get_int("DATABASE_POOL_SIZE", 10, 1, 100),
            database_max_overflow=_get_int(
                "DATABASE_MAX_OVERFLOW", 20, 0, 200
            ),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0").strip(),
            redis_timeout_seconds=_get_float(
                "REDIS_TIMEOUT_SECONDS", 1.0, 0.1, 30.0
            ),
            cors_origins=origins,
            log_level=log_level,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
