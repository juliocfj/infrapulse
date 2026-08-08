import psutil


def check_memory():
    usage_percent = psutil.virtual_memory().percent

    if usage_percent < 75:
        status = "healthy"
    elif usage_percent < 90:
        status = "warning"
    else:
        status = "critical"

    return {
        "metric": "memory",
        "value": usage_percent,
        "unit": "%",
        "status": status,
    }
