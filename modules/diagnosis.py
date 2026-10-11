
def diagnose_incidents(
    system_info,
    processes,
    services,
    network_results,
    anomalies,
):
    """Analyze monitoring results and suggest investigation steps."""

    incidents = []

    # 1. Diagnose resource anomalies
    for anomaly in anomalies:
        metric = anomaly["metric"]
        value = anomaly["value"]

        if metric == "cpu_usage":
            suspected_processes = sorted(
                processes,
                key=lambda process: process.get("cpu", 0),
                reverse=True,
            )[:3]

            incidents.append({
                "title": "High CPU usage",
                "severity": anomaly["severity"],
                "evidence": f"CPU usage is {value:.1f}%.",
                "possible_cause": (
                    "A CPU-intensive process or unusually heavy workload."
                ),
                "recommended_action": (
                    "Inspect the top CPU-consuming processes and check "
                    "whether the workload is expected."
                ),
                "related_processes": [
                    process.get("name", "unknown")
                    for process in suspected_processes
                ],
            })

        elif metric == "memory_usage":
            suspected_processes = sorted(
                processes,
                key=lambda process: process.get("memory", 0),
                reverse=True,
            )[:3]

            incidents.append({
                "title": "High memory usage",
                "severity": anomaly["severity"],
                "evidence": f"Memory usage is {value:.1f}%.",
                "possible_cause": (
                    "Memory-intensive applications or increasing memory "
                    "consumption."
                ),
                "recommended_action": (
                    "Inspect memory-consuming processes and check whether "
                    "memory usage continues to increase."
                ),
                "related_processes": [
                    process.get("name", "unknown")
                    for process in suspected_processes
                ],
            })

        elif metric == "disk_usage":
            incidents.append({
                "title": "High disk usage",
                "severity": anomaly["severity"],
                "evidence": f"Disk usage is {value:.1f}%.",
                "possible_cause": (
                    "Large files, accumulated logs, or insufficient "
                    "available storage."
                ),
                "recommended_action": (
                    "Inspect disk usage and large files before removing "
                    "anything."
                ),
                "related_processes": [],
            })

    # 2. Diagnose unhealthy services
    for service in services:
        service_name = service.get("name", "unknown service")
        active_state = service.get("active_state", "unknown")
        health = service.get("health", "UNKNOWN")

        if health == "HEALTHY":
            continue

        if active_state == "failed" or health == "FAILED":
            incidents.append({
                "title": f"Service failure: {service_name}",
                "severity": "ERROR",
                "evidence": (
                    f"{service_name} has active state '{active_state}'."
                ),
                "possible_cause": (
                    "The service may have crashed, failed to start, "
                    "or encountered a configuration problem."
                ),
                "recommended_action": (
                    f"Inspect service logs with: "
                    f"journalctl -u {service_name} -n 50 --no-pager"
                ),
                "related_processes": [],
            })

        elif active_state == "inactive" or health == "INACTIVE":
            incidents.append({
                "title": f"Inactive service: {service_name}",
                "severity": "WARNING",
                "evidence": (
                    f"{service_name} is inactive."
                ),
                "possible_cause": (
                    "The service may be stopped intentionally or may "
                    "not have started when expected."
                ),
                "recommended_action": (
                    f"Check whether the service should be running, "
                    f"then inspect it with: systemctl status {service_name}"
                ),
                "related_processes": [],
            })

        else:
            incidents.append({
                "title": f"Service status unknown: {service_name}",
                "severity": "WARNING",
                "evidence": (
                    f"Service state is '{active_state}'."
                ),
                "possible_cause": (
                    "The service state could not be confirmed."
                ),
                "recommended_action": (
                    f"Inspect the service with: systemctl status "
                    f"{service_name}"
                ),
                "related_processes": [],
            })

    # 3. Diagnose network failures
    for result in network_results:
        if result.get("status") == "CONNECTED":
            continue

        host = result.get("host", "unknown host")
        port = result.get("port", "unknown port")
        status = result.get("status", "UNKNOWN")

        incidents.append({
            "title": f"Network connectivity issue: {host}:{port}",
            "severity": "ERROR",
            "evidence": (
                f"Connection status is {status}."
            ),
            "possible_cause": (
                "The destination may be unavailable, a connection may "
                "be blocked, or the network may be experiencing problems."
            ),
            "recommended_action": (
                f"Verify network connectivity and check whether "
                f"{host}:{port} is reachable."
            ),
            "related_processes": [],
        })

    return incidents

