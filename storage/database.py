"""Lớp lưu trữ nhẹ dựa trên SQLite cho dữ liệu của crawler, bộ lập lịch và báo cáo."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Optional


@dataclass
class KeywordRanking:
    keyword: str
    url: str
    position: float
    impressions: int
    clicks: int
    fetched_at: str


@dataclass
class ScheduledContent:
    id: int
    title: str
    author: str
    publish_at: str
    status: str


@dataclass
class TrafficReport:
    id: int
    start_date: str
    end_date: str
    total_clicks: int
    total_impressions: int
    average_position: float
    new_users: int
    returning_users: int


class Database:
    """Simple SQLite wrapper for persisting application data."""

    def __init__(self, db_path: Path | str = ":memory:") -> None:
        if db_path == ":memory:":
            self.db_path = db_path
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._initialise()

    def close(self) -> None:
        self._conn.close()

    @contextmanager
    def cursor(self) -> Iterator[sqlite3.Cursor]:
        cur = self._conn.cursor()
        try:
            yield cur
            self._conn.commit()
        finally:
            cur.close()

    def _initialise(self) -> None:
        with self.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS keyword_rankings (
                    keyword TEXT NOT NULL,
                    url TEXT NOT NULL,
                    position REAL NOT NULL,
                    impressions INTEGER NOT NULL,
                    clicks INTEGER NOT NULL,
                    fetched_at TEXT NOT NULL,
                    PRIMARY KEY (keyword, fetched_at)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS content_schedule (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    publish_at TEXT NOT NULL,
                    status TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS traffic_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    total_clicks INTEGER NOT NULL,
                    total_impressions INTEGER NOT NULL,
                    average_position REAL NOT NULL,
                    new_users INTEGER NOT NULL,
                    returning_users INTEGER NOT NULL
                )
                """
            )

    # Các thao tác xếp hạng từ khóa -------------------------------------------------
    def upsert_keyword_ranking(self, ranking: KeywordRanking) -> None:
        with self.cursor() as cur:
            cur.execute(
                """
                INSERT OR REPLACE INTO keyword_rankings
                (keyword, url, position, impressions, clicks, fetched_at)
                VALUES (:keyword, :url, :position, :impressions, :clicks, :fetched_at)
                """,
                ranking.__dict__,
            )

    def fetch_keyword_rankings(self, keyword: Optional[str] = None) -> List[KeywordRanking]:
        with self.cursor() as cur:
            if keyword:
                cur.execute(
                    "SELECT * FROM keyword_rankings WHERE keyword = ? ORDER BY fetched_at DESC",
                    (keyword,),
                )
            else:
                cur.execute("SELECT * FROM keyword_rankings ORDER BY fetched_at DESC")
            rows = cur.fetchall()
        return [KeywordRanking(**dict(row)) for row in rows]

    # Các thao tác bộ lập lịch nội dung ----------------------------------------------
    def add_content(self, title: str, author: str, publish_at: str, status: str) -> int:
        with self.cursor() as cur:
            cur.execute(
                """
                INSERT INTO content_schedule (title, author, publish_at, status)
                VALUES (?, ?, ?, ?)
                """,
                (title, author, publish_at, status),
            )
            return int(cur.lastrowid)

    def update_content_status(self, content_id: int, status: str) -> None:
        with self.cursor() as cur:
            cur.execute(
                "UPDATE content_schedule SET status = ? WHERE id = ?",
                (status, content_id),
            )

    def fetch_content(self, status: Optional[str] = None) -> List[ScheduledContent]:
        with self.cursor() as cur:
            if status:
                cur.execute(
                    "SELECT * FROM content_schedule WHERE status = ? ORDER BY publish_at",
                    (status,),
                )
            else:
                cur.execute("SELECT * FROM content_schedule ORDER BY publish_at")
            rows = cur.fetchall()
        return [ScheduledContent(**dict(row)) for row in rows]

    def fetch_due_content(self, now_iso: str) -> List[ScheduledContent]:
        with self.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM content_schedule
                WHERE publish_at <= ? AND status != 'Posted'
                ORDER BY publish_at
                """,
                (now_iso,),
            )
            rows = cur.fetchall()
        return [ScheduledContent(**dict(row)) for row in rows]

    # Các thao tác báo cáo ------------------------------------------------------
    def insert_report(self, report: Dict[str, object]) -> int:
        with self.cursor() as cur:
            cur.execute(
                """
                INSERT INTO traffic_reports (
                    start_date,
                    end_date,
                    total_clicks,
                    total_impressions,
                    average_position,
                    new_users,
                    returning_users
                ) VALUES (:start_date, :end_date, :total_clicks, :total_impressions,
                          :average_position, :new_users, :returning_users)
                """,
                report,
            )
            return int(cur.lastrowid)

    def fetch_reports(self) -> List[TrafficReport]:
        with self.cursor() as cur:
            cur.execute("SELECT * FROM traffic_reports ORDER BY end_date DESC")
            rows = cur.fetchall()
        return [TrafficReport(**dict(row)) for row in rows]


__all__ = [
    "Database",
    "KeywordRanking",
    "ScheduledContent",
    "TrafficReport",
]
