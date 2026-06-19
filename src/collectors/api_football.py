"""API-Football v3 collector: squad, injuries, player stats."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

import httpx

from src.config import Settings
from src.schemas.team import Player, TeamSquad, TeamStats, TopScorer
from src.storage.gcs import GCSStorage

logger = logging.getLogger(__name__)

_BASE_URL = "https://v3.football.api-sports.io"
_DAILY_COUNTER_FILE = Path("data/.api_football_calls.json")


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
            injured_names = {
                inj["player"]["name"]
                for inj in injuries_data["response"]
            }
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
            p for p in data.get("response", [])
            if p["statistics"][0]["team"]["id"] == team_id
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
