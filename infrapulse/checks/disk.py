import psutil


def check_disk():
    disk_usage = psutil.disk_usage("/")
    usage_percent = disk_usage.percent

    if usage_percent < 80:
        status = "healthy"
    elif usage_percent < 90:
        status = "warning"
    else:
        status = "critical"

    return {
        "metric": "disk",
        "value": usage_percent,
        "unit": "%",
        "total_bytes": disk_usage.total,
        "used_bytes": disk_usage.used,
        "free_bytes": disk_usage.free,
        "status": status,
    }
