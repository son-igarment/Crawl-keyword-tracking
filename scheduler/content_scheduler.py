"""Tiện ích lập lịch nội dung để theo dõi quy trình xuất bản."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from storage.database import Database


@dataclass
class ScheduledPost:
    id: int
    title: str
    author: str
    publish_at: str
    status: str


class ContentScheduler:
    """Quản lý vòng đời nội dung từ lập kế hoạch đến xuất bản."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def schedule_post(self, title: str, author: str, publish_at: datetime) -> ScheduledPost:
        post_id = self.database.add_content(
            title=title,
            author=author,
            publish_at=publish_at.isoformat(timespec="seconds"),
            status="Scheduled",
        )
        return ScheduledPost(post_id, title, author, publish_at.isoformat(timespec="seconds"), "Scheduled")

    def list_posts(self, status: Optional[str] = None) -> List[ScheduledPost]:
        posts = self.database.fetch_content(status)
        return [ScheduledPost(**post.__dict__) for post in posts]

    def due_posts(self, now: Optional[datetime] = None) -> List[ScheduledPost]:
        now = now or datetime.utcnow()
        due = self.database.fetch_due_content(now.isoformat(timespec="seconds"))
        return [ScheduledPost(**post.__dict__) for post in due]

    def mark_posted(self, post_id: int) -> None:
        self.database.update_content_status(post_id, "Posted")

    def run_due(self, now: Optional[datetime] = None) -> List[ScheduledPost]:
        due = self.due_posts(now)
        for post in due:
            self.mark_posted(post.id)
        return due


__all__ = ["ContentScheduler", "ScheduledPost"]
