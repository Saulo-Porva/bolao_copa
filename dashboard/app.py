"""Streamlit entry point — GCS auth, navigation, shared state."""
from __future__ import annotations

import streamlit as st

from src.config import Settings
from src.storage.gcs import GCSStorage, make_gcs_client, make_gcs_client_from_streamlit

st.set_page_config(
    page_title="Copa 2026 Analyzer",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_gcs_storage() -> GCSStorage:
    settings = _get_settings()
    if "gcp_service_account" in st.secrets:
        client = make_gcs_client_from_streamlit(dict(st.secrets["gcp_service_account"]))
    else:
        client = make_gcs_client(settings.gcs_project)
    return GCSStorage(settings.gcs_bucket, client)


@st.cache_resource
def _get_settings() -> Settings:
    return Settings()


@st.cache_data(ttl=300)
def load_teams() -> list[dict]:
    import json
    from pathlib import Path

    path = Path("data/teams_48.json")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    raw = get_gcs_storage().download_json("_meta/teams_48.json")
    return raw or []


def main() -> None:
    st.sidebar.title("⚽ Copa 2026 Analyzer")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Módulo",
        [
            "🔮 Análise de Partida",
            "🏴 Perfil de Seleção",
            "⚔️ H2H Explorer",
            "💰 Monitor de Odds",
            "🧠 Sentimento",
            "🏆 Tabela Copa 2026",
        ],
    )

    storage = get_gcs_storage()
    raw = storage.download_json("_meta/last_updated.json")
    if raw:
        st.sidebar.caption(f"Dados atualizados: {raw.get('updated_at', 'N/A')[:16]}")

    if page == "🔮 Análise de Partida":
        from dashboard.pages.match_analyzer import render
        render(storage, _get_settings())
    elif page == "🏴 Perfil de Seleção":
        from dashboard.pages.team_profile import render
        render(storage)
    elif page == "⚔️ H2H Explorer":
        from dashboard.pages.h2h_explorer import render
        render(storage)
    elif page == "💰 Monitor de Odds":
        from dashboard.pages.odds_monitor import render
        render(storage)
    elif page == "🧠 Sentimento":
        from dashboard.pages.sentiment import render
        render(storage)
    elif page == "🏆 Tabela Copa 2026":
        from dashboard.pages.tournament import render
        render(storage)


if __name__ == "__main__":
    main()
