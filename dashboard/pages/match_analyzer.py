"""M1: Match Analyzer — Copa 2026 fixture selection + Claude Sonnet 4.6 prediction."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from dashboard.components.prediction_card import render_outcome_summary, render_prediction_cards
from dashboard.components.sentiment_gauge import render_sentiment_gauge
from src.analyzers.match_analyzer import MatchAnalyzer
from src.analyzers.sentiment import SentimentAnalyzer
from src.collectors.odds import OddsCollector
from src.config import Settings
from src.schemas.match import H2HHistory
from src.schemas.team import TeamForm, TeamSquad
from src.storage.gcs import GCSStorage


def _load_teams(storage: GCSStorage) -> dict[str, dict]:
    path = Path("data/teams_48.json")
    if path.exists():
        raw = json.loads(path.read_text(encoding="utf-8"))
    else:
        raw = storage.download_json("_meta/teams_48.json") or []
    return {t["code"]: t for t in raw}


def _load_fixtures(storage: GCSStorage) -> list[dict]:
    path = Path("data/copa2026_fixtures.json")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return storage.download_json("_meta/copa2026_fixtures.json") or []


def _load_form(storage: GCSStorage, code: str) -> TeamForm | None:
    raw = storage.download_json(f"teams/{code}/form.json")
    if not raw:
        return None
    try:
        return TeamForm.model_validate(raw)
    except Exception:
        return None


def _load_squad(storage: GCSStorage, code: str) -> TeamSquad | None:
    raw = storage.download_json(f"teams/{code}/squad.json")
    if not raw:
        return None
    try:
        return TeamSquad.model_validate(raw)
    except Exception:
        return None


def _load_h2h(storage: GCSStorage, code_a: str, code_b: str) -> H2HHistory | None:
    key = H2HHistory.make_key(code_a, code_b)
    raw = storage.download_json(f"matches/h2h/{key}.json")
    if not raw:
        return None
    try:
        return H2HHistory.model_validate(raw)
    except Exception:
        return None


def render(storage: GCSStorage, settings: Settings) -> None:
    st.title("🔮 Análise de Partida — Copa 2026")
    st.caption("Selecione o confronto e obtenha predição de placares com Claude Sonnet 4.6.")

    teams_map = _load_teams(storage)
    if not teams_map:
        st.error("Nenhuma seleção encontrada. Execute o pipeline primeiro.")
        return

    fixtures = _load_fixtures(storage)

    mode = st.radio(
        "Modo de seleção",
        ["🏆 Confronto Copa 2026", "🔧 Seleção Livre"],
        horizontal=True,
    )

    code_a: str | None = None
    code_b: str | None = None
    phase = "Group Stage"

    if mode == "🏆 Confronto Copa 2026" and fixtures:
        group_labels = [
            f"Grupo {g['group']} — {' · '.join(g['teams'])}"
            for g in fixtures
        ]
        group_idx = st.selectbox("Selecione o grupo", range(len(group_labels)),
                                  format_func=lambda i: group_labels[i])
        selected_group = fixtures[group_idx]

        match_labels = [m["label"] for m in selected_group["matches"]]
        match_idx = st.selectbox("Selecione o confronto", range(len(match_labels)),
                                  format_func=lambda i: match_labels[i])
        selected_match = selected_group["matches"][match_idx]

        code_a = selected_match["home"]
        code_b = selected_match["away"]

        team_a = teams_map.get(code_a, {"code": code_a, "name_pt": code_a})
        team_b = teams_map.get(code_b, {"code": code_b, "name_pt": code_b})

        col1, col2, col3 = st.columns([2, 1, 2])
        col1.metric("Casa", team_a["name_pt"])
        col2.markdown("<h3 style='text-align:center;margin-top:20px'>VS</h3>",
                      unsafe_allow_html=True)
        col3.metric("Fora", team_b["name_pt"])

    else:
        team_options = {
            f"{t['name_pt']} ({t['code']})": t
            for t in sorted(teams_map.values(), key=lambda x: x["name_pt"])
        }
        col1, col2 = st.columns(2)
        with col1:
            label_a = st.selectbox("Seleção A (Casa)", list(team_options.keys()), index=0)
        with col2:
            label_b = st.selectbox("Seleção B (Fora)", list(team_options.keys()), index=1)
        team_a = team_options[label_a]
        team_b = team_options[label_b]
        code_a = team_a["code"]
        code_b = team_b["code"]

        phase = st.selectbox(
            "Fase",
            ["Group Stage", "Round of 16", "Quarter-final", "Semi-final", "Final"],
        )

    if code_a and code_b and code_a == code_b:
        st.warning("Selecione duas seleções diferentes.")
        return

    if not (code_a and code_b):
        return

    st.markdown("---")

    if st.button("🔮 Analisar Partida", type="primary", use_container_width=True):
        with st.spinner("Carregando dados e gerando análise com Claude Sonnet 4.6..."):
            form_a = _load_form(storage, code_a)
            form_b = _load_form(storage, code_b)

            if not form_a or not form_b:
                st.warning(
                    "Dados de forma recente não disponíveis — análise será baseada em "
                    "dados históricos e sentimento. Execute o pipeline para enriquecer a predição."
                )

            squad_a = _load_squad(storage, code_a)
            squad_b = _load_squad(storage, code_b)
            h2h = _load_h2h(storage, code_a, code_b)

            sent_analyzer = SentimentAnalyzer(settings, storage)
            sentiment_a = sent_analyzer.load_history(code_a)
            sentiment_b = sent_analyzer.load_history(code_b)

            odds_collector = OddsCollector(settings, storage)
            match_key = H2HHistory.make_key(code_a, code_b)
            odds = odds_collector.collect_match_odds(match_key)

            analyzer = MatchAnalyzer(settings, storage)
            try:
                analysis = analyzer.analyze(
                    team_a_code=code_a,
                    team_b_code=code_b,
                    team_a_name=team_a["name_pt"],
                    team_b_name=team_b["name_pt"],
                    form_a=form_a,
                    form_b=form_b,
                    squad_a=squad_a,
                    squad_b=squad_b,
                    sentiment_a=sentiment_a,
                    sentiment_b=sentiment_b,
                    h2h=h2h,
                    odds=odds,
                    phase=phase,
                )
            except Exception as exc:
                st.error(f"Erro na análise: {exc}")
                return

        st.markdown("---")
        render_outcome_summary(analysis)
        st.markdown("---")
        render_prediction_cards(analysis)

        st.markdown("---")
        st.subheader("🧠 Sentimento de Vestiário")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            render_sentiment_gauge(team_a["name_pt"], sentiment_a)
        with col_s2:
            render_sentiment_gauge(team_b["name_pt"], sentiment_b)

        if analysis.llm_reasoning:
            st.markdown("---")
            st.subheader("💭 Raciocínio do Analista")
            st.info(analysis.llm_reasoning)

        st.markdown("---")
        st.subheader("📡 Sinais Utilizados")
        with st.expander("Ver detalhes dos sinais"):
            st.json(analysis.signals_used)
