import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
EVENT_LOG = REPORTS_DIR / "events.jsonl"

VALID_SEVERITIES = {"INFO", "WARNING", "ERROR", "CRITICAL"}


def record_event(source, event_type, severity, message, details=None):
    """Record a structured event in a JSON Lines file."""

    severity = severity.upper()

    if severity not in VALID_SEVERITIES:
        raise ValueError(f"Invalid severity: {severity}")

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "event_type": event_type,
        "severity": severity,
        "message": message,
        "details": details or {},
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    with EVENT_LOG.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event) + "\n")

    return event


def read_events(limit=100, severity=None):
    """Return recent events, optionally filtered by severity."""

    if limit < 1:
        raise ValueError("limit must be at least 1")

    if severity is not None:
        severity = severity.upper()

        if severity not in VALID_SEVERITIES:
            raise ValueError(f"Invalid severity filter: {severity}")

    if not EVENT_LOG.exists():
        return []

    events = []

    with EVENT_LOG.open("r", encoding="utf-8") as file:
        for line in file:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            if severity is None or event.get("severity") == severity:
                events.append(event)

    return events[-limit:]


def get_event_summary():
    """Count recorded events by severity."""

    summary = {
        "total": 0,
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 0,
        "CRITICAL": 0,
    }

    for event in read_events(limit=100000):
        summary["total"] += 1
        severity = event.get("severity")

        if severity in summary:
            summary[severity] += 1

    return summary
