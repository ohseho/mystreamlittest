"""Validated CSV loading and cached data prepared for interactive views."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from .analysis import Overview, checkpoint_signals, overview_stats, split_values
from .config import ALL_GENRES, THRESHOLDS
from .paths import AppPaths

DATA_FILES = ("games.csv", "checkpoints.csv", "daily.csv")
DAILY_COLUMNS = ("appid", "date", "rel_day", "ccu", "twitch_viewers")
FileSignature = tuple[tuple[str, int, int], ...]
RuleSignature = tuple[tuple[str, float], ...]


@dataclass(frozen=True, slots=True)
class DashboardData:
    games: pd.DataFrame
    checkpoint_30: pd.DataFrame
    daily_by_game: dict[str, pd.DataFrame]
    genre_options: tuple[str, ...]
    genre_game_ids: dict[str, tuple[str, ...]]
    pattern_sample: pd.DataFrame
    overview: Overview
    last_date: pd.Timestamp | None


def find_data_dir(paths: AppPaths) -> Path:
    configured = os.environ.get("STEAM_DATA_DIR")
    candidates = [
        Path(configured).expanduser() if configured else None,
        paths.app_dir / "데이터",
        paths.app_dir / "data",
        paths.app_dir,
        paths.project_dir / "데이터",
        paths.project_dir / "data",
        paths.project_dir,
        paths.project_dir.parent / "ML_DL프로젝트" / "데이터",
    ]
    for candidate in candidates:
        if candidate is not None and all(
            (candidate / name).is_file() for name in DATA_FILES
        ):
            return candidate.resolve()
    raise FileNotFoundError(
        "games.csv, checkpoints.csv, daily.csv가 있는 폴더를 찾지 못했습니다. "
        "STEAM_DATA_DIR 환경 변수에 데이터 폴더를 지정해 주세요."
    )


def file_signature(folder: Path) -> FileSignature:
    result = []
    for name in DATA_FILES:
        path = folder / name
        stat = path.stat()
        result.append((str(path), stat.st_mtime_ns, stat.st_size))
    return tuple(result)


def normalize_outcome(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().str.lower().map(
        {"true": 1.0, "false": 0.0, "1": 1.0, "0": 0.0, "1.0": 1.0, "0.0": 0.0}
    )


def read_tables(folder: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Read, validate, and normalize CSVs without running UI commands."""
    games = pd.read_csv(folder / "games.csv", dtype={"appid": "string"}, low_memory=False)
    checkpoints = pd.read_csv(
        folder / "checkpoints.csv", dtype={"appid": "string"}, low_memory=False
    )
    daily = pd.read_csv(
        folder / "daily.csv",
        dtype={"appid": "string"},
        low_memory=False,
        usecols=lambda column: column in DAILY_COLUMNS,
    )
    requirements = {
        "games.csv": (games, {"appid", "name", "success", "release"}),
        "checkpoints.csv": (checkpoints, {"appid", "day", "success", *THRESHOLDS}),
        "daily.csv": (daily, {"appid", "date", "ccu", "twitch_viewers"}),
    }
    for filename, (frame, required) in requirements.items():
        missing = required.difference(frame.columns)
        if missing:
            raise ValueError(f"{filename}에 필요한 열이 없습니다: {', '.join(sorted(missing))}")
        if frame["appid"].isna().any():
            raise ValueError(f"{filename}에 게임 ID가 없는 행이 있습니다.")
    if games["appid"].duplicated().any():
        raise ValueError("games.csv에 중복 게임 ID가 있습니다.")

    games["name"] = games["name"].fillna("이름 없는 게임").astype(str)
    games["success"] = normalize_outcome(games["success"])
    checkpoints["success"] = normalize_outcome(checkpoints["success"])
    games["release"] = pd.to_datetime(games["release"], errors="coerce")
    daily["date"] = pd.to_datetime(daily["date"], errors="coerce")
    for frame, names in (
        (games, ("reviews", "positive_ratio", "reviewer_median_hours", "price_usd")),
        (checkpoints, ("day", "positive_ratio", *THRESHOLDS)),
        (daily, ("ccu", "twitch_viewers", "rel_day")),
    ):
        for name in names:
            if name in frame:
                frame[name] = pd.to_numeric(frame[name], errors="coerce").replace(
                    [np.inf, -np.inf], np.nan
                )
    if "rel_day" not in daily:
        releases = daily["appid"].map(games.set_index("appid")["release"])
        daily["rel_day"] = (daily["date"] - releases).dt.days
    if checkpoints.loc[checkpoints["day"].eq(30), "appid"].duplicated().any():
        raise ValueError("출시 30일 체크포인트에 중복 게임 ID가 있습니다.")
    return games, checkpoints, daily.loc[:, list(DAILY_COLUMNS)]


