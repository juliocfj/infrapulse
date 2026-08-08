import requests


def check_http(url, timeout=3):
    status_code = None
    reachable = False
    response_time_ms = None

    try:
        response = requests.get(url, timeout=timeout)
        status_code = response.status_code
        reachable = True
        response_time_ms = round(response.elapsed.total_seconds() * 1000)
    except requests.RequestException:
        status = "critical"
    else:
        if 200 <= status_code <= 299:
            status = "healthy"
        elif 300 <= status_code <= 399:
            status = "warning"
        else:
            status = "critical"

    return {
        "metric": "http",
        "value": status_code,
        "unit": "status_code",
        "status": status,
        "url": url,
        "reachable": reachable,
        "response_time_ms": response_time_ms,
    }
