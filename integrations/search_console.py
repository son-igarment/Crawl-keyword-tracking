"""Mocked Google Search Console client used for local testing."""
from __future__ import annotations

import hashlib
import math
from datetime import date, datetime, timedelta
from typing import Dict, List


class SearchConsoleClient:
    """Utility class that simulates Search Console responses."""

    def __init__(self, site_url: str, keyword_dataset: Dict[str, Dict[str, float]] | None = None) -> None:
        self.site_url = site_url
        self.keyword_dataset = keyword_dataset or {}

    def fetch_keyword_metrics(self, keyword: str) -> Dict[str, float | str]:
        payload = self.keyword_dataset.get(keyword)
        if payload is None:
            digest = int(hashlib.sha256(keyword.encode("utf-8")).hexdigest(), 16)
            position = round(1 + (digest % 100) / 10, 2)
            impressions = 100 + digest % 500
            clicks = int(impressions * (1 / (1 + math.exp((position - 5) / 2))))
            payload = {
                "keyword": keyword,
                "url": f"{self.site_url}/search/{keyword.replace(' ', '-')}",
                "position": position,
                "impressions": impressions,
                "clicks": clicks,
            }
        payload = dict(payload)
        payload.setdefault("keyword", keyword)
        payload.setdefault("url", f"{self.site_url}/search/{keyword.replace(' ', '-')}")
        payload.setdefault("position", 10.0)
        payload.setdefault("impressions", 0)
        payload.setdefault("clicks", 0)
        payload["fetched_at"] = datetime.utcnow().isoformat(timespec="seconds")
        return payload

    def fetch_query_metrics(self, start: date, end: date) -> List[Dict[str, int | float | str]]:
        days = (end - start).days + 1
        results: List[Dict[str, int | float | str]] = []
        for i in range(days):
            day = start + timedelta(days=i)
            base = int(hashlib.sha256(f"{self.site_url}-{day.isoformat()}".encode("utf-8")).hexdigest(), 16)
            clicks = base % 500 + 100
            impressions = clicks * 5
            avg_position = round(1 + (base % 90) / 10, 2)
            results.append(
                {
                    "date": day.isoformat(),
                    "clicks": clicks,
                    "impressions": impressions,
                    "average_position": avg_position,
                }
            )
        return results


__all__ = ["SearchConsoleClient"]
