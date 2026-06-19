"""Match analysis schemas — H2H, odds, and scoreline prediction structures."""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, computed_field, model_validator


class H2HMatch(BaseModel):
    date: date
    competition: str
    team_a_code: str
    team_b_code: str
    score_a: int = Field(ge=0)
    score_b: int = Field(ge=0)
    stage: str | None = None

    @computed_field
    @property
    def scoreline(self) -> str:
        return f"{self.score_a}x{self.score_b}"


class H2HHistory(BaseModel):
    team_a: str
    team_b: str
    matches: list[H2HMatch] = Field(default_factory=list)

    @model_validator(mode="after")
    def ensure_sorted_codes(self) -> H2HHistory:
        if self.team_a > self.team_b:
            self.team_a, self.team_b = self.team_b, self.team_a
        return self

    @computed_field
    @property
    def team_a_wins(self) -> int:
        return sum(1 for m in self.matches if m.score_a > m.score_b)

    @computed_field
    @property
    def team_b_wins(self) -> int:
        return sum(1 for m in self.matches if m.score_b > m.score_a)

    @computed_field
    @property
    def draws(self) -> int:
        return sum(1 for m in self.matches if m.score_a == m.score_b)

    @computed_field
    @property
    def common_scorelines(self) -> list[str]:
        from collections import Counter
        counts = Counter(f"{m.score_a}x{m.score_b}" for m in self.matches)
        return [s for s, _ in counts.most_common(5)]

    @classmethod
    def make_key(cls, code_a: str, code_b: str) -> str:
        return "_".join(sorted([code_a, code_b]))


class BookmakerOdds(BaseModel):
    home_win: float = Field(gt=1.0)
    draw: float = Field(gt=1.0)
    away_win: float = Field(gt=1.0)

    @computed_field
    @property
    def implied_home(self) -> float:
        return round(1 / self.home_win, 4)

    @computed_field
    @property
    def implied_draw(self) -> float:
        return round(1 / self.draw, 4)

    @computed_field
    @property
    def implied_away(self) -> float:
        return round(1 / self.away_win, 4)


class OddsSnapshot(BaseModel):
    match_key: str
    date: date
    bookmakers: dict[str, BookmakerOdds] = Field(default_factory=dict)

    def average_implied(self) -> dict[str, float]:
        if not self.bookmakers:
            return {"home": 0.45, "draw": 0.25, "away": 0.30}
        home = sum(b.implied_home for b in self.bookmakers.values()) / len(self.bookmakers)
        draw = sum(b.implied_draw for b in self.bookmakers.values()) / len(self.bookmakers)
        away = sum(b.implied_away for b in self.bookmakers.values()) / len(self.bookmakers)
        total = home + draw + away
        return {
            "home": round(home / total, 4),
            "draw": round(draw / total, 4),
            "away": round(away / total, 4),
        }


class ScorelinePrediction(BaseModel):
    scoreline: str
    probability: float = Field(ge=0.0, le=1.0)
    market_implied: float | None = Field(default=None, ge=0.0, le=1.0)
    narrative: str

    @computed_field
    @property
    def value_pp(self) -> float | None:
        if self.market_implied is None:
            return None
        return round((self.probability - self.market_implied) * 100, 1)

    @computed_field
    @property
    def is_value_bet(self) -> bool:
        return self.value_pp is not None and self.value_pp > 5.0


class MatchAnalysis(BaseModel):
    match_key: str
    team_a_code: str
    team_b_code: str
    team_a_name: str
    team_b_name: str
    generated_at: datetime
    cached_until: datetime
    scoreline_predictions: list[ScorelinePrediction]
    outcome_summary: dict[str, float]
    signals_used: dict
    confidence_level: Literal["high", "medium", "low"]
    data_freshness_hours: float
    llm_reasoning: str = ""

    @model_validator(mode="after")
    def validate_probabilities(self) -> MatchAnalysis:
        total = sum(p.probability for p in self.scoreline_predictions)
        if total > 1.01:
            raise ValueError(f"Probabilities sum to {total:.3f} > 1.0")
        return self

    @computed_field
    @property
    def value_bets(self) -> list[ScorelinePrediction]:
        return [p for p in self.scoreline_predictions if p.is_value_bet]
