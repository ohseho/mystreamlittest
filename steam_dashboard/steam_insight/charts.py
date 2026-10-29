"""Charts for player trajectories and observed success patterns."""

from __future__ import annotations

import altair as alt
import pandas as pd

from .config import MINT, MUTED


def chart_style(chart):
    return (
        chart.configure_view(strokeWidth=0)
        .configure_axis(
            labelColor=MUTED, titleColor=MUTED, gridColor="#213047",
            domain=False, tickColor="#243247", labelFontSize=11,
            titleFontSize=11, labelPadding=9, titlePadding=12,
        )
        .configure_legend(labelColor="#CFD9E8", titleColor=MUTED, orient="top")
        .properties(background="transparent")
    )


def trajectory_chart(series: pd.DataFrame, column: str, color: str, period: int,
                     smooth: bool, comparison: pd.DataFrame | None = None):
    frames = []
    for source, series_name in ((series, "선택 게임"), (comparison, "비교 게임")):
        if source is None or source.empty:
            continue
        # Reindex to preserve gaps. Missing observations stay missing on the chart.
        values = source.set_index("rel_day")[column].reindex(range(period + 1))
        if smooth:
            values = values.rolling(7, min_periods=3).mean().where(values.notna())
        frame = values.rename("value").rename_axis("day").reset_index()
        frame["series"] = series_name
        frames.append(frame)
    if not frames:
        return None
    data = pd.concat(frames, ignore_index=True)
    if data["value"].notna().sum() == 0:
        return None
    base = alt.Chart(data).encode(
        x=alt.X("day:Q", title="출시 후 경과일", scale=alt.Scale(domain=[0, period])),
        y=alt.Y("value:Q", title="인원", scale=alt.Scale(zero=True),
                axis=alt.Axis(format="~s")),
        color=alt.Color("series:N", title=None,
                        scale=alt.Scale(domain=["선택 게임", "비교 게임"],
                                        range=[color, "#B69BFF"])),
        tooltip=[alt.Tooltip("series:N", title="게임"),
                 alt.Tooltip("day:Q", title="출시 후 일수", format="d"),
                 alt.Tooltip("value:Q", title="인원", format=",.1f")],
    )
    line = base.mark_line(strokeWidth=2.5, point=alt.OverlayMarkDef(size=10))
    return chart_style(line.properties(height=235))


def cohort_chart(complete: pd.DataFrame):
    grouped = complete.groupby("pass_count")["success"].agg(["mean", "size", "sum"])
    grouped = grouped.reindex(range(6)).reset_index()
    base = alt.Chart(grouped).encode(
        x=alt.X("pass_count:O", title="충족한 기준 수", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("mean:Q", title="표본 내 성공률", scale=alt.Scale(domain=[0, 1]),
                axis=alt.Axis(format=".0%")),
        tooltip=[alt.Tooltip("pass_count:O", title="충족 수"),
                 alt.Tooltip("mean:Q", title="성공률", format=".1%"),
                 alt.Tooltip("size:Q", title="표본 수", format=",d"),
                 alt.Tooltip("sum:Q", title="성공 게임 수", format=",d")],
    )
    bars = base.mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
        color=alt.condition(alt.datum.pass_count >= 3, alt.value(MINT), alt.value("#466382"))
    )
    labels = base.mark_text(dy=-10, color="#CFD9E8", fontSize=11).encode(
        text=alt.Text("mean:Q", format=".1%")
    )
    return chart_style((bars + labels).properties(height=295))
