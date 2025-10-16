from __future__ import annotations

from datetime import date, datetime, timedelta

from config.settings import Settings
from crawler.bot import CrawlerController, KeywordCrawler
from integrations.ga4 import GA4Client
from integrations.search_console import SearchConsoleClient
from reporting.pipeline import ReportingPipeline
from scheduler.content_scheduler import ContentScheduler
from storage.database import Database


def test_keyword_crawler_persists_rankings() -> None:
    db = Database()
    settings = Settings.load()
    client = SearchConsoleClient(settings.search_console["site_url"])
    controller = CrawlerController(rate_limit_per_minute=120)
    crawler = KeywordCrawler(client=client, database=db, controller=controller)

    results = crawler.crawl_keywords(["seo tips", "content marketing"])

    assert len(results) == 2
    stored = db.fetch_keyword_rankings()
    assert {row.keyword for row in stored} == {"seo tips", "content marketing"}
    assert all(row.impressions >= row.clicks for row in stored)


def test_content_scheduler_marks_due_posts() -> None:
    db = Database()
    scheduler = ContentScheduler(db)

    now = datetime.utcnow()
    past_post = scheduler.schedule_post("Post 1", "Alice", now - timedelta(hours=1))
    future_post = scheduler.schedule_post("Post 2", "Bob", now + timedelta(hours=1))

    due = scheduler.run_due(now)
    assert [post.id for post in due] == [past_post.id]

    pending = scheduler.list_posts("Scheduled")
    assert [post.id for post in pending] == [future_post.id]


def test_reporting_pipeline_generates_summary() -> None:
    db = Database()
    settings = Settings.load()
    ga_client = GA4Client(settings.ga4["property_id"])
    sc_client = SearchConsoleClient(settings.search_console["site_url"])
    pipeline = ReportingPipeline(ga_client, sc_client, db)

    start = date.today() - timedelta(days=6)
    end = date.today()
    summary = pipeline.generate(start, end)

    assert summary.total_clicks > 0
    assert summary.total_impressions >= summary.total_clicks
    assert summary.new_users >= 0
    assert len(pipeline.list_reports()) == 1
