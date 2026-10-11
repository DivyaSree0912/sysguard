import psutil


def get_processes():
    processes = []

    for process in psutil.process_iter(
        ['pid', 'name', 'cpu_percent', 'memory_percent']
    ):
        try:
            info = process.info

            processes.append({
                "pid": info["pid"],
                "name": info["name"],
                "cpu": info["cpu_percent"],
                "memory": info["memory_percent"]
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return processes


def get_top_memory_processes(processes, limit=5):
    return sorted(
        processes,
        key=lambda process: process["memory"],
        reverse=True
    )[:limit]
