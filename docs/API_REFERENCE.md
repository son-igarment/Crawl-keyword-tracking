# API Reference

This document outlines the primary modules, classes, and functions that make up Crawl Keyword Tracking. All components are regular Python modules and can be imported directly in your own applications. Optional dependencies are noted where applicable.

## Conventions

- All code snippets assume `from __future__ import annotations` is enabled (as in the repo).
- Timestamps are ISO 8601 strings with second precision.
- Unless stated otherwise, arguments are required.

## `config.settings`

### `Settings`

```python
from config.settings import Settings
```

- `Settings.search_console: dict` — configuration for Search Console clients.
- `Settings.ga4: dict` — configuration for GA4 clients.
- `Settings.crawler: dict` — configuration for crawler behaviour.

#### `Settings.load(config_path: str | None = None) -> Settings`

Loads configuration data from JSON.

- **Parameters**
  - `config_path`: Optional path to a JSON file. Defaults to the value of the `CKT_CONFIG` environment variable or `config/settings.json`.
- **Returns** a `Settings` instance populated from the file or the defaults in `config.settings.DEFAULT_CONFIG`.

## `storage.database`

### Dataclasses

- `KeywordRanking` — represents a snapshot of ranking metrics for a keyword.
- `ScheduledContent` — editorial schedule entry persisted in SQLite.
- `TrafficReport` — aggregated analytics summary row.

### `Database`

```python
from storage.database import Database
db = Database("data/ckt.db")
```

Wraps SQLite persistence for rankings, scheduled content, and reports.

- **Constructor arguments**
  - `db_path: str | Path` (default `":memory:"`) — path to the SQLite database file.

#### Keyword ranking methods

- `upsert_keyword_ranking(ranking: KeywordRanking) -> None` — inserts or replaces a ranking snapshot keyed by `(keyword, fetched_at)`.
- `fetch_keyword_rankings(keyword: str | None = None) -> list[KeywordRanking]` — returns ranking records. When `keyword` is supplied, results are filtered accordingly.

#### Content scheduling methods

- `add_content(title: str, author: str, publish_at: str, status: str) -> int` — creates a new schedule entry and returns its auto-increment identifier.
- `update_content_status(content_id: int, status: str) -> None` — updates workflow status (e.g., `"Posted"`).
- `fetch_content(status: str | None = None) -> list[ScheduledContent]` — reads entries optionally filtered by status.
- `fetch_due_content(now_iso: str) -> list[ScheduledContent]` — returns content entries due for publication at or before `now_iso`.

#### Report methods

- `insert_report(report: dict[str, object]) -> int` — builds a new aggregated report row and returns its identifier.
- `fetch_reports() -> list[TrafficReport]` — returns all saved reports ordered by newest `end_date`.

Close connections explicitly via `Database.close()` when you manage lifecycle manually.

## `integrations.search_console`

### `SearchConsoleClient`

Mockable Search Console API client.

- **Constructor arguments**
  - `site_url: str` — base URL used when synthesising keyword landing pages.
  - `keyword_dataset: dict[str, dict[str, float]] | None` — optional pre-baked data used during tests.

#### `fetch_keyword_metrics(keyword: str) -> dict[str, float | str]`

Generates deterministic ranking metrics for a keyword, returning keys: `keyword`, `url`, `position`, `impressions`, `clicks`, `fetched_at`.

#### `fetch_query_metrics(start: date, end: date) -> list[dict[str, int | float | str]]`

Returns daily aggregates with fields `date`, `clicks`, `impressions`, `average_position`.

## `integrations.ga4`

### `GA4Client`

Mock GA4 property wrapper.

- **Constructor arguments**
  - `property_id: str` — seed for deterministic analytics values.

#### `fetch_traffic_metrics(start: date, end: date) -> list[dict[str, int]]`

Returns new and returning user counts per day between `start` and `end`, inclusive.

## `integrations.google_auth`

### `GoogleCredentials`

Dataclass storing optional `service_account_file: Path | None`. Use `GoogleCredentials.to_dict()` when wiring true Google libraries.

### `load_credentials(path: str | None = None) -> GoogleCredentials`

Loads a credentials object, verifying the path exists when provided.

## `crawler.bot`

### `CrawlerController`

Rate limiter and pause/resume guard for crawler jobs.

- **Constructor arguments**
  - `rate_limit_per_minute: int = 60` — maximum keyword fetches per rolling minute. Values less than one are normalised to one.

#### Methods

- `set_rate_limit(rate_limit_per_minute: int) -> None` — updates the cap at runtime.
- `pause() -> None` and `resume() -> None` — toggles the paused state.
- `wait_for_slot() -> None` — blocks until a request slot is available, observing pause state.

