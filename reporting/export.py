"""Export utilities to write data to JSON files for Looker Studio.

Exports keyword rankings and report summaries to newline-delimited JSON
or array JSON, configurable by function.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Iterable, Optional

from storage.database import Database, KeywordRanking, TrafficReport


logger = logging.getLogger(__name__)


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def export_keyword_rankings(
    db: Database,
    out_path: str | Path,
    keyword: Optional[str] = None,
    newline_delimited: bool = False,
) -> Path:
    path = Path(out_path)
    _ensure_parent(path)
    rows = db.fetch_keyword_rankings(keyword)
    try:
        if newline_delimited:
            with path.open("w", encoding="utf-8") as f:
                for row in rows:
                    f.write(json.dumps(row.__dict__, ensure_ascii=False) + "\n")
        else:
            payload = [row.__dict__ for row in rows]
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("Exported %s keyword ranking rows to %s", len(rows), path)
    except Exception:
        logger.exception("Failed to export keyword rankings to %s", path)
        raise
    return path


def export_reports(
    db: Database,
    out_path: str | Path,
    newline_delimited: bool = False,
) -> Path:
    path = Path(out_path)
    _ensure_parent(path)
    rows = db.fetch_reports()
    try:
        if newline_delimited:
            with path.open("w", encoding="utf-8") as f:
                for row in rows:
                    f.write(json.dumps(row.__dict__, ensure_ascii=False) + "\n")
        else:
            payload = [row.__dict__ for row in rows]
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("Exported %s reports to %s", len(rows), path)
    except Exception:
        logger.exception("Failed to export reports to %s", path)
        raise
    return path


__all__ = ["export_keyword_rankings", "export_reports"]

