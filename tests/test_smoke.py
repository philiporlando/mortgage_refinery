from pathlib import Path

from mortgage_refinery.rate_tracker import RateTracker


def test_imports() -> None:
    import mortgage_refinery.config  # noqa: F401
    import mortgage_refinery.email  # noqa: F401
    import mortgage_refinery.health  # noqa: F401
    import mortgage_refinery.main  # noqa: F401
    import mortgage_refinery.rate_tracker  # noqa: F401


def test_rate_tracker_first_alert(tmp_path: Path) -> None:
    tracker = RateTracker(state_file=tmp_path / "state.json")
    assert tracker.should_send_alert(current_rate=6.0, threshold=6.5) is True


def test_rate_tracker_no_alert_above_threshold(tmp_path: Path) -> None:
    tracker = RateTracker(state_file=tmp_path / "state.json")
    assert tracker.should_send_alert(current_rate=7.0, threshold=6.5) is False
