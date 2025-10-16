# Crawl Keyword Tracking Toolkit

This project provides a self-contained toolkit for:

- Crawling keyword ranking and SEO metrics with configurable rate limiting and pause/resume controls.
- Scheduling and tracking content publication plans.
- Aggregating Search Console and GA4 style metrics into traffic reports.
- Demonstrating the full workflow via an executable demo script.

All integrations are implemented with lightweight, deterministic mocks so the system can be tested locally without external credentials. A SQLite-backed persistence layer keeps track of rankings, schedules, and generated reports.

## Getting Started

1. **Install dependencies** (only the Python standard library is used).
2. **Run the automated tests:**

   ```bash
   pytest
   ```

3. **Run the demo workflow** to observe the crawler, scheduler, and reporting outputs together:

   ```bash
   python demo.py
   ```

4. **Integrate in your own project** by importing the relevant packages:

   - `crawler.KeywordCrawler` for keyword crawling with `CrawlerController` to adjust speed or pause/resume.
   - `scheduler.ContentScheduler` for registering and executing planned posts.
   - `reporting.ReportingPipeline` for generating aggregated reports.

Configuration defaults are stored in `config/settings.py`. Provide a JSON override at `config/settings.json` or set the `CKT_CONFIG` environment variable to point to a custom file.

## Repository Structure

```
config/           # Trình tải cấu hình và giá trị mặc định
crawler/          # Triển khai crawler từ khóa
scheduler/        # Dịch vụ lập lịch nội dung
reporting/        # Pipeline báo cáo lưu lượng
integrations/     # Tích hợp giả lập cho các API của Google
storage/          # Lớp lưu trữ SQLite
tests/            # Bộ kiểm thử tự động
```

## Running the Toolkit

The modules can be composed together for an end-to-end workflow:

1. Load settings and instantiate integrations.
2. Use the crawler to collect keyword metrics and store them.
3. Schedule upcoming content with the scheduler.
4. Generate reports using the reporting pipeline.

The automated test suite demonstrates this workflow.
