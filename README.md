# Smart Fitness Session Analyzer

**Selected option:** Option A — Smart Fitness Session Analyzer

**Student name:** Jeppe
**Student number:** S400995

## Description

This program simulates and analyzes wearable-device measurements from
fitness training sessions. It organizes participants and their reference
baseline values, validates incoming sensor measurements, compares a
session's actual readings against the participant's personal baseline,
and classifies the session as resting, moderate activity, high activity,
recovering, or insufficient data, printing a readable report for each.

## Class design

- **Observation** — represents one measurement window (heart rate, skin
  response, temperature, activity level, signal quality). Validates
  itself on construction and exposes `is_valid`. Provides
  `Observation.from_dict()`, a classmethod alternative constructor that
  builds an Observation directly from the raw dictionaries returned by
  `data_generator.generate_fitness_data()`.

- **Participant** — represents a participant and their personal baseline
  values (baseline heart rate, skin response, temperature). Also provides
  a `from_dict()` classmethod constructor.

- **Session** — represents a full training session: a Participant plus a
  list of Observations. This is the composition relationship in the
  design — a Session *has* Observations, it does not inherit from
  Observation. Provides summary statistics (`average`, `minimum`,
  `maximum`), `compare_to_baseline()` (returns a structured dict of
  differences from baseline), and `classify()`.

- **RecoverySession(Session)** — a subclass that overrides `classify()`
  to detect whether heart rate and activity level actually decline over
  the course of the session (comparing the early half of valid
  observations to the late half), rather than relying on the overall
  average alone. When no decline is detected, it falls back to
  `super().classify()`, so it never duplicates the parent's threshold
  logic. The program always builds a RecoverySession regardless of
  which scenario produced the data, since real sensor data would not
  come pre-labeled with a scenario name; the class decides from the
  data itself whether a recovery pattern is present.

### Where the object-oriented requirements are demonstrated

- **Composition:** Session holds a list of Observation objects and a
  Participant object.
- **Encapsulation:** all instance attributes on Observation, Participant,
  and Session are private (double-underscore), accessed only through
  `@property` getters or methods.
- **Inheritance and overriding:** RecoverySession inherits from Session
  and overrides `classify()`, calling `super().classify()` as a fallback.
- **Classmethods as alternative constructors:** `Observation.from_dict()`
  and `Participant.from_dict()` both use `cls(...)`, so they stay correct
  even if either class is subclassed later.
- **Standalone functions:** `in_range()`, `build_session()`,
  `build_all_sessions()`, `count_by_classification()`, and
  `format_report()` in `fitness.py` are all free functions rather than
  methods, since none of them are responsible to a single instance.

## Assumptions and classification rules

- Classification is based on the session's **average activity level**
  across valid observations only: below 0.25 is `resting`, 0.25–0.67 is
  `moderate_activity`, above 0.67 is `high_activity`. These thresholds
  were chosen to sit between the ranges the data generator itself uses
  for each scenario.
- `RecoverySession` reclassifies a session as `recovering` only if
  **both** average heart rate and average activity level are lower in
  the second half of valid, timestamp-sorted observations than in the
  first half.
- An observation is considered invalid (flagged, excluded from all
  statistics) if any of the following hold: `heart_rate` is missing or
  outside 35–205 bpm; `skin_response` is missing or negative;
  `temperature` is missing or outside 25–42°C; `activity_level` is
  missing or outside 0–1; `signal_quality` is missing or below 0.5.
- **Design decision on signal_quality:** the data generator's
  `poor_quality` scenario always drives `signal_quality` below the 0.5
  threshold, regardless of what else is wrong with a given reading. This
  means every `poor_quality` observation is flagged, and that session
  reports `insufficient_data`. This was a deliberate choice: an
  unreliable reading should not be trusted even if its individual values
  happen to look plausible. Because this means the `poor_quality`
  scenario alone cannot demonstrate that the other field-level checks
  (missing/impossible heart rate, negative activity level) work
  independently, `tests.py` includes a dedicated test
  (`test_field_validation_independent_of_signal_quality`) that
  constructs Observations directly with a high signal_quality to prove
  those checks work on their own.
- A session with zero valid observations returns `None` from `average()`,
  `minimum()`, `maximum()`, and `compare_to_baseline()`, and `classify()`
  returns `"insufficient_data"` rather than raising an error.

## Installation and running instructions

```
git clone https://github.com/Jeppess123/acit4420-fitness-analyzer.git
cd acit4420-fitness-analyzer
python3 main.py
```

If your system uses `python` rather than `python3`, use that instead.

No third-party packages are required; this project uses only the Python
standard library (see `requirements.txt`).

To run the test suite:

```
python3 tests.py
```

## Example output

```
--- Participant(P001) ---
Observations: 12 valid out of 12
Average heart rate: 80.0
Average activity level: 0.11
Heart rate vs baseline: +2.0
Classification: resting

--- Participant(P001) ---
Observations: 12 valid out of 12
Average heart rate: 105.8
Average activity level: 0.51
Heart rate vs baseline: +27.8
Classification: moderate_activity

--- Participant(P001) ---
Observations: 12 valid out of 12
Average heart rate: 135.7
Average activity level: 0.80
Heart rate vs baseline: +57.7
Classification: high_activity

--- Participant(P001) ---
Observations: 12 valid out of 12
Average heart rate: 112.8
Average activity level: 0.48
Heart rate vs baseline: +34.8
Classification: recovering

--- Participant(P001) ---
Observations: 0 valid out of 12
Classification: insufficient_data

--- Summary across all sessions ---
resting: 1
moderate_activity: 1
high_activity: 1
recovering: 1
insufficient_data: 1
```

## Known limitations

- `RecoverySession.classify()` detects a decline by comparing only the
  first half of valid observations to the second half; it does not fit
  a trend line or use a more statistically robust method, so a session
  with a noisy but non-monotonic decline could be misclassified.
- Because `poor_quality` observations are always flagged on
  `signal_quality` alone, the classifier currently cannot distinguish
  between "signal was unreliable" and "signal was fine but the
  underlying measurement was clearly impossible" in its final output;
  both simply become part of the same `insufficient_data` result.
- `tests.py` builds its scenario-to-session mapping in the same fixed
  order as `data_generator.FITNESS_SCENARIOS`. `sample_data.py`'s
  `get_all_scenarios()` avoids this by keying its result by scenario
  name instead of list position.