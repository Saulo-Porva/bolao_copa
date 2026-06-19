"""Claude Sonnet 4.6 match analyzer: scoreline predictions with narratives."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta

import anthropic

from src.config import Settings
from src.schemas.match import H2HHistory, MatchAnalysis, OddsSnapshot, ScorelinePrediction
from src.schemas.sentiment import SentimentHistory
from src.schemas.team import TeamForm, TeamSquad
from src.storage.gcs import GCSStorage

logger = logging.getLogger(__name__)

_PROMPT_TEMPLATE = """\
You are an elite football match analyst combining statistical rigor with qualitative intelligence.
Your job: predict the most likely SPECIFIC SCORELINES for this match, not just win/draw/lose.

Match: {team_a_name} vs {team_b_name}
Competition: FIFA World Cup 2026 — {phase}

## HEAD-TO-HEAD ({h2h_total} matches)
{h2h_table}
Most frequent scorelines: {common_scorelines}
{team_a_name} wins: {h2h_a_wins} | Draws: {h2h_draws} | {team_b_name} wins: {h2h_b_wins}

## RECENT FORM (last 10 games)
{team_a_name}: {form_a_record} | Avg scored: {form_a_scored} | Avg conceded: {form_a_conceded}
{team_b_name}: {form_b_record} | Avg scored: {form_b_scored} | Avg conceded: {form_b_conceded}

## SQUAD ALERTS
{team_a_name} absences: {alerts_a}
{team_b_name} absences: {alerts_b}

## SQUAD MORALE (0=very negative, 10=very positive)
{team_a_name}: {sentiment_a}/10 (trend: {trend_a}) | Key signals: {signals_a}
{team_b_name}: {sentiment_b}/10 (trend: {trend_b}) | Key signals: {signals_b}

## MARKET REFERENCE (for calibration only — markets may already reflect public info)
Market odds: {team_a_name} {odds_home_pct}% | Draw {odds_draw_pct}% | {team_b_name} {odds_away_pct}%

## YOUR TASK
Generate the 5 most probable specific scorelines.
Rules:
- Format: "{team_a_name} 2x1 {team_b_name}" (team_a always first, use real name not code)
- Probabilities must sum to ≤ 0.72 (remaining probability = other outcomes)
- Each narrative: 2-3 sentences explaining WHY this exact score
- Compare your probability vs market_implied for that scoreline (estimate market_implied if unknown)
- Flag if your_prob > market_implied + 0.05 (potential value bet)

