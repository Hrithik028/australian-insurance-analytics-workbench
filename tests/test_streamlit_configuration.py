import importlib

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
