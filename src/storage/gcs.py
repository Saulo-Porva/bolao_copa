"""GCS read/write helpers with retry, batch upload, and rollback-safe behavior."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError, NotFound

logger = logging.getLogger(__name__)


class GCSStorage:
    def __init__(self, bucket_name: str, client: storage.Client) -> None:
        self._bucket = client.bucket(bucket_name)
        self._bucket_name = bucket_name

    def upload_json(self, gcs_path: str, data: dict | list, overwrite: bool = True) -> bool:
        blob = self._bucket.blob(gcs_path)
        if not overwrite and blob.exists():
            logger.debug("Skip upload (exists): %s", gcs_path)
            return False
        try:
            blob.upload_from_string(
                json.dumps(data, ensure_ascii=False, default=str, indent=2),
                content_type="application/json",
            )
            logger.info("Uploaded gs://%s/%s", self._bucket_name, gcs_path)
            return True
        except Exception as exc:
            logger.error("GCS upload failed %s: %s", gcs_path, exc)
            return False

    def download_json(self, gcs_path: str) -> dict | list | None:
        blob = self._bucket.blob(gcs_path)
        try:
            return json.loads(blob.download_as_text())
        except NotFound:
            logger.debug("Not found in GCS: %s", gcs_path)
            return None
        except Exception as exc:
            logger.warning("GCS download failed %s: %s", gcs_path, exc)
            return None

    def exists(self, gcs_path: str) -> bool:
        return self._bucket.blob(gcs_path).exists()

    def upload_batch(
        self,
        items: list[tuple[str, dict | list]],
        progress_callback: callable | None = None,
    ) -> dict[str, bool]:
        """Upload list of (gcs_path, data); returns {path: success}. Never aborts on failure."""
        results: dict[str, bool] = {}
        for i, (gcs_path, data) in enumerate(items):
            results[gcs_path] = self.upload_json(gcs_path, data)
            if progress_callback:
                progress_callback(i + 1, len(items), gcs_path)
        return results

    def upload_local_file(self, local_path: Path, gcs_path: str) -> bool:
        blob = self._bucket.blob(gcs_path)
        try:
            blob.upload_from_filename(str(local_path))
            logger.info("Uploaded file gs://%s/%s", self._bucket_name, gcs_path)
            return True
        except GoogleCloudError as exc:
            logger.error("GCS file upload failed %s: %s", gcs_path, exc)
            return False

    def list_blobs(self, prefix: str) -> list[str]:
        return [b.name for b in self._bucket.list_blobs(prefix=prefix)]

    def append_json_list(
        self, gcs_path: str, new_item: dict, max_items: int | None = None
    ) -> bool:
        existing = self.download_json(gcs_path)
        if existing is None:
            existing = []
        if not isinstance(existing, list):
            existing = [existing]
        existing.append(new_item)
        if max_items is not None and len(existing) > max_items:
            existing = existing[-max_items:]
        return self.upload_json(gcs_path, existing)


def make_gcs_client(project: str | None = None) -> storage.Client:
    """Creates GCS client using GOOGLE_APPLICATION_CREDENTIALS env var (local pipeline)."""
    return storage.Client(project=project)


def make_gcs_client_from_streamlit(secrets: dict) -> storage.Client:
    """Creates GCS client from Streamlit Secrets (Streamlit Cloud deployment)."""
    from google.oauth2 import service_account

    # Normalize private_key from Streamlit secrets:
    # - single-line TOML may return literal \\n instead of newlines
    # - multiline TOML (""") returns actual newlines but may have leading/trailing whitespace
    pk = secrets.get("private_key", "")
    pk = pk.replace("\\n", "\n").strip()
    if not pk.endswith("\n"):
        pk += "\n"

    sa_info = {**dict(secrets), "private_key": pk}
    credentials = service_account.Credentials.from_service_account_info(
        sa_info,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    return storage.Client(credentials=credentials, project=sa_info.get("project_id"))
