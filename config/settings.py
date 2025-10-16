"""Bộ nạp cấu hình cho bộ công cụ tự động hóa."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


DEFAULT_CONFIG = {
    "search_console": {
        "site_url": "https://example.com",
    },
    "ga4": {
        "property_id": "GA4-TEST",
    },
    "crawler": {
        "rate_limit_per_minute": 30,
    },
}


@dataclass
class Settings:
    search_console: Dict[str, Any]
    ga4: Dict[str, Any]
    crawler: Dict[str, Any]

    @classmethod
    def load(cls, config_path: str | None = None) -> "Settings":
        if config_path is None:
            config_path = os.environ.get("CKT_CONFIG", "config/settings.json")
        config_file = Path(config_path)
        if config_file.exists():
            data = json.loads(config_file.read_text())
        else:
            data = DEFAULT_CONFIG
        return cls(**data)


__all__ = ["Settings", "DEFAULT_CONFIG"]
