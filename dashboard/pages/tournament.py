"""M6: Tournament Table — WC2026 standings, top scorers, historical champions."""
from __future__ import annotations

import streamlit as st

from src.storage.gcs import GCSStorage

_WC_CHAMPIONS = [
    (2022, "Argentina"), (2018, "França"), (2014, "Alemanha"), (2010, "Espanha"),
    (2006, "Itália"), (2002, "Brasil"), (1998, "França"), (1994, "Brasil"),
    (1990, "Alemanha Ocidental"), (1986, "Argentina"), (1982, "Itália"),
    (1978, "Argentina"), (1974, "Alemanha Ocidental"), (1970, "Brasil"),
    (1966, "Inglaterra"), (1962, "Brasil"), (1958, "Brasil"), (1954, "Alemanha Ocidental"),
    (1950, "Uruguai"), (1938, "Itália"), (1934, "Itália"), (1930, "Uruguai"),
]


def render(storage: GCSStorage) -> None:
    st.title("🏆 Copa do Mundo 2026")

    tab_table, tab_scorers, tab_history = st.tabs([
        "📋 Tabela de Grupos",
        "⚽ Artilheiros",
        "🏅 Campeões Históricos",
    ])

    with tab_table:
        _render_group_table(storage)

    with tab_scorers:
        _render_top_scorers(storage)

    with tab_history:
        _render_champions()


def _render_group_table(storage: GCSStorage) -> None:
    st.subheader("Tabela de Grupos — Copa 2026")
    raw = storage.download_json("wc2026/standings.json")
    if not raw:
        st.info(
            "Tabela de grupos ainda não disponível. "
            "Os jogos da Copa 2026 começam em junho de 2026."
        )
        st.caption("Os dados serão coletados automaticamente assim que os jogos iniciarem.")
        return

    import pandas as pd
    groups = raw if isinstance(raw, dict) else {}
    for group_name, teams in groups.items():
        st.subheader(f"Grupo {group_name}")
        st.dataframe(pd.DataFrame(teams), use_container_width=True, hide_index=True)


def _render_top_scorers(storage: GCSStorage) -> None:
    st.subheader("Artilheiros da Copa 2026")
    raw = storage.download_json("wc2026/top_scorers.json")
    if not raw:
        st.info("Artilheiros disponíveis quando os jogos iniciarem (junho 2026).")

    st.markdown("---")
    st.subheader("Artilheiros Históricos de Copa do Mundo")
    history_raw = storage.download_json("history/wc_top_scorers.json")
    if history_raw and isinstance(history_raw, list):
        import pandas as pd
        st.dataframe(pd.DataFrame(history_raw[:20]), use_container_width=True, hide_index=True)
    else:
        st.info("Execute o script de inicialização histórica: `python scripts/init_historical.py`")


def _render_champions() -> None:
    st.subheader("🏆 Campeões da Copa do Mundo (1930–2022)")
    import pandas as pd

    df = pd.DataFrame(_WC_CHAMPIONS, columns=["Ano", "Campeão"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    champions_count: dict[str, int] = {}
    for _, champ in _WC_CHAMPIONS:
        champ_key = champ.replace("Alemanha Ocidental", "Alemanha")
        champions_count[champ_key] = champions_count.get(champ_key, 0) + 1

    st.subheader("Total de Títulos por País")
    count_df = pd.DataFrame(
        sorted(champions_count.items(), key=lambda x: x[1], reverse=True),
        columns=["País", "Títulos"],
    )
    st.bar_chart(count_df.set_index("País"))
