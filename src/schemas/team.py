"""Team data schemas — source of truth for all team-related structures."""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, computed_field


class MatchResult(BaseModel):
    date: date
    opponent_code: str
    home_or_away: Literal["home", "away", "neutral"]
    goals_scored: int = Field(ge=0)
    goals_conceded: int = Field(ge=0)
    competition: str
    result: Literal["W", "D", "L"]


class TeamForm(BaseModel):
    code: str
    matches: list[MatchResult]
    updated_at: datetime

    @computed_field
    @property
    def avg_goals_scored(self) -> float:
        if not self.matches:
            return 0.0
        return round(sum(m.goals_scored for m in self.matches) / len(self.matches), 2)

    @computed_field
    @property
    def avg_goals_conceded(self) -> float:
        if not self.matches:
            return 0.0
        return round(sum(m.goals_conceded for m in self.matches) / len(self.matches), 2)

    @computed_field
    @property
    def record(self) -> str:
        w = sum(1 for m in self.matches if m.result == "W")
        d = sum(1 for m in self.matches if m.result == "D")
        losses = sum(1 for m in self.matches if m.result == "L")
        return f"{w}W-{d}D-{losses}L"


class TeamProfile(BaseModel):
    code: str
    name: str
    name_pt: str
    confederation: Literal["UEFA", "CONMEBOL", "CONCACAF", "CAF", "AFC", "OFC"]
    fifa_ranking: int = Field(ge=1)
    group: str | None = None
    api_football_id: int | None = None
    football_data_id: int | None = None
    updated_at: datetime


class Player(BaseModel):
    name: str
    position: Literal["GK", "DF", "MF", "FW"]
    club: str
    status: Literal["fit", "doubtful", "injured", "suspended"]
    notes: str | None = None


class TeamSquad(BaseModel):
    code: str
    players: list[Player]
    updated_at: datetime

    @computed_field
    @property
    def key_absences(self) -> list[str]:
        return [
            p.name for p in self.players
            if p.status in ("injured", "suspended")
        ]


class TopScorer(BaseModel):
    name: str
    goals: int = Field(ge=0)
    assists: int = Field(ge=0)
    position: str


class TopPasser(BaseModel):
    name: str
    passes: int = Field(ge=0)
    key_passes: int = Field(ge=0)


class TeamStats(BaseModel):
    code: str
    top_scorers: list[TopScorer]
    top_passers: list[TopPasser]
    goals_conceded_total: int = Field(ge=0)
    goals_conceded_rank: int | None = None
    updated_at: datetime
