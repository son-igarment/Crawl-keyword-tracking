"""Automated keyword crawler with rate control and pause/resume capabilities."""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from threading import Condition
from typing import Deque, Iterable, List, Optional

from integrations.search_console import SearchConsoleClient
from storage.database import Database, KeywordRanking


class CrawlerController:
    """Controls crawl pacing and provides pause/resume mechanics."""

    def __init__(self, rate_limit_per_minute: int = 60) -> None:
        self.rate_limit_per_minute = max(1, rate_limit_per_minute)
        self._timestamps: Deque[float] = deque()
        self._condition = Condition()
        self._paused = False

    def set_rate_limit(self, rate_limit_per_minute: int) -> None:
        with self._condition:
            self.rate_limit_per_minute = max(1, rate_limit_per_minute)
            self._condition.notify_all()

    def pause(self) -> None:
        with self._condition:
            self._paused = True

    def resume(self) -> None:
        with self._condition:
            self._paused = False
            self._condition.notify_all()

    def wait_for_slot(self) -> None:
        with self._condition:
            while True:
                while self._paused:
                    self._condition.wait()
                now = time.time()
                # Remove timestamps older than a minute
                while self._timestamps and now - self._timestamps[0] >= 60:
                    self._timestamps.popleft()
                if len(self._timestamps) < self.rate_limit_per_minute:
                    self._timestamps.append(now)
                    return
                # Need to wait for the earliest timestamp to expire
                wait_time = 60 - (now - self._timestamps[0])
                if wait_time > 0:
                    self._condition.wait(timeout=wait_time)
                else:
                    self._timestamps.popleft()


@dataclass
class CrawlResult:
    keyword: str
    url: str
    position: float
    impressions: int
    clicks: int
    fetched_at: str


class KeywordCrawler:
    def __init__(
        self,
        client: SearchConsoleClient,
        database: Database,
        controller: Optional[CrawlerController] = None,
    ) -> None:
        self.client = client
        self.database = database
        self.controller = controller or CrawlerController()

    def crawl_keywords(self, keywords: Iterable[str]) -> List[CrawlResult]:
        results: List[CrawlResult] = []
        for keyword in keywords:
            self.controller.wait_for_slot()
            metrics = self.client.fetch_keyword_metrics(keyword)
            ranking = KeywordRanking(**metrics)
            self.database.upsert_keyword_ranking(ranking)
            results.append(CrawlResult(**metrics))
        return results


__all__ = ["CrawlerController", "KeywordCrawler", "CrawlResult"]
