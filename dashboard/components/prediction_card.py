"""Scoreline prediction card with value bet highlighting."""
from __future__ import annotations

import streamlit as st

from src.schemas.match import MatchAnalysis, ScorelinePrediction


def render_prediction_cards(analysis: MatchAnalysis) -> None:
    st.subheader("🔮 Placares Mais Prováveis")

    for i, pred in enumerate(analysis.scoreline_predictions):
        _render_single_card(pred, rank=i + 1)

    if analysis.value_bets:
        count = len(analysis.value_bets)
        st.success(
            f"⭐ **{count} value bet(s) identificado(s)**"
            " — probabilidade do modelo supera o mercado em >5pp"
        )

    st.caption(
        f"Confiança: **{analysis.confidence_level.upper()}** | "
        f"Gerado: {analysis.generated_at.strftime('%d/%m %H:%M')} | "
        f"Cache até: {analysis.cached_until.strftime('%d/%m %H:%M')}"
    )


def _render_single_card(pred: ScorelinePrediction, rank: int) -> None:
    medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
    pct = f"{pred.probability * 100:.1f}%"

    value_badge = ""
    if pred.is_value_bet and pred.value_pp is not None:
        value_badge = f" ⭐ VALUE +{pred.value_pp:.1f}pp"

    market_str = ""
    if pred.market_implied is not None:
        market_str = f" (mercado: {pred.market_implied * 100:.1f}%)"

    with st.container(border=True):
        col_score, col_pct, col_text = st.columns([2, 1, 3])
        with col_score:
            st.markdown(f"### {medal} {pred.scoreline}")
        with col_pct:
            color = "green" if pred.is_value_bet else "blue"
            html = f"<h3 style='color:{color}'>{pct}{value_badge}</h3>{market_str}"
            st.markdown(html, unsafe_allow_html=True)
        with col_text:
            st.markdown(f"*{pred.narrative}*")


def render_outcome_summary(analysis: MatchAnalysis) -> None:
    st.subheader("📊 Probabilidades de Resultado")
    summary = analysis.outcome_summary
    col_a, col_d, col_b = st.columns(3)

    with col_a:
        st.metric(
            f"🏆 {analysis.team_a_name} Vence",
            f"{summary.get('team_a_wins', 0) * 100:.1f}%",
        )
    with col_d:
        st.metric("⚖️ Empate", f"{summary.get('draw', 0) * 100:.1f}%")
    with col_b:
        st.metric(
            f"🏆 {analysis.team_b_name} Vence",
            f"{summary.get('team_b_wins', 0) * 100:.1f}%",
        )
