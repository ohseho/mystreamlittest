"""Pure calculations and text formatting; importing this module renders no UI."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .config import OUTCOMES, SIGNAL_SUMMARY_INSIGHTS, THRESHOLDS


@dataclass(frozen=True)
class Overview:
    """The values used by the four overview cards."""

    game_count: int
    labelled_count: int
    success_count: int
    base_rate: float
    high_count: int
    high_success_count: int
    high_rate: float
    complete_count: int
    checkpoint_count: int


def overview_stats(games: pd.DataFrame, checkpoint: pd.DataFrame) -> Overview:
    labelled = games.loc[games["success"].isin([0, 1]), "success"]
    checkpoint_labelled = checkpoint["success"].isin([0, 1])
    high_pass = checkpoint.loc[
        checkpoint_labelled & checkpoint["pass_count"].ge(3), "success"
    ]
    return Overview(
        game_count=len(games),
        labelled_count=len(labelled),
        success_count=int(labelled.sum()),
        base_rate=labelled.mean(),
        high_count=len(high_pass),
        high_success_count=int(high_pass.sum()),
        high_rate=high_pass.mean(),
        complete_count=int((checkpoint_labelled & checkpoint["complete"]).sum()),
        checkpoint_count=len(checkpoint),
    )


def checkpoint_signals(checkpoints: pd.DataFrame) -> pd.DataFrame:
    frame = checkpoints.loc[checkpoints["day"].eq(30)].copy()
    observed = frame[list(THRESHOLDS)].notna()
    frame["observed_count"] = observed.sum(axis=1)
    frame["complete"] = observed.all(axis=1)
    passes = pd.DataFrame(
        {feature: frame[feature].ge(spec[1]).fillna(False)
         for feature, spec in THRESHOLDS.items()},
        index=frame.index,
    )
    frame["pass_count"] = passes.sum(axis=1)
    return frame

def signal_score(record: pd.Series) -> float:
    """Threshold heuristic: 80 base points + at most 20 bonus points.

    Missing signals fail their threshold and contribute no points.
    This is not a fitted model or a probability; its maximum is 100.
    """
    total = 0.0
    for feature, (_, threshold, _, _) in THRESHOLDS.items():
        value = record[feature]
        if pd.isna(value):
            continue
        ratio = max(float(value) / threshold, 0.0)
        if ratio >= 1:
            total += 16 + min(ratio - 1, 1) * 4
    return min(total, 100.0)

def format_value(feature: str, value: float) -> str:
    if pd.isna(value):
        return "관측 없음"
    if feature == "ccu_retention":
        return f"{value:.1%}"
    # Checkpoint fields can be averages; retain their fractional information.
    number = f"{value:,.1f}".rstrip("0").rstrip(".")
    return f"{number}{THRESHOLDS[feature][2]}"

def signal_summary(record: pd.Series) -> str:
    """Choose concise, deterministic copy for the actual five-signal combination."""
    passed = frozenset(
        feature for feature, (_, threshold, _, _) in THRESHOLDS.items()
        if pd.notna(record[feature]) and record[feature] >= threshold
    )
    missing_count = sum(pd.isna(record[feature]) for feature in THRESHOLDS)
    if missing_count == len(THRESHOLDS):
        return (
            "출시 30일의 다섯 지표는 관측값이 없어 모두 미달로 반영했습니다. "
            "리뷰·동접·팔로워·Twitch 데이터가 확보된 뒤 초기 반응을 다시 살펴볼 필요가 있습니다."
        )
    missing_note = f"(미관측 {missing_count}개는 미달 반영)" if missing_count else ""
    return (
        f"출시 30일 기준 5개 중 {len(passed)}개 지표를 충족했습니다{missing_note}. "
        + SIGNAL_SUMMARY_INSIGHTS[passed]
    )

def split_values(value: object, limit: int | None = None) -> list[str]:
    if value is None or pd.isna(value):
        return []
    parts = [part.strip() for part in str(value).split("|") if part.strip()]
    return parts if limit is None else parts[:limit]

def outcome_label(value: float) -> str:
    return OUTCOMES.get(value, "라벨 없음")

def percent_or_dash(value: float) -> str:
    return f"{value:.1%}" if pd.notna(value) else "—"
