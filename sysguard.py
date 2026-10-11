
from modules.system import get_system_info
from modules.processes import get_processes, get_top_memory_processes
from modules.services import get_services_status, classify_service_health
from modules.network import check_multiple_connections
from modules.events import record_event, get_event_summary
from modules.anomaly import detect_anomalies
from modules.diagnosis import diagnose_incidents
from modules.healing import restart_service


def main():
    # Module 1: System monitoring
    system = get_system_info()

    # Module 2: Process monitoring
    processes = get_processes()
    top_memory = get_top_memory_processes(processes)

    # Module 3: Service health monitoring
    service_names = [
        "cron.service",
        "rsyslog.service",
        "systemd-resolved.service",
    ]
    services = get_services_status(service_names)

    # Module 4: Network health monitoring
    endpoints = [("example.com", 443)]
    network_results = check_multiple_connections(endpoints)

    # Module 5: Record unhealthy service and network events
    for service in services:
        health = classify_service_health(service)

        if health != "HEALTHY":
            severity = "ERROR" if health == "FAILED" else "WARNING"

            record_event(
                source="service_monitor",
                event_type="SERVICE_HEALTH",
                severity=severity,
                message=f"Service {service['name']} reported {health}",
                details=service,
            )

    for result in network_results:
        if result["status"] != "CONNECTED":
            record_event(
                source="network_monitor",
                event_type="NETWORK_CONNECTIVITY",
                severity="ERROR",
                message=(
                    f"Connection to {result['host']}:{result['port']} "
                    f"reported {result['status']}"
                ),
                details=result,
            )

    # Module 6: Detect resource anomalies
    anomalies = detect_anomalies(system)

    # Module 7: Diagnose potential incidents
    diagnosed_services = []

    for service in services:
        diagnosed_service = service.copy()
        diagnosed_service["health"] = classify_service_health(service)
        diagnosed_services.append(diagnosed_service)

    incidents = diagnose_incidents(
        system_info=system,
        processes=processes,
        services=diagnosed_services,
        network_results=network_results,
        anomalies=anomalies,
    )

    # Module 8: Propose safe recovery actions (dry-run only)
    recovery_plans = []

    for service in diagnosed_services:
        if service["health"] in ("FAILED", "INACTIVE"):
            recovery = restart_service(
                service["name"],
                dry_run=True,
            )
            recovery_plans.append(recovery)

    # Display system information
    print("========== SYSGUARD ==========")

    print("\nSYSTEM INFORMATION")
    print("------------------------------")
    print(f"HOSTNAME      : {system['hostname']}")
    print(f"OS            : {system['os']}")
    print(f"OS VERSION    : {system['os_version']}")
    print(f"CPU USAGE     : {system['cpu_usage']:.1f}%")
    print(f"MEMORY USAGE  : {system['memory_usage']:.1f}%")
    print(f"DISK USAGE    : {system['disk_usage']:.1f}%")
    print(f"UPTIME        : {system['uptime'] / 3600:.2f} hours")

    # Display top memory-consuming processes
    print("\nTOP MEMORY PROCESSES")
    print("------------------------------")

    for process in top_memory:
        print(
            f"PID: {process['pid']:<6} "
            f"NAME: {process['name']:<20} "
            f"MEMORY: {process['memory']:.2f}%"
        )

    # Display service health
    print("\nSERVICE HEALTH")
    print("------------------------------")

    for service in services:
        print(
            f"SERVICE: {service['name']:<28} "
            f"HEALTH: {classify_service_health(service):<8} "
            f"STATE: {service.get('active_state', 'unknown')}"
        )

    # Display network health
    print("\nNETWORK HEALTH")
    print("------------------------------")

    for result in network_results:
        latency = result["latency_ms"]
        latency_text = "N/A" if latency is None else f"{latency:.2f} ms"

        print(
            f"HOST: {result['host']:<18} "
            f"PORT: {result['port']:<5} "
            f"STATUS: {result['status']:<10} "
            f"TIME: {latency_text}"
        )

    # Display anomaly detection
    print("\nANOMALY DETECTION")
    print("------------------------------")

    if anomalies:
        for anomaly in anomalies:
            print(f"WARNING: {anomaly['message']}")
    else:
        print("No resource anomalies detected.")

    # Display incident diagnosis
    print("\nINCIDENT DIAGNOSIS")
    print("------------------------------")

    if incidents:
        for incident in incidents:
            print(f"\nINCIDENT : {incident['title']}")
            print(f"SEVERITY : {incident['severity']}")
            print(f"EVIDENCE : {incident['evidence']}")
            print(f"POSSIBLE CAUSE : {incident['possible_cause']}")
            print(f"ACTION : {incident['recommended_action']}")

            if incident["related_processes"]:
                print(
                    "RELATED PROCESSES : "
                    + ", ".join(incident["related_processes"])
                )
    else:
        print("No incidents requiring diagnosis.")

    # Display self-healing proposals
    print("\nSELF-HEALING")
    print("------------------------------")
    print("Mode: DRY RUN (no services will be restarted)")

    if recovery_plans:
        for recovery in recovery_plans:
            print(f"SERVICE : {recovery['service']}")
            print(f"STATUS  : {recovery['status']}")
            print(f"ACTION  : {recovery['message']}")
    else:
        print("No service recovery actions proposed.")

    # Display event summary
    summary = get_event_summary()

    print("\nEVENT SUMMARY")
    print("------------------------------")
    print(f"TOTAL EVENTS : {summary['total']}")
    print(f"INFO         : {summary['INFO']}")
    print(f"WARNING      : {summary['WARNING']}")
    print(f"ERROR        : {summary['ERROR']}")
    print(f"CRITICAL     : {summary['CRITICAL']}")
    print("==============================")


if __name__ == "__main__":
    main()

