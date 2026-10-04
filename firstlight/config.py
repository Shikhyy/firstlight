import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()


def load_config():
    config_path = Path("config.yaml")
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}


config_data = load_config()

NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "default-topic")
NTFY_BASE_URL = os.environ.get("NTFY_BASE_URL", "https://ntfy.sh")
ACTION_TOKEN = os.environ.get("ACTION_TOKEN", "secret")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")
PUBLIC_URL = os.environ.get("PUBLIC_URL", "http://localhost:5000")

PROFILE = config_data.get("profile", {})
SCHEDULE = config_data.get("schedule", {})
SOURCES = config_data.get("sources", {})
AI_CONFIG = config_data.get("ai", {})
