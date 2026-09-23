# Smart Fitness Session Analyzer

**Selected option:** Option A — Smart Fitness Session Analyzer
**Student name:** Jeppe
**Student number:** S400995

## Description

Simulates and analyzes wearable-device data from fitness sessions.
Validates sensor readings, compares a session against the participant's
personal baseline, and classifies it as resting, moderate activity, high
activity, recovering, or insufficient data.

## Class design

- **Observation** — one measurement window. Validates itself on
  construction (`is_valid`). `from_dict()` classmethod builds one from
  the generator's raw dicts.
- **Participant** — a participant's baseline values. Also has
  `from_dict()`.
- **Session** — a Participant plus a list of Observations (composition,
  not inheritance). Provides `average`/`minimum`/`maximum`,
  `compare_to_baseline()`, and `classify()`.
- **RecoverySession(Session)** — overrides `classify()` to detect a
  decline in heart rate and activity across the session; falls back to
  `super().classify()` if no decline is found. Always used instead of a
  plain Session, since the program shouldn't need to know the scenario
  name in advance.

**OOP requirements:** composition (Session holds Observations),
encapsulation (private attributes + `@property` getters throughout),
inheritance/overriding (RecoverySession), classmethod constructors
(`from_dict()` on Observation and Participant), and standalone functions
(`in_range`, `build_session`, `build_all_sessions`,
`count_by_classification`, `format_report` in `fitness.py`).

## Assumptions and classification rules

- Classification uses average activity level: `<0.25` resting,
  `0.25–0.67` moderate, `>0.67` high.
- `RecoverySession` calls it `recovering` only if both average heart
  rate and activity are lower in the second half of the session than
  the first.
- An observation is invalid if any field is missing or out of range:
  heart rate 35–205, temperature 25–42, activity 0–1, skin response
  ≥ 0, signal quality ≥ 0.5.
- The `poor_quality` scenario always fails on signal quality alone
  (by design — unreliable readings shouldn't be trusted regardless of
  other values), so it can't demonstrate the other field checks on its
  own. `tests.py` covers those separately with a dedicated test using a
  high signal quality.
- With zero valid observations, stats methods return `None` and
  `classify()` returns `"insufficient_data"`.

## Installation and running

```
git clone https://github.com/Jeppess123/acit4420-fitness-analyzer.git
cd acit4420-fitness-analyzer
python3 main.py
```

Use `python` instead of `python3` if that's what your system uses.
Standard library only, no packages to install (see `requirements.txt`).

Run tests with `python3 tests.py`.

## Example output

```
--- Participant(P001) ---
Observations: 12 valid out of 12
Average heart rate: 80.0
Classification: resting
...
--- Summary across all sessions ---
resting: 1
moderate_activity: 1
high_activity: 1
recovering: 1
insufficient_data: 1
```

## Known limitations

- `RecoverySession` detects decline by comparing two halves of the
  session, not a proper trend fit; a noisy, non-monotonic decline could
  be missed.
- `insufficient_data` doesn't distinguish "signal was unreliable" from
  "a value was clearly impossible" — both end up the same way.