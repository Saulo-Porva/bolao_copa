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

# Map The Odds API team names → our codes
_NAME_TO_CODE: dict[str, str] = {
    "Mexico": "MEX", "South Korea": "KOR", "Czech Republic": "CZE", "South Africa": "RSA",
    "Canada": "CAN", "Switzerland": "SUI", "Bosnia Herzegovina": "BIH",
    "Bosnia and Herzegovina": "BIH", "Qatar": "QAT",
    "Morocco": "MAR", "Scotland": "SCO", "Brazil": "BRA", "Haiti": "HTI",
    "United States": "USA", "Australia": "AUS", "Turkey": "TUR", "Paraguay": "PAR",
    "Germany": "GER", "Ivory Coast": "CIV", "Cote d'Ivoire": "CIV", "Ecuador": "ECU",
    "Curacao": "CUR",
    "Sweden": "SWE", "Japan": "JPN", "Netherlands": "NED", "Tunisia": "TUN",
    "New Zealand": "NZL", "Iran": "IRN", "Belgium": "BEL", "Egypt": "EGY",
    "Uruguay": "URU", "Saudi Arabia": "SAU", "Spain": "ESP", "Cape Verde": "CPV",
    "Norway": "NOR", "France": "FRA", "Senegal": "SEN", "Iraq": "IRQ",
    "Argentina": "ARG", "Austria": "AUT", "Jordan": "JOR", "Algeria": "ALG",
    "Colombia": "COL", "DR Congo": "COD", "Portugal": "POR", "Uzbekistan": "UZB",
    "England": "ENG", "Ghana": "GHA", "Panama": "PAN", "Croatia": "CRO",
}


def _team_code(name: str) -> str:
    return _NAME_TO_CODE.get(name, name[:3].upper())


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

    def collect_all_copa2026(self) -> list[OddsSnapshot]:
        """Fetch all Copa 2026 odds and save one GCS file per match."""
        if self._calls_this_month() >= self._settings.odds_api_monthly_limit - 10:
            logger.warning("Odds API monthly limit approaching, skipping bulk fetch")
            return []

        try:
            resp = self._client.get(
                "/sports/soccer_fifa_world_cup/odds",
                params={
                    "apiKey": self._settings.odds_api_key,
                    "regions": "eu,uk",
                    "markets": "h2h",
                    "oddsFormat": "decimal",
                },
            )
            resp.raise_for_status()
            self._increment_counter()
            events = resp.json()
        except httpx.HTTPError as exc:
            logger.error("Odds API bulk fetch failed: %s", exc)
            return []

        today = date.today().isoformat()
        snapshots: list[OddsSnapshot] = []

        for event in events:
            home_name = event.get("home_team", "")
            away_name = event.get("away_team", "")
            home_code = _team_code(home_name)
            away_code = _team_code(away_name)
            key_a, key_b = sorted([home_code, away_code])
            match_key = f"{key_a}_{key_b}"

            gcs_path = f"odds/{today}/{match_key}.json"

            bookmakers: dict[str, BookmakerOdds] = {}
            for bm in event.get("bookmakers", []):
                markets = {m["key"]: m for m in bm.get("markets", [])}
                h2h = markets.get("h2h")
                if not h2h:
                    continue
                outcomes = {o["name"]: o["price"] for o in h2h.get("outcomes", [])}
                home_odds = outcomes.get(home_name)
                away_odds = outcomes.get(away_name)
                draw_odds = outcomes.get("Draw")
                if home_odds and away_odds and draw_odds:
                    try:
                        bookmakers[bm["key"]] = BookmakerOdds(
                            home_win=home_odds,
                            draw=draw_odds,
                            away_win=away_odds,
                        )
                    except Exception:
                        continue

            if bookmakers:
                snap = OddsSnapshot(match_key=match_key, date=date.today(), bookmakers=bookmakers)
                self._storage.upload_json(gcs_path, snap.model_dump(mode="json"))
                snapshots.append(snap)
                logger.info("Odds saved: %s (%d bookmakers)", match_key, len(bookmakers))

        logger.info("Collected odds for %d Copa 2026 matches", len(snapshots))
        return snapshots

    def collect_match_odds(
        self, match_key: str, event_id: str | None = None
    ) -> OddsSnapshot | None:
        today = date.today().isoformat()
        gcs_path = f"odds/{today}/{match_key}.json"

        cached = self._storage.download_json(gcs_path)
        if cached:
            try:
                snap = OddsSnapshot.model_validate(cached)
                return snap
            except Exception:
                pass
        return None

    def close(self) -> None:
        self._client.close()
