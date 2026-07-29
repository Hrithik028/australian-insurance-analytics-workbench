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


def apra_table(name: str) -> pd.DataFrame:
    return read_parquet(str(settings.apra_processed / f"{name}.parquet"))


def french_table(name: str) -> pd.DataFrame:
    return read_parquet(str(settings.french_processed / f"{name}.parquet"))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
