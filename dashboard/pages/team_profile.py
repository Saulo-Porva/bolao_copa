"""M2: Team Profile — form, squad status, stats."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from src.schemas.team import TeamForm, TeamSquad, TeamStats
from src.storage.gcs import GCSStorage


def render(storage: GCSStorage) -> None:
    st.title("🏴 Perfil de Seleção")

    teams = _load_teams(storage)
    if not teams:
        st.error("Nenhuma seleção encontrada.")
        return

    options = {
        f"{t['name_pt']} ({t['code']})": t
        for t in sorted(teams, key=lambda x: x["name_pt"])
    }
    selected_label = st.selectbox("Selecionar seleção", list(options.keys()))
    team = options[selected_label]
    code = team["code"]

    col_info, col_rank = st.columns([3, 1])
    with col_info:
        st.subheader(f"🌍 {team['name_pt']}")
        st.caption(
            f"Confederação: {team.get('confederation', 'N/A')}"
            f" | Grupo Copa 2026: {team.get('group', 'TBD')}"
        )
    with col_rank:
        st.metric("Ranking FIFA", team.get("fifa_ranking", "N/A"))

    st.markdown("---")

    tab_form, tab_squad, tab_stats = st.tabs(["📈 Forma Recente", "👥 Elenco", "📊 Estatísticas"])

    with tab_form:
        _render_form(storage, code)

    with tab_squad:
        _render_squad(storage, code)

    with tab_stats:
        _render_stats(storage, code)


def _render_form(storage: GCSStorage, code: str) -> None:
    raw = storage.download_json(f"teams/{code}/form.json")
    if not raw:
        st.info("Dados de forma não disponíveis. Execute o pipeline.")
        return
    try:
        form = TeamForm.model_validate(raw)
    except Exception as exc:
        st.error(f"Erro ao carregar forma: {exc}")
        return

    st.subheader(f"Últimos {len(form.matches)} jogos: **{form.record}**")
    col1, col2, col3 = st.columns(3)
    col1.metric("Média gols marcados", f"{form.avg_goals_scored:.1f}")
    col2.metric("Média gols sofridos", f"{form.avg_goals_conceded:.1f}")
    col3.metric("Atualizado", raw.get("updated_at", "N/A")[:10])

    rows = []
    for m in reversed(form.matches):
        icon = {"W": "✅", "D": "🟡", "L": "❌"}[m.result]
        rows.append({
            "": icon,
            "Data": str(m.date),
            "Adversário": m.opponent_code,
            "Local": m.home_or_away,
            "Placar": f"{m.goals_scored}x{m.goals_conceded}",
            "Competição": m.competition,
        })

    import pandas as pd
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _render_squad(storage: GCSStorage, code: str) -> None:
    raw = storage.download_json(f"teams/{code}/squad.json")
    if not raw:
        st.info("Elenco não disponível.")
        return
    try:
        squad = TeamSquad.model_validate(raw)
    except Exception as exc:
        st.error(f"Erro ao carregar elenco: {exc}")
        return

    if squad.key_absences:
        st.error(f"⚠️ Ausências: {', '.join(squad.key_absences)}")

    import pandas as pd

    pos_order = {"GK": 0, "DF": 1, "MF": 2, "FW": 3}
    status_icon = {"fit": "🟢", "doubtful": "🟡", "injured": "🔴", "suspended": "🟠"}

    players_sorted = sorted(squad.players, key=lambda p: (pos_order.get(p.position, 9), p.name))
    rows = [
        {
            "": status_icon.get(p.status, "⚪"),
            "Nome": p.name,
            "Pos": p.position,
            "Clube": p.club,
            "Status": p.status,
            "Obs": p.notes or "",
        }
        for p in players_sorted
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.caption(f"Atualizado: {raw.get('updated_at', 'N/A')[:16]}")


def _render_stats(storage: GCSStorage, code: str) -> None:
    raw = storage.download_json(f"teams/{code}/stats.json")
    if not raw:
        st.info("Estatísticas não disponíveis.")
        return
    try:
        stats = TeamStats.model_validate(raw)
    except Exception as exc:
        st.error(f"Erro ao carregar stats: {exc}")
        return

    if stats.top_scorers:
        st.subheader("⚽ Artilheiros")
        import pandas as pd
        rows = [
            {"Nome": s.name, "Gols": s.goals, "Assistências": s.assists, "Posição": s.position}
            for s in stats.top_scorers
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if stats.top_passers:
        st.subheader("🎯 Principais Criadores")
        rows = [
            {"Nome": p.name, "Passes": p.passes, "Passes-chave": p.key_passes}
            for p in stats.top_passers
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.metric("Gols sofridos (temporada)", stats.goals_conceded_total)


def _load_teams(storage: GCSStorage) -> list[dict]:
    path = Path("data/teams_48.json")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return storage.download_json("_meta/teams_48.json") or []
