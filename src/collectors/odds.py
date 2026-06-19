"""The Odds API v4 collector: match odds from multiple bookmakers."""
from __future__ import annotations

import json
import logging
from datetime import date, datetime
from pathlib import Path

import httpx

from src.config import Settings
from src.schemas.match import BookmakerOdds, OddsSnapshot
from src.storage.gcs import GCSStorage

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.the-odds-api.com/v4"
_MONTHLY_COUNTER_FILE = Path("data/.odds_api_calls.json")


class OddsCollector:
    def __init__(self, settings: Settings, storage: GCSStorage) -> None:
        self._settings = settings
        self._storage = storage
        self._client = httpx.Client(base_url=_BASE_URL, timeout=30)

    def _calls_this_month(self) -> int:
        if not _MONTHLY_COUNTER_FILE.exists():
            return 0
        try:
            data = json.loads(_MONTHLY_COUNTER_FILE.read_text())
            month = datetime.utcnow().strftime("%Y-%m")
            if data.get("month") != month:
                return 0
            return data.get("count", 0)
        except Exception:
            return 0

    def _increment_counter(self) -> None:
        count = self._calls_this_month() + 1
        _MONTHLY_COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
        month = datetime.utcnow().strftime("%Y-%m")
        _MONTHLY_COUNTER_FILE.write_text(json.dumps({"month": month, "count": count}))

    def collect_match_odds(
        self, match_key: str, event_id: str | None = None
    ) -> OddsSnapshot | None:
        today = date.today().isoformat()
        gcs_path = f"odds/{today}/{match_key}.json"

        cached = self._storage.download_json(gcs_path)
        if cached:
            try:
                snap = OddsSnapshot.model_validate(cached)
                snap_dt = datetime.combine(snap.date, datetime.min.time())
                age_hours = (datetime.utcnow() - snap_dt).total_seconds() / 3600
                if age_hours < self._settings.odds_cache_hours:
                    logger.debug("Cache hit odds %s", match_key)
                    return snap
            except Exception:
                pass

        if self._calls_this_month() >= self._settings.odds_api_monthly_limit - 10:
            logger.warning("Odds API monthly limit approaching, using cache for %s", match_key)
            return OddsSnapshot.model_validate(cached) if cached else None

        try:
            resp = self._client.get(
                "/sports/soccer_fifa_world_cup/odds",
                params={
                    "apiKey": self._settings.odds_api_key,
                    "regions": "eu,uk",
                    "markets": "h2h",
                    "oddsFormat": "decimal",
                    "eventIds": event_id or "",
                },
            )
            resp.raise_for_status()
            self._increment_counter()
            events = resp.json()
            snapshot = self._parse_events(match_key, events)
            self._storage.upload_json(gcs_path, snapshot.model_dump(mode="json"))
            return snapshot
        except httpx.HTTPError as exc:
            logger.error("Odds API error for %s: %s", match_key, exc)
            return OddsSnapshot.model_validate(cached) if cached else None

    def _parse_events(self, match_key: str, events: list) -> OddsSnapshot:
        bookmakers: dict[str, BookmakerOdds] = {}
        for event in events:
            for bm in event.get("bookmakers", []):
                markets = {m["key"]: m for m in bm.get("markets", [])}
                h2h = markets.get("h2h")
                if not h2h:
                    continue
                outcomes = {o["name"]: o["price"] for o in h2h.get("outcomes", [])}
                if len(outcomes) >= 3:
                    keys = list(outcomes.keys())
                    try:
                        bookmakers[bm["key"]] = BookmakerOdds(
                            home_win=outcomes.get(keys[0], 2.0),
                            draw=outcomes.get("Draw", 3.0),
                            away_win=outcomes.get(keys[1], 2.0),
                        )
                    except Exception:
                        continue
        return OddsSnapshot(match_key=match_key, date=date.today(), bookmakers=bookmakers)

    def close(self) -> None:
        self._client.close()
