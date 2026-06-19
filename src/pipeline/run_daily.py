"""Daily pipeline: collect → analyze → upload to GCS.

Run via Windows Task Scheduler:
  python -m src.pipeline.run_daily
  python -m src.pipeline.run_daily --teams BRA,FRA,ARG  (subset for testing)
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from src.analyzers.sentiment import SentimentAnalyzer
from src.collectors.api_football import ApiFootballCollector
from src.collectors.football_data import FootballDataCollector
from src.collectors.historical import HistoricalCollector
from src.collectors.news import NewsCollector
from src.collectors.odds import OddsCollector
from src.config import get_settings
from src.storage.gcs import GCSStorage, make_gcs_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

_PROGRESS_FILE = Path("data/.upload_progress.json")
_LOG_FILE = Path("data/.pipeline_log.json")


def load_teams(teams_file: str) -> list[dict]:
    path = Path(teams_file)
    if not path.exists():
        logger.error("Teams file not found: %s", teams_file)
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def load_progress() -> set[str]:
    if not _PROGRESS_FILE.exists():
        return set()
    try:
        data = json.loads(_PROGRESS_FILE.read_text())
        run_date = data.get("date")
        if run_date != datetime.utcnow().date().isoformat():
            return set()
        return set(data.get("completed", []))
    except Exception:
        return set()


def save_progress(completed: set[str]) -> None:
    _PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _PROGRESS_FILE.write_text(
        json.dumps({"date": datetime.utcnow().date().isoformat(), "completed": list(completed)})
    )


def run(team_filter: list[str] | None = None) -> dict:
    settings = get_settings()
    client = make_gcs_client(settings.gcs_project)
    storage = GCSStorage(settings.gcs_bucket, client)

    teams = load_teams(settings.teams_file)
    if team_filter:
        teams = [t for t in teams if t["code"] in team_filter]
    if not teams:
        logger.error("No teams to process.")
        return {"status": "error", "reason": "no teams"}

    completed = load_progress()
    start_time = datetime.utcnow()

    historical = HistoricalCollector(settings, storage)
    historical.initialize_if_needed()

    fd_collector = FootballDataCollector(settings, storage)
    af_collector = ApiFootballCollector(settings, storage)
    news_collector = NewsCollector(settings, storage)
    odds_collector = OddsCollector(settings, storage)
    sentiment_analyzer = SentimentAnalyzer(settings, storage)

    errors: list[dict] = []

    for team in teams:
        code = team["code"]
        if code in completed:
            logger.info("Skip %s (already done today)", code)
            continue

        logger.info("Processing %s...", code)
        team_errors: list[str] = []

        try:
            fd_collector.collect_team_form(code, team.get("football_data_id", 0))
        except Exception as exc:
            team_errors.append(f"form: {exc}")

        try:
            af_collector.collect_squad(code, team.get("api_football_id", 0))
        except Exception as exc:
            team_errors.append(f"squad: {exc}")

        try:
            articles = news_collector.collect_team_news(code, team.get("name", code))
            sentiment_analyzer.analyze_team(code, team.get("name", code), articles)
        except Exception as exc:
            team_errors.append(f"news/sentiment: {exc}")

        if team_errors:
            errors.append({"team": code, "errors": team_errors})
            logger.warning("%s completed with errors: %s", code, team_errors)
        else:
            logger.info("%s OK", code)

        completed.add(code)
        save_progress(completed)

    fd_collector.close()
    af_collector.close()
    news_collector.close()
    odds_collector.close()

    duration = (datetime.utcnow() - start_time).total_seconds()
    log_entry = {
        "date": start_time.isoformat(),
        "duration_seconds": round(duration),
        "teams_processed": len(completed),
        "errors": errors,
    }

    _append_pipeline_log(log_entry)
    storage.upload_json("_meta/last_updated.json", {"updated_at": datetime.utcnow().isoformat()})
    storage.upload_json("_meta/collection_log.json", _load_pipeline_log())

    logger.info(
        "Pipeline complete: %d teams in %.0fs, %d errors",
        len(completed), duration, len(errors),
    )
    return log_entry


def _append_pipeline_log(entry: dict) -> None:
    _LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing: list[dict] = []
    if _LOG_FILE.exists():
        try:
            existing = json.loads(_LOG_FILE.read_text())[-6:]
        except Exception:
            existing = []
    existing.append(entry)
    _LOG_FILE.write_text(json.dumps(existing, indent=2))


def _load_pipeline_log() -> list[dict]:
    if not _LOG_FILE.exists():
        return []
    try:
        return json.loads(_LOG_FILE.read_text())
    except Exception:
        return []


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copa 2026 daily data pipeline")
    parser.add_argument("--teams", type=str, help="Comma-separated team codes (e.g. BRA,FRA,ARG)")
    args = parser.parse_args()
    team_filter = args.teams.upper().split(",") if args.teams else None
    result = run(team_filter=team_filter)
    sys.exit(0 if result.get("status") != "error" else 1)
