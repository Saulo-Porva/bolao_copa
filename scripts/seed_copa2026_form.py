"""Seed form.json from Copa 2026 standings for teams without API data.

Builds synthetic MatchResult entries from aggregate standings (J/V/E/D/GM/GS).
Only writes teams that currently have 0 matches in their form.json.
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Settings
from src.schemas.team import MatchResult, TeamForm
from src.storage.gcs import GCSStorage, make_gcs_client

# Round 1 each group plays 2 matches simultaneously; opponent pairing:
# positions 0-3 in group → (0v1, 2v3) on R1; (0v2, 1v3) on R2; (0v3, 1v2) on R3
_R1 = date(2026, 6, 12)
_R2 = date(2026, 6, 16)
_R3 = date(2026, 6, 20)

GROUPS: dict[str, list[str]] = {
    "A": ["MEX", "KOR", "CZE", "RSA"],
    "B": ["CAN", "SUI", "BIH", "QAT"],
    "C": ["MAR", "SCO", "BRA", "HTI"],
    "D": ["USA", "AUS", "TUR", "PAR"],
    "E": ["GER", "CIV", "ECU", "CUR"],
    "F": ["SWE", "JPN", "NED", "TUN"],
    "G": ["NZL", "IRN", "BEL", "EGY"],
    "H": ["URU", "SAU", "ESP", "CPV"],
    "I": ["NOR", "FRA", "SEN", "IRQ"],
    "J": ["ARG", "AUT", "JOR", "ALG"],
    "K": ["COL", "COD", "POR", "UZB"],
    "L": ["ENG", "GHA", "PAN", "CRO"],
}

# Each round: list of (idx_a, idx_b, date)
ROUNDS: list[list[tuple[int, int, date]]] = [
    [(0, 1, _R1), (2, 3, _R1)],
    [(0, 2, _R2), (1, 3, _R2)],
    [(0, 3, _R3), (1, 2, _R3)],
]


def _distribute_goals(total_gm: int, total_gs: int, wins: int, draws: int, losses: int) -> list[tuple[int, int]]:
    """Distribute GM/GS across W/D/L matches. Returns list of (gs, gc) per match."""
    n = wins + draws + losses
    if n == 0:
        return []
    results = []
    rem_gm = total_gm
    rem_gs = total_gs

    # Assign wins first, then draws, then losses
    for _ in range(wins):
        # allocate a win: score more than concede
        gs = math.ceil(rem_gm / max(wins + draws + losses - len(results), 1))
        gc = max(0, math.floor(rem_gs / max(wins + draws + losses - len(results), 1)))
        gs = max(1, gs)
        if gc >= gs:
            gc = gs - 1
        rem_gm -= gs
        rem_gs -= gc
        results.append((gs, gc))

    for _ in range(draws):
        share = rem_gm // max(draws + losses - (len(results) - wins), 1)
        gs = gc = max(0, share)
        rem_gm -= gs
        rem_gs -= gc
        results.append((gs, gc))

    for _ in range(losses):
        gc = math.ceil(rem_gs / max(losses - (len(results) - wins - draws), 1))
        gs = max(0, math.floor(rem_gm / max(losses - (len(results) - wins - draws), 1)))
        gc = max(1, gc)
        if gs >= gc:
            gs = gc - 1
        rem_gm -= gs
        rem_gs -= gc
        results.append((gs, gc))

    return results


def build_team_matches(
    team_code: str,
    group_codes: list[str],
    standings_map: dict[str, dict],
) -> list[MatchResult]:
    st = standings_map.get(team_code)
    if not st:
        return []

    rounds_played = st["J"]
    wins_left = st["V"]
    draws_left = st["E"]
    losses_left = st["D"]

    scores = _distribute_goals(st["GM"], st["GS"], wins_left, draws_left, losses_left)
    score_iter = iter(scores)

    matches: list[MatchResult] = []
    team_idx = group_codes.index(team_code)

    for round_num, round_matches in enumerate(ROUNDS):
        if round_num >= rounds_played:
            break
        for idx_a, idx_b, match_date in round_matches:
            if idx_a == team_idx:
                try:
                    gs, gc = next(score_iter)
                except StopIteration:
                    break
                result = "W" if gs > gc else ("D" if gs == gc else "L")
                opp = group_codes[idx_b]
                matches.append(MatchResult(
                    date=match_date.isoformat(),
                    opponent_code=opp,
                    home_or_away="home",
                    goals_scored=gs,
                    goals_conceded=gc,
                    competition="FIFA World Cup 2026",
                    result=result,
                ))
            elif idx_b == team_idx:
                try:
                    gs, gc = next(score_iter)
                except StopIteration:
                    break
                result = "W" if gs > gc else ("D" if gs == gc else "L")
                opp = group_codes[idx_a]
                matches.append(MatchResult(
                    date=match_date.isoformat(),
                    opponent_code=opp,
                    home_or_away="away",
                    goals_scored=gs,
                    goals_conceded=gc,
                    competition="FIFA World Cup 2026",
                    result=result,
                ))

    return matches


def main() -> None:
    settings = Settings()
    client = make_gcs_client(settings.gcs_project)
    storage = GCSStorage(settings.gcs_bucket, client)

    with open("data/copa2026_standings.json", encoding="utf-8") as f:
        standings_by_group: dict[str, list[dict]] = json.load(f)

    seeded = skipped = 0
    for group, codes in GROUPS.items():
        group_standings = standings_by_group.get(group, [])
        standings_map = {s["code"]: s for s in group_standings}

        for code in codes:
            gcs_path = f"teams/{code}/form.json"
            cached = storage.download_json(gcs_path)
            if cached:
                try:
                    existing = TeamForm.model_validate(cached)
                    if existing.matches:
                        print(f"SKIP {code}: {len(existing.matches)} matches already")
                        skipped += 1
                        continue
                except Exception:
                    pass

            matches = build_team_matches(code, codes, standings_map)
            if not matches:
                print(f"SKIP {code}: 0 rounds played per standings")
                skipped += 1
                continue

            form = TeamForm(code=code, matches=matches, updated_at=datetime.now())
            storage.upload_json(gcs_path, form.model_dump(mode="json"))
            print(f"SEEDED {code} (Grupo {group}): {form.record} ({len(matches)} matches)")
            seeded += 1

    print(f"\nDone: {seeded} seeded, {skipped} skipped.")


if __name__ == "__main__":
    main()
