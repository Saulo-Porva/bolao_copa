"""Sentiment schemas — squad morale and news signal structures."""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class SentimentDimensions(BaseModel):
    cohesion: float = Field(ge=0.0, le=10.0, description="Squad unity and harmony")
    media_pressure: float = Field(ge=0.0, le=10.0, description="Press scrutiny level (10=extreme)")
    motivation: float = Field(ge=0.0, le=10.0, description="Team drive and focus")
    coach_confidence: float = Field(ge=0.0, le=10.0, description="Trust in the manager")


class SentimentRecord(BaseModel):
    date: date
    overall_score: float = Field(ge=0.0, le=10.0)
    dimensions: SentimentDimensions
    alerts: list[str] = Field(default_factory=list, max_length=5)
    articles_analyzed: int = Field(ge=0)
    data_quality: Literal["good", "limited", "insufficient"]

    @property
    def is_negative(self) -> bool:
        return self.overall_score < 4.0

    @property
    def is_positive(self) -> bool:
        return self.overall_score > 7.0


class SentimentHistory(BaseModel):
    code: str
    records: list[SentimentRecord] = Field(default_factory=list)

    def latest(self) -> SentimentRecord | None:
        return self.records[-1] if self.records else None

    def trend(self, days: int = 7) -> str:
        if len(self.records) < 2:
            return "→"
        recent = self.records[-min(days, len(self.records)):]
        delta = recent[-1].overall_score - recent[0].overall_score
        if delta > 0.5:
            return "↑"
        if delta < -0.5:
            return "↓"
        return "→"

    def append(self, record: SentimentRecord) -> None:
        existing_dates = {r.date for r in self.records}
        if record.date not in existing_dates:
            self.records.append(record)
            self.records.sort(key=lambda r: r.date)