def prepare_data(
    games: pd.DataFrame, checkpoints: pd.DataFrame, daily: pd.DataFrame
) -> DashboardData:
    """Prepare normalized tables once; retain all observed history and gaps."""
    checkpoint_30 = checkpoint_signals(checkpoints)
    # Every existing view restricts checkpoints to IDs in the game catalogue.
    checkpoint_30 = checkpoint_30.loc[
        checkpoint_30["appid"].isin(games["appid"])
    ].copy()
    genre_ids: dict[str, list[str]] = {}
    if "genres" in games:
        for appid, value in zip(games["appid"], games["genres"]):
            for genre in dict.fromkeys(split_values(value)):
                genre_ids.setdefault(genre, []).append(str(appid))
    genre_options = tuple(sorted(genre_ids))
    genre_game_ids = {genre: tuple(genre_ids[genre]) for genre in genre_options}

    pattern_sample = checkpoint_30.loc[
        checkpoint_30["success"].isin([0, 1])
    ].copy()
    last_observed = daily["date"].max()
    last_date = last_observed if pd.notna(last_observed) else None
    daily_by_game = {
        str(appid): frame.sort_values("rel_day")
        for appid, frame in daily.loc[:, list(DAILY_COLUMNS)].groupby(
            "appid", sort=False, observed=True
        )
    }
    return DashboardData(
        games=games,
        checkpoint_30=checkpoint_30,
        daily_by_game=daily_by_game,
        genre_options=genre_options,
        genre_game_ids=genre_game_ids,
        pattern_sample=pattern_sample,
        overview=overview_stats(games, checkpoint_30),
        last_date=last_date,
    )


@st.cache_data(ttl=3600, max_entries=2, show_spinner="게임의 첫 30일을 살펴보고 있습니다…")
def load_data(
    folder_name: str, signature: FileSignature, rule_signature: RuleSignature = ()
) -> DashboardData:
    # Both signatures deliberately participate in the cache key.
    del signature, rule_signature
    return prepare_data(*read_tables(Path(folder_name)))


def select_genre(data: DashboardData, genre: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    if genre == ALL_GENRES:
        return data.games, data.checkpoint_30
    game_ids = data.genre_game_ids.get(genre, ())
    return (
        data.games.loc[data.games["appid"].isin(game_ids)].copy(),
        data.checkpoint_30.loc[data.checkpoint_30["appid"].isin(game_ids)].copy(),
    )


def daily_for_game(data: DashboardData, appid: str | None, period: int) -> pd.DataFrame:
    frame = data.daily_by_game.get(str(appid)) if appid is not None else None
    if frame is None:
        return pd.DataFrame({
            "rel_day": pd.Series(dtype="float64"),
            "ccu": pd.Series(dtype="float64"),
            "twitch_viewers": pd.Series(dtype="float64"),
            "date": pd.Series(dtype="datetime64[ns]"),
            "appid": pd.Series(dtype="string"),
        })
    return frame.loc[frame["rel_day"].between(0, period)].copy()
