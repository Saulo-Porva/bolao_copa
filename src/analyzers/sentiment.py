"""Hybrid sentiment pipeline: XLM-RoBERTa (local, free) + Claude Haiku (extreme articles only)."""
from __future__ import annotations

import json
import logging
from datetime import date

import anthropic

from src.config import Settings
from src.schemas.sentiment import SentimentDimensions, SentimentHistory, SentimentRecord
from src.storage.gcs import GCSStorage

logger = logging.getLogger(__name__)

_XLM_MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
_xlm_pipeline = None


def _get_xlm_pipeline():
    global _xlm_pipeline
    if _xlm_pipeline is None:
        from transformers import pipeline as hf_pipeline

        _xlm_pipeline = hf_pipeline(
            "sentiment-analysis",
            model=_XLM_MODEL,
            device=-1,
            truncation=True,
            max_length=512,
        )
    return _xlm_pipeline


def _xlm_score(text: str) -> float:
    """Returns a 0-10 score: 0=very negative, 10=very positive."""
    try:
        result = _get_xlm_pipeline()(text[:512])[0]
        label = result["label"].lower()
        confidence = result["score"]
        raw = {"positive": 10.0, "neutral": 5.0, "negative": 0.0}.get(label, 5.0)
        return round(raw * confidence + 5.0 * (1 - confidence), 2)
    except Exception as exc:
        logger.warning("XLM scoring failed: %s", exc)
        return 5.0


class SentimentAnalyzer:
    def __init__(self, settings: Settings, storage: GCSStorage) -> None:
        self._settings = settings
        self._storage = storage
        self._anthropic = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def analyze_team(self, team_code: str, team_name: str, articles: list[dict]) -> SentimentRecord:
        gcs_history_path = f"teams/{team_code}/sentiment/history.json"

        if len(articles) < 3:
            record = SentimentRecord(
                date=date.today(),
                overall_score=5.0,
                dimensions=SentimentDimensions(
                    cohesion=5, media_pressure=5, motivation=5, coach_confidence=5
                ),
                alerts=[],
                articles_analyzed=len(articles),
                data_quality="insufficient",
            )
        else:
            record = self._run_pipeline(team_name, articles)

        self._append_to_history(gcs_history_path, record)
        return record

    def _run_pipeline(self, team_name: str, articles: list[dict]) -> SentimentRecord:
        scores: list[float] = []
        extreme: list[tuple[dict, float]] = []

        for article in articles:
            text = f"{article.get('title', '')} {article.get('summary', '')}"
            score = _xlm_score(text)
            scores.append(score)
            lo = self._settings.sentiment_low_threshold
            hi = self._settings.sentiment_high_threshold
            if score < lo or score > hi:
                extreme.append((article, score))

        overall = round(sum(scores) / len(scores), 1)

        if not extreme:
            return SentimentRecord(
                date=date.today(),
                overall_score=overall,
                dimensions=SentimentDimensions(
                    cohesion=overall,
                    media_pressure=round(10 - overall, 1),
                    motivation=overall,
                    coach_confidence=overall,
                ),
                alerts=[],
                articles_analyzed=len(articles),
                data_quality="good",
            )

        return self._haiku_deep_analysis(team_name, extreme, overall, len(articles))

    def _haiku_deep_analysis(
        self,
        team_name: str,
        extreme_articles: list[tuple[dict, float]],
        overall_score: float,
        total_articles: int,
    ) -> SentimentRecord:
        articles_text = "\n\n---\n\n".join(
            f"Score: {score:.1f}/10\nTitle: {a['title']}\nSummary: {a.get('summary', '')[:300]}"
            for a, score in extreme_articles[:5]
        )

        prompt = f"""Analyze these news articles about {team_name} national football team.
Extract structured intelligence signals from a football analyst perspective.

Articles:
{articles_text}

Return ONLY valid JSON with this exact structure:
{{
  "dimensions": {{
    "cohesion": <0-10, squad unity — 10 means completely united>,
    "media_pressure": <0-10, press scrutiny — 10 means extreme pressure>,
    "motivation": <0-10, team drive and focus>,
    "coach_confidence": <0-10, trust in the manager>
  }},
  "alerts": ["<concrete alert 1>", "<concrete alert 2>"]
}}

Alerts must be specific: "Striker X doubtful with hamstring injury", not "team has problems".
Maximum 3 alerts. Return only JSON, no markdown or explanation."""

        try:
            msg = self._anthropic.messages.create(
                model=self._settings.haiku_model,
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}],
            )
            data = json.loads(msg.content[0].text)
            return SentimentRecord(
                date=date.today(),
                overall_score=overall_score,
                dimensions=SentimentDimensions(**data["dimensions"]),
                alerts=data.get("alerts", [])[:3],
                articles_analyzed=total_articles,
                data_quality="good",
            )
        except Exception as exc:
            logger.error("Haiku deep analysis failed for %s: %s", team_name, exc)
            return SentimentRecord(
                date=date.today(),
                overall_score=overall_score,
                dimensions=SentimentDimensions(
                    cohesion=5, media_pressure=5, motivation=5, coach_confidence=5
                ),
                alerts=[],
                articles_analyzed=total_articles,
                data_quality="limited",
            )

    def _append_to_history(self, gcs_path: str, record: SentimentRecord) -> None:
        raw = self._storage.download_json(gcs_path)
        if raw:
            try:
                history = SentimentHistory.model_validate(raw)
            except Exception:
                history = SentimentHistory(code=gcs_path.split("/")[1], records=[])
        else:
            history = SentimentHistory(code=gcs_path.split("/")[1], records=[])

        history.append(record)
        self._storage.upload_json(gcs_path, history.model_dump(mode="json"))

    def load_history(self, team_code: str) -> SentimentHistory | None:
        raw = self._storage.download_json(f"teams/{team_code}/sentiment/history.json")
        if not raw:
            return None
        try:
            return SentimentHistory.model_validate(raw)
        except Exception:
            return None
