"""One-time initialization: download Kaggle WC dataset and StatsBomb data to GCS.

Usage:
    python scripts/init_historical.py
"""
from __future__ import annotations

import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    from src.collectors.historical import HistoricalCollector
    from src.config import get_settings
    from src.storage.gcs import GCSStorage, make_gcs_client

    settings = get_settings()
    client = make_gcs_client(settings.gcs_project)
    storage = GCSStorage(settings.gcs_bucket, client)
    collector = HistoricalCollector(settings, storage)

    ran = collector.initialize_if_needed()
    if ran:
        logger.info("Historical data initialization complete.")
    else:
        logger.info("Historical data already present in GCS. Nothing to do.")


if __name__ == "__main__":
    main()
    sys.exit(0)
