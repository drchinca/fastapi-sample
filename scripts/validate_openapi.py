#!/usr/bin/env python3
"""Validate generated OpenAPI output against Marketo import requirements."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import app  # noqa: E402
from openapi_config import validate_marketo_openapi  # noqa: E402


def main() -> int:
    schema = app.openapi()
    errors = validate_marketo_openapi(schema)

    if errors:
        print("OpenAPI validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("OpenAPI validation passed.")
    print(json.dumps(
        {
            "openapi": schema["openapi"],
            "servers": schema["servers"],
            "security": schema["security"],
            "securitySchemes": schema["components"]["securitySchemes"],
            "paths": list(schema["paths"].keys()),
        },
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
