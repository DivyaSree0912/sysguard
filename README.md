# SysGuard — Linux System Monitoring & Safe Self-Healing Platform

SysGuard is a Python-based Linux monitoring and incident-diagnosis platform designed to identify resource anomalies, inspect service health, detect network connectivity issues, and recommend safe recovery actions.

The project demonstrates practical systems programming concepts, Linux service management, observability, automated testing, and defensive recovery design.

## Features

- **System Monitoring:** Collects CPU, memory, disk usage, OS information, and uptime.
- **Process Monitoring:** Lists running processes and identifies top memory consumers.
- **Service Health Monitoring:** Inspects Linux systemd services and classifies their health.
- **Network Monitoring:** Checks TCP connectivity and measures connection latency.
- **Event Logging:** Stores structured events in JSON Lines format.
- **Anomaly Detection:** Flags resource readings that exceed configurable thresholds.
- **Incident Diagnosis:** Uses rule-based logic to suggest potential causes and troubleshooting actions.
- **Safe Self-Healing:** Supports dry-run recovery proposals, service allowlisting, explicit approval, and post-action verification.
- **Automated Tests:** Uses Python's built-in `unittest` framework to verify core functionality and safety safeguards.

## Architecture

```text
System and Process Monitoring
            |
            v
Service and Network Health Checks
            |
            v
       Event Logging
            |
            v
     Anomaly Detection
            |
            v
     Incident Diagnosis
            |
            v
 Safe Recovery Proposals
            |
            v
       CLI Dashboard
```

## Technology Stack

- Python
- Linux and systemd
- psutil
- TCP sockets
- JSON Lines event storage
- unittest

## Requirements

- Python 3.10 or later
- Linux environment with systemd for service monitoring
- Network access for external connectivity checks

SysGuard has been developed and tested in Ubuntu running under WSL2. Service availability and permissions may differ between Linux distributions and environments.

## Setup

Clone the repository and enter the project directory:

```bash
git clone https://github.com/DivyaSree0912/sysguard.git
cd sysguard
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run SysGuard

```bash
python sysguard.py
```

The dashboard reports system resources, processes, service health, network connectivity, detected anomalies, incident diagnoses, recovery proposals, and event summaries.

## Run Tests

```bash
python -m unittest discover -s tests -v
```

Compile-check the project:

```bash
python -m compileall -q modules tests sysguard.py
```

## Safety

Service recovery operates in dry-run mode by default. Restart attempts are restricted to an explicit service allowlist and require explicit approval when dry-run mode is disabled.

Actual service restarts can require operating-system authorization. SysGuard does not bypass those permissions. Review the proposed action and its impact before authorizing a recovery operation.

## Current Limitations

- Incident diagnosis is rule-based, not an AI model.
- Event history is stored locally in a JSON Lines file.
- Network checks currently use configured endpoints.
- Recovery actions are limited to approved systemd services.
- Monitoring and recovery behavior depends on the permissions and capabilities of the host environment.

## Future Improvements

- Add configurable monitoring thresholds.
- Introduce event deduplication and alert cooldowns.
- Add automated log ingestion and richer incident evidence.
- Expand tests for timeouts, permission failures, and malformed inputs.
- Add structured reporting and continuous integration.

## Author

**Divya Sree**

Developed as a systems engineering project to explore Linux monitoring, incident diagnosis, observability, and safe automated recovery.
