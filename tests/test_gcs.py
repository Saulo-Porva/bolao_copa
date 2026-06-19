"""Unit tests for GCS storage adapter using mocked google-cloud-storage."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from src.storage.gcs import GCSStorage


@pytest.fixture
def mock_client():
    client = MagicMock()
    bucket = MagicMock()
    client.bucket.return_value = bucket
    return client, bucket


@pytest.fixture
def storage(mock_client):
    client, _ = mock_client
    return GCSStorage(client=client, bucket_name="test-bucket")


class TestGCSStorageUpload:
    def test_upload_json_serializes_and_writes(self, storage, mock_client):
        _, bucket = mock_client
        blob = MagicMock()
        bucket.blob.return_value = blob

        data = {"team": "BRA", "score": 5}
        result = storage.upload_json("teams/BRA.json", data)

        assert result is True
        blob.upload_from_string.assert_called_once()
        call_args = blob.upload_from_string.call_args
        uploaded = json.loads(call_args[0][0])
        assert uploaded["team"] == "BRA"
        assert call_args[1]["content_type"] == "application/json"

    def test_upload_json_returns_false_on_error(self, storage, mock_client):
        _, bucket = mock_client
        blob = MagicMock()
        blob.upload_from_string.side_effect = Exception("GCS error")
        bucket.blob.return_value = blob

        result = storage.upload_json("teams/BRA.json", {"x": 1})

        assert result is False


class TestGCSStorageDownload:
    def test_download_json_returns_parsed_dict(self, storage, mock_client):
        _, bucket = mock_client
        blob = MagicMock()
        blob.download_as_text.return_value = json.dumps({"code": "BRA"})
        bucket.blob.return_value = blob

        result = storage.download_json("teams/BRA.json")

        assert result == {"code": "BRA"}

    def test_download_json_returns_none_when_not_found(self, storage, mock_client):
        from google.cloud.exceptions import NotFound

        _, bucket = mock_client
        blob = MagicMock()
        blob.download_as_text.side_effect = NotFound("blob not found")
        bucket.blob.return_value = blob

        result = storage.download_json("teams/MISSING.json")

        assert result is None

    def test_download_json_returns_none_on_generic_error(self, storage, mock_client):
        _, bucket = mock_client
        blob = MagicMock()
        blob.download_as_text.side_effect = Exception("network timeout")
        bucket.blob.return_value = blob

        result = storage.download_json("teams/BRA.json")

        assert result is None


class TestGCSStorageExists:
    def test_exists_returns_true_when_blob_present(self, storage, mock_client):
        _, bucket = mock_client
        blob = MagicMock()
        blob.exists.return_value = True
        bucket.blob.return_value = blob

        assert storage.exists("teams/BRA.json") is True

    def test_exists_returns_false_when_blob_absent(self, storage, mock_client):
        _, bucket = mock_client
        blob = MagicMock()
        blob.exists.return_value = False
        bucket.blob.return_value = blob

        assert storage.exists("teams/BRA.json") is False


class TestGCSStorageBatch:
    def test_upload_batch_calls_upload_for_each_item(self, storage):
        items = [
            ("teams/BRA.json", {"code": "BRA"}),
            ("teams/FRA.json", {"code": "FRA"}),
        ]

        with patch.object(storage, "upload_json", return_value=True) as mock_upload:
            results = storage.upload_batch(items)

        assert len(results) == 2
        assert all(v is True for v in results.values())
        assert mock_upload.call_count == 2

    def test_upload_batch_continues_on_partial_failure(self, storage):
        items = [
            ("teams/BRA.json", {"code": "BRA"}),
            ("teams/FAIL.json", {"code": "FAIL"}),
            ("teams/FRA.json", {"code": "FRA"}),
        ]

        def _side_effect(path, data):
            return path != "teams/FAIL.json"

        with patch.object(storage, "upload_json", side_effect=_side_effect):
            results = storage.upload_batch(items)

        assert results["teams/BRA.json"] is True
        assert results["teams/FAIL.json"] is False
        assert results["teams/FRA.json"] is True


class TestGCSStorageAppend:
    def test_append_json_list_creates_new_when_missing(self, storage):
        new_item = {"id": "1", "text": "article"}

        with (
            patch.object(storage, "download_json", return_value=None),
            patch.object(storage, "upload_json", return_value=True) as mock_upload,
        ):
            storage.append_json_list("news/BRA.json", new_item)

        uploaded_list = mock_upload.call_args[0][1]
        assert len(uploaded_list) == 1
        assert uploaded_list[0]["id"] == "1"

    def test_append_json_list_appends_to_existing(self, storage):
        existing = [{"id": "0", "text": "old"}]
        new_item = {"id": "1", "text": "new"}

        with (
            patch.object(storage, "download_json", return_value=existing),
            patch.object(storage, "upload_json", return_value=True) as mock_upload,
        ):
            storage.append_json_list("news/BRA.json", new_item)

        uploaded_list = mock_upload.call_args[0][1]
        assert len(uploaded_list) == 2
        assert uploaded_list[-1]["id"] == "1"

    def test_append_json_list_enforces_max_items(self, storage):
        existing = [{"id": str(i)} for i in range(100)]
        new_item = {"id": "999"}

        with (
            patch.object(storage, "download_json", return_value=existing),
            patch.object(storage, "upload_json", return_value=True) as mock_upload,
        ):
            storage.append_json_list("news/BRA.json", new_item, max_items=50)

        uploaded_list = mock_upload.call_args[0][1]
        assert len(uploaded_list) == 50
        assert uploaded_list[-1]["id"] == "999"
