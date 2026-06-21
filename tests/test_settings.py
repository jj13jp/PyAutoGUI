from settings import AutomationSettings


def test_defaults():
    s = AutomationSettings()
    assert s.image_path == ""
    assert s.confidence == 0.8
    assert s.wait_seconds == 4.0
    assert s.grayscale is True


def test_confidence_bounds_constants():
    assert AutomationSettings.CONFIDENCE_MIN == 0.1
    assert AutomationSettings.CONFIDENCE_MAX == 1.0
    assert AutomationSettings.CONFIDENCE_DEFAULT == 0.8
