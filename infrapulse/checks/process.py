import psutil


def check_process(process_name):
    target_name = process_name.lower()
    running = False

    for process in psutil.process_iter(["name"]):
        try:
            current_name = process.info["name"]
            if current_name and current_name.lower() == target_name:
                running = True
                break
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue

    if running:
        status = "healthy"
    else:
        status = "critical"

    return {
        "metric": "process",
        "value": process_name,
        "unit": "state",
        "status": status,
        "running": running,
    }
