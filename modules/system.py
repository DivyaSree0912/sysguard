
import platform
import time
import psutil


def get_system_info():
    boot_time = psutil.boot_time()
    uptime = time.time() - boot_time

    cpu_usage = max(0.0, psutil.cpu_percent(interval=1))

    return {
        "hostname": platform.node(),
        "os": platform.system(),
        "os_version": platform.release(),
        "cpu_usage": cpu_usage,
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage("/").percent,
        "uptime": uptime,
    }

