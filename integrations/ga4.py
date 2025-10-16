"""Mocked Google Analytics 4 client."""
from __future__ import annotations

import hashlib
from datetime import date, timedelta
from typing import Dict, List


class GA4Client:
    def __init__(self, property_id: str) -> None:
        self.property_id = property_id

    def fetch_traffic_metrics(self, start: date, end: date) -> List[Dict[str, int]]:
        days = (end - start).days + 1
        metrics: List[Dict[str, int]] = []
        for i in range(days):
            day = start + timedelta(days=i)
            digest = int(hashlib.sha256(f"{self.property_id}-{day.isoformat()}".encode("utf-8")).hexdigest(), 16)
            new_users = digest % 300 + 50
            returning_users = digest % 200
            metrics.append(
                {
                    "date": day.isoformat(),
                    "new_users": new_users,
                    "returning_users": returning_users,
                }
            )
        return metrics


__all__ = ["GA4Client"]
