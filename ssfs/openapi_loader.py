import json
import os
from pathlib import Path
from typing import Any

OPENAPI_PATH = Path(__file__).resolve().parent / "openapi.json"


def load_openapi() -> dict[str, Any]:
    spec = json.loads(OPENAPI_PATH.read_text())
    if base_url := os.getenv("API_BASE_URL", "").strip():
        spec["servers"] = [{"url": base_url.rstrip("/")}]
    elif domain := os.getenv("REPLIT_DEV_DOMAIN", "").strip():
        spec["servers"] = [{"url": f"https://{domain}"}]
    return spec
