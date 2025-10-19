# Crawl Keyword Tracking

Crawl Keyword Tracking is a modular reference implementation for monitoring SEO keyword performance, managing editorial schedules, and consolidating traffic analytics. The code base is intentionally self-contained and ships with lightweight mocks for Google Search Console and GA4 so you can validate workflows without live credentials.

## Key Capabilities

- Keyword crawler with rate limiting, pause/resume controls, and persistent storage.
- Content scheduling service for newsroom-style editorial calendars.
- Reporting pipeline that merges Search Console style query metrics with GA4 traffic data.
- Export utilities that generate JSON or NDJSON files ready for Looker Studio and similar BI tools.
- Demo script stitching every subsystem together and pytest coverage for core scenarios.

## Architecture Overview

The project is organised as independent Python packages that collaborate through clear interfaces:

- `config` loads project settings at runtime from `config/settings.json` or environment overrides.
- `crawler` contains the rate-limited `KeywordCrawler`, HTTP fetch helpers, and orchestration logic.
- `integrations` exposes mock clients for Google services and credentials helpers.
- `scheduler` provides editorial workflow automation (content queue + APScheduler jobs).
- `storage` wraps SQLite for keyword rankings, content schedule, and aggregated reports.
- `reporting` assembles analytics and exports structured data for downstream tools.

Refer to `docs/API_REFERENCE.md` for module-level APIs and method signatures.

## Quick Start

1. Ensure Python 3.10+ is available. (The project uses the standard library plus a few pip packages.)
2. Install dependencies:

   ```bash
   pip install requests beautifulsoup4 apscheduler pytest
   ```

3. Run tests to confirm the environment:

   ```bash
   pytest
   ```

4. Execute the end-to-end demo:

   ```bash
   python demo.py
   ```

   The script crawls sample keywords, schedules content, generates traffic reports, and exports JSON artefacts in `reporting/output/`.

## Configuration

- Default settings live in `config/settings.py`.
- Provide a custom configuration file at `config/settings.json` or point the `CKT_CONFIG` environment variable at an alternate JSON file.
- Supply `search_console.site_url`, `ga4.property_id`, and optional `crawler.rate_limit_per_minute` overrides as needed.

## Project Layout

```
config/           # Settings definitions and loading helpers
crawler/          # Keyword crawling logic and HTTP fetch utilities
integrations/     # Mock Search Console, GA4, and Google auth helpers
reporting/        # Analytics pipeline and JSON export tools
scheduler/        # Editorial calendar + APScheduler job wrapper
storage/          # SQLite persistence layer and domain models
tests/            # Pytest suites covering crawler, scheduler, and reporting flows
demo.py           # Orchestrated walkthrough of the full workflow
```

## Operational Notes

- Logging is configured in `demo.py`; adjust handlers as needed for production deployments.
- The SQLite database defaults to in-memory storage. Pass a filesystem path to `storage.Database` in your application to persist data across runs.
- APScheduler runs in-process via `scheduler.job_scheduler.JobScheduler`. In production, ensure the process stays alive and set an appropriate executor for concurrency needs.
- Exports write UTF-8 encoded files to `reporting/output/`. Change destinations or formats by extending `reporting/export.py`.

## Testing

- `pytest` validates keyword persistence, content scheduling transitions, and reporting summaries.
- Extend `tests/` with integration tests when wiring real Search Console or GA4 APIs.

## Further Reading

- API details, request/response schemas, and integration patterns: `docs/API_REFERENCE.md`.
- Deployment considerations for local, containerised, and cloud environments: `docs/DEPLOYMENT_GUIDE.md`.

Both documents are maintained alongside this README to provide comprehensive technical context.
