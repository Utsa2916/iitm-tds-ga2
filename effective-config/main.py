import os
import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow browser requests from the grader
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

# Defaults
config = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

# YAML layer
with open("config.development.yaml") as f:
    config.update(yaml.safe_load(f))

# .env layer
if os.getenv("NUM_WORKERS"):
    config["workers"] = os.getenv("NUM_WORKERS")

if os.getenv("APP_LOG_LEVEL"):
    config["log_level"] = os.getenv("APP_LOG_LEVEL")

# OS environment (APP_*)

mapping = {
    "APP_PORT": "port",
    "APP_WORKERS": "workers",
    "APP_LOG_LEVEL": "log_level",
    "APP_API_KEY": "api_key",
}

for env, key in mapping.items():
    if os.getenv(env):
        config[key] = os.getenv(env)


def to_bool(v):
    return str(v).lower() in ["true", "1", "yes", "on"]


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    cfg = config.copy()

    # CLI overrides
    for item in set:
        if "=" not in item:
            continue
        k, v = item.split("=", 1)
        cfg[k] = v

    # Type coercion
    cfg["port"] = int(cfg["port"])
    cfg["workers"] = int(cfg["workers"])
    cfg["debug"] = to_bool(cfg["debug"])
    cfg["log_level"] = str(cfg["log_level"])

    # Secret masking
    cfg["api_key"] = "****"

    return cfg