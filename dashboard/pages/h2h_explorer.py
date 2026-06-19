"""M3: H2H Explorer — historical head-to-head between any two teams."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from src.schemas.match import H2HHistory
from src.storage.gcs import GCSStorage


def render(storage: GCSStorage) -> None:
    st.title("⚔️ H2H Explorer")
    st.caption("Histórico de confrontos diretos entre qualquer par de seleções.")

    teams = _load_teams(storage)
    if not teams:
        st.error("Nenhuma seleção encontrada.")
        return

    options = {
        f"{t['name_pt']} ({t['code']})": t
        for t in sorted(teams, key=lambda x: x["name_pt"])
    }
    col1, col2 = st.columns(2)
    with col1:
        label_a = st.selectbox("Seleção A", list(options.keys()), key="h2h_a")
    with col2:
        label_b = st.selectbox("Seleção B", list(options.keys()), index=1, key="h2h_b")

    team_a = options[label_a]
    team_b = options[label_b]

    if team_a["code"] == team_b["code"]:
        st.warning("Selecione duas seleções diferentes.")
        return

    competition_filter = st.multiselect(
        "Filtrar por competição",
        ["Copa do Mundo FIFA", "Eliminatórias", "Amistosos", "Todos"],
        default=["Todos"],
    )

    key = H2HHistory.make_key(team_a["code"], team_b["code"])
    raw = storage.download_json(f"matches/h2h/{key}.json")

    if not raw:
        st.info(f"Nenhum histórico encontrado para {team_a['name_pt']} vs {team_b['name_pt']}.")
        st.caption("Execute o pipeline para coletar dados H2H via football-data.org.")
        return

    try:
        h2h = H2HHistory.model_validate(raw)
    except Exception as exc:
        st.error(f"Erro ao carregar H2H: {exc}")
        return

    matches = h2h.matches
    if "Todos" not in competition_filter and competition_filter:
        keywords = {
            "Copa do Mundo FIFA": "World Cup",
            "Eliminatórias": "Qualifying",
            "Amistosos": "Friendly",
        }
        keep = set()
        for label in competition_filter:
            keep.add(keywords.get(label, label))
        matches = [m for m in matches if any(k.lower() in m.competition.lower() for k in keep)]

    name_a = team_a["name_pt"]
    name_b = team_b["name_pt"]

    col_a, col_draw, col_b = st.columns(3)
    col_a.metric(f"✅ Vitórias {name_a}", h2h.team_a_wins)
    col_draw.metric("🟡 Empates", h2h.draws)
    col_b.metric(f"✅ Vitórias {name_b}", h2h.team_b_wins)

    st.caption(f"Placares mais frequentes: **{', '.join(h2h.common_scorelines) or 'N/A'}**")
    st.markdown("---")

    if not matches:
        st.info("Nenhuma partida encontrada com os filtros selecionados.")
        return

    import pandas as pd

    rows = []
    for m in sorted(matches, key=lambda x: x.date, reverse=True):
        if m.score_a > m.score_b:
            winner = name_a
        elif m.score_b > m.score_a:
            winner = name_b
        else:
            winner = "Empate"
        rows.append({
            "Data": str(m.date),
            "Competição": m.competition,
            "Fase": m.stage or "—",
            "Placar": f"{name_a} {m.score_a}x{m.score_b} {name_b}",
            "Resultado": winner,
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.caption(f"Total: {len(matches)} partidas exibidas | Dados: football-data.org")


def _load_teams(storage: GCSStorage) -> list[dict]:
    path = Path("data/teams_48.json")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return storage.download_json("_meta/teams_48.json") or []
