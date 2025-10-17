"""Tập lệnh minh hoạ cho bộ công cụ Crawl Keyword Tracking.

Bổ sung:
- Requests + BeautifulSoup để fetch HTML an toàn (crawler/fetcher.py)
- APScheduler để lặp định kỳ kèm pause/resume linh hoạt (scheduler/job_scheduler.py)
- try/except + logging để tránh crash khi lỗi mạng
- Xuất dữ liệu .json để team SEO import Looker Studio
"""
from __future__ import annotations

import logging
import time
from datetime import date, datetime, timedelta

from config.settings import Settings
from crawler.bot import CrawlerController, KeywordCrawler
from crawler.fetcher import WebFetcher
from reporting.pipeline import ReportingPipeline
from reporting.export import export_keyword_rankings, export_reports
from scheduler.content_scheduler import ContentScheduler
from scheduler.job_scheduler import JobScheduler
from storage.database import Database
from integrations.search_console import SearchConsoleClient
from integrations.ga4 import GA4Client


def run_demo() -> None:
    """Thực thi luồng crawler, lịch nội dung và báo cáo với đầu ra in ra màn hình."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    settings = Settings.load()
    database = Database()

    # --- Phần demo Crawler -------------------------------------------------------
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

    # Demo Requests + BeautifulSoup: lấy tiêu đề HTML của URL đầu tiên
    try:
        fetcher = WebFetcher(timeout=5, max_retries=2)
        sample_url = results[0].url
        fetched = fetcher.get(sample_url)
        print(f"Fetched {sample_url} -> status {fetched.status_code}, title='{fetched.parsed_title}'")
    except Exception:
        logging.exception("Fetcher demo failed")

    print("\nStored rankings (latest first):")
    for ranking in database.fetch_keyword_rankings():
        print(
            f"{ranking.fetched_at} - {ranking.keyword} -> {ranking.position} ({ranking.clicks}/{ranking.impressions})"
        )
    # Xuất JSON cho Looker Studio
    export_keyword_rankings(database, "reporting/output/keyword_rankings.json")

    # --- Phần demo Bố trí lịch ---------------------------------------------------
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

    # --- Phần demo Báo cáo -------------------------------------------------------
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
    export_reports(database, "reporting/output/reports.json")

    print("\nSaved reports:")
    for saved in reporting.list_reports():
        print(
            f"#{saved.report_id} {saved.start_date} -> {saved.end_date}: "
            f"{saved.total_clicks} clicks, {saved.new_users} new users"
        )

    # --- Demo APScheduler với pause/resume job crawler ---------------------------
    print("\n== APScheduler demo (crawl job every 1s; pause/resume) ==")
    job_scheduler = JobScheduler()

    def job_run_once() -> None:
        try:
            crawler.crawl_keywords(["ap scheduler", "beautiful soup"])
        except Exception:
            logging.exception("Scheduled crawl errored")

    job_scheduler.start()
    job_scheduler.schedule_crawler(job_run_once, every_seconds=1)
    time.sleep(2.5)  # cho job chạy đôi lần
    print("Pausing...")
    job_scheduler.pause()
    time.sleep(1.5)
    print("Resuming...")
    job_scheduler.resume()
    time.sleep(1.5)
    job_scheduler.shutdown(wait=False)


if __name__ == "__main__":
    run_demo()

