"""Reusable dashboard artwork, metrics and attainment markup."""

from __future__ import annotations

import base64
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from .analysis import format_value
from .config import AMBER, FEATURE_DETAILS, MINT, THRESHOLDS
from .paths import AppPaths
from .styles import ATTAINMENT_STYLE


@st.cache_data(max_entries=2, show_spinner=False)
def main_banner_svg(path_string: str, modified_ns: int) -> str:
    del modified_ns
    encoded = base64.b64encode(Path(path_string).read_bytes()).decode("ascii")
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="200" viewBox="0 0 1200 200">'
        f'<image href="data:image/png;base64,{encoded}" width="1200" height="200" preserveAspectRatio="xMidYMid slice"/>'
        '</svg>'
    )


def dashboard_metric(
    label: str, value: str, image_name: str, fallback_icon: str, *, art_dir: Path
) -> None:
    image_path = art_dir / image_name
    if image_path.is_file():
        with st.container(horizontal=True, vertical_alignment="center", gap="small"):
            st.image(image_path, width=48, alt="")
            st.metric(label, value)
    else:
        st.metric(label, value, icon=fallback_icon)


def attainment_html(record: pd.Series) -> str:
    rows = []
    for feature, (label, threshold, _, _) in THRESHOLDS.items():
        value = record[feature]
        ratio = max(float(value) / threshold, 0) if pd.notna(value) else 0.0
        passed = pd.notna(value) and value >= threshold
        color = MINT if passed else AMBER
        value_text = f"{format_value(feature, value)} · {ratio:,.1%}"
        threshold_text = f"기준 {format_value(feature, threshold)}"
        description = FEATURE_DETAILS[feature]
        status = "기준 충족" if passed else "기준 미달"
        details = f"{label}: {value_text} / {threshold_text} · {status}"
        rows.append(f"""
        <div class="steam-attainment-row" data-feature="{feature}">
          <div class="steam-attainment-label">
            <span>{escape(label)}</span>
            <span class="steam-attainment-help">
              <button type="button" aria-label="{escape(label)} 설명"
                      aria-describedby="steam-help-{feature}">?</button>
              <span class="steam-attainment-tooltip" role="tooltip"
                    id="steam-help-{feature}">{escape(description)}</span>
            </span>
          </div>
          <div class="steam-attainment-bar" role="progressbar" tabindex="0"
               aria-label="{escape(label)}" aria-valuemin="0" aria-valuemax="100"
               aria-valuenow="{min(ratio, 1.0) * 100:.3f}"
               aria-valuetext="{escape(details)}" title="{escape(details)}">
            <span class="steam-attainment-fill"
                  style="width:{min(ratio, 1.0) * 100:.3f}%;background:{color};"></span>
            <span class="steam-attainment-values">
              <span class="steam-attainment-observed">{escape(value_text)}</span>
              <span class="steam-attainment-threshold">{escape(threshold_text)}</span>
            </span>
          </div>
        </div>""")
    return ATTAINMENT_STYLE + '<div class="steam-attainment" role="group" aria-label="다섯 가지 성장 지표">' + ''.join(rows) + '</div>'


def render_identity(paths: AppPaths) -> None:
    with st.sidebar:
        st.subheader("Indie insight", icon=":material/sports_esports:")
        st.caption("Steam 인디게임의 첫 30일을 읽다")
        st.badge("Launch +30", color="green", icon=":material/insights:")
        if paths.hero_path.is_file():
            st.image(paths.hero_path, width="stretch",
                     alt="분석 데이터에 등장하는 협동·공포·모험·전략 테마의 오리지널 인디게임 아트")

    top_left, top_right = st.columns([3, 1], vertical_alignment="center")
    with top_left:
        st.caption("STEAM / INDIE INSIGHT / LAUNCH ANALYTICS")
    with top_right:
        st.badge("첫 30일의 성장 신호", color="green", icon=":material/query_stats:")
    st.title("작은 게임, 다음의 큰 가능성.")
    st.markdown("리뷰부터 플레이어와 시청자까지. **출시 첫 달의 데이터**에서 게임의 성장 신호를 발견하세요.")
    main_image_path = paths.main_hero_path if paths.main_hero_path.is_file() else paths.hero_path
    if main_image_path.is_file():
        st.image(main_banner_svg(str(main_image_path), main_image_path.stat().st_mtime_ns), width="stretch",
                 alt="민트빛 부유 섬과 산악길을 함께 탐험하는 모험가를 그린 오리지널 인디게임 파노라마")
        st.caption("INDIE WORLDS · 분석 데이터의 다양한 게임 테마를 담은 AI 제작 콘셉트 아트")
