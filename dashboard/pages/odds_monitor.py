"""M4: Odds Monitor — current odds + implied probability + value bet detection."""
from __future__ import annotations

from datetime import date

import streamlit as st

from src.collectors.odds import OddsCollector
from src.config import Settings
from src.schemas.match import OddsSnapshot
from src.storage.gcs import GCSStorage


def render(storage: GCSStorage) -> None:
    st.title("💰 Monitor de Odds")
    st.caption(
        "Odds de múltiplos bookmakers com probabilidades implícitas e detecção de value bets."
    )

    today = date.today().isoformat()
    blobs = storage.list_blobs(f"odds/{today}/")

    col_refresh, _ = st.columns([1, 3])
    with col_refresh:
        if st.button("🔄 Buscar Odds Agora", use_container_width=True):
            with st.spinner("Consultando The Odds API..."):
                try:
                    settings = Settings()
                    collector = OddsCollector(settings, storage)
                    snaps = collector.collect_all_copa2026()
                    collector.close()
                    if snaps:
                        st.success(f"{len(snaps)} partidas com odds coletadas.")
                        blobs = storage.list_blobs(f"odds/{today}/")
                    else:
                        st.warning("Nenhuma odd disponível no momento (API sem dados ativos).")
                except Exception as exc:
                    st.error(f"Erro ao buscar odds: {exc}")

    if not blobs:
        st.info(
            f"Nenhuma odds coletada para {today}. "
            "Clique em 'Buscar Odds Agora' ou aguarde o pipeline diário."
        )
        return

    st.markdown(f"**{len(blobs)} partidas com odds disponíveis** para {today}")
    st.markdown("---")

    for blob_path in sorted(blobs):
        raw = storage.download_json(blob_path)
        if not raw:
            continue
        try:
            snap = OddsSnapshot.model_validate(raw)
            _render_odds_row(snap)
        except Exception:
            continue


def _render_odds_row(snap: OddsSnapshot) -> None:
    if not snap.bookmakers:
        return

    implied = snap.average_implied()
    parts = snap.match_key.split("_")
    label = f"{parts[0]} vs {parts[1]}" if len(parts) == 2 else snap.match_key

    home_pct = f"{implied['home'] * 100:.1f}%"
    draw_pct = f"{implied['draw'] * 100:.1f}%"
    away_pct = f"{implied['away'] * 100:.1f}%"
    header = f"⚽ {label}  |  🏠 {home_pct} — 🤝 {draw_pct} — ✈️ {away_pct}"

    with st.expander(header):
        import pandas as pd

        rows = []
        for bm_name, bm in snap.bookmakers.items():
            rows.append({
                "Bookmaker": bm_name,
                "Casa (odds)": f"{bm.home_win:.2f}",
                "Empate (odds)": f"{bm.draw:.2f}",
                "Fora (odds)": f"{bm.away_win:.2f}",
                "Prob. Casa": f"{bm.implied_home * 100:.1f}%",
                "Prob. Empate": f"{bm.implied_draw * 100:.1f}%",
                "Prob. Fora": f"{bm.implied_away * 100:.1f}%",
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        margin = sum(implied.values()) - 1.0
        if margin > 0:
            st.caption(f"Margem média dos bookmakers: {margin * 100:.1f}%")
