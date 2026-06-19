"""Unit tests for the sentiment analysis pipeline."""
from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from src.analyzers.sentiment import SentimentAnalyzer, _xlm_score
from src.config import Settings
from src.schemas.sentiment import SentimentDimensions, SentimentHistory, SentimentRecord


@pytest.fixture
def settings():
    return Settings(
        anthropic_api_key="test_key",
        haiku_model="claude-haiku-4-5-20251001",
        sentiment_low_threshold=3.0,
        sentiment_high_threshold=8.0,
    )


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    storage.download_json.return_value = None
    storage.upload_json.return_value = True
    return storage


@pytest.fixture
def analyzer(settings, mock_storage):
    return SentimentAnalyzer(settings, mock_storage)


class TestXlmScore:
    def test_returns_float_in_range(self):
        with patch("src.analyzers.sentiment._get_xlm_pipeline") as mock_pipe:
            mock_pipe.return_value = lambda text, **kw: [{"label": "positive", "score": 0.9}]
            score = _xlm_score("Brazil wins again!")
        assert 0.0 <= score <= 10.0

    def test_negative_label_returns_low_score(self):
        with patch("src.analyzers.sentiment._get_xlm_pipeline") as mock_pipe:
            mock_pipe.return_value = lambda text, **kw: [{"label": "negative", "score": 0.95}]
            score = _xlm_score("Team in crisis, coach fired")
        assert score < 3.0

    def test_returns_neutral_on_exception(self):
        err = Exception("model error")
        with patch("src.analyzers.sentiment._get_xlm_pipeline", side_effect=err):
            score = _xlm_score("some text")
        assert score == 5.0


class TestSentimentAnalyzer:
    def test_insufficient_articles_returns_neutral(self, analyzer):
        articles = [{"title": "one"}, {"title": "two"}]
        record = analyzer.analyze_team("BRA", "Brazil", articles=articles)
        assert record.data_quality == "insufficient"
        assert record.overall_score == 5.0
        assert record.articles_analyzed == 2

    def test_moderate_articles_skips_haiku(self, analyzer, settings):
        articles = [
            {"title": f"Article {i}", "summary": "Team plays well this season"}
            for i in range(5)
        ]
        with patch("src.analyzers.sentiment._get_xlm_pipeline") as mock_pipe:
            mock_pipe.return_value = lambda text, **kw: [{"label": "neutral", "score": 0.8}]
            with patch.object(analyzer, "_haiku_deep_analysis") as mock_haiku:
                record = analyzer.analyze_team("BRA", "Brazil", articles)

        mock_haiku.assert_not_called()
        assert record.data_quality == "good"

    def test_extreme_articles_triggers_haiku(self, analyzer):
        articles = [{"title": f"Crisis {i}", "summary": "Total collapse"} for i in range(5)]
        haiku_record = SentimentRecord(
            date=date.today(),
            overall_score=1.5,
            dimensions=SentimentDimensions(
                cohesion=2, media_pressure=9, motivation=2, coach_confidence=1
            ),
            alerts=["Coach fired", "Players on strike"],
            articles_analyzed=5,
            data_quality="good",
        )
        with patch("src.analyzers.sentiment._get_xlm_pipeline") as mock_pipe:
            mock_pipe.return_value = lambda text, **kw: [{"label": "negative", "score": 0.99}]
            with patch.object(
                analyzer, "_haiku_deep_analysis", return_value=haiku_record
            ) as mock_haiku:
                record = analyzer.analyze_team("BRA", "Brazil", articles)

        mock_haiku.assert_called_once()
        assert record.alerts == ["Coach fired", "Players on strike"]

    def test_load_history_returns_none_when_missing(self, analyzer, mock_storage):
        mock_storage.download_json.return_value = None
        result = analyzer.load_history("BRA")
        assert result is None

    def test_load_history_parses_correctly(self, analyzer, mock_storage):
        history = SentimentHistory(code="BRA", records=[])
        mock_storage.download_json.return_value = history.model_dump(mode="json")
        result = analyzer.load_history("BRA")
        assert result is not None
        assert result.code == "BRA"
