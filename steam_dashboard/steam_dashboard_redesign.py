"""Steam indie insight: run this entrypoint with Streamlit.

python -m streamlit run steam_dashboard_redesign.py
Keep the adjacent steam_insight package with this file when sharing.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from steam_insight.analysis import overview_stats
from steam_insight.components import render_identity
from steam_insight.config import ALL_GENRES, PATTERN_VIEW, REPORT_VIEW, THRESHOLDS
from steam_insight.data import file_signature, find_data_dir, load_data, select_genre
from steam_insight.paths import AppPaths
from steam_insight.styles import TOOLTIP_STYLE
from steam_insight.views import (
    render_data_notes, render_game_report, render_overview, render_success_pattern,
)


st.set_page_config(
    page_title="Steam indie insight · 첫 30일의 신호",
    page_icon=":material/sports_esports:",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.html(TOOLTIP_STYLE)

paths = AppPaths.from_app(__file__)
render_identity(paths)

try:
    data_dir = find_data_dir(paths)
    rules = tuple((name, spec[1]) for name, spec in THRESHOLDS.items())
    data = load_data(str(data_dir), file_signature(data_dir), rules)
except (OSError, ValueError, pd.errors.ParserError, UnicodeError) as error:
    st.error(str(error), icon=":material/error:")
    st.stop()

with st.sidebar:
    st.space("small")
    st.caption("EXPLORE / 분석 범위")
    selected_genre = st.selectbox("장르", [ALL_GENRES, *data.genre_options], key="genre")

filtered_games, filtered_checkpoint = select_genre(data, selected_genre)
available = filtered_games.loc[
    filtered_games["appid"].isin(filtered_checkpoint["appid"])
].sort_values("name")
game_names = dict(zip(available["appid"], available["name"]))
game_options = list(game_names)
preferred = available.loc[available["name"].eq("Ghost Exile"), "appid"].tolist()
if st.session_state.get("selected_game") not in game_options:
    st.session_state["selected_game"] = preferred[0] if preferred else (
        game_options[0] if game_options else None
    )

with st.sidebar:
    selected_game_id = st.selectbox(
        "분석할 게임", game_options, format_func=lambda value: game_names.get(value, str(value)),
        key="selected_game", placeholder="30일 데이터가 있는 게임을 선택하세요",
    )
    st.caption(f"검색 가능한 게임 {len(available):,}개 · 이름을 입력해 찾아보세요")
    st.space("small")
    st.caption("ABOUT / 데이터 안내")
    if pd.notna(data.last_date):
        st.caption(f"일별 관측 마지막 날짜 · {data.last_date:%Y.%m.%d}")
    st.caption("표본 내 관찰 결과이며, 모든 Steam 게임을 대표하지는 않습니다.")

is_pattern_view = st.session_state.get("view", REPORT_VIEW) == PATTERN_VIEW
stats = data.overview if is_pattern_view or selected_genre == ALL_GENRES else (
    overview_stats(filtered_games, filtered_checkpoint)
)
st.space("small")
st.caption("AT A GLANCE / 전체 게임 · 고정 분석 범위" if is_pattern_view
           else f"AT A GLANCE / {selected_genre} · 현재 분석 범위")
render_overview(stats, paths)

st.space("small")
view = st.segmented_control(
    "분석 화면", [REPORT_VIEW, PATTERN_VIEW], default=REPORT_VIEW,
    required=True, label_visibility="collapsed", key="view",
)

if view == REPORT_VIEW:
    render_game_report(data, available, filtered_checkpoint, selected_game_id, game_names)
elif view == PATTERN_VIEW:
    render_success_pattern(data)

render_data_notes()
