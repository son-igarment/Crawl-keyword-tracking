"""Job scheduler built on APScheduler's BackgroundScheduler.

Provides a simple interface to schedule crawling jobs and pause/resume
them dynamically at runtime.
"""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Callable, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


logger = logging.getLogger(__name__)


class JobScheduler:
    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler()
        self._job_id: Optional[str] = None

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self, wait: bool = False) -> None:
        try:
            self.scheduler.shutdown(wait=wait)
        except Exception:
            logger.exception("Error shutting down scheduler")

    def schedule_crawler(
        self,
        func: Callable[[], None],
        every_seconds: int = 60,
        job_id: str = "crawler_job",
    ) -> None:
        self._job_id = job_id
        trigger = IntervalTrigger(seconds=max(1, int(every_seconds)))
        # Replace existing to allow reconfiguration
        self.scheduler.add_job(func, trigger=trigger, id=job_id, replace_existing=True)
        logger.info("Scheduled crawler job every %ss (id=%s)", every_seconds, job_id)

    def pause(self) -> None:
        if self._job_id:
            try:
                self.scheduler.pause_job(self._job_id)
                logger.info("Paused job %s", self._job_id)
            except Exception:
                logger.exception("Failed to pause job %s", self._job_id)

    def resume(self) -> None:
        if self._job_id:
            try:
                self.scheduler.resume_job(self._job_id)
                logger.info("Resumed job %s", self._job_id)
            except Exception:
                logger.exception("Failed to resume job %s", self._job_id)


__all__ = ["JobScheduler"]

