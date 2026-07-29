import zipfile

import pytest

from src.apra.discovery import discover_workbooks, safe_extract


def test_safe_zip_extraction(tmp_path):
    archive = tmp_path / "source.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("book.xlsx", b"test")
    paths = safe_extract(archive, tmp_path / "out")
    assert paths[0].read_bytes() == b"test"


def test_zip_slip_is_rejected(tmp_path):
    archive = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("../escape.xlsx", b"test")
    with pytest.raises(ValueError, match="Unsafe"):
        safe_extract(archive, tmp_path / "out")


def test_workbook_discovery_ignores_lock_files(tmp_path):
    (tmp_path / "a.xlsx").touch()
    (tmp_path / "~$a.xlsx").touch()
    assert [path.name for path in discover_workbooks(tmp_path)] == ["a.xlsx"]
