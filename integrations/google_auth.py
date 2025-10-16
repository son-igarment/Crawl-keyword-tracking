"""Trình trợ giúp xác thực Google đơn giản cho phát triển cục bộ."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class GoogleCredentials:
    service_account_file: Optional[Path]

    def to_dict(self) -> dict:
        if self.service_account_file and self.service_account_file.exists():
            return {"service_account_file": str(self.service_account_file)}
        return {"service_account_file": None}


def load_credentials(path: str | None = None) -> GoogleCredentials:
    if path is None:
        return GoogleCredentials(service_account_file=None)
    file_path = Path(path)
    return GoogleCredentials(service_account_file=file_path if file_path.exists() else None)


__all__ = ["GoogleCredentials", "load_credentials"]
