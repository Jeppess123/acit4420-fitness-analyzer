"""Small behavior checks for the Smart Fitness Session Analyzer.

Run this file directly with ``python tests.py``.
"""

from fitness import Observation, count_by_classification, format_report
from sample_data import get_all_scenarios


def test_generated_scenarios_have_expected_labels():
    expected = {
        "resting": "resting",
        "moderate_activity": "moderate_activity",
        "high_activity": "high_activity",
        "recovery": "recovering",
        "poor_quality": "insufficient_data",
    }
    scenarios = get_all_scenarios()

    assert set(scenarios) == set(expected)
    for scenario_name, expected_label in expected.items():
        assert scenarios[scenario_name].classify() == expected_label


def test_unusable_session_has_no_statistics():
    session = get_all_scenarios()["poor_quality"]

    assert session.valid_observations() == []
    assert session.average("heart_rate") is None
    assert session.minimum("activity_level") is None
    assert session.maximum("temperature") is None
    assert session.compare_to_baseline() is None


def test_summary_and_report_use_session_results():
    scenarios = get_all_scenarios()
    summary = count_by_classification(list(scenarios.values()))
    report = format_report(scenarios["moderate_activity"])

    assert summary == {
        "resting": 1,
        "moderate_activity": 1,
        "high_activity": 1,
        "recovering": 1,
        "insufficient_data": 1,
    }
    assert "Observations: 12 valid out of 12" in report
    assert "Classification: moderate_activity" in report


def make_observation(**changes):
    values = {
        "timestamp": 10,
        "heart_rate": 80,
        "skin_response": 1.5,
        "temperature": 32.0,
        "activity_level": 0.4,
        "signal_quality": 0.95,
    }
    values.update(changes)
    return Observation(**values)


def test_observation_accepts_boundary_values():
    reading = make_observation(
        heart_rate=35,
        temperature=42,
        activity_level=1,
        signal_quality=0.5,
    )

    assert reading.is_valid
    assert reading.timestamp == 10
    assert reading.heart_rate == 35


def test_observation_rejects_bad_sensor_values_even_with_good_signal():
    invalid_readings = [
        make_observation(heart_rate=None),
        make_observation(heart_rate=206),
        make_observation(skin_response=-0.1),
        make_observation(temperature=24.9),
        make_observation(activity_level=-0.01),
        make_observation(signal_quality=0.49),
    ]

    assert all(not reading.is_valid for reading in invalid_readings)


def run_all():
    checks = [
        test_generated_scenarios_have_expected_labels,
        test_unusable_session_has_no_statistics,
        test_summary_and_report_use_session_results,
        test_observation_accepts_boundary_values,
        test_observation_rejects_bad_sensor_values_even_with_good_signal,
    ]
    for check in checks:
        check()
        print(f"PASS: {check.__name__}")


if __name__ == "__main__":
    run_all()