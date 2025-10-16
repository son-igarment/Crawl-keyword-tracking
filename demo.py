"""Tập lệnh minh họa cho bộ công cụ Crawl Keyword Tracking."""
from __future__ import annotations

from datetime import date, datetime, timedelta

from config.settings import Settings
from crawler.bot import CrawlerController, KeywordCrawler
from reporting.pipeline import ReportingPipeline
from scheduler.content_scheduler import ContentScheduler
from storage.database import Database
from integrations.search_console import SearchConsoleClient
from integrations.ga4 import GA4Client


def run_demo() -> None:
    """Thực thi luồng crawler, lập lịch và báo cáo với đầu ra in ra màn hình."""
    settings = Settings.load()
    database = Database()

    # --- Bản demo Crawler -------------------------------------------------------
    search_console = SearchConsoleClient(settings.search_console["site_url"])
    controller = CrawlerController(rate_limit_per_minute=settings.crawler["rate_limit_per_minute"])
    crawler = KeywordCrawler(search_console, database, controller)

    keywords = ["seo tips", "keyword research", "technical seo"]
    print("\n== Crawling keyword rankings ==")
    results = crawler.crawl_keywords(keywords)
    for result in results:
        print(
            f"{result.keyword:18} | position {result.position:5.2f} | "
            f"impressions {result.impressions:4d} | clicks {result.clicks:4d}"
        )

    print("\nStored rankings (latest first):")
    for ranking in database.fetch_keyword_rankings():
        print(
            f"{ranking.fetched_at} - {ranking.keyword} -> {ranking.position} ({ranking.clicks}/{ranking.impressions})"
        )

    # --- Bản demo Bộ lập lịch ----------------------------------------------------
    scheduler = ContentScheduler(database)
    now = datetime.utcnow()
    print("\n== Scheduling content ==")
    scheduler.schedule_post("Cluster audit", "Alice", now - timedelta(hours=2))
    scheduler.schedule_post("Link building tactics", "Bob", now + timedelta(hours=4))

    due_posts = scheduler.run_due(now)
    print("Due posts:")
    for post in due_posts:
        print(f"- {post.title} by {post.author} (status -> Posted)")

    pending = scheduler.list_posts("Scheduled")
    print("Pending posts:")
    for post in pending:
        print(f"- {post.title} scheduled at {post.publish_at}")

    # --- Bản demo Báo cáo ----------------------------------------------------
    ga_client = GA4Client(settings.ga4["property_id"])
    reporting = ReportingPipeline(ga_client, search_console, database)
    start = date.today() - timedelta(days=6)
    end = date.today()
    print("\n== Generating traffic report ==")
    report = reporting.generate(start, end)
    print(
        "Report: {start_date} to {end_date}\n"
        "Clicks: {total_clicks}\n"
        "Impressions: {total_impressions}\n"
        "Avg. position: {average_position}\n"
        "Users (new/returning): {new_users}/{returning_users}"
        .format(**report.__dict__)
    )

    print("\nSaved reports:")
    for saved in reporting.list_reports():
        print(
            f"#{saved.report_id} {saved.start_date} -> {saved.end_date}: "
            f"{saved.total_clicks} clicks, {saved.new_users} new users"
        )


if __name__ == "__main__":
    run_demo()
