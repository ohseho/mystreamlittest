"""Report and success-pattern views, independent of the entrypoint location."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .analysis import (
    Overview, format_value, outcome_label, percent_or_dash,
    signal_score, signal_summary, split_values,
)
from .charts import cohort_chart, trajectory_chart
from .components import attainment_html, dashboard_metric
from .config import BLUE, FEATURE_DETAILS, MINT, THRESHOLDS
from .data import DashboardData, daily_for_game
from .paths import AppPaths


def render_game_report(
    data: DashboardData,
    available: pd.DataFrame,
    filtered_checkpoint: pd.DataFrame,
    selected_game_id: str | None,
    game_names: dict[str, str],
) -> None:
    game_options = list(game_names)
    selected_rows = filtered_checkpoint.loc[filtered_checkpoint["appid"].eq(selected_game_id)]
    if selected_rows.empty:
        st.info("이 범위에는 출시 30일 데이터가 있는 게임이 없습니다. 다른 장르를 선택해 주세요.")
    else:
        record = selected_rows.iloc[0]
        game = available.loc[available["appid"].eq(selected_game_id)].iloc[0]
        score = signal_score(record)
        pass_count = int(record["pass_count"])
        with st.container(border=True):
            heading, store = st.columns([3, 1], vertical_alignment="center")
            with heading:
                st.caption("GAME SPOTLIGHT / 선택 게임 리포트")
                st.subheader(game["name"])
                release_text = game["release"].strftime("%Y.%m.%d") if pd.notna(game["release"]) else "날짜 미확인"
                developer = str(game.get("developers", ""))
                st.caption(f"출시 {release_text}" + (f" · {developer}" if developer and developer != "nan" else ""))
            with store:
                st.link_button("Steam에서 보기", f"https://store.steampowered.com/app/{selected_game_id}/",
                               icon=":material/open_in_new:", width="stretch")
            with st.container(horizontal=True, vertical_alignment="center"):
                outcome = game["success"]
                st.badge(f"최종 성과 · {outcome_label(outcome)}",
                         color="green" if outcome == 1 else "gray",
                         icon=":material/flag:")
                for tag in split_values(game.get("top_tags", game.get("genres")), limit=3):
                    st.badge(tag, color="gray")

        left, right = st.columns([1.7, 1], gap="medium")
        with left:
            with st.container(border=True, height="stretch"):
                st.subheader("다섯 가지 성장 신호", icon=":material/equalizer:")
                st.caption("게임 출시 후 30일 기준 데이터")
                st.html(attainment_html(record))
                st.caption("100%", text_alignment="right")
                st.caption("기준 대비 달성도", text_alignment="center")
                st.caption("막대 왼쪽에는 실제 값·달성도를, 오른쪽에는 기준값을 표시합니다. 막대는 최대 100%이며, 문구와 툴팁에는 100%를 넘는 실제 달성도도 표시합니다.")
        with right:
            with st.container(border=True, height="stretch"):
                st.caption("SIGNAL SUMMARY / 한눈에 보기")
                st.metric("30일 기준 충족", f"{pass_count} / 5",
                          icon=":material/task_alt:")
                st.metric("성공률", f"{score:.1f}%",
                          help="기준 충족마다 16%p를 더합니다. 기준 초과 달성 시 지표당 최대 4%p를 추가합니다. 미관측 지표는 미달로 처리하며 가산하지 않습니다. 합계 최대 100%입니다.")
                st.markdown(signal_summary(record))
                st.caption("기준으로 환산한 참고 성공률이며, 실제 성공 확률을 추정한 값은 아닙니다.")

        with st.container(border=True):
            st.subheader("첫날부터 이어진 플레이", icon=":material/show_chart:")
            st.caption("플레이어와 스트리밍 반응을 서로 다른 축의 차트로 확인하세요.")
            controls = st.columns([1, 1.7, 1], vertical_alignment="bottom")
            with controls[0]:
                period = st.segmented_control("관측 기간", [30, 60, 90], default=90, required=True,
                                              format_func=lambda value: f"{value}일", key="period")
            with controls[1]:
                comparison_options = [None, *[value for value in game_options if value != selected_game_id]]
                if st.session_state.get("comparison") not in comparison_options:
                    st.session_state["comparison"] = None
                comparison_id = st.selectbox("비교할 게임", comparison_options, key="comparison",
                                              format_func=lambda value: "비교 없이 보기" if value is None else game_names[value])
            with controls[2]:
                smooth = st.toggle("7일 이동평균", key="smooth", value=False)
            selected_daily = daily_for_game(data, selected_game_id, period)
            compare_daily = daily_for_game(data, comparison_id, period) if comparison_id else None
            if comparison_id:
                st.caption(f"선택 게임 · {game_names[selected_game_id]} / 비교 게임 · {game_names[comparison_id]}")
            for col, field, title, color in zip(st.columns(2), ("ccu", "twitch_viewers"),
                                                 ("동시 접속 플레이어", "Twitch 시청자"), (MINT, BLUE)):
                with col:
                    st.markdown(f"**{title}**")
                    chart = trajectory_chart(selected_daily, field, color, period, smooth, compare_daily)
                    if chart is None:
                        st.info("선택 기간에 관측된 값이 없습니다.")
                    else:
                        st.altair_chart(chart, width="stretch", alt=f"출시 후 {period}일 동안의 {title} 변화")
            st.caption("빈 구간은 관측 없음이며, 이동평균은 최소 3개 관측값으로 계산합니다. 30일 기준표는 체크포인트 집계값을 사용하므로 일별 값과 다를 수 있습니다.")

        with st.expander("지표별 실제 값과 기준선", icon=":material/fact_check:"):
            indicator_rows = []
            for feature, (label, threshold, _, _) in THRESHOLDS.items():
                value = record[feature]
                indicator_rows.append({"지표": label, "관측 값": format_value(feature, value),
                                       "기준선": format_value(feature, threshold),
                                       "상태": "충족" if pd.notna(value) and value >= threshold else "미달"})
            st.dataframe(pd.DataFrame(indicator_rows), hide_index=True,
                         alt="선택 게임의 30일 지표별 관측 값과 기준선")


def render_success_pattern(data: DashboardData) -> None:
    pattern_sample = data.pattern_sample
    pattern_high_pass = pattern_sample.loc[pattern_sample["pass_count"].ge(3), "success"]
    pattern_high_rate = pattern_high_pass.mean()
    st.subheader("다섯 지표로 보는 전체 게임 성공 패턴", icon=":material/insights:")
    st.caption("전체 게임의 출시 30일 체크포인트를 기준으로 고정합니다. 장르나 선택 게임을 바꿔도 같은 결과를 표시합니다.")
    if pattern_sample.empty:
        st.info("30일 체크포인트와 성과 라벨이 있는 게임이 없습니다.")
    else:
        chart_col, context_col = st.columns([1.7, 1], gap="medium")
        with chart_col:
            with st.container(border=True, height="stretch"):
                st.markdown("**전체 표본의 기준 충족 수별 성공률**")
                st.altair_chart(cohort_chart(pattern_sample), width="stretch",
                                alt="전체 게임의 30일 기준 충족 수별 성공률과 표본 수")
        with context_col:
            with st.container(border=True, height="stretch"):
                st.caption("READ THE PATTERN / 해석의 실마리")
                same_cohort_rate = pattern_sample["success"].mean()
                st.metric("전체 분석 표본의 성공률", percent_or_dash(same_cohort_rate))
                st.caption(f"동일한 분석 집단 {len(pattern_sample):,}개 기준")
                st.metric("3개 이상 충족한 그룹", percent_or_dash(pattern_high_rate))
                st.caption(f"그룹 표본 {len(pattern_high_pass):,}개 · 성공 {int(pattern_high_pass.sum()):,}개")
                st.markdown("표본 수가 작은 막대는 함께 살펴보세요. 기준을 더 많이 충족해도 성공률이 항상 순서대로 높아지지는 않습니다.")
        st.caption("관찰된 연관성은 인과관계나 새로운 게임의 성공 확률을 뜻하지 않습니다.")

    with st.container(border=True):
        st.subheader("다섯 지표의 고정 기준", icon=":material/flag:")
        st.caption("출시 후 30일 체크포인트 기준이며, 모든 게임에 같은 기준값을 적용합니다.")
        for feature, (label, threshold, _, icon) in THRESHOLDS.items():
            with st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="center"):
                st.markdown(f":material/{icon}: **{label}**")
                st.badge(f"{format_value(feature, threshold)} 이상", color="green")
            st.markdown(FEATURE_DETAILS[feature])


def render_data_notes() -> None:
    st.space("small")
    with st.expander("데이터와 성공률을 읽는 방법", icon=":material/info:"):
        st.markdown(
            "- **표본 내 성공률**은 최종 성과 라벨이 있는 게임만 분모로 계산합니다.\n"
            "- **성공 패턴**은 전체 게임 중 30일 체크포인트와 성과 라벨이 있는 표본으로 고정합니다. 장르나 선택 게임을 바꿔도 그래프·성공률·기준값은 유지됩니다.\n"
            "- **성공률(기준 환산)**은 다섯 기준의 충족·초과 달성 정도를 %로 표시한 참고값입니다. 다섯 기준을 모두 충족하면 80%, 초과 달성 가산은 지표당 최대 4%p(기준의 두 배에서 최대)로 총 100%입니다. 실제 성공 확률을 추정한 값은 아닙니다.\n"
            "- **성과 라벨**은 원본 CSV의 값을 유지합니다. 원본 대시보드는 리뷰 500개·긍정률 80%·리뷰어 중위 플레이 5시간 이상이라는 정의를 안내합니다.\n"
            "- **미관측 지표**는 기준 미달로 처리하며 성공률 계산에 가산하지 않습니다. 원본 관측값과 일별 시계열의 빈 값은 유지합니다. 체크포인트가 평균 등 집계값이면 소수점이 있을 수 있습니다.\n"
            "- **배너 이미지**는 데이터에 등장하는 인디게임 테마에서 영감을 받아 AI로 제작한 오리지널 콘셉트 아트이며, 특정 게임의 스크린샷이 아닙니다."
        )
    st.caption("INDIE INSIGHT · 출시 첫 달의 신호를, 더 선명하게.")


def render_overview(stats: Overview, paths: AppPaths) -> None:
    cards = st.columns(4, border=True)
    with cards[0]:
        dashboard_metric("분석 대상 게임", f"{stats.game_count:,}",
                         "kpi_game_library.png", ":material/stadia_controller:", art_dir=paths.art_dir)
        st.caption(f"최종 성과 라벨 {stats.labelled_count:,}개 확인")
    with cards[1]:
        dashboard_metric("표본 내 성공률", percent_or_dash(stats.base_rate),
                         "kpi_success_rate.png", ":material/flag:", art_dir=paths.art_dir)
        st.caption(f"성공 {stats.success_count:,} / {stats.labelled_count:,}개")
    with cards[2]:
        dashboard_metric("3개 이상 기준 충족 그룹", percent_or_dash(stats.high_rate),
                         "kpi_threshold_group.png", ":material/verified:", art_dir=paths.art_dir)
        st.caption(f"성공 {stats.high_success_count:,} / {stats.high_count:,}개")
    with cards[3]:
        dashboard_metric("5개 지표 완전 관측", f"{stats.complete_count:,}",
                         "kpi_data_complete.png", ":material/data_check:", art_dir=paths.art_dir)
        st.caption(f"30일 관측 {stats.checkpoint_count:,}개 중 성과 라벨도 있는 게임")
