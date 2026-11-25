"""Smoke tests for the Streamlit dashboard using Streamlit's AppTest."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from netflix_analysis.config import PROJECT_ROOT


def test_streamlit_app_renders_without_exception() -> None:
    """Dashboard should boot on sample/raw data with zero uncaught exceptions."""
    app_path = Path(PROJECT_ROOT) / "app" / "streamlit_app.py"
    at = AppTest.from_file(str(app_path), default_timeout=30)
    at.run()

    assert not at.exception
    assert len(at.title) == 1
    assert "Netflix" in at.title[0].value
    assert len(at.tabs) == 6
    assert len(at.metric) == 4
