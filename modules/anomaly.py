
from modules.events import record_event


DEFAULT_THRESHOLDS = {
    "cpu_usage": 80.0,
    "memory_usage": 85.0,
    "disk_usage": 90.0,
}


def detect_anomalies(system_info, thresholds=None):
    """Detect resource readings that exceed configured thresholds."""

    limits = DEFAULT_THRESHOLDS.copy()

    if thresholds:
        limits.update(thresholds)

    anomalies = []

    for metric, threshold in limits.items():
        if metric not in system_info:
            continue

        value = system_info[metric]

        if not isinstance(value, (int, float)):
            continue

        if value > threshold:
            anomaly = {
                "metric": metric,
                "value": value,
                "threshold": threshold,
                "severity": "WARNING",
                "message": (
                    f"{metric} is {value:.1f}%, "
                    f"above the threshold of {threshold:.1f}%"
                ),
            }

            anomalies.append(anomaly)

            record_event(
                source="anomaly_detector",
                event_type="RESOURCE_ANOMALY",
                severity="WARNING",
                message=anomaly["message"],
                details=anomaly,
            )

    return anomalies
