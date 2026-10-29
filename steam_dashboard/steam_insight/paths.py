"""Resolve app assets relative to the entry script, including shared ZIPs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AppPaths:
    app_dir: Path
    project_dir: Path
    image_dir: Path
    art_dir: Path
    hero_path: Path
    main_hero_path: Path

    @classmethod
    def from_app(cls, filename: str | Path) -> AppPaths:
        app_dir = Path(filename).resolve().parent
        project_dir = app_dir if (app_dir / "assets").is_dir() else app_dir.parent
        image_dir = project_dir / "assets" / "steam_insight_v2"
        art_dir = image_dir / "reference_refresh"
        hero_path = art_dir / "indie_genre_collage.png"
        if not hero_path.is_file():
            hero_path = image_dir / "indie_world_hero.png"
        return cls(
            app_dir=app_dir,
            project_dir=project_dir,
            image_dir=image_dir,
            art_dir=art_dir,
            hero_path=hero_path,
            main_hero_path=art_dir / "indie_main_panorama_v2.png",
        )
