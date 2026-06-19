"""API-Football v3 collector: squad, injuries, Copa 2026 form, player stats."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

import httpx

from src.config import Settings
from src.schemas.team import MatchResult, Player, TeamForm, TeamSquad, TeamStats, TopScorer
from src.storage.gcs import GCSStorage

logger = logging.getLogger(__name__)

_BASE_URL = "https://v3.football.api-sports.io"
_DAILY_COUNTER_FILE = Path("data/.api_football_calls.json")

_WC2026_LEAGUE = 1
_WC2026_SEASON = 2026


class ApiFootballCollector:
    def __init__(self, settings: Settings, storage: GCSStorage) -> None:
        self._settings = settings
        self._storage = storage
        self._client = httpx.Client(
            base_url=_BASE_URL,
            headers={"x-apisports-key": settings.api_football_key},
            timeout=30,
        )

    def _calls_today(self) -> int:
        if not _DAILY_COUNTER_FILE.exists():
            return 0
        try:
            data = json.loads(_DAILY_COUNTER_FILE.read_text())
            if data.get("date") != datetime.utcnow().date().isoformat():
                return 0
            return data.get("count", 0)
        except Exception:
            return 0

    def _increment_counter(self) -> None:
        count = self._calls_today() + 1
        _DAILY_COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
        _DAILY_COUNTER_FILE.write_text(
            json.dumps({"date": datetime.utcnow().date().isoformat(), "count": count})
        )

    def _get(self, path: str, params: dict | None = None) -> dict | None:
        if self._calls_today() >= self._settings.api_football_daily_limit - 2:
            logger.warning("API-Football daily limit approaching, skipping %s", path)
            return None
        try:
            resp = self._client.get(path, params=params)
            resp.raise_for_status()
            self._increment_counter()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            logger.error("API-Football %s %s: %s", exc.response.status_code, path, exc)
            return None
        except httpx.HTTPError as exc:
            logger.error("API-Football network error %s: %s", path, exc)
            return None

    def collect_copa2026_form(self, team_code: str, team_id: int) -> TeamForm | None:
        gcs_path = f"teams/{team_code}/form.json"
        cached = self._storage.download_json(gcs_path)
        if cached:
            try:
                form = TeamForm.model_validate(cached)
                if form.matches:
                    age_hours = (datetime.utcnow() - form.updated_at).total_seconds() / 3600
                    if age_hours < self._settings.form_cache_hours:
                        logger.debug("Cache hit Copa form %s", team_code)
                        return form
            except Exception:
                pass

        data = self._get(
            "/fixtures",
            {"league": _WC2026_LEAGUE, "season": _WC2026_SEASON, "team": team_id, "status": "FT"},
        )
        if not data or not data.get("response"):
            logger.warning("No Copa 2026 fixtures from API-Football for %s (id=%s)", team_code, team_id)
            return TeamForm.model_validate(cached) if cached else None

        matches = [self._parse_fixture(f, team_id) for f in data["response"]]
        form = TeamForm(code=team_code, matches=matches, updated_at=datetime.utcnow())
        self._storage.upload_json(gcs_path, form.model_dump(mode="json"))
        logger.info("Copa 2026 form %s: %d matches", team_code, len(matches))
        return form

    def collect_squad(self, team_code: str, team_id: int, season: int = 2025) -> TeamSquad | None:
        gcs_path = f"teams/{team_code}/squad.json"
        cached = self._storage.download_json(gcs_path)
        if cached:
            try:
                squad = TeamSquad.model_validate(cached)
                age_hours = (datetime.utcnow() - squad.updated_at).total_seconds() / 3600
                if age_hours < self._settings.squad_cache_hours:
                    logger.debug("Cache hit squad %s (%.1fh old)", team_code, age_hours)
                    return squad
            except Exception:
                pass

        data = self._get("/players/squads", {"team": team_id})
        if not data or not data.get("response"):
            return TeamSquad.model_validate(cached) if cached else None

        raw_players = data["response"][0].get("players", []) if data["response"] else []
        players = [self._parse_player(p) for p in raw_players]

        injuries_data = self._get("/injuries", {"team": team_id, "season": season})
        if injuries_data and injuries_data.get("response"):
            injured_names = {inj["player"]["name"] for inj in injuries_data["response"]}
            for p in players:
                if p.name in injured_names:
                    p.status = "injured"

        squad = TeamSquad(code=team_code, players=players, updated_at=datetime.utcnow())
        self._storage.upload_json(gcs_path, squad.model_dump(mode="json"))
        return squad

    def collect_stats(self, team_code: str, team_id: int, season: int = 2025) -> TeamStats | None:
        gcs_path = f"teams/{team_code}/stats.json"
        cached = self._storage.download_json(gcs_path)
        if cached:
            try:
                stats = TeamStats.model_validate(cached)
                age_hours = (datetime.utcnow() - stats.updated_at).total_seconds() / 3600
                if age_hours < self._settings.squad_cache_hours:
                    return stats
            except Exception:
                pass

        data = self._get("/players/topscorers", {"league": 1, "season": season})
        if not data:
            return TeamStats.model_validate(cached) if cached else None

        team_scorers = [
            p for p in data.get("response", []) if p["statistics"][0]["team"]["id"] == team_id
        ]
        top_scorers = [
            TopScorer(
                name=p["player"]["name"],
                goals=p["statistics"][0]["goals"]["total"] or 0,
                assists=p["statistics"][0]["goals"]["assists"] or 0,
                position=p["player"]["position"],
            )
            for p in team_scorers[:10]
        ]

        stats = TeamStats(
            code=team_code,
            top_scorers=top_scorers,
            top_passers=[],
            goals_conceded_total=0,
            updated_at=datetime.utcnow(),
        )
        self._storage.upload_json(gcs_path, stats.model_dump(mode="json"))
        return stats

    def _parse_fixture(self, fixture: dict, team_id: int) -> MatchResult:
        home = fixture["teams"]["home"]
        away = fixture["teams"]["away"]
        goals = fixture["goals"]
        fix = fixture["fixture"]

        is_home = home["id"] == team_id
        gs = (goals["home"] if is_home else goals["away"]) or 0
        gc = (goals["away"] if is_home else goals["home"]) or 0

        if gs > gc:
            result = "W"
        elif gs < gc:
            result = "L"
        else:
            result = "D"

        opp_name = away["name"] if is_home else home["name"]
        opp_code = opp_name[:3].upper()

        return MatchResult(
            date=fix["date"][:10],
            opponent_code=opp_code,
            home_or_away="home" if is_home else "away",
            goals_scored=gs,
            goals_conceded=gc,
            competition="FIFA World Cup 2026",
            result=result,
        )

    def _parse_player(self, raw: dict) -> Player:
        pos_map = {"Goalkeeper": "GK", "Defender": "DF", "Midfielder": "MF", "Attacker": "FW"}
        return Player(
            name=raw.get("name", "Unknown"),
            position=pos_map.get(raw.get("position", ""), "MF"),
            club=(
                raw.get("club", {}).get("name", "Unknown")
                if isinstance(raw.get("club"), dict)
                else "Unknown"
            ),
            status="fit",
        )

    def close(self) -> None:
        self._client.close()
