"""One-time bulk download: Kaggle WC dataset + StatsBomb open data."""
from __future__ import annotations

import logging
from pathlib import Path

from src.config import Settings
from src.storage.gcs import GCSStorage

logger = logging.getLogger(__name__)

_KAGGLE_DATASET = "abecklas/fifa-world-cup"
_STATSBOMB_BASE = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"

_GCS_WC_RESULTS = "history/wc_results_1930_2022.json"
_GCS_TOP_SCORERS = "history/wc_top_scorers.json"
_GCS_TEAM_STATS = "history/wc_team_stats.json"


class HistoricalCollector:
    def __init__(self, settings: Settings, storage: GCSStorage) -> None:
        self._settings = settings
        self._storage = storage

    def initialize_if_needed(self) -> bool:
        """Download historical data only if not already in GCS. Returns True if ran."""
        if self._storage.exists(_GCS_WC_RESULTS):
            logger.info("Historical data already in GCS, skipping.")
            return False

        logger.info("Initializing historical data...")
        self._download_kaggle()
        self._download_statsbomb_metadata()
        return True

    def _download_kaggle(self) -> None:
        try:
            import kaggle  # noqa: F401

            local_dir = Path("data/kaggle_raw")
            local_dir.mkdir(parents=True, exist_ok=True)
            import subprocess

            subprocess.run(
                [
                    "kaggle", "datasets", "download",
                    "-d", _KAGGLE_DATASET, "-p", str(local_dir), "--unzip",
                ],
                check=True,
                capture_output=True,
            )
            self._process_kaggle_results(local_dir)
        except Exception as exc:
            logger.error("Kaggle download failed: %s — using empty history", exc)
            self._storage.upload_json(_GCS_WC_RESULTS, [])
            self._storage.upload_json(_GCS_TOP_SCORERS, [])
            self._storage.upload_json(_GCS_TEAM_STATS, {})

    def _process_kaggle_results(self, local_dir: Path) -> None:
        import csv

        results_file = next(local_dir.glob("WorldCups*.csv"), None)
        if not results_file:
            logger.warning("Kaggle CSV not found in %s", local_dir)
            self._storage.upload_json(_GCS_WC_RESULTS, [])
            return

        results = []
        with results_file.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                results.append(dict(row))

        self._storage.upload_json(_GCS_WC_RESULTS, results)
        logger.info("Uploaded %d WC results to GCS", len(results))

    def _download_statsbomb_metadata(self) -> None:
        import httpx

        try:
            resp = httpx.get(f"{_STATSBOMB_BASE}/competitions.json", timeout=30)
            resp.raise_for_status()
            competitions = resp.json()
            wc = [c for c in competitions if "World Cup" in c.get("competition_name", "")]
            self._storage.upload_json("history/statsbomb_competitions.json", wc)
            logger.info("StatsBomb: %d WC competitions indexed", len(wc))
        except Exception as exc:
            logger.warning("StatsBomb metadata download failed: %s", exc)
