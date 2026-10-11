
import socket
import time


def check_tcp_connection(host, port, timeout=3):
    """Check whether a TCP connection can be established."""

    start_time = time.perf_counter()

    try:
        with socket.create_connection(
            (host, port),
            timeout=timeout,
        ):
            latency_ms = (time.perf_counter() - start_time) * 1000

            return {
                "host": host,
                "port": port,
                "status": "CONNECTED",
                "latency_ms": round(latency_ms, 2),
            }

    except (socket.timeout, TimeoutError):
        return {
            "host": host,
            "port": port,
            "status": "TIMEOUT",
            "latency_ms": None,
        }

    except OSError as error:
        return {
            "host": host,
            "port": port,
            "status": "FAILED",
            "latency_ms": None,
            "error": str(error),
        }

def check_multiple_connections(endpoints, timeout=3):
    """Check the TCP connectivity of multiple endpoints."""

    results = []

    for host, port in endpoints:
        result = check_tcp_connection(host, port, timeout)
        results.append(result)

    return results
