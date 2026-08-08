from datetime import datetime

import psutil


def check_uptime():
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time

    total_seconds = int(uptime.total_seconds())
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    return {
        "metric": "uptime",
        "value": total_seconds,
        "unit": "seconds",
        "days": days,
        "hours": hours,
        "minutes": minutes,
    }
