
import subprocess


def get_service_status(service_name):
    """Retrieve the state of one systemd service."""

    command = [
        "systemctl",
        "show",
        service_name,
        "--property=Id",
        "--property=Description",
        "--property=LoadState",
        "--property=ActiveState",
        "--property=SubState",
        "--no-pager",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        if result.returncode != 0:
            return {
                "name": service_name,
                "status": "error",
                "error": result.stderr.strip()
                or "systemctl command failed",
            }

        details = {}

        for line in result.stdout.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                details[key] = value

        if details.get("LoadState") == "not-found":
            return {
                "name": service_name,
                "status": "not-found",
                "error": "Service does not exist",
            }

        return {
            "name": details.get("Id", service_name),
            "description": details.get("Description", ""),
            "load_state": details.get("LoadState", "unknown"),
            "active_state": details.get("ActiveState", "unknown"),
            "sub_state": details.get("SubState", "unknown"),
        }

    except subprocess.TimeoutExpired:
        return {
            "name": service_name,
            "status": "error",
            "error": "Service query timed out",
        }

    except OSError as error:
        return {
            "name": service_name,
            "status": "error",
            "error": str(error),
        }


def get_services_status(service_names):
    """Retrieve the states of multiple systemd services."""

    return [
        get_service_status(service_name)
        for service_name in service_names
    ]
def classify_service_health(service):
    """Classify a service using its reported systemd state."""

    if service.get("status") in ("not-found", "error"):
        return "UNKNOWN"

    active_state = service.get("active_state")

    if active_state == "failed":
        return "FAILED"

    if active_state == "active":
        return "HEALTHY"

    if active_state == "inactive":
        return "INACTIVE"

    return "UNKNOWN"
