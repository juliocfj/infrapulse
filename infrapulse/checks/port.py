import socket


def check_port(host, port, timeout=2):
    reachable = False

    try:
        with socket.create_connection((host, port), timeout=timeout):
            reachable = True
    except OSError:
        reachable = False

    if reachable:
        status = "healthy"
    else:
        status = "critical"

    return {
        "metric": "tcp_port",
        "value": port,
        "unit": "port",
        "status": status,
        "host": host,
        "reachable": reachable,
    }
