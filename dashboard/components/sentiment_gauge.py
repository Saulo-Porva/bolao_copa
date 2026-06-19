"""Sentiment gauge component with trend and alert display."""
from __future__ import annotations

import streamlit as st

from src.schemas.sentiment import SentimentHistory, SentimentRecord


def render_sentiment_gauge(team_name: str, history: SentimentHistory | None) -> None:
    if not history or not history.latest():
        st.info(f"Sem dados de sentimento para {team_name}")
        return

    latest = history.latest()
    trend = history.trend()
    score = latest.overall_score

    color = _score_color(score)
    label = _score_label(score)

    st.markdown(
        f"""
        <div style="border:1px solid #ddd; border-radius:8px; padding:12px; text-align:center">
            <div style="font-size:0.85rem; color:#666">{team_name} — Sentimento de Vestiário</div>
            <div style="font-size:2.5rem; font-weight:bold; color:{color}">{score:.1f}</div>
            <div style="font-size:1rem">{trend} {label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if latest.alerts:
        for alert in latest.alerts:
            st.warning(f"⚠️ {alert}")

    if latest.data_quality == "insufficient":
        st.caption("⚠️ Dados insuficientes (< 3 artigos coletados)")


def render_sentiment_dimensions(record: SentimentRecord) -> None:
    dims = record.dimensions
    st.caption("Dimensões de sentimento:")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🤝 Coesão", f"{dims.cohesion:.1f}/10")
        st.metric("🎯 Motivação", f"{dims.motivation:.1f}/10")
    with col2:
        st.metric("📰 Pressão Mídia", f"{dims.media_pressure:.1f}/10")
        st.metric("👔 Confiança no Técnico", f"{dims.coach_confidence:.1f}/10")


def render_sentiment_history_chart(history: SentimentHistory) -> None:
    if len(history.records) < 2:
        st.caption("Histórico insuficiente para gráfico (mínimo 2 dias)")
        return

    import pandas as pd

    df = pd.DataFrame([
        {"Data": r.date.isoformat(), "Sentimento": r.overall_score}
        for r in history.records[-30:]
    ])
    st.line_chart(df.set_index("Data"))


def _score_color(score: float) -> str:
    if score >= 7:
        return "#28a745"
    if score >= 4:
        return "#ffc107"
    return "#dc3545"


def _score_label(score: float) -> str:
    if score >= 8:
        return "Excelente"
    if score >= 6.5:
        return "Positivo"
    if score >= 4.5:
        return "Neutro"
    if score >= 3:
        return "Negativo"
    return "Crítico"
