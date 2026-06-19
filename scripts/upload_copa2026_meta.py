"""Upload Copa 2026 meta files to GCS."""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Settings
from src.storage.gcs import GCSStorage, make_gcs_client


def main() -> None:
    settings = Settings()
    client = make_gcs_client(settings.gcs_project)
    storage = GCSStorage(settings.gcs_bucket, client)

    files = {
        "_meta/teams_48.json": "data/teams_48.json",
        "_meta/copa2026_fixtures.json": "data/copa2026_fixtures.json",
        "wc2026/standings.json": "data/copa2026_standings.json",
    }

    for gcs_path, local_path in files.items():
        with open(local_path, encoding="utf-8") as f:
            data = json.load(f)
        storage.upload_json(gcs_path, data)
        print(f"Uploaded {local_path} -> gs://{settings.gcs_bucket}/{gcs_path}")

    print("All uploads complete.")


if __name__ == "__main__":
    main()