### `KeywordCrawler`

Coordinates the Search Console client with persistence.

- **Constructor arguments**
  - `client: SearchConsoleClient`
  - `database: Database`
  - `controller: CrawlerController | None` — optional custom controller.

#### `crawl_keywords(keywords: Iterable[str]) -> list[CrawlResult]`

For each keyword, enforces rate limiting, fetches metrics, upserts into the database, and returns collected `CrawlResult` dataclasses. Exceptions are logged (via `logging`) and skipped without crashing the run.

### `CrawlResult`

Dataclass mirroring the payload of `fetch_keyword_metrics`, returned by `crawl_keywords`.

## `crawler.fetcher`

### `WebFetcher`

Robust HTTP downloader that uses `requests` and `BeautifulSoup` with retry and exponential backoff.

- **Constructor arguments**
  - `timeout: int = 10`
  - `max_retries: int = 3`
  - `backoff_factor: float = 0.5`
  - `headers: dict[str, str] | None = None`

#### `get(url: str) -> FetchResult`

Performs an HTTP GET. When parsing succeeds, `FetchResult.parsed_title` contains the `<title>` text. Network errors trigger retry attempts until `max_retries` is exceeded, at which point the exception is propagated to the caller.

### `FetchResult`

Dataclass returning `url`, `status_code`, `text`, and optional `parsed_title`.

## `scheduler.content_scheduler`

### `ContentScheduler`

High-level interface for the editorial queue.

- **Constructor arguments**
  - `database: Database`

#### Methods

- `schedule_post(title: str, author: str, publish_at: datetime) -> ScheduledPost`
- `list_posts(status: str | None = None) -> list[ScheduledPost]`
- `due_posts(now: datetime | None = None) -> list[ScheduledPost]`
- `mark_posted(post_id: int) -> None`
- `run_due(now: datetime | None = None) -> list[ScheduledPost]` — marks all due posts as `"Posted"` and returns them.

### `ScheduledPost`

Dataclass matching the schema of scheduled items.

## `scheduler.job_scheduler`

### `JobScheduler`

Thin wrapper around `apscheduler.schedulers.background.BackgroundScheduler` for crawl jobs.

- `start() -> None` — boots the scheduler if not already running.
- `shutdown(wait: bool = False) -> None` — gracefully stops the scheduler.
- `schedule_crawler(func: Callable[[], None], every_seconds: int = 60, job_id: str = "crawler_job") -> None` — schedules a callable at fixed intervals. The job replaces existing jobs with the same id.
- `pause() -> None` and `resume() -> None` — control the scheduled crawler job identified by `job_id`.

## `reporting.pipeline`

### `ReportingPipeline`

Aggregates Search Console and GA4 style metrics, then persists them.

- **Constructor arguments**
  - `ga_client: GA4Client`
  - `sc_client: SearchConsoleClient`
  - `database: Database`

#### `generate(start: date, end: date) -> ReportSummary`

Collects query metrics and traffic metrics between `start` and `end`. Persists the aggregated summary using `Database.insert_report` and returns a `ReportSummary`.

#### `list_reports() -> list[ReportSummary]`

Returns existing reports ordered by newest `end_date`.

### `ReportSummary`

Dataclass bundling aggregated analytics plus the persisted `report_id`.

## `reporting.export`

### `export_keyword_rankings`

```python
from reporting.export import export_keyword_rankings
path = export_keyword_rankings(db, "reporting/output/keyword_rankings.json", newline_delimited=False)
```

- **Parameters**
  - `db: Database`
  - `out_path: str | Path`
  - `keyword: str | None` — optional filter.
  - `newline_delimited: bool = False` — set to `True` for NDJSON output.
- **Returns** the `Path` written to disk.

### `export_reports`

Same signature as `export_keyword_rankings` without the `keyword` argument. Writes aggregated report rows.

Both functions create parent directories automatically and log export outcomes.

## `demo.run_demo`

`demo.py` contains a `run_demo()` function illustrating the full workflow. Import the function to integrate the demo pipeline into other scripts.

```python
from demo import run_demo

if __name__ == "__main__":
    run_demo()
```

## Practical Integration Tips

- Compose mocks (e.g., `SearchConsoleClient`) with real implementations by matching method signatures defined above.
- Wrap long-running crawls in try/except blocks and rely on `CrawlerController.wait_for_slot()` to respect rate limits.
- When persisting to disk, supply a `Path` pointing at an existing writable directory to `Database`.
- To run multiple scheduled jobs, extend `JobScheduler` or instantiate additional APScheduler jobs with unique identifiers.
