"""HTTP fetching utilities using Requests + BeautifulSoup with logging.

This module is optional to the mock integrations and demonstrates
real-world resilient fetching with retries to avoid crashes on
transient network errors.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


@dataclass
class FetchResult:
    url: str
    status_code: int
    text: str
    parsed_title: Optional[str]


class WebFetcher:
    def __init__(
        self,
        timeout: int = 10,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.timeout = timeout
        self.max_retries = max(0, max_retries)
        self.backoff_factor = max(0.0, backoff_factor)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (compatible; KeywordBot/1.0; +https://example.com/bot)"
                )
            }
        )
        if headers:
            self.session.headers.update(headers)

    def get(self, url: str) -> FetchResult:
        attempt = 0
        while True:
            try:
                resp = self.session.get(url, timeout=self.timeout)
                text = resp.text
                title = None
                try:
                    soup = BeautifulSoup(text, "html.parser")
                    title_tag = soup.find("title")
                    title = title_tag.get_text(strip=True) if title_tag else None
                except Exception:  # parsing errors shouldn't crash the bot
                    logger.exception("Failed to parse HTML for %s", url)
                return FetchResult(url=url, status_code=resp.status_code, text=text, parsed_title=title)
            except requests.RequestException as exc:
                attempt += 1
                logger.warning("Network error on GET %s (attempt %s/%s): %s", url, attempt, self.max_retries, exc)
                if attempt > self.max_retries:
                    # Re-raise to let callers decide how to handle ultimate failure
                    logger.error("Exhausted retries for %s", url)
                    raise
                sleep_s = self.backoff_factor * (2 ** (attempt - 1))
                time.sleep(sleep_s)


__all__ = ["WebFetcher", "FetchResult"]

