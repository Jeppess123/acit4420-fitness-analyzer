"""Builds the sample scenarios used by main.py and tests.py.

The assignment requires at least five scenarios: normal, unusual, and
invalid-data cases. data_generator.py's five named scenarios cover this
directly: resting, moderate_activity, and high_activity (normal cases),
recovery (unusual: values trend rather than staying flat), and
poor_quality (invalid-data: missing, impossible, or unreliable readings).
"""

from data_generator import available_scenarios
from fitness import build_all_sessions


def get_all_scenarios(seed=42):
    """Return a dict mapping scenario name -> Session, one per scenario."""
    sessions = build_all_sessions(seed=seed)
    return dict(zip(available_scenarios(), sessions))


if __name__ == "__main__":
    for name, session in get_all_scenarios().items():
        print(f"{name}: {session.classify()}")