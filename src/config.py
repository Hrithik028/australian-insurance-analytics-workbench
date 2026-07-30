"""Central, environment-aware project configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def _path_env(name: str, default: Path) -> Path:
    value = os.getenv(name)
    return Path(value).expanduser().resolve() if value else default.resolve()


def _bool_env(name: str, default: bool = True) -> bool:
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    root: Path = PROJECT_ROOT
    apra_policy_zip: Path = _path_env(
        "APRA_POLICY_ZIP",
        PROJECT_ROOT / "data/raw/apra/Policy Reports Masked December 2024.zip",
    )
    apra_claims_zip: Path = _path_env(
        "APRA_CLAIMS_ZIP",
        PROJECT_ROOT / "data/raw/apra/Claims Reports Masked December 2024.zip",
    )
    fremtpl2_local_path: Path | None = (
        _path_env("FREMTPL2_LOCAL_PATH", PROJECT_ROOT / "data/external/fremtpl2")
        if os.getenv("FREMTPL2_LOCAL_PATH")
        else None
    )
    enable_french_module: bool = _bool_env("ENABLE_FRENCH_MODULE", True)
    data_mode: str = os.getenv("INSURANCE_DATA_MODE", "auto").strip().lower()
    duckdb_path: Path = _path_env("DUCKDB_PATH", PROJECT_ROOT / "database/insurance_analytics.duckdb")
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

    @property
    def apra_interim(self) -> Path:
        return self.root / "data/interim/apra"

    @property
    def apra_processed(self) -> Path:
        return self.root / "data/processed/apra"

    @property
    def french_external(self) -> Path:
        return self.root / "data/external/fremtpl2"

    @property
    def french_processed(self) -> Path:
        return self.root / "data/processed/fremtpl2"

    @property
    def demo_root(self) -> Path:
        return self.root / "demo_data"


settings = Settings()
