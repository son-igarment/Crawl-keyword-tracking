# Deployment Guide

This guide explains how to deploy Crawl Keyword Tracking across common environments, from local development to managed cloud runtimes. Adapt the instructions to your infrastructure policies.

## 1. Prerequisites

- Python 3.10 or newer.
- Pip (recommended: `python -m pip install --upgrade pip`).
- Access to a persistent storage location for SQLite (local disk, mounted volume, or managed file share).
- Optional: Google service credentials if replacing the mock integrations with production APIs.

## 2. Dependency Management

Install runtime dependencies in a dedicated virtual environment to keep isolation between projects:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install requests beautifulsoup4 apscheduler
```

Add `pytest` and any linting tools (flake8, mypy, etc.) for CI validation.

## 3. Configuration Strategy

1. Copy `config/settings.py::DEFAULT_CONFIG` into `config/settings.json`.
2. Override fields as needed:
   - `search_console.site_url` — canonical domain for Search Console queries.
   - `ga4.property_id` — GA4 property identifier.
   - `crawler.rate_limit_per_minute` — tune to match API quotas.
3. For environment-specific overrides, set the `CKT_CONFIG` environment variable to the path of an alternative JSON file.
4. Store secrets (API keys, service account paths) using your secret manager instead of committing them to the repository.

## 4. Local Deployment

1. Create a writable SQLite location, e.g. `data/ckt.db`.
2. Instantiate the database with a filesystem path:

   ```python
   from storage.database import Database
   db = Database("data/ckt.db")
   ```

3. Run the demo workflow or your own orchestration script.
4. Inspect exported JSON files under `reporting/output/` and the SQLite database contents to validate the deployment.

## 5. Containerisation (Optional)

1. Use a slim Python base image (e.g., `python:3.11-slim`).
2. Copy the repository, install dependencies with `pip`, and set `PYTHONUNBUFFERED=1` for real-time logging.
3. Mount volumes for:
   - `/app/config` (configuration files)
   - `/app/data` (SQLite persistence)
   - `/app/reporting/output` (export artefacts)
4. Expose a process supervisor (e.g., `python demo.py`, `uvicorn` if you add APIs).
5. Handle graceful shutdown by propagating signals so that APScheduler can stop cleanly via `JobScheduler.shutdown(wait=True)`.

## 6. Production Integration

- **Scheduler**: Run the process under a supervisor (systemd, PM2, Kubernetes Deployment) that ensures a single instance of the APScheduler job. Configure health checks to detect stalled jobs.
- **Database**: For higher concurrency, replace SQLite with a server database by porting `storage.database.Database` to use SQLAlchemy or a similar abstraction. Keep the dataclass contract intact for compatibility.
- **Real APIs**: Swap mock clients with production implementations. Keep method signatures identical to avoid refactoring downstream code.
- **Exports**: Consider writing to object storage (AWS S3, GCS) by extending functions in `reporting/export.py`.

## 7. Observability

- Configure `logging` handlers to route messages to stdout/stderr for container logs or to files/syslog for VM deployments.
- Add structured logging (JSON) if you plan to ingest logs into ELK or Cloud Logging.
- Monitor:
  - Crawl throughput vs. rate limits (track the configured `rate_limit_per_minute`).
  - Scheduler job execution latency and failures.
  - Size and growth of the SQLite database or alternative storage backend.
  - Export job outcomes (success vs. exception counts).

## 8. Continuous Integration / Delivery

- Run `pytest` in CI to guard core workflows.
- Optionally add static analysis (flake8, black, mypy).
- Package build artefacts (Docker image or wheel) and promote through environments.
- Store configuration overlays per environment in a secure secrets store; inject them at deploy time.

## 9. Maintenance

- Rotate credentials and update configuration files regularly.
- Back up database files or switch to a managed database with automated backups.
- Review APScheduler job logs to ensure the crawler is executing on schedule.
- Refresh dependency versions quarterly, re-running regression tests after upgrades.
