"""Unit tests for data collectors using HTTP mocks."""
from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.collectors.football_data import FootballDataCollector
from src.collectors.news import NewsCollector
from src.config import Settings
from src.schemas.team import TeamForm


@pytest.fixture
def settings():
    return Settings(
        football_data_api_key="test_key",
        api_football_key="test_key",
        odds_api_key="test_key",
        anthropic_api_key="test_key",
        form_cache_hours=20,
        football_data_sleep_seconds=0.0,
    )


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    storage.download_json.return_value = None
    storage.upload_json.return_value = True
    return storage


@pytest.fixture
def fd_collector(settings, mock_storage):
    return FootballDataCollector(settings, mock_storage)


class TestFootballDataCollector:
    def test_returns_cached_form_when_fresh(self, fd_collector, mock_storage):
        cached_form = TeamForm(
            code="BRA",
            matches=[],
            updated_at=datetime.utcnow(),
        ).model_dump(mode="json")
        mock_storage.download_json.return_value = cached_form

        result = fd_collector.collect_team_form("BRA", 63)

        assert result is not None
        assert result.code == "BRA"
        mock_storage.upload_json.assert_not_called()

    def test_falls_back_to_cache_on_api_error(self, fd_collector, mock_storage):
        cached_form = TeamForm(
            code="BRA",
            matches=[],
            updated_at=datetime(2020, 1, 1),
        ).model_dump(mode="json")
        mock_storage.download_json.return_value = cached_form

        with patch.object(fd_collector._client, "get", side_effect=Exception("network error")):
            result = fd_collector.collect_team_form("BRA", 63)

        assert result is not None
        assert result.code == "BRA"
        mock_storage.upload_json.assert_not_called()

    def test_returns_none_when_no_cache_and_api_fails(self, fd_collector, mock_storage):
        mock_storage.download_json.return_value = None

        with patch.object(fd_collector._client, "get", side_effect=Exception("network error")):
            result = fd_collector.collect_team_form("BRA", 63)

        assert result is None

    def test_parse_match_home_win(self, fd_collector):
        raw = {
            "utcDate": "2025-03-22T20:00:00Z",
            "homeTeam": {"id": 63},
            "awayTeam": {"id": 64},
            "score": {"fullTime": {"home": 3, "away": 1}},
            "competition": {"name": "Friendly"},
            "stage": "REGULAR_SEASON",
        }
        result = fd_collector._parse_match(raw, team_id=63)
        assert result.result == "W"
        assert result.goals_scored == 3
        assert result.goals_conceded == 1
        assert result.home_or_away == "home"

    def test_parse_match_away_loss(self, fd_collector):
        raw = {
            "utcDate": "2025-03-22T20:00:00Z",
            "homeTeam": {"id": 64},
            "awayTeam": {"id": 63},
            "score": {"fullTime": {"home": 2, "away": 0}},
            "competition": {"name": "WC Qualifier"},
            "stage": "GROUP_STAGE",
        }
        result = fd_collector._parse_match(raw, team_id=63)
        assert result.result == "L"
        assert result.goals_scored == 0
        assert result.goals_conceded == 2
        assert result.home_or_away == "away"


class TestNewsCollector:
    def test_deduplicate_removes_same_url(self, settings, mock_storage):
        collector = NewsCollector(settings, mock_storage)
        articles = [
            {"id": "abc123", "title": "Article 1", "url": "http://example.com/1"},
            {"id": "abc123", "title": "Article 1 duplicate", "url": "http://example.com/1"},
            {"id": "def456", "title": "Article 2", "url": "http://example.com/2"},
        ]
        result = collector._deduplicate(articles)
        assert len(result) == 2
        assert result[0]["id"] == "abc123"
        assert result[1]["id"] == "def456"

    def test_returns_cached_news(self, settings, mock_storage):
        cached = [{"id": "x", "title": "cached", "url": "http://x.com"}]
        mock_storage.download_json.return_value = cached

        collector = NewsCollector(settings, mock_storage)
        result = collector.collect_team_news("BRA", "Brazil")

        assert result == cached
        mock_storage.upload_json.assert_not_called()
