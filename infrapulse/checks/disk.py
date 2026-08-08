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
        "metric": "disk_usage",
        "usage_percent": usage_percent,
        "total_space": disk_usage.total,
        "used_space": disk_usage.used,
        "free_space": disk_usage.free,
        "status": status,
    }
