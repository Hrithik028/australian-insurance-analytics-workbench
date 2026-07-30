"""Cached application data access."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import settings


@st.cache_data
def read_parquet(path: str) -> pd.DataFrame:
    target = Path(path)
    return pd.read_parquet(target) if target.exists() else pd.DataFrame()


def _resolved_path(primary: Path, demo: Path) -> Path:
    if settings.data_mode == "demo":
        return demo
    if settings.data_mode == "local":
        return primary
    return primary if primary.exists() else demo


def apra_table(name: str) -> pd.DataFrame:
    target = _resolved_path(
        settings.apra_processed / f"{name}.parquet",
        settings.demo_root / "apra" / f"{name}.parquet",
    )
    return read_parquet(str(target))


def french_table(name: str) -> pd.DataFrame:
    target = _resolved_path(
        settings.french_processed / f"{name}.parquet",
        settings.demo_root / "fremtpl2" / f"{name}.parquet",
    )
    return read_parquet(str(target))


def read_json(path: Path) -> dict:
    target = path
    if path.parent == settings.apra_processed:
        target = _resolved_path(path, settings.demo_root / "apra" / path.name)
    elif path.parent == settings.french_processed:
        target = _resolved_path(path, settings.demo_root / "fremtpl2" / path.name)
    return json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}


def using_demo_data() -> bool:
    if settings.data_mode == "demo":
        return True
    return settings.data_mode == "auto" and not settings.apra_processed.exists()
