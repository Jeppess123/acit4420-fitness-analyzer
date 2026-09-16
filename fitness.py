"""Classes for the Smart Fitness Session Analyzer.

This file defines Observation, Participant, Session, and RecoverySession,
plus a few standalone helper functions. main.py is what actually runs
the program using these.
"""

from data_generator import available_scenarios, generate_fitness_data


class Observation:
    """One measurement window from a fitness session (heart rate, skin
    response, temperature, activity level, signal quality)."""

    # Bounds used to decide if a reading is valid or should be flagged.
    MIN_HEART_RATE = 35
    MAX_HEART_RATE = 205
    MIN_SIGNAL_QUALITY = 0.5

    def __init__(self, timestamp, heart_rate, skin_response,
                 temperature, activity_level, signal_quality):
        self.__timestamp = timestamp
        self.__heart_rate = heart_rate
        self.__skin_response = skin_response
        self.__temperature = temperature
        self.__activity_level = activity_level
        self.__signal_quality = signal_quality
        self.__is_valid = self._validate()

    @classmethod
    def from_dict(cls, data):
        """Build an Observation from one of the raw dicts data_generator.py
        produces."""
        return cls(
            timestamp=data.get("timestamp"),
            heart_rate=data.get("heart_rate"),
            skin_response=data.get("skin_response"),
            temperature=data.get("temperature"),
            activity_level=data.get("activity_level"),
            signal_quality=data.get("signal_quality"),
        )

    def _validate(self):
        """Check every field. Returns False as soon as one fails, True if
        they all pass."""
        if not in_range(self.__heart_rate, self.MIN_HEART_RATE, self.MAX_HEART_RATE):
            return False

        if self.__skin_response is None:
            return False
        if self.__skin_response < 0:
            return False

        if not in_range(self.__temperature, 25, 42):
            return False

        if not in_range(self.__activity_level, 0, 1):
            return False

        if self.__signal_quality is None:
            return False
        if self.__signal_quality < self.MIN_SIGNAL_QUALITY:
            return False

        return True

    @property
    def is_valid(self):
        return self.__is_valid

    @property
    def timestamp(self):
        return self.__timestamp

    @property
    def heart_rate(self):
        return self.__heart_rate

    @property
    def skin_response(self):
        return self.__skin_response

    @property
    def temperature(self):
        return self.__temperature

    @property
    def activity_level(self):
        return self.__activity_level

    @property
    def signal_quality(self):
        return self.__signal_quality

    def __str__(self):
        status = "valid" if self.__is_valid else "flagged"
        return f"Observation(t={self.__timestamp}, hr={self.__heart_rate}, {status})"


class Participant:
    """A participant and their personal baseline values."""

    def __init__(self, participant_id, baseline_heart_rate,
                 baseline_skin_response, baseline_temperature):
        self.__participant_id = participant_id
        self.__baseline_heart_rate = baseline_heart_rate
        self.__baseline_skin_response = baseline_skin_response
        self.__baseline_temperature = baseline_temperature

    @classmethod
    def from_dict(cls, data):
        """Build a Participant from the profile dict generate_fitness_data()
        returns."""
        return cls(
            participant_id=data.get("participant_id"),
            baseline_heart_rate=data.get("baseline_heart_rate"),
            baseline_skin_response=data.get("baseline_skin_response"),
            baseline_temperature=data.get("baseline_temperature"),
        )

    @property
    def participant_id(self):
        return self.__participant_id

    @property
    def baseline_heart_rate(self):
        return self.__baseline_heart_rate

    @property
    def baseline_skin_response(self):
        return self.__baseline_skin_response

    @property
    def baseline_temperature(self):
        return self.__baseline_temperature

    def __str__(self):
        return f"Participant({self.__participant_id})"


