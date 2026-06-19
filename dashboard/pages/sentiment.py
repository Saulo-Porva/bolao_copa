"""M5: Sentiment Monitor — heatmap and time series of squad morale."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from dashboard.components.sentiment_gauge import (
    render_sentiment_dimensions,
    render_sentiment_gauge,
    render_sentiment_history_chart,
)
from src.schemas.sentiment import SentimentHistory
from src.storage.gcs import GCSStorage


def render(storage: GCSStorage) -> None:
    st.title("🧠 Sentimento de Vestiário")
    st.caption("Score de morale por seleção com histórico temporal e alertas detectados via LLM.")

    teams = _load_teams(storage)
    if not teams:
        st.error("Nenhuma seleção encontrada.")
        return

    st.subheader("🗺️ Panorama Geral")
    _render_heatmap(storage, teams)

    st.markdown("---")
    st.subheader("🔍 Análise Individual")

    options = {
        f"{t['name_pt']} ({t['code']})": t
        for t in sorted(teams, key=lambda x: x["name_pt"])
    }
    selected_label = st.selectbox("Selecionar seleção", list(options.keys()))
    team = options[selected_label]
    code = team["code"]

    raw = storage.download_json(f"teams/{code}/sentiment/history.json")
    if not raw:
        st.info("Histórico de sentimento não disponível para esta seleção.")
        return

    try:
        history = SentimentHistory.model_validate(raw)
    except Exception as exc:
        st.error(f"Erro ao carregar sentimento: {exc}")
        return

    col_gauge, col_dims = st.columns([1, 2])
    with col_gauge:
        render_sentiment_gauge(team["name_pt"], history)
    with col_dims:
        if history.latest():
            render_sentiment_dimensions(history.latest())

    st.subheader("📈 Evolução do Sentimento (últimos 30 dias)")
    render_sentiment_history_chart(history)

    if history.records:
        latest = history.latest()
        if latest and latest.alerts:
            st.subheader("⚠️ Alertas Recentes")
            for alert in latest.alerts:
                st.warning(alert)

        with st.expander("Ver histórico completo"):
            import pandas as pd
            rows = [
                {
                    "Data": str(r.date),
                    "Score": f"{r.overall_score:.1f}",
                    "Coesão": f"{r.dimensions.cohesion:.1f}",
                    "Pressão Mídia": f"{r.dimensions.media_pressure:.1f}",
                    "Motivação": f"{r.dimensions.motivation:.1f}",
                    "Artigos": r.articles_analyzed,
                    "Qualidade": r.data_quality,
                }
                for r in reversed(history.records)
            ]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _render_heatmap(storage: GCSStorage, teams: list[dict]) -> None:
    scores: list[dict] = []
    for team in teams:
        raw = storage.download_json(f"teams/{team['code']}/sentiment/history.json")
        if not raw:
            continue
        try:
            history = SentimentHistory.model_validate(raw)
            latest = history.latest()
            if latest:
                scores.append({
                    "Seleção": team["name_pt"],
                    "Score": latest.overall_score,
                    "Trend": history.trend(),
                    "Alertas": len(latest.alerts),
                    "Data": str(latest.date),
                })
        except Exception:
            continue

    if not scores:
        st.info("Nenhum dado de sentimento disponível ainda. Execute o pipeline.")
        return

    import pandas as pd

    df = pd.DataFrame(scores).sort_values("Score", ascending=False)
    st.dataframe(
        df.style.background_gradient(subset=["Score"], cmap="RdYlGn", vmin=0, vmax=10),
        use_container_width=True,
        hide_index=True,
    )


def _load_teams(storage: GCSStorage) -> list[dict]:
    path = Path("data/teams_48.json")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return storage.download_json("_meta/teams_48.json") or []
