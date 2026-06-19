"""Unit tests for the match analyzer (Sonnet 4.6 prediction)."""
from __future__ import annotations

import json
from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

from src.analyzers.match_analyzer import MatchAnalyzer
from src.config import Settings
from src.schemas.match import MatchAnalysis, ScorelinePrediction
from src.schemas.team import MatchResult, TeamForm


@pytest.fixture
def settings():
    return Settings(
        anthropic_api_key="test_key",
        sonnet_model="claude-sonnet-4-6",
        analysis_cache_hours=24,
    )


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    storage.download_json.return_value = None
    storage.upload_json.return_value = True
    return storage


@pytest.fixture
def analyzer(settings, mock_storage):
    return MatchAnalyzer(settings, mock_storage)


def _make_form(code: str, wins: int = 6, draws: int = 2, losses: int = 2) -> TeamForm:
    matches = []
    results = ["W"] * wins + ["D"] * draws + ["L"] * losses
    for i, result in enumerate(results[:10]):
        gs, gc = (2, 0) if result == "W" else ((1, 1) if result == "D" else (0, 1))
        matches.append(MatchResult(
            date=date(2025, 1, i + 1),
            opponent_code="OPP",
            home_or_away="home",
            goals_scored=gs,
            goals_conceded=gc,
            competition="Friendly",
            result=result,
        ))
    return TeamForm(code=code, matches=matches, updated_at=datetime.utcnow())


_VALID_LLM_RESPONSE = {
    "scoreline_predictions": [
        {"scoreline": "Brasil 2x0 França", "probability": 0.22,
         "market_implied": 0.14, "narrative": "Brasil dominant."},
        {"scoreline": "Brasil 1x0 França", "probability": 0.18,
         "market_implied": 0.16, "narrative": "Narrow win."},
        {"scoreline": "Brasil 1x1 França", "probability": 0.15,
         "market_implied": 0.18, "narrative": "Draw likely."},
        {"scoreline": "França 1x0 Brasil", "probability": 0.12,
         "market_implied": 0.13, "narrative": "Upset."},
        {"scoreline": "Brasil 2x1 França", "probability": 0.11,
         "market_implied": 0.10, "narrative": "Open game."},
    ],
    "outcome_summary": {"team_a_wins": 0.58, "draw": 0.22, "team_b_wins": 0.20},
    "confidence_level": "high",
    "reasoning": "Brasil has superior form and home advantage.",
}


class TestMatchAnalyzer:
    def test_returns_valid_analysis_on_success(self, analyzer, mock_storage):
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=json.dumps(_VALID_LLM_RESPONSE))]

        with patch.object(analyzer._anthropic.messages, "create", return_value=mock_msg):
            result = analyzer.analyze(
                team_a_code="BRA", team_b_code="FRA",
                team_a_name="Brasil", team_b_name="França",
                form_a=_make_form("BRA"), form_b=_make_form("FRA"),
                squad_a=None, squad_b=None,
                sentiment_a=None, sentiment_b=None,
                h2h=None, odds=None,
            )

        assert isinstance(result, MatchAnalysis)
        assert len(result.scoreline_predictions) == 5
        assert result.confidence_level == "high"
        assert result.team_a_name == "Brasil"
        mock_storage.upload_json.assert_called_once()

    def test_returns_cached_analysis_when_valid(self, analyzer, mock_storage):
        from datetime import timedelta
        cached = MatchAnalysis(
            match_key="BRA_FRA", team_a_code="BRA", team_b_code="FRA",
            team_a_name="Brasil", team_b_name="França",
            generated_at=datetime.utcnow(),
            cached_until=datetime.utcnow() + timedelta(hours=12),
            scoreline_predictions=[
                ScorelinePrediction(
                    scoreline="Brasil 1x0 França", probability=0.20, narrative="cached"
                )
            ],
            outcome_summary={"team_a_wins": 0.5, "draw": 0.25, "team_b_wins": 0.25},
            signals_used={}, confidence_level="medium", data_freshness_hours=1.0,
        )
        mock_storage.download_json.return_value = cached.model_dump(mode="json")

        with patch.object(analyzer._anthropic.messages, "create") as mock_create:
            result = analyzer.analyze(
                team_a_code="BRA", team_b_code="FRA",
                team_a_name="Brasil", team_b_name="França",
                form_a=_make_form("BRA"), form_b=_make_form("FRA"),
                squad_a=None, squad_b=None,
                sentiment_a=None, sentiment_b=None,
                h2h=None, odds=None,
            )

        mock_create.assert_not_called()
        assert result.scoreline_predictions[0].scoreline == "Brasil 1x0 França"

    def test_uses_fallback_on_json_error(self, analyzer, mock_storage):
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text="not valid json {{{")]

        with patch.object(analyzer._anthropic.messages, "create", return_value=mock_msg):
            result = analyzer.analyze(
                team_a_code="BRA", team_b_code="FRA",
                team_a_name="Brasil", team_b_name="França",
                form_a=_make_form("BRA"), form_b=_make_form("FRA"),
                squad_a=None, squad_b=None,
                sentiment_a=None, sentiment_b=None,
                h2h=None, odds=None,
            )

        assert result.confidence_level == "low"
        assert len(result.scoreline_predictions) == 5

    def test_value_bets_identified(self, analyzer, mock_storage):
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=json.dumps(_VALID_LLM_RESPONSE))]

        with patch.object(analyzer._anthropic.messages, "create", return_value=mock_msg):
            result = analyzer.analyze(
                team_a_code="BRA", team_b_code="FRA",
                team_a_name="Brasil", team_b_name="França",
                form_a=_make_form("BRA"), form_b=_make_form("FRA"),
                squad_a=None, squad_b=None,
                sentiment_a=None, sentiment_b=None,
                h2h=None, odds=None,
            )

        value_bets = result.value_bets
        assert any(vb.scoreline == "Brasil 2x0 França" for vb in value_bets)
