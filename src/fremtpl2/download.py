"""Revision-pinned Hugging Face download with an explicit offline fallback."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

from src.config import Settings, settings
from src.utils import sha256

REPO_ID = "mabilton/fremtpl2"
FILES = ("freMTPL2freq.csv", "freMTPL2sev.csv")


def _validate_files(directory: Path) -> dict[str, Path]:
    paths = {filename: directory / filename for filename in FILES}
    missing = [filename for filename, path in paths.items() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing freMTPL2 files: {', '.join(missing)}")
    return paths


def acquire_fremtpl2(config: Settings = settings) -> dict[str, object]:
    destination = config.french_external
    destination.mkdir(parents=True, exist_ok=True)
    revision = "offline-local"
    existing_metadata_path = destination / "dataset_metadata.json"
    existing_metadata = (
        json.loads(existing_metadata_path.read_text(encoding="utf-8")) if existing_metadata_path.exists() else {}
    )
    source = config.fremtpl2_local_path
    if source and source.resolve() != destination.resolve():
        for filename, path in _validate_files(source).items():
            shutil.copy2(path, destination / filename)
    elif not all((destination / filename).exists() for filename in FILES):
        info = HfApi().dataset_info(REPO_ID)
        revision = info.sha
        for filename in FILES:
            hf_hub_download(
                repo_id=REPO_ID,
                repo_type="dataset",
                filename=filename,
                revision=revision,
                local_dir=destination,
            )
    else:
        try:
            revision = HfApi().dataset_info(REPO_ID).sha
        except Exception:
            revision = existing_metadata.get("revision", "cached-offline")
    paths = _validate_files(destination)
    checksums = {filename: sha256(path) for filename, path in paths.items()}
    rows = {filename: int(len(pd.read_csv(path))) for filename, path in paths.items()}
    metadata = {
        "repository": REPO_ID,
        "repository_type": "dataset",
        "revision": revision,
        "downloaded_at": datetime.now(UTC).isoformat(),
        "files": [
            {
                "filename": filename,
                "size_bytes": path.stat().st_size,
                "row_count": rows[filename],
                "sha256": checksums[filename],
            }
            for filename, path in paths.items()
        ],
    }
    (destination / "dataset_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (destination / "checksums.json").write_text(json.dumps(checksums, indent=2), encoding="utf-8")
    return metadata
