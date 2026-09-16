"""Tests for the Smart Fitness Session Analyzer.

Run with:
    python3 tests.py
"""

from fitness import Observation, build_all_sessions


def test_resting_classified_correctly():
    sessions = build_all_sessions()
    resting_session = sessions[0]  # order matches data_generator.FITNESS_SCENARIOS
    assert resting_session.classify() == "resting", (
        f"expected resting, got {resting_session.classify()}"
    )


def test_moderate_activity_classified_correctly():
    sessions = build_all_sessions()
    moderate_session = sessions[1]
    assert moderate_session.classify() == "moderate_activity", (
        f"expected moderate_activity, got {moderate_session.classify()}"
    )


def test_high_activity_classified_correctly():
    sessions = build_all_sessions()
    high_session = sessions[2]
    assert high_session.classify() == "high_activity", (
        f"expected high_activity, got {high_session.classify()}"
    )


def test_recovery_session_detects_decline():
    sessions = build_all_sessions()
    recovery_session = sessions[3]
    assert recovery_session.classify() == "recovering", (
        f"expected recovering, got {recovery_session.classify()}"
    )


def test_poor_quality_observations_are_flagged():
    sessions = build_all_sessions()
    poor_quality_session = sessions[4]
    assert len(poor_quality_session.valid_observations()) == 0, (
        "expected every poor_quality observation to be flagged due to low signal_quality"
    )
    assert poor_quality_session.classify() == "insufficient_data", (
        f"expected insufficient_data, got {poor_quality_session.classify()}"
    )


def test_field_validation_independent_of_signal_quality():
    """Confirm the individual field checks (heart_rate, activity_level,
    etc.) work on their own, using a good signal_quality so the
    signal_quality gate doesn't mask the result. This exists because the
    generator's poor_quality scenario always fails signal_quality too,
    which means it alone can't prove the other checks work.
    """
    good_signal = 0.95

    missing_heart_rate = Observation(
        timestamp=0, heart_rate=None, skin_response=1.5,
        temperature=32.0, activity_level=0.3, signal_quality=good_signal,
    )
    assert missing_heart_rate.is_valid is False

    impossible_heart_rate = Observation(
        timestamp=1, heart_rate=300, skin_response=1.5,
        temperature=32.0, activity_level=0.3, signal_quality=good_signal,
    )
    assert impossible_heart_rate.is_valid is False

    negative_activity = Observation(
        timestamp=2, heart_rate=80, skin_response=1.5,
        temperature=32.0, activity_level=-0.1, signal_quality=good_signal,
    )
    assert negative_activity.is_valid is False

    all_good = Observation(
        timestamp=3, heart_rate=80, skin_response=1.5,
        temperature=32.0, activity_level=0.3, signal_quality=good_signal,
    )
    assert all_good.is_valid is True


def run_all():
    tests = [
        test_resting_classified_correctly,
        test_moderate_activity_classified_correctly,
        test_high_activity_classified_correctly,
        test_recovery_session_detects_decline,
        test_poor_quality_observations_are_flagged,
        test_field_validation_independent_of_signal_quality,
    ]
    for test in tests:
        test()
        print(f"{test.__name__}: OK")


if __name__ == "__main__":
    run_all()