import sys
from unittest.mock import MagicMock

import pytest

# Mock pyautogui before importing worker
sys.modules["pyautogui"] = MagicMock()

import worker as worker_module
from settings import AutomationSettings
from worker import AutomationWorker


def _make_worker():
    return AutomationWorker(AutomationSettings(image_path="x.png", confidence=0.8))


def test_iterate_found_clicks_center(monkeypatch):
    calls = {}

    def fake_locate(path, confidence, grayscale):
        calls["locate"] = (path, confidence, grayscale)
        return (120, 240)

    def fake_click(location):
        calls["click"] = location

    monkeypatch.setattr(worker_module.pyautogui, "locateCenterOnScreen", fake_locate)
    monkeypatch.setattr(worker_module.pyautogui, "click", fake_click)

    result = _make_worker().iterate()

    assert result.status == "clicked"
    assert result.location == (120, 240)
    assert calls["click"] == (120, 240)
    assert calls["locate"] == ("x.png", 0.8, True)


def test_iterate_not_found(monkeypatch):
    monkeypatch.setattr(
        worker_module.pyautogui, "locateCenterOnScreen", lambda *a, **k: None
    )
    clicked = {"n": 0}
    monkeypatch.setattr(
        worker_module.pyautogui,
        "click",
        lambda *a, **k: clicked.__setitem__("n", clicked["n"] + 1),
    )

    result = _make_worker().iterate()

    assert result.status == "not_found"
    assert clicked["n"] == 0


def test_iterate_error(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("画面取得失敗")

    monkeypatch.setattr(worker_module.pyautogui, "locateCenterOnScreen", boom)

    result = _make_worker().iterate()

    assert result.status == "error"
    assert "画面取得失敗" in result.message


def test_request_stop_sets_flag():
    w = _make_worker()
    assert w._stop_requested is False
    w.request_stop()
    assert w._stop_requested is True