Return ONLY valid JSON, no markdown:
{{
  "scoreline_predictions": [
    {{
      "scoreline": "string",
      "probability": 0.00,
      "market_implied": 0.00,
      "narrative": "string"
    }}
  ],
  "outcome_summary": {{"team_a_wins": 0.00, "draw": 0.00, "team_b_wins": 0.00}},
  "confidence_level": "high|medium|low",
  "reasoning": "1-2 sentence overall assessment"
}}"""


class MatchAnalyzer:
    def __init__(self, settings: Settings, storage: GCSStorage) -> None:
        self._settings = settings
        self._storage = storage
        self._anthropic = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def analyze(
        self,
        team_a_code: str,
        team_b_code: str,
        team_a_name: str,
        team_b_name: str,
        form_a: TeamForm | None,
        form_b: TeamForm | None,
        squad_a: TeamSquad | None,
        squad_b: TeamSquad | None,
        sentiment_a: SentimentHistory | None,
        sentiment_b: SentimentHistory | None,
        h2h: H2HHistory | None,
        odds: OddsSnapshot | None,
        phase: str = "Group Stage",
    ) -> MatchAnalysis:
        match_key = H2HHistory.make_key(team_a_code, team_b_code)
        gcs_path = f"matches/wc2026/analysis/{match_key}.json"

        cached = self._storage.download_json(gcs_path)
        if cached:
            try:
                analysis = MatchAnalysis.model_validate(cached)
                if analysis.cached_until > datetime.utcnow():
                    logger.debug("Cache hit analysis %s", match_key)
                    return analysis
            except Exception:
                pass

        prompt = self._build_prompt(
            team_a_name, team_b_name, form_a, form_b,
            squad_a, squad_b, sentiment_a, sentiment_b,
            h2h, odds, phase,
        )

        try:
            msg = self._anthropic.messages.create(
                model=self._settings.sonnet_model,
                max_tokens=2500,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = json.loads(msg.content[0].text)
        except json.JSONDecodeError:
            logger.error("Sonnet returned invalid JSON for %s", match_key)
            raw = self._fallback_response(team_a_name, team_b_name)
        except Exception as exc:
            logger.error("Sonnet analysis failed for %s: %s", match_key, exc)
            raw = self._fallback_response(team_a_name, team_b_name)

        predictions = [ScorelinePrediction(**p) for p in raw["scoreline_predictions"]]
        analysis = MatchAnalysis(
            match_key=match_key,
            team_a_code=team_a_code,
            team_b_code=team_b_code,
            team_a_name=team_a_name,
            team_b_name=team_b_name,
            generated_at=datetime.utcnow(),
            cached_until=datetime.utcnow() + timedelta(hours=self._settings.analysis_cache_hours),
            scoreline_predictions=predictions,
            outcome_summary=raw.get(
                "outcome_summary", {"team_a_wins": 0.4, "draw": 0.25, "team_b_wins": 0.35}
            ),
            signals_used={
                "form_a": form_a.record if form_a else "N/A",
                "form_b": form_b.record if form_b else "N/A",
                "h2h_matches": len(h2h.matches) if h2h else 0,
                "sentiment_a": (
                    sentiment_a.latest().overall_score
                    if sentiment_a and sentiment_a.latest() else None
                ),
                "sentiment_b": (
                    sentiment_b.latest().overall_score
                    if sentiment_b and sentiment_b.latest() else None
                ),
                "odds_available": odds is not None and bool(odds.bookmakers),
            },
            confidence_level=raw.get("confidence_level", "medium"),
            data_freshness_hours=0.0,
            llm_reasoning=raw.get("reasoning", ""),
        )

        self._storage.upload_json(gcs_path, analysis.model_dump(mode="json"))
        return analysis

    def _build_prompt(
        self,
        team_a_name: str, team_b_name: str,
        form_a: TeamForm, form_b: TeamForm,
        squad_a: TeamSquad | None, squad_b: TeamSquad | None,
        sentiment_a: SentimentHistory | None, sentiment_b: SentimentHistory | None,
        h2h: H2HHistory | None, odds: OddsSnapshot | None,
        phase: str,
    ) -> str:
        h2h_table = "No historical data available."
        h2h_total = 0
        h2h_a_wins = h2h_draws = h2h_b_wins = 0
        common_scorelines = "N/A"
        if h2h and h2h.matches:
            h2h_total = len(h2h.matches)
            h2h_a_wins = h2h.team_a_wins
            h2h_draws = h2h.draws
            h2h_b_wins = h2h.team_b_wins
            common_scorelines = ", ".join(h2h.common_scorelines[:5]) or "N/A"
            rows = "\n".join(
                f"  {m.date} | {m.competition} | {m.score_a}x{m.score_b}"
                for m in sorted(h2h.matches, key=lambda x: x.date, reverse=True)[:8]
            )
            h2h_table = rows or "No matches found."

        alerts_a = ", ".join(squad_a.key_absences) if squad_a and squad_a.key_absences else "None"
        alerts_b = ", ".join(squad_b.key_absences) if squad_b and squad_b.key_absences else "None"

        sent_a = sentiment_a.latest() if sentiment_a else None
        sent_b = sentiment_b.latest() if sentiment_b else None
        sa_score = f"{sent_a.overall_score:.1f}" if sent_a else "N/A"
        sb_score = f"{sent_b.overall_score:.1f}" if sent_b else "N/A"
        sa_trend = sentiment_a.trend() if sentiment_a else "→"
        sb_trend = sentiment_b.trend() if sentiment_b else "→"
        sa_signals = ", ".join(sent_a.alerts[:2]) if sent_a and sent_a.alerts else "None"
        sb_signals = ", ".join(sent_b.alerts[:2]) if sent_b and sent_b.alerts else "None"

        implied = odds.average_implied() if odds else {"home": 0.45, "draw": 0.25, "away": 0.30}

        return _PROMPT_TEMPLATE.format(
            team_a_name=team_a_name, team_b_name=team_b_name, phase=phase,
            h2h_total=h2h_total, h2h_table=h2h_table, common_scorelines=common_scorelines,
            h2h_a_wins=h2h_a_wins, h2h_draws=h2h_draws, h2h_b_wins=h2h_b_wins,
            form_a_record=form_a.record if form_a else "N/A (sem dados)",
            form_a_scored=form_a.avg_goals_scored if form_a else 0.0,
            form_a_conceded=form_a.avg_goals_conceded if form_a else 0.0,
            form_b_record=form_b.record if form_b else "N/A (sem dados)",
            form_b_scored=form_b.avg_goals_scored if form_b else 0.0,
            form_b_conceded=form_b.avg_goals_conceded if form_b else 0.0,
            alerts_a=alerts_a, alerts_b=alerts_b,
            sentiment_a=sa_score, trend_a=sa_trend, signals_a=sa_signals,
            sentiment_b=sb_score, trend_b=sb_trend, signals_b=sb_signals,
            odds_home_pct=round(implied["home"] * 100, 1),
            odds_draw_pct=round(implied["draw"] * 100, 1),
            odds_away_pct=round(implied["away"] * 100, 1),
        )

    def _fallback_response(self, team_a_name: str, team_b_name: str) -> dict:
        return {
            "scoreline_predictions": [
                {
                    "scoreline": f"{team_a_name} 1x0 {team_b_name}",
                    "probability": 0.18, "market_implied": 0.16,
                    "narrative": "Narrow victory based on statistical advantage.",
                },
                {
                    "scoreline": f"{team_a_name} 2x1 {team_b_name}",
                    "probability": 0.15, "market_implied": 0.14,
                    "narrative": "Open game with both teams scoring.",
                },
                {
                    "scoreline": f"{team_a_name} 1x1 {team_b_name}",
                    "probability": 0.14, "market_implied": 0.15,
                    "narrative": "Draw reflects balanced recent form.",
                },
                {
                    "scoreline": f"{team_b_name} 1x0 {team_a_name}",
                    "probability": 0.12, "market_implied": 0.13,
                    "narrative": "Upset scenario — away side finds a winner.",
                },
                {
                    "scoreline": f"{team_a_name} 2x0 {team_b_name}",
                    "probability": 0.11, "market_implied": 0.10,
                    "narrative": "Dominant display with clean sheet.",
                },
            ],
            "outcome_summary": {"team_a_wins": 0.50, "draw": 0.25, "team_b_wins": 0.25},
            "confidence_level": "low",
            "reasoning": "Fallback prediction — LLM analysis unavailable.",
        }
