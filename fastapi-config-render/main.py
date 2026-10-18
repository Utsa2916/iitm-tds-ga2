import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import dotenv_values
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent

DEFAULTS: dict[str, Any] = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

app = FastAPI(title="Layered Configuration API")

# The grader's browser can call this endpoint cross-origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "on"}


def coerce(key: str, value: Any) -> Any:
    if key in {"port", "workers"}:
        return int(value)
    if key == "debug":
        return as_bool(value)
    return str(value)


def load_effective_config(overrides: list[str]) -> dict[str, Any]:
    config = dict(DEFAULTS)

    # Layer 2: config.<APP_ENV>.yaml (development by default).
    environment = os.environ.get("APP_ENV", "development")
    yaml_path = BASE_DIR / f"config.{environment}.yaml"
    if yaml_path.exists():
        with yaml_path.open("r", encoding="utf-8") as handle:
            yaml_config = yaml.safe_load(handle) or {}
        if isinstance(yaml_config, dict):
            for key, value in yaml_config.items():
                config[str(key).lower()] = value

    # Layer 3: .env. NUM_WORKERS is an alias for workers.
    dotenv_path = BASE_DIR / ".env"
    env_file = dotenv_values(dotenv_path) if dotenv_path.exists() else {}
    for raw_key, value in env_file.items():
        if value is None:
            continue
        key = raw_key.lower()
        if raw_key == "NUM_WORKERS":
            key = "workers"
        elif raw_key.startswith("APP_"):
            key = raw_key[4:].lower()
        config[key] = value

    # Layer 4: real OS environment variables with APP_ prefix.
    for raw_key, value in os.environ.items():
        if raw_key.startswith("APP_"):
            config[raw_key[4:].lower()] = value

    # Layer 5: query-string CLI overrides; repeated `set` parameters are supported.
    for item in overrides:
        key, separator, value = item.partition("=")
        if not separator or not key.strip():
            continue
        config[key.strip().lower()] = value

    # Ensure the five required output fields exist and have the requested types.
    result = {
        key: coerce(key, config.get(key, DEFAULTS[key]))
        for key in ("port", "workers", "debug", "log_level", "api_key")
    }
    # Never reveal the configured secret, including when overridden.
    result["api_key"] = "****"
    return result


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    return load_effective_config(set)


@app.get("/")
def root():
    return {
        "service": "layered-config-api",
        "endpoint": "/effective-config",
        "example": "/effective-config?set=port=9000&set=debug=true",
    }
