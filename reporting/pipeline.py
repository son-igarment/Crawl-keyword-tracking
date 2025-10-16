"""Reporting pipeline aggregating traffic and query metrics."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from statistics import mean
from typing import List

from integrations.ga4 import GA4Client
from integrations.search_console import SearchConsoleClient
from storage.database import Database


@dataclass
class ReportSummary:
    start_date: str
    end_date: str
    total_clicks: int
    total_impressions: int
    average_position: float
    new_users: int
    returning_users: int
    report_id: int | None = None


class ReportingPipeline:
    def __init__(self, ga_client: GA4Client, sc_client: SearchConsoleClient, database: Database) -> None:
        self.ga_client = ga_client
        self.sc_client = sc_client
        self.database = database

    def generate(self, start: date, end: date) -> ReportSummary:
        search_rows = self.sc_client.fetch_query_metrics(start, end)
        traffic_rows = self.ga_client.fetch_traffic_metrics(start, end)

        total_clicks = sum(row["clicks"] for row in search_rows)
        total_impressions = sum(row["impressions"] for row in search_rows)
        avg_position = mean(row["average_position"] for row in search_rows)
        new_users = sum(row["new_users"] for row in traffic_rows)
        returning_users = sum(row["returning_users"] for row in traffic_rows)

        summary_dict = {
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "total_clicks": int(total_clicks),
            "total_impressions": int(total_impressions),
            "average_position": float(round(avg_position, 2)),
            "new_users": int(new_users),
            "returning_users": int(returning_users),
        }
        report_id = self.database.insert_report(summary_dict)
        summary_dict["report_id"] = report_id
        return ReportSummary(**summary_dict)

    def list_reports(self) -> List[ReportSummary]:
        reports = self.database.fetch_reports()
        return [
            ReportSummary(
                report.start_date,
                report.end_date,
                report.total_clicks,
                report.total_impressions,
                report.average_position,
                report.new_users,
                report.returning_users,
                report.id,
            )
            for report in reports
        ]


__all__ = ["ReportingPipeline", "ReportSummary"]
