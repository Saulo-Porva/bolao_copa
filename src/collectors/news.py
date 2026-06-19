"""Google News RSS + Reddit RSS collector: local news per national team."""
from __future__ import annotations

import hashlib
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import quote

import httpx

from src.config import Settings
from src.storage.gcs import GCSStorage

logger = logging.getLogger(__name__)

_REDDIT_SUBREDDITS: dict[str, str] = {
    "BRA": "brazil", "ARG": "argentina", "MEX": "mexico", "USA": "ussoccer",
    "CAN": "CanadaSoccer", "COL": "colombia", "CHL": "chile", "URU": "uruguay",
    "ECU": "ecuador", "PER": "peru", "PAR": "paraguay", "CRC": "CostaRica",
    "HON": "Honduras", "PAN": "panama", "JAM": "jamaica", "VEN": "venezuela",
    "BOL": "bolivia", "FRA": "france", "ENG": "england", "GER": "germany",
    "ESP": "spain", "POR": "portugal", "NED": "netherlands", "BEL": "belgium",
    "CRO": "croatia", "SUI": "switzerland", "AUT": "austria", "POL": "poland",
    "SRB": "serbia", "HUN": "hungary", "SCO": "Scotland", "WAL": "Wales",
}

_NEWS_LANGS: dict[str, tuple[str, str]] = {
    "BRA": ("pt-BR", "BR"), "ARG": ("es-AR", "AR"), "MEX": ("es-MX", "MX"),
    "USA": ("en-US", "US"), "CAN": ("en-CA", "CA"), "FRA": ("fr-FR", "FR"),
    "ENG": ("en-GB", "GB"), "GER": ("de-DE", "DE"), "ESP": ("es-ES", "ES"),
    "POR": ("pt-PT", "PT"), "NED": ("nl-NL", "NL"), "BEL": ("fr-BE", "BE"),
    "CRO": ("hr-HR", "HR"), "POL": ("pl-PL", "PL"), "SRB": ("sr-RS", "RS"),
    "JPN": ("ja-JP", "JP"), "KOR": ("ko-KR", "KR"), "MAR": ("ar-MA", "MA"),
    "SEN": ("fr-SN", "SN"), "CMR": ("fr-CM", "CM"), "EGY": ("ar-EG", "EG"),
    "NGA": ("en-NG", "NG"), "GHA": ("en-GH", "GH"), "SAU": ("ar-SA", "SA"),
    "IRN": ("fa-IR", "IR"), "AUS": ("en-AU", "AU"), "NZL": ("en-NZ", "NZ"),
}


class NewsCollector:
    def __init__(self, settings: Settings, storage: GCSStorage) -> None:
        self._settings = settings
        self._storage = storage
        self._client = httpx.Client(timeout=15, follow_redirects=True)

    def collect_team_news(self, team_code: str, team_name: str) -> list[dict]:
        today = datetime.utcnow().date().isoformat()
        gcs_path = f"teams/{team_code}/news/{today}.json"

        cached = self._storage.download_json(gcs_path)
        if cached:
            return cached

        articles: list[dict] = []
        articles.extend(self._fetch_google_news(team_code, team_name))
        articles.extend(self._fetch_reddit_rss(team_code))
        articles = self._deduplicate(articles)

        if articles:
            self._storage.upload_json(gcs_path, articles)
            logger.info("Collected %d articles for %s", len(articles), team_code)
        return articles

    def _fetch_google_news(self, team_code: str, team_name: str) -> list[dict]:
        lang, country = _NEWS_LANGS.get(team_code, ("en-US", "US"))
        query = quote(f'"{team_name}" seleção OR seleccion OR national team soccer football')
        url = f"https://news.google.com/rss/search?q={query}&hl={lang}&gl={country}&ceid={country}:{lang[:2]}"
        return self._parse_rss(url, source="google_news", team_code=team_code)

    def _fetch_reddit_rss(self, team_code: str) -> list[dict]:
        subreddit = _REDDIT_SUBREDDITS.get(team_code)
        if not subreddit:
            return []
        url = f"https://www.reddit.com/r/{subreddit}/new/.rss?limit=25"
        return self._parse_rss(url, source="reddit", team_code=team_code)

    def _parse_rss(self, url: str, source: str, team_code: str) -> list[dict]:
        try:
            resp = self._client.get(url, headers={"User-Agent": "CopaBet/1.0"})
            resp.raise_for_status()
            root = ET.fromstring(resp.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            articles = []

            for item in root.findall(".//item"):
                title = item.findtext("title", "").strip()
                link = item.findtext("link", "").strip()
                pub_date = item.findtext("pubDate", "")
                description = item.findtext("description", "").strip()[:500]
                if title and link:
                    articles.append({
                        "id": hashlib.md5(link.encode()).hexdigest(),
                        "title": title,
                        "url": link,
                        "summary": description,
                        "published": pub_date,
                        "source": source,
                        "team_code": team_code,
                    })

            for entry in root.findall("atom:entry", ns):
                title = entry.findtext("atom:title", "", ns).strip()
                link_el = entry.find("atom:link", ns)
                link = link_el.get("href", "") if link_el is not None else ""
                summary = entry.findtext("atom:summary", "", ns).strip()[:500]
                updated = entry.findtext("atom:updated", "")
                if title and link:
                    articles.append({
                        "id": hashlib.md5(link.encode()).hexdigest(),
                        "title": title,
                        "url": link,
                        "summary": summary,
                        "published": updated,
                        "source": source,
                        "team_code": team_code,
                    })

            return articles
        except Exception as exc:
            logger.warning("RSS fetch failed %s (%s): %s", url, team_code, exc)
            return []

    def _deduplicate(self, articles: list[dict]) -> list[dict]:
        seen: set[str] = set()
        unique = []
        for a in articles:
            if a["id"] not in seen:
                seen.add(a["id"])
                unique.append(a)
        return unique

    def close(self) -> None:
        self._client.close()
