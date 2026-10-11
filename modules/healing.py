
import subprocess
from datetime import datetime, timezone

from modules.events import record_event


# Only explicitly approved services can be restarted.
ALLOWED_SERVICES = {
    "cron.service",
    "rsyslog.service",
    "systemd-resolved.service",
}


def get_service_state(service_name):
    """Return the current state of an allowlisted service."""

    if service_name not in ALLOWED_SERVICES:
        return {
            "success": False,
            "state": "REJECTED",
            "message": "Service is not in the allowlist.",
        }

    try:
        result = subprocess.run(
            [
                "systemctl",
                "show",
                service_name,
                "--property=ActiveState",
                "--value",
            ],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        if result.returncode != 0:
            return {
                "success": False,
                "state": "UNKNOWN",
                "message": (
                    result.stderr.strip()
                    or "Could not retrieve service state."
                ),
            }

        state = result.stdout.strip()

        if not state:
            return {
                "success": False,
                "state": "UNKNOWN",
                "message": "System returned an empty service state.",
            }

        return {
            "success": True,
            "state": state,
            "message": "Service state retrieved.",
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "state": "UNKNOWN",
            "message": "Timed out while checking service state.",
        }

    except OSError as error:
        return {
            "success": False,
            "state": "UNKNOWN",
            "message": str(error),
        }


def restart_service(service_name, dry_run=True, approved=False):
    """Safely restart an allowlisted service and verify its state."""

    timestamp = datetime.now(timezone.utc).isoformat()

    # Safety check 1: Only allowlisted services are permitted.
    if service_name not in ALLOWED_SERVICES:
        return {
            "success": False,
            "action": "restart_service",
            "service": service_name,
            "status": "REJECTED",
            "message": "Service is not in the allowlist.",
            "timestamp": timestamp,
        }

    # Safety check 2: Dry-run mode never changes the system.
    if dry_run:
        return {
            "success": True,
            "action": "restart_service",
            "service": service_name,
            "status": "DRY_RUN",
            "message": "No changes made. Restart would be attempted.",
            "timestamp": timestamp,
        }

    # Safety check 3: Require explicit approval.
    if not approved:
        return {
            "success": False,
            "action": "restart_service",
            "service": service_name,
            "status": "APPROVAL_REQUIRED",
            "message": "Explicit approval is required.",
            "timestamp": timestamp,
        }

    # Check the service before attempting recovery.
    before = get_service_state(service_name)

    if not before["success"]:
        result_data = {
            "success": False,
            "action": "restart_service",
            "service": service_name,
            "status": "PRECHECK_FAILED",
            "message": (
                "Cannot safely attempt restart: "
                + before["message"]
            ),
            "timestamp": timestamp,
        }
        return result_data

    try:
        result = subprocess.run(
            ["systemctl", "restart", service_name],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )

        if result.returncode != 0:
            message = (
                result.stderr.strip()
                or result.stdout.strip()
                or "Restart command failed."
            )

            if (
                "access denied" in message.lower()
                or "authentication" in message.lower()
                or "not authorized" in message.lower()
                or "permission denied" in message.lower()
            ):
                status = "PERMISSION_DENIED"
            else:
                status = "FAILED"

        else:
            # Verify the service after the restart command succeeds.
            after = get_service_state(service_name)

            if after["success"] and after["state"] == "active":
                status = "VERIFIED"
                message = (
                    "Restart command succeeded and the service "
                    "is active."
                )
            else:
                status = "UNVERIFIED"
                message = (
                    "Restart command completed, but an active service "
                    "state could not be confirmed."
                )

    except subprocess.TimeoutExpired:
        status = "TIMEOUT"
        message = "Restart command timed out."

    except OSError as error:
        status = "FAILED"
        message = str(error)

    result_data = {
        "success": status == "VERIFIED",
        "action": "restart_service",
        "service": service_name,
        "status": status,
        "message": message,
        "timestamp": timestamp,
    }

    # Record the actual recovery attempt for auditing.
    try:
        record_event(
            source="self_healing",
            event_type="SERVICE_RESTART",
            severity="INFO" if status == "VERIFIED" else "ERROR",
            message=f"{service_name}: {status} - {message}",
            details=result_data,
        )
    except OSError:
        # Do not hide the recovery result if audit writing fails.
        pass

    return result_data