class Session:
    """A Participant plus a list of Observations for one training session.
    A Session HAS Observations (composition); it doesn't inherit from
    Observation."""

    def __init__(self, participant, observations):
        self.__participant = participant
        self.__observations = observations

    @property
    def participant(self):
        return self.__participant

    @property
    def observations(self):
        return self.__observations

    def valid_observations(self):
        """Just the observations that passed validation."""
        return [obs for obs in self.__observations if obs.is_valid]

    def _values(self, attr_name):
        """Pull one field (by name) from every valid observation."""
        valid = self.valid_observations()
        return [getattr(obs, attr_name) for obs in valid]

    def average(self, attr_name):
        values = self._values(attr_name)
        if not values:
            return None
        return sum(values) / len(values)

    def minimum(self, attr_name):
        values = self._values(attr_name)
        if not values:
            return None
        return min(values)

    def maximum(self, attr_name):
        values = self._values(attr_name)
        if not values:
            return None
        return max(values)

    def compare_to_baseline(self):
        """How far this session's averages are from the participant's
        baseline. None if there's nothing valid to compare."""
        avg_heart_rate = self.average("heart_rate")
        if avg_heart_rate is None:
            return None

        return {
            "heart_rate_diff": avg_heart_rate - self.__participant.baseline_heart_rate,
            "skin_response_diff": self.average("skin_response") - self.__participant.baseline_skin_response,
            "temperature_diff": self.average("temperature") - self.__participant.baseline_temperature,
        }

    def classify(self):
        """Classify based on average activity level."""
        avg_activity = self.average("activity_level")
        if avg_activity is None:
            return "insufficient_data"
        if avg_activity < 0.25:
            return "resting"
        if avg_activity < 0.67:
            return "moderate_activity"
        return "high_activity"


class RecoverySession(Session):
    """Same as Session, but also checks whether heart rate and activity
    are actually declining toward the end of the session. That's what
    makes it different from just "moderate activity on average"."""

    def classify(self):
        valid = self.valid_observations()
        if not valid:
            return "insufficient_data"

        # split into an early half and a late half, sorted by time
        valid_sorted = sorted(valid, key=lambda obs: obs.timestamp)
        midpoint = len(valid_sorted) // 2
        if midpoint == 0:
            # not enough data to compare a trend
            return super().classify()

        early, late = valid_sorted[:midpoint], valid_sorted[midpoint:]
        early_hr = sum(o.heart_rate for o in early) / len(early)
        late_hr = sum(o.heart_rate for o in late) / len(late)
        early_activity = sum(o.activity_level for o in early) / len(early)
        late_activity = sum(o.activity_level for o in late) / len(late)

        if late_hr < early_hr and late_activity < early_activity:
            return "recovering"

        # no real decline, use the normal rules instead
        return super().classify()


def in_range(value, low, high):
    """True if value isn't None and falls between low and high."""
    if value is None:
        return False
    return low <= value <= high


def build_session(profile_dict, observation_dicts):
    """Turn one raw (profile, observations) pair into a RecoverySession.

    Always returns a RecoverySession rather than a plain Session, since
    its classify() only reports "recovering" when it actually finds a
    decline, and otherwise behaves like a normal Session. That way the
    program doesn't need to know in advance which scenario it's looking at.
    """
    participant = Participant.from_dict(profile_dict)
    observations = [Observation.from_dict(d) for d in observation_dicts]
    return RecoverySession(participant, observations)


def build_all_sessions(seed=42, participant_id="P001"):
    """Build one session per scenario in data_generator.py.

    Shared by main.py, sample_data.py, and tests.py so none of them have
    to repeat this same loop.
    """
    sessions = []
    for scenario in available_scenarios():
        profile, observations = generate_fitness_data(
            participant_id=participant_id,
            scenario=scenario,
            seed=seed,
        )
        sessions.append(build_session(profile, observations))
    return sessions


def count_by_classification(sessions):
    """How many sessions fall into each classification."""
    counts = {}
    for session in sessions:
        label = session.classify()
        counts[label] = counts.get(label, 0) + 1
    return counts


def format_report(session):
    """Build the report text for one session (as a string, not printed)."""
    total = len(session.observations)
    valid = len(session.valid_observations())

    lines = [
        f"--- {session.participant} ---",
        f"Observations: {valid} valid out of {total}",
    ]

    if valid == 0:
        lines.append("Classification: insufficient_data")
        return "\n".join(lines)

    baseline_diff = session.compare_to_baseline()
    lines.append(f"Average heart rate: {session.average('heart_rate'):.1f}")
    lines.append(f"Average activity level: {session.average('activity_level'):.2f}")
    lines.append(f"Heart rate vs baseline: {baseline_diff['heart_rate_diff']:+.1f}")
    lines.append(f"Classification: {session.classify()}")
    return "\n".join(lines)