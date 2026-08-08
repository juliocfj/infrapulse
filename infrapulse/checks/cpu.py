import psutil


def check_cpu():
    usage_percent = psutil.cpu_percent(interval=1)

    if usage_percent < 70:
        status = "healthy"
    elif usage_percent < 90:
        status = "warning"
    else:
        status = "critical"

    return {
        "metric": "cpu_usage",
        "usage_percent": usage_percent,
        "status": status,
    }
