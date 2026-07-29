import importlib
from pathlib import Path

from app.config import APP_TITLE
from src import config


def test_streamlit_title_is_configured():
    assert "Australian Insurance" in APP_TITLE


def test_french_module_can_be_disabled(monkeypatch):
    monkeypatch.setenv("ENABLE_FRENCH_MODULE", "false")
    reloaded = importlib.reload(config)
    assert reloaded.settings.enable_french_module is False
    monkeypatch.delenv("ENABLE_FRENCH_MODULE")
    importlib.reload(config)


def test_streamlit_entrypoint_does_not_shadow_app_package():
    app_files = [Path("app/app.py"), *Path("app/pages").glob("*.py")]
    assert all("from app." not in path.read_text(encoding="utf-8") for path in app_files)
    entrypoint = Path("app/app.py").read_text(encoding="utf-8")
    assert 'st.Page("pages/00_Home.py"' in entrypoint
    assert "default=True" in entrypoint
