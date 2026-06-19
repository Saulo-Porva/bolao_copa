"""football-data.org API v4 collector: form, H2H, standings."""
from __future__ import annotations

import logging
import time
from datetime import datetime

import httpx

from src.config import Settings
from src.schemas.match import H2HHistory, H2HMatch
from src.schemas.team import MatchResult, TeamForm
from src.storage.gcs import GCSStorage

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.football-data.org/v4"


class FootballDataCollector:
    def __init__(self, settings: Settings, storage: GCSStorage) -> None:
        self._settings = settings
        self._storage = storage
        self._client = httpx.Client(
            base_url=_BASE_URL,
            headers={"X-Auth-Token": settings.football_data_api_key},
            timeout=30,
        )

    def _get(self, path: str, params: dict | None = None) -> dict | None:
        time.sleep(self._settings.football_data_sleep_seconds)
        try:
            resp = self._client.get(path, params=params)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            logger.error("football-data.org %s %s: %s", exc.response.status_code, path, exc)
            return None
        except Exception as exc:
            logger.error("football-data.org error %s: %s", path, exc)
            return None

    def collect_team_form(self, team_code: str, team_id: int) -> TeamForm | None:
        gcs_path = f"teams/{team_code}/form.json"
        cached = self._storage.download_json(gcs_path)
        if cached:
            try:
                form = TeamForm.model_validate(cached)
                age_hours = (datetime.utcnow() - form.updated_at).total_seconds() / 3600
                if age_hours < self._settings.form_cache_hours:
                    logger.debug("Cache hit form %s (%.1fh old)", team_code, age_hours)
                    return form
            except Exception:
                pass

        data = self._get(f"/teams/{team_id}/matches", {"limit": 10, "status": "FINISHED"})
        if not data:
            return TeamForm.model_validate(cached) if cached else None

        matches = [self._parse_match(m, team_id) for m in data.get("matches", [])]
        form = TeamForm(code=team_code, matches=matches, updated_at=datetime.utcnow())
        self._storage.upload_json(gcs_path, form.model_dump(mode="json"))
        return form

    def collect_h2h(self, team_a: str, team_b: str, team_a_id: int) -> H2HHistory | None:
        key = H2HHistory.make_key(team_a, team_b)
        gcs_path = f"matches/h2h/{key}.json"
        cached = self._storage.download_json(gcs_path)
        if cached:
            try:
                h2h = H2HHistory.model_validate(cached)
                updated = datetime.fromisoformat(cached.get("updated_at", "2000-01-01"))
                age_days = (datetime.utcnow() - updated).days
                if age_days < self._settings.h2h_cache_days:
                    return h2h
            except Exception:
                pass

        data = self._get(f"/teams/{team_a_id}/matches", {"limit": 50, "status": "FINISHED"})
        if not data:
            return H2HHistory.model_validate(cached) if cached else None

        ta, tb = sorted([team_a, team_b])
        all_matches = data.get("matches", [])
        h2h_raw = [m for m in all_matches if self._involves_both(m, team_a_id)]
        h2h_matches = [self._parse_h2h_match(m, ta, tb) for m in h2h_raw]

        h2h = H2HHistory(team_a=ta, team_b=tb, matches=h2h_matches)
        payload = h2h.model_dump(mode="json")
        payload["updated_at"] = datetime.utcnow().isoformat()
        self._storage.upload_json(gcs_path, payload)
        return h2h

    def _involves_both(self, match: dict, team_id: int) -> bool:
        home_id = match.get("homeTeam", {}).get("id")
        away_id = match.get("awayTeam", {}).get("id")
        return team_id in (home_id, away_id)

    def _parse_match(self, raw: dict, team_id: int) -> MatchResult:
        home_id = raw["homeTeam"]["id"]
        is_home = home_id == team_id
        home_score = raw["score"]["fullTime"].get("home") or 0
        away_score = raw["score"]["fullTime"].get("away") or 0
        gs = home_score if is_home else away_score
        gc = away_score if is_home else home_score
        result: str
        if gs > gc:
            result = "W"
        elif gs < gc:
            result = "L"
        else:
            result = "D"
        opponent_id = raw["awayTeam"]["id"] if is_home else raw["homeTeam"]["id"]
        return MatchResult(
            date=raw["utcDate"][:10],
            opponent_code=str(opponent_id),
            home_or_away="home" if is_home else "away",
            goals_scored=gs,
            goals_conceded=gc,
            competition=raw["competition"]["name"],
            result=result,
        )

    def _parse_h2h_match(self, raw: dict, team_a: str, team_b: str) -> H2HMatch:
        home_score = raw["score"]["fullTime"].get("home") or 0
        away_score = raw["score"]["fullTime"].get("away") or 0
        return H2HMatch(
            date=raw["utcDate"][:10],
            competition=raw["competition"]["name"],
            team_a_code=team_a,
            team_b_code=team_b,
            score_a=home_score,
            score_b=away_score,
            stage=raw.get("stage"),
        )

    def close(self) -> None:
        self._client.close()
