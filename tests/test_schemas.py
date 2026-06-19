"""Unit tests for all Pydantic schemas."""
from __future__ import annotations

from datetime import date, datetime

import pytest

from src.schemas.match import (
    BookmakerOdds,
    H2HHistory,
    H2HMatch,
    MatchAnalysis,
    OddsSnapshot,
    ScorelinePrediction,
)
from src.schemas.sentiment import SentimentDimensions, SentimentHistory, SentimentRecord
from src.schemas.team import MatchResult, Player, TeamForm, TeamSquad


class TestTeamSchemas:
    def test_team_form_computed_fields(self):
        matches = [
            MatchResult(date=date(2025, 1, i + 1), opponent_code="ARG", home_or_away="home",
                        goals_scored=2, goals_conceded=1, competition="Friendly", result="W")
            for i in range(5)
        ] + [
            MatchResult(date=date(2025, 1, i + 6), opponent_code="FRA", home_or_away="away",
                        goals_scored=0, goals_conceded=0, competition="Friendly", result="D")
            for i in range(3)
        ] + [
            MatchResult(date=date(2025, 1, i + 9), opponent_code="GER", home_or_away="neutral",
                        goals_scored=1, goals_conceded=2, competition="Friendly", result="L")
            for i in range(2)
        ]
        form = TeamForm(code="BRA", matches=matches, updated_at=datetime.utcnow())
        assert form.record == "5W-3D-2L"
        assert form.avg_goals_scored == 1.2
        assert form.avg_goals_conceded == 0.9

    def test_team_form_empty_matches(self):
        form = TeamForm(code="BRA", matches=[], updated_at=datetime.utcnow())
        assert form.avg_goals_scored == 0.0
        assert form.avg_goals_conceded == 0.0
        assert form.record == "0W-0D-0L"

    def test_team_squad_key_absences(self):
        players = [
            Player(name="Vinicius Jr", position="FW", club="Real Madrid", status="fit"),
            Player(name="Neymar", position="FW", club="Al-Hilal",
                   status="injured", notes="hamstring"),
            Player(name="Casemiro", position="MF", club="Man United", status="suspended"),
        ]
        squad = TeamSquad(code="BRA", players=players, updated_at=datetime.utcnow())
        assert "Neymar" in squad.key_absences
        assert "Casemiro" in squad.key_absences
        assert "Vinicius Jr" not in squad.key_absences


class TestSentimentSchemas:
    def _make_record(self, score: float, d: date | None = None) -> SentimentRecord:
        return SentimentRecord(
            date=d or date.today(),
            overall_score=score,
            dimensions=SentimentDimensions(
                cohesion=score, media_pressure=5, motivation=score, coach_confidence=5
            ),
            alerts=[],
            articles_analyzed=10,
            data_quality="good",
        )

    def test_sentiment_record_properties(self):
        assert self._make_record(2.0).is_negative is True
        assert self._make_record(8.0).is_positive is True
        assert self._make_record(5.0).is_negative is False
        assert self._make_record(5.0).is_positive is False

    def test_sentiment_history_trend_up(self):
        history = SentimentHistory(code="BRA", records=[
            self._make_record(4.0, date(2025, 1, 1)),
            self._make_record(7.0, date(2025, 1, 7)),
        ])
        assert history.trend() == "↑"

    def test_sentiment_history_trend_down(self):
        history = SentimentHistory(code="FRA", records=[
            self._make_record(8.0, date(2025, 1, 1)),
            self._make_record(4.0, date(2025, 1, 7)),
        ])
        assert history.trend() == "↓"

    def test_sentiment_history_no_duplicate_dates(self):
        history = SentimentHistory(code="BRA", records=[])
        record = self._make_record(7.0, date(2025, 1, 1))
        history.append(record)
        history.append(record)
        assert len(history.records) == 1

    def test_sentiment_history_latest(self):
        history = SentimentHistory(code="BRA", records=[
            self._make_record(5.0, date(2025, 1, 1)),
            self._make_record(8.0, date(2025, 1, 5)),
        ])
        assert history.latest().overall_score == 8.0


class TestMatchSchemas:
    def test_h2h_key_always_sorted(self):
        assert H2HHistory.make_key("FRA", "BRA") == "BRA_FRA"
        assert H2HHistory.make_key("BRA", "FRA") == "BRA_FRA"

    def test_h2h_computed_stats(self):
        def _h2h(d, comp, sa, sb):
            return H2HMatch(
                date=d, competition=comp,
                team_a_code="BRA", team_b_code="FRA",
                score_a=sa, score_b=sb,
            )

        matches = [
            _h2h(date(2022, 12, 9), "WC", 1, 0),
            _h2h(date(2018, 6, 23), "WC", 2, 1),
            _h2h(date(2006, 7, 1), "WC", 0, 1),
            _h2h(date(2004, 8, 18), "Friendly", 0, 0),
        ]
        h2h = H2HHistory(team_a="BRA", team_b="FRA", matches=matches)
        assert h2h.team_a_wins == 2
        assert h2h.team_b_wins == 1
        assert h2h.draws == 1

    def test_scoreline_value_bet_detection(self):
        good = ScorelinePrediction(
            scoreline="BRA 2x0 FRA", probability=0.22, market_implied=0.14, narrative="x"
        )
        no_value = ScorelinePrediction(
            scoreline="BRA 1x0 FRA", probability=0.18, market_implied=0.16, narrative="x"
        )
        assert good.is_value_bet is True
        assert good.value_pp == pytest.approx(8.0, abs=0.1)
        assert no_value.is_value_bet is False

    def test_match_analysis_rejects_probability_overflow(self):
        predictions = [
            ScorelinePrediction(
                scoreline=f"BRA {i}x0 FRA", probability=0.25,
                market_implied=0.10, narrative="x",
            )
            for i in range(5)
        ]
        with pytest.raises(ValueError, match="Probabilities sum"):
            MatchAnalysis(
                match_key="BRA_FRA", team_a_code="BRA", team_b_code="FRA",
                team_a_name="Brasil", team_b_name="França",
                generated_at=datetime.utcnow(), cached_until=datetime.utcnow(),
                scoreline_predictions=predictions,
                outcome_summary={"team_a_wins": 0.5, "draw": 0.25, "team_b_wins": 0.25},
                signals_used={}, confidence_level="high", data_freshness_hours=1.0,
            )

    def test_bookmaker_odds_implied_probability(self):
        odds = BookmakerOdds(home_win=2.0, draw=3.5, away_win=4.0)
        assert odds.implied_home == pytest.approx(0.5, abs=0.01)
        assert odds.implied_draw == pytest.approx(0.2857, abs=0.001)

    def test_odds_snapshot_average_implied(self):
        snap = OddsSnapshot(
            match_key="BRA_FRA",
            date=date.today(),
            bookmakers={
                "bet365": BookmakerOdds(home_win=1.9, draw=3.4, away_win=4.2),
                "pinnacle": BookmakerOdds(home_win=1.95, draw=3.5, away_win=4.1),
            },
        )
        implied = snap.average_implied()
        assert sum(implied.values()) == pytest.approx(1.0, abs=0.01)
