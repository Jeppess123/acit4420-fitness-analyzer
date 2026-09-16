"""Entry point for the Smart Fitness Session Analyzer.

Run with:
    python3 main.py
"""

from fitness import build_all_sessions, format_report, count_by_classification


def print_report(session):
    """Print a readable console report for one session."""
    print(format_report(session))
    print()


def main():
    sessions = build_all_sessions()

    for session in sessions:
        print_report(session)

    print("--- Summary across all sessions ---")
    for label, count in count_by_classification(sessions).items():
        print(f"{label}: {count}")


if __name__ == "__main__":
    main()